from __future__ import annotations

import base64
import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.ai_brain import RISK_COLUMNS, predict_environmental_risk, train_ai_brain
from src.data_pipeline import (
    apply_what_if_controls,
    expected_api_schema,
    generate_environmental_data,
    prototype_api_contracts,
)
from src.recommendations import build_recommendations, explain_prediction, make_action_table, ranked_hazards
from src.rl_agent import ContextualBandit

APP_DIR = Path(__file__).resolve().parent
AUTHOR = "Angad Singh"
MENTOR = "Dr. Qingyang Xiao"

st.set_page_config(
    page_title="AI Environmental Suggestion App",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    css_path = APP_DIR / "styles" / "lovable_streamlit.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def image_data_uri(path: Path) -> str:
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def risk_tone(score: float) -> tuple[str, str, str]:
    if score >= 75:
        return "#dc5d55", "#fdeae7", "Severe"
    if score >= 55:
        return "#e8903e", "#fff0df", "High"
    if score >= 35:
        return "#d3a52e", "#fff7dc", "Moderate"
    return "#3ba86a", "#e7f8ec", "Low"


def kpi_card(icon: str, label: str, value: str, hint: str, tone: str, soft: str) -> str:
    return f"""
    <div class="kpi-card" style="--tone:{tone};--soft:{soft};--tint:{tone};">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-value">{html.escape(value)}</div>
      <div class="kpi-label">{html.escape(label)}</div>
      <div class="kpi-hint">{html.escape(hint)}</div>
    </div>
    """


def risk_bar_html(hazard_scores: list[tuple[str, float]]) -> str:
    rows = []
    for hazard, score in hazard_scores:
        score = max(0.0, min(100.0, float(score)))
        rows.append(
            f"""
            <div class="risk-row">
              <div class="risk-name">{html.escape(hazard)}</div>
              <div class="risk-track"><div class="risk-fill" style="width:{score:.1f}%"></div></div>
              <div class="risk-score">{score:.0f}</div>
            </div>
            """
        )
    return "<div class='risk-list'>" + "".join(rows) + "</div>"


def action_card(action: str, rank: int) -> str:
    if action.startswith("[") and "]" in action:
        tag, body = action.split("]", 1)
        tag = tag[1:]
        body = body.strip()
    else:
        tag, body = f"Action {rank}", action
    return f"""
    <div class="action-card">
      <div class="action-top"><span class="action-chip">{html.escape(tag)}</span></div>
      <div class="action-text"><strong>{rank}.</strong> {html.escape(body)}</div>
    </div>
    """


def make_risk_chart(pred: pd.DataFrame) -> go.Figure:
    risk_plot_df = pred[["timestamp", *[f"pred_{c}" for c in RISK_COLUMNS]]].melt(
        id_vars="timestamp", var_name="risk_type", value_name="risk_score"
    )
    risk_plot_df["risk_type"] = (
        risk_plot_df["risk_type"]
        .str.replace("pred_", "", regex=False)
        .str.replace("_risk_score", "", regex=False)
        .str.replace("_", " ", regex=False)
        .str.title()
    )
    fig = px.area(
        risk_plot_df,
        x="timestamp",
        y="risk_score",
        color="risk_type",
        line_group="risk_type",
        markers=True,
        title=None,
    )
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=15, b=10),
        legend_title_text="Hazard",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        font=dict(color="#35544a"),
    )
    fig.update_xaxes(showgrid=False, title=None)
    fig.update_yaxes(range=[0, 100], title="Risk score", gridcolor="rgba(45,100,78,.10)")
    return fig


def make_cluster_chart(profile: pd.DataFrame) -> go.Figure:
    plot_df = profile[
        [
            "cluster_name",
            "flood_risk_score",
            "heat_risk_score",
            "cold_risk_score",
            "acid_rain_risk_score",
            "air_quality_risk_score",
        ]
    ].melt(id_vars="cluster_name", var_name="risk_type", value_name="average_score")
    plot_df["risk_type"] = (
        plot_df["risk_type"]
        .str.replace("_risk_score", "", regex=False)
        .str.replace("_", " ", regex=False)
        .str.title()
    )
    fig = px.bar(plot_df, x="cluster_name", y="average_score", color="risk_type", barmode="group")
    fig.update_layout(
        height=410,
        margin=dict(l=10, r=10, t=15, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Hazard",
        font=dict(color="#35544a"),
    )
    fig.update_xaxes(title=None, showgrid=False)
    fig.update_yaxes(range=[0, 100], title="Average risk score", gridcolor="rgba(45,100,78,.10)")
    return fig


load_css()


@st.cache_data(show_spinner=False)
def load_demo_data() -> pd.DataFrame:
    return generate_environmental_data(n_days=540, start_date="2025-01-01", seed=17)


@st.cache_resource(show_spinner=True)
def cached_train_model(df: pd.DataFrame):
    return train_ai_brain(df, random_state=42, n_clusters=4)


def prepare_uploaded_data(uploaded_file) -> pd.DataFrame:
    data = pd.read_csv(uploaded_file)
    if "timestamp" in data.columns:
        data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data


# Sidebar — Lovable-inspired workspace panel
with st.sidebar:
    st.markdown(
        f"""
        <div class="brand-card">
          <div class="brand-row">
            <div class="brand-icon">🌱</div>
            <div>
              <div class="brand-title">AI Environmental<br/>Suggestion App</div>
              <div class="brand-tag">Greener, safer, together</div>
            </div>
          </div>
        </div>
        <div class="team-card">
          <div class="team-label">Author</div><div class="team-name">{AUTHOR}</div>
          <div class="team-label">Mentor</div><div class="team-name">{MENTOR}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Prototype controls")
    uploaded = st.file_uploader("Optional CSV with prototype schema", type=["csv"])
    user_type = st.selectbox("User group", ["Farmer", "Resident", "Local Government"])
    forecast_window = st.slider("Rows to view", min_value=7, max_value=45, value=21, step=7)

    st.divider()
    st.markdown("### What-if scenario")
    temp_delta = st.slider("Temperature change (°C)", -10.0, 12.0, 0.0, 0.5)
    rainfall_multiplier = st.slider("Rainfall multiplier", 0.0, 3.0, 1.0, 0.1)
    pm25_delta = st.slider("PM2.5 change (µg/m³)", -20.0, 60.0, 0.0, 1.0)
    traffic_delta = st.slider("Traffic change (0–100 index)", -50.0, 50.0, 0.0, 1.0)

try:
    df = prepare_uploaded_data(uploaded) if uploaded else load_demo_data()
except Exception as exc:
    st.error(f"Could not load uploaded data, so the app is using demo data. Upload error: {exc}")
    df = load_demo_data()

needed_risk_cols = set(RISK_COLUMNS + ["primary_hazard", "overall_risk_score"])
if not needed_risk_cols.issubset(df.columns):
    st.warning(
        "Uploaded data is missing training labels, so the prototype is using demo data for model training. "
        "Use the API Schema tab to match the expected fields."
    )
    df = load_demo_data()

bundle = cached_train_model(df)
available_districts = sorted(df["district"].dropna().unique().tolist())
with st.sidebar:
    district = st.selectbox("District / community area", available_districts)
    st.markdown("<span class='status-pill'>● AI brain ready</span>", unsafe_allow_html=True)

selected = df[df["district"] == district].sort_values("timestamp").tail(forecast_window).copy()
scenario = apply_what_if_controls(selected, temp_delta, rainfall_multiplier, pm25_delta, traffic_delta)
pred = predict_environmental_risk(bundle, scenario)
latest = pred.sort_values("timestamp").iloc[-1]

map_base = df.sort_values("timestamp").groupby("district", as_index=False).tail(1).copy()
map_scenario = apply_what_if_controls(map_base, temp_delta, rainfall_multiplier, pm25_delta, traffic_delta)
map_pred = predict_environmental_risk(bundle, map_scenario)

if "bandit" not in st.session_state:
    st.session_state.bandit = ContextualBandit(epsilon=0.05, alpha=0.35, seed=123)

banner_uri = image_data_uri(APP_DIR / "assets" / "dashboard-banner.jpg")
st.markdown(
    f"""
    <section class="hero-shell" style="background-image:url('{banner_uri}')">
      <div class="hero-glow"></div>
      <div class="hero-copy">
        <div class="hero-kicker">✦ AI environmental intelligence prototype</div>
        <div class="hero-title">AI Environmental Suggestion App</div>
        <div class="hero-sub">
          Weather, flooding, acid rain, air quality, crop conditions and traffic translated into
          practical AI-guided actions for farmers, residents and local government.
        </div>
        <div class="hero-badges">
          <span class="hero-badge">Author · {AUTHOR}</span>
          <span class="hero-badge">Mentor · {MENTOR}</span>
          <span class="hero-badge">Python 3.12 · Colab · Streamlit</span>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# Audience/location context row
st.markdown(
    f"<span class='status-pill'>👤 {html.escape(user_type)}</span> &nbsp; "
    f"<span class='status-pill'>📍 {html.escape(str(district))}</span> &nbsp; "
    f"<span class='status-pill'>🧪 What-if scenario active</span>",
    unsafe_allow_html=True,
)

(tab_dashboard, tab_suggestions, tab_clusters, tab_pipeline, tab_api, tab_about) = st.tabs(
    ["Dashboard", "AI Suggestions + RL", "Clustering", "AI Pipeline", "API Schema", "About"]
)

with tab_dashboard:
    st.markdown(f"<div class='section-title'>Current risk snapshot for {html.escape(str(district))}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-caption'>Live-style prototype view generated from the selected scenario and trained AI models.</div>", unsafe_allow_html=True)

    score = float(latest["pred_overall_risk_score"])
    tone, soft, band = risk_tone(score)
    primary = str(latest["primary_hazard_score_based"])
    classifier = str(latest["primary_hazard_classifier"])
    cluster = int(latest["cluster"])
    cards = "".join(
        [
            kpi_card("⚠", "Overall risk", f"{score:.1f}/100", f"{band} risk", tone, soft),
            kpi_card("🌦", "Primary hazard", primary, "score-based AI", "#2f8fca", "#e8f4fb"),
            kpi_card("🧠", "ML classifier", classifier, "supervised model", "#8d64d9", "#f1ebfb"),
            kpi_card("◉", "Environmental cluster", f"Cluster {cluster}", "unsupervised pattern", "#2e9b69", "#e7f7ee"),
        ]
    )
    st.markdown(f"<div class='kpi-grid'>{cards}</div>", unsafe_allow_html=True)

    left, right = st.columns([1.8, 1], gap="large")
    with left:
        st.markdown("#### Risk trend")
        st.plotly_chart(make_risk_chart(pred), use_container_width=True, config={"displayModeBar": False})
    with right:
        hazards = ranked_hazards(latest)[:5]
        st.markdown(
            f"""
            <div class="lovable-panel">
              <h3>AI risk brief</h3>
              <div class="muted">{html.escape(explain_prediction(latest))}</div>
              {risk_bar_html(hazards)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        with st.container(border=True):
            st.markdown("**Prototype goal assistant**")
            goal = st.text_input(
                "Ask about a local environmental goal",
                placeholder="e.g., protect seedlings from heavy rain",
                label_visibility="collapsed",
                key="goal_prompt",
            )
            if goal:
                goal_l = goal.lower()
                actions = build_recommendations(latest, user_type=user_type, max_actions=6)
                matched = [a for a in actions if any(token in a.lower() for token in goal_l.split() if len(token) > 3)]
                response = matched[0] if matched else actions[0]
                st.success(response)

    st.markdown("#### Community map")
    st.caption("Latest model-estimated risk across all demo districts under the selected what-if controls.")
    st.map(map_pred.rename(columns={"pred_overall_risk_score": "risk"})[["lat", "lon", "risk"]])

    with st.expander("Latest scenario observations"):
        show_cols = [
            "timestamp",
            "district",
            "temperature_c",
            "rainfall_mm",
            "river_level_m",
            "rain_ph",
            "pm25_ugm3",
            "traffic_congestion_idx",
            "pred_overall_risk_score",
            "pred_risk_level",
            "primary_hazard_score_based",
            "cluster",
        ]
        st.dataframe(pred[show_cols].tail(10), use_container_width=True, hide_index=True)

with tab_suggestions:
    st.markdown("<div class='section-title'>Tailored AI environmental suggestions</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='section-caption'>Actions are ranked for <strong>{html.escape(user_type)}</strong> using the current model output; user feedback updates a contextual-bandit RL policy.</div>",
        unsafe_allow_html=True,
    )

    actions = build_recommendations(latest, user_type=user_type, max_actions=6)
    primary_hazard = str(latest["primary_hazard_score_based"])
    chosen_action = st.session_state.bandit.choose_action(user_type, primary_hazard, actions)

    first_col, feedback_col = st.columns([1.55, 1], gap="large")
    with first_col:
        st.markdown(
            f"""
            <div class="lovable-panel">
              <h3>✦ Recommended first action</h3>
              <div class="muted">RL policy selection for {html.escape(user_type)} · {html.escape(primary_hazard)}</div>
              <div style="margin-top:14px;font-size:1.02rem;line-height:1.55;font-weight:750;">{html.escape(chosen_action)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with feedback_col:
        with st.container(border=True):
            st.markdown("**Teach the RL policy**")
            rating = st.slider("How useful was this recommendation?", 1, 5, 4)
            if st.button("Submit feedback and learn", use_container_width=True):
                reward = (rating - 1) / 4
                q_value = st.session_state.bandit.update(user_type, primary_hazard, chosen_action, reward)
                st.success(f"Feedback stored. Updated policy value: {q_value:.3f}")

    st.markdown("#### Suggested action feed")
    for idx, action in enumerate(actions, start=1):
        st.markdown(action_card(action, idx), unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("#### Top hazards")
        st.dataframe(pd.DataFrame(ranked_hazards(latest), columns=["hazard", "risk_score"]), hide_index=True, use_container_width=True)
    with col_b:
        st.markdown("#### Current RL policy table")
        st.dataframe(st.session_state.bandit.policy_table(), hide_index=True, use_container_width=True)

    with st.expander("Suggestions for every audience"):
        st.dataframe(make_action_table(latest), hide_index=True, use_container_width=True)

with tab_clusters:
    st.markdown("<div class='section-title'>Environmental pattern clustering</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Unsupervised learning groups days and places with similar weather, pollution, traffic, crop and sensor patterns.</div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(make_cluster_chart(bundle.cluster_profiles), use_container_width=True, config={"displayModeBar": False})
    st.dataframe(bundle.cluster_profiles, use_container_width=True, hide_index=True)

with tab_pipeline:
    st.markdown("<div class='section-title'>Prototype AI brain pipeline</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Lovable-style visual workflow showing how the prototype turns local data into forecasts, clusters and adaptive recommendations.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="pipeline-grid">
          <div class="pipeline-card"><div class="pipeline-num">01</div><h4>APIs & sensors</h4><p>Weather forecasts, river and soil sensors, rain pH, air quality and traffic feeds.</p></div>
          <div class="pipeline-card"><div class="pipeline-num">02</div><h4>Data engineering</h4><p>Normalize timestamps, locations, crop context and numerical environmental features.</p></div>
          <div class="pipeline-card"><div class="pipeline-num">03</div><h4>ML + DNN</h4><p>Supervised classification and multi-output risk forecasting, plus nonlinear neural-network learning.</p></div>
          <div class="pipeline-card"><div class="pipeline-num">04</div><h4>Clusters + RL</h4><p>Discover recurring patterns and learn which recommended action works best from user feedback.</p></div>
          <div class="pipeline-card"><div class="pipeline-num">05</div><h4>Decision support</h4><p>Dashboard, risk scores, maps, action suggestions and stakeholder-specific preparedness guidance.</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("#### Model evaluation")
        st.dataframe(pd.DataFrame([bundle.metrics]).T.rename(columns={0: "value"}), use_container_width=True)
    with c2:
        st.markdown("#### Model inputs and outputs")
        with st.container(border=True):
            st.markdown("**Feature columns**")
            st.write(", ".join(bundle.feature_columns))
            st.markdown("**Risk target columns**")
            st.write(", ".join(bundle.risk_columns))

with tab_api:
    st.markdown("<div class='section-title'>Production API schema</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-caption'>Keep these normalized fields stable when replacing the demo generator with real weather, sensor, air-quality and traffic APIs.</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(expected_api_schema(), hide_index=True, use_container_width=True)
    st.markdown("#### Prototype API contracts")
    contracts = [spec.__dict__ for spec in prototype_api_contracts()]
    st.dataframe(pd.DataFrame(contracts), hide_index=True, use_container_width=True)
    st.info(
        "Recommended production step: implement four adapters — weather forecast, local environmental sensors, air quality, and traffic — "
        "then map each response into the schema above so the AI pipeline remains unchanged."
    )

with tab_about:
    st.markdown("<div class='section-title'>Project team & prototype scope</div>", unsafe_allow_html=True)
    a, m = st.columns(2, gap="large")
    with a:
        st.markdown(
            f"<div class='about-card'><div class='about-role'>Author</div><div class='about-name'>{AUTHOR}</div><p>Student developer and project author for the AI Environmental Suggestion App prototype.</p></div>",
            unsafe_allow_html=True,
        )
    with m:
        st.markdown(
            f"<div class='about-card'><div class='about-role'>Mentor</div><div class='about-name'>{MENTOR}</div><p>Project mentor and advisor supporting the AI architecture, modeling workflow and deployment strategy.</p></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(
        """
        ### What this prototype demonstrates
        This educational prototype combines synthetic/local environmental data with supervised machine learning,
        a multi-layer neural network, clustering and contextual-bandit reinforcement learning. The Streamlit interface
        has been migrated from the supplied Lovable React/Tailwind visual concept while keeping the Python AI stack
        deployable on Streamlit Community Cloud.

        **Intended audiences:** farmers, local residents and local government teams.  
        **Intended uses:** environmental awareness, scenario exploration, preparedness planning and educational demonstrations.
        """
    )
    st.warning(
        "Prototype only: do not use this app as a replacement for official emergency alerts, medical/public-health guidance, "
        "agronomist recommendations, engineering decisions, or local-government emergency procedures."
    )

st.markdown(
    f"<div class='footer-note'>AI Environmental Suggestion App · Author: {AUTHOR} · Mentor: {MENTOR} · Lovable UI migrated to Streamlit</div>",
    unsafe_allow_html=True,
)

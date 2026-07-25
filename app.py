from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ai_brain import RISK_COLUMNS, predict_environmental_risk, train_ai_brain
from src.data_pipeline import (
    DISTRICT_METADATA,
    apply_what_if_controls,
    expected_api_schema,
    generate_environmental_data,
    prototype_api_contracts,
)
from src.recommendations import build_recommendations, explain_prediction, make_action_table, ranked_hazards
from src.rl_agent import ContextualBandit

st.set_page_config(
    page_title="AI Environmental Suggestion App",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 AI Environmental Suggestion App")
st.caption("Prototype dashboard for farmers, residents, and local government: weather, flooding, acid rain, air quality, crop risk, traffic, AI suggestions, clustering, and feedback learning.")


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


with st.sidebar:
    st.header("Prototype controls")
    st.markdown("**Author:** Angad Singh")
    st.markdown("**Mentor:** Dr. Qingyang Xiao")
    st.divider()
    uploaded = st.file_uploader("Optional: upload data with the prototype schema", type=["csv"])
    user_type = st.selectbox("User group", ["Farmer", "Resident", "Local Government"])
    forecast_window = st.slider("Rows to view for selected district", min_value=7, max_value=45, value=21, step=7)
    st.divider()
    st.subheader("What-if scenario")
    temp_delta = st.slider("Temperature change (°C)", -10.0, 12.0, 0.0, 0.5)
    rainfall_multiplier = st.slider("Rainfall multiplier", 0.0, 3.0, 1.0, 0.1)
    pm25_delta = st.slider("PM2.5 change (µg/m³)", -20.0, 60.0, 0.0, 1.0)
    traffic_delta = st.slider("Traffic change (0-100 index)", -50.0, 50.0, 0.0, 1.0)

try:
    df = prepare_uploaded_data(uploaded) if uploaded else load_demo_data()
except Exception as exc:
    st.error(f"Could not load uploaded data, so the app is using demo data. Upload error: {exc}")
    df = load_demo_data()

needed_risk_cols = set(RISK_COLUMNS + ["primary_hazard", "overall_risk_score"])
if not needed_risk_cols.issubset(df.columns):
    st.warning("Uploaded data is missing training labels, so the prototype is using demo data for model training. Use the API Schema tab to match the expected fields.")
    df = load_demo_data()

bundle = cached_train_model(df)

available_districts = sorted(df["district"].dropna().unique().tolist())
with st.sidebar:
    district = st.selectbox("District / community area", available_districts)

selected = df[df["district"] == district].sort_values("timestamp").tail(forecast_window).copy()
scenario = apply_what_if_controls(selected, temp_delta, rainfall_multiplier, pm25_delta, traffic_delta)
pred = predict_environmental_risk(bundle, scenario)
latest = pred.sort_values("timestamp").iloc[-1]

if "bandit" not in st.session_state:
    st.session_state.bandit = ContextualBandit(epsilon=0.05, alpha=0.35, seed=123)

tab_dashboard, tab_suggestions, tab_clusters, tab_pipeline, tab_api, tab_about = st.tabs(
    ["Dashboard", "AI Suggestions + RL", "Clustering", "AI Pipeline", "API Schema", "About"]
)

with tab_dashboard:
    st.subheader(f"Current risk snapshot for {district}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall risk", f"{latest['pred_overall_risk_score']:.1f}/100", latest["pred_risk_level"])
    c2.metric("Primary hazard", str(latest["primary_hazard_score_based"]), "score-based")
    c3.metric("Classifier hazard", str(latest["primary_hazard_classifier"]), "supervised ML")
    c4.metric("Cluster", int(latest["cluster"]))

    risk_plot_df = pred[["timestamp", *[f"pred_{c}" for c in RISK_COLUMNS]]].melt(
        id_vars="timestamp", var_name="risk_type", value_name="risk_score"
    )
    risk_plot_df["risk_type"] = risk_plot_df["risk_type"].str.replace("pred_", "", regex=False).str.replace("_risk_score", "", regex=False).str.replace("_", " ").str.title()
    fig = px.line(risk_plot_df, x="timestamp", y="risk_score", color="risk_type", markers=True, title="Predicted environmental risk by hazard")
    fig.update_yaxes(range=[0, 100], title="Risk score")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Local map view")
    latest_by_district = pred.groupby("district", as_index=False).tail(1).copy()
    st.map(latest_by_district.rename(columns={"pred_overall_risk_score": "risk"})[["lat", "lon", "risk"]])

    with st.expander("Latest scenario data"):
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
    st.subheader("AI-generated suggestions")
    st.info(explain_prediction(latest))
    actions = build_recommendations(latest, user_type=user_type, max_actions=6)
    primary_hazard = str(latest["primary_hazard_score_based"])
    chosen_action = st.session_state.bandit.choose_action(user_type, primary_hazard, actions)

    st.markdown("**Recommended first action from reinforcement-learning policy**")
    st.success(chosen_action)

    st.markdown("**Full recommendation list**")
    for idx, action in enumerate(actions, start=1):
        st.write(f"{idx}. {action}")

    rating = st.slider("How useful was the first recommendation?", 1, 5, 4)
    if st.button("Submit feedback and update RL policy"):
        reward = (rating - 1) / 4
        q_value = st.session_state.bandit.update(user_type, primary_hazard, chosen_action, reward)
        st.success(f"Feedback stored. Updated policy value: {q_value:.3f}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Top hazards**")
        st.dataframe(pd.DataFrame(ranked_hazards(latest), columns=["hazard", "risk_score"]), hide_index=True, use_container_width=True)
    with col_b:
        st.markdown("**Current RL policy table**")
        st.dataframe(st.session_state.bandit.policy_table(), hide_index=True, use_container_width=True)

    with st.expander("Suggestions for all user groups"):
        st.dataframe(make_action_table(latest), hide_index=True, use_container_width=True)

with tab_clusters:
    st.subheader("Environmental clustering")
    st.write("The clustering model groups locations and days with similar weather, pollution, traffic, crop, and sensor patterns.")
    st.dataframe(bundle.cluster_profiles, use_container_width=True, hide_index=True)

    profile = bundle.cluster_profiles.copy()
    profile_plot = profile[["cluster_name", "flood_risk_score", "heat_risk_score", "cold_risk_score", "acid_rain_risk_score", "air_quality_risk_score"]].melt(
        id_vars="cluster_name", var_name="risk_type", value_name="average_score"
    )
    profile_plot["risk_type"] = profile_plot["risk_type"].str.replace("_risk_score", "", regex=False).str.replace("_", " ").str.title()
    fig_cluster = px.bar(profile_plot, x="cluster_name", y="average_score", color="risk_type", barmode="group", title="Average hazard profile by cluster")
    fig_cluster.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_cluster, use_container_width=True)

with tab_pipeline:
    st.subheader("Prototype AI brain")
    st.markdown(
        """
        **Supervised machine learning** predicts the primary hazard class and multi-hazard risk scores from labeled historical data.  
        **Deep neural network** uses a multi-layer perceptron to learn nonlinear relationships across weather, sensors, crops, and traffic.  
        **Clustering** identifies recurring local environmental patterns.  
        **Reinforcement learning** uses user feedback to improve which suggestion is shown first for each user group and hazard context.
        """
    )
    st.dataframe(pd.DataFrame([bundle.metrics]).T.rename(columns={0: "value"}), use_container_width=True)
    st.markdown("**Feature columns**")
    st.write(", ".join(bundle.feature_columns))
    st.markdown("**Risk target columns**")
    st.write(", ".join(bundle.risk_columns))

with tab_api:
    st.subheader("API integration schema")
    st.write("Use this schema for real API adapters. The prototype demo generator already returns this structure.")
    st.dataframe(expected_api_schema(), hide_index=True, use_container_width=True)
    st.markdown("**Prototype API contracts**")
    contracts = [spec.__dict__ for spec in prototype_api_contracts()]
    st.dataframe(pd.DataFrame(contracts), hide_index=True, use_container_width=True)
    st.markdown(
        """
        Suggested next production step: replace the demo generator with four adapters: weather forecast, local environmental sensors, air-quality, and traffic. Keep the output columns stable so the AI pipeline does not need to change.
        """
    )

with tab_about:
    st.subheader("Project team")
    st.markdown("### AI Environmental Suggestion App")
    col_author, col_mentor = st.columns(2)
    with col_author:
        st.markdown("**Author**")
        st.write("Angad Singh")
    with col_mentor:
        st.markdown("**Mentor**")
        st.write("Dr. Qingyang Xiao")

    st.markdown("---")
    st.markdown(
        """
        This educational prototype demonstrates how weather, flooding, acid-rain, air-quality,
        crop, community-vulnerability, and traffic data can support farmers, residents, and local
        government teams. It combines supervised machine learning, a neural-network model,
        environmental clustering, and feedback-based reinforcement learning.

        **Prototype notice:** The dashboard is for research and education. Users should follow
        official emergency alerts and qualified agricultural, environmental, and public-health guidance.
        """
    )

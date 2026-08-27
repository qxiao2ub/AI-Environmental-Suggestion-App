# AI Environmental Suggestion App

A Python 3.12-compatible educational prototype that turns local environmental signals into AI-assisted risk forecasts, clustering, and stakeholder-specific preparedness suggestions.

## Project team

- **Author:** Angad Singh
- **Mentor:** Dr. Qingyang Xiao

## Lovable UI migration

The supplied Lovable React/Tailwind design has been migrated into the Streamlit app while keeping the original Python AI pipeline intact. The migration includes:

- Environmental hero artwork and green/blue visual language
- Mesh-style background and rounded dashboard panels
- Lovable-inspired KPI cards, risk panels, action cards, tab styling, and gradients
- Responsive Streamlit sidebar with author/mentor credits and scenario controls
- AI suggestion feed adapted to the real prototype recommendation engine
- Pipeline, clustering, API schema, and reinforcement-learning views

The original supplied `src/` UI package is preserved in `lovable_ui_source/src/` for reference. The deployed app does **not** need Node.js or React; Streamlit runs directly from `app.py`.

## AI functionality

- **Supervised machine learning:** predicts the primary environmental hazard and risk scores from labeled historical/demo data.
- **Deep learning / neural network:** a multi-layer perceptron learns nonlinear relationships across weather, sensors, crops, pollution and traffic.
- **Clustering:** groups recurring local environmental conditions into interpretable risk profiles.
- **Reinforcement learning:** a contextual bandit learns which recommendation should appear first using user usefulness feedback.
- **What-if simulation:** adjusts temperature, rainfall, PM2.5 and traffic to explore possible future conditions.

## Main audiences

- Farmers: flooding, crop/seed exposure, heat/cold, air quality and acid-rain preparedness
- Residents: extreme-weather, air-quality and senior/community preparedness
- Local government: operational readiness, public alerts, road access, cooling/warming centers and sensor deployment

## Repository structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── assets/
│   └── dashboard-banner.jpg
├── styles/
│   └── lovable_streamlit.css
├── data/
│   └── sample_environmental_data.csv
├── notebooks/
│   └── environmental_suggestion_ai_brain_colab.ipynb
├── src/
│   ├── __init__.py
│   ├── ai_brain.py
│   ├── data_pipeline.py
│   ├── recommendations.py
│   └── rl_agent.py
└── lovable_ui_source/
    ├── README.md
    └── src/                  # original supplied Lovable UI source
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create or open the GitHub repository for this project.
2. Put `app.py`, `requirements.txt`, `src/`, `assets/`, `styles/`, `data/`, and `.streamlit/` at the repository root.
3. In Streamlit Community Cloud, select the repository and choose `app.py` as the entrypoint.
4. Use a Python 3.12 runtime when available.
5. Deploy.

No API key is required for the demo mode.

## Connect real APIs later

Replace the demo generator with adapters that normalize external responses into the existing schema:

- Weather: temperature, humidity, rainfall and wind speed
- Local sensors: river level, soil moisture, soil pH and rain pH
- Air quality: PM2.5, ozone, NO2 and SO2
- Traffic: congestion index and future road-closure signals
- Farm/community profile: district, crop type, crop stage and vulnerability indicators

Keeping the normalized columns stable means the model and Streamlit layers do not need to be redesigned when live APIs are added.

## Safety note

This is an educational decision-support prototype. It must not replace official emergency alerts, public-health guidance, agronomist advice, engineering decisions, or local-government emergency procedures.

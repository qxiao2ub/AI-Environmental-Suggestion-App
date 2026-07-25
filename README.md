# AI Environmental Suggestion App Prototype

This repository contains a student-friendly prototype for an AI-based Environmental Suggestion App. It is designed for local farmers, residents, and local government teams that need early environmental risk awareness and practical action suggestions.


## Project team

- **Author:** Angad Singh
- **Mentor:** Dr. Qingyang Xiao

## What the prototype does

- Generates realistic demo data for weather, flooding, acid rain, air quality, crop status, senior vulnerability, and traffic.
- Trains supervised machine-learning models to predict primary environmental hazards and multi-hazard risk scores.
- Trains a deep-neural-network style multi-layer perceptron to learn nonlinear risk patterns.
- Clusters local environmental patterns into recurring risk profiles.
- Uses a lightweight reinforcement-learning contextual bandit to improve which recommendation appears first based on user feedback.
- Runs as a Streamlit dashboard that can be uploaded to GitHub and deployed.

## Project structure

```text
environmental_suggestion_app/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── data/
│   └── sample_environmental_data.csv
└── src/
    ├── __init__.py
    ├── ai_brain.py
    ├── data_pipeline.py
    ├── recommendations.py
    └── rl_agent.py
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload all files from this folder to the repository root.
3. Go to Streamlit Community Cloud and create a new app.
4. Select your GitHub repository, branch, and `app.py` as the entrypoint file.
5. In Advanced settings, select Python 3.12 if the option appears.
6. Deploy.

## Replace demo data with real APIs

The app currently calls `generate_environmental_data()` so it can run without API keys. For production, replace that step with API adapters that output the same columns:

- Weather forecast: `temperature_c`, `humidity_pct`, `rainfall_mm`, `wind_speed_kph`
- Local sensors: `river_level_m`, `soil_moisture_pct`, `soil_ph`, `rain_ph`
- Air quality: `pm25_ugm3`, `ozone_ppb`, `no2_ppb`, `so2_ppb`
- Traffic: `traffic_congestion_idx`
- Community/farm profile: `district`, `crop_type`, `crop_stage`, `senior_density`

The target labels in the demo data are synthetic. For a real model, collect historical labels such as verified flood events, heat advisories, crop-loss records, air-quality alerts, acid-rain pH measurements, emergency calls, or public-health outcome proxies.

## Important safety note

This is a prototype and educational decision-support tool. It should not replace official emergency alerts, agronomist guidance, public-health guidance, or local government decisions.

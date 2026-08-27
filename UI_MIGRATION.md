# Lovable UI → Streamlit migration notes

The supplied Lovable package is a React/Tailwind user-interface concept. This repository keeps Streamlit as the deployable application and translates the design into Streamlit-compatible HTML/CSS and native widgets.

## Design elements migrated

| Lovable concept | Streamlit implementation |
|---|---|
| Environmental hero scene / banner | `assets/dashboard-banner.jpg` in a responsive hero panel |
| Green/blue mesh background | CSS gradients in `styles/lovable_streamlit.css` |
| Dark rounded information panels | `.lovable-panel` and Streamlit container styling |
| Workspace sidebar | Streamlit sidebar with branded project/team cards and scenario controls |
| Audience-aware suggestions | Existing `build_recommendations()` AI/rule layer tied to the selected user group |
| Dashboard stat cards | Custom responsive KPI cards using the model's current outputs |
| Impact/risk visualization | Plotly risk trend and cluster charts |
| Suggestion feed | AI action cards generated from the current predicted hazards |
| Adaptive actions | Contextual-bandit reinforcement-learning feedback controls |
| Responsive layout | Streamlit columns + responsive CSS media queries |

## Runtime architecture

The React source is retained under `lovable_ui_source/src/` as design reference only. The deployed app does not require Node.js or a JavaScript build step.

Streamlit runtime:

`app.py` → `src/data_pipeline.py` → `src/ai_brain.py` → `src/recommendations.py` / `src/rl_agent.py` → Streamlit dashboard

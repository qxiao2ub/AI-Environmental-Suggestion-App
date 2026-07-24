"""Rule + model recommendation layer for farmers, residents, and local government."""
from __future__ import annotations

from typing import Iterable

import pandas as pd

from .data_pipeline import HAZARD_LABELS, RISK_COLUMNS

PREDICTED_RISK_COLUMNS = [f"pred_{column}" for column in RISK_COLUMNS]
PREDICTED_TO_HAZARD = {f"pred_{column}": label for column, label in HAZARD_LABELS.items()}

ACTION_LIBRARY: dict[str, dict[str, list[str]]] = {
    "Farmer": {
        "Flood": [
            "Inspect field drainage, ditches, pumps, and low-lying access roads before the next rainfall window.",
            "Delay fertilizer or pesticide application until runoff risk drops; document any crop-loss evidence for insurance.",
            "Move seed, feed, and equipment away from flood-prone storage areas; prioritize fields near the river first.",
        ],
        "Extreme Heat": [
            "Irrigate early morning or evening and check soil moisture before applying extra water.",
            "Use shade cloth or temporary row covers for vulnerable seedlings and flowering crops.",
            "Avoid transplanting, spraying, or heavy field work during peak afternoon heat.",
        ],
        "Extreme Cold": [
            "Prepare frost cloth, low tunnels, or greenhouse covers for sensitive crops and seedlings.",
            "Irrigate lightly before a freeze only when agronomically appropriate for the crop and soil condition.",
            "Move portable livestock water systems and check backup power for barn ventilation/heating.",
        ],
        "Acid Rain": [
            "Test rainwater and soil pH; schedule lime or soil-amendment review with an extension specialist.",
            "Cover exposed seedbeds and delay sensitive seeding until rain pH and soil pH stabilize.",
            "Rinse leaf surfaces after acidic precipitation when crop guidance allows and water supply is safe.",
        ],
        "Air Quality": [
            "Reduce outdoor labor during high PM2.5/ozone periods; shift work to lower-exposure hours.",
            "Protect livestock and workers from dusty or smoky areas; improve barn filtration or ventilation as feasible.",
            "Avoid burning, tilling dusty fields, or other activities that add particulates during poor-air alerts.",
        ],
    },
    "Resident": {
        "Flood": [
            "Move valuables and medications above floor level and keep phones charged before heavy rain begins.",
            "Avoid flooded roads and underpasses; use official detours if traffic alerts show closures.",
            "Check on neighbors who may need help, especially seniors or people with mobility limitations.",
        ],
        "Extreme Heat": [
            "Drink water regularly, limit outdoor activity during peak heat, and use cooling centers if home cooling is limited.",
            "Check on seniors, infants, and people with chronic conditions at least twice daily during severe heat.",
            "Close blinds during the day, open safe ventilation at night, and avoid using ovens in the hottest hours.",
        ],
        "Extreme Cold": [
            "Prepare warm layers, protect pipes, and keep emergency blankets and flashlights accessible.",
            "Check on seniors and neighbors who rely on electric heat before the coldest hours arrive.",
            "Avoid unsafe indoor heating methods; never use grills or generators indoors.",
        ],
        "Acid Rain": [
            "Avoid collecting rainwater for gardens or pets until pH readings return to normal.",
            "Rinse outdoor surfaces and garden leaves later with clean water when safe and practical.",
            "Use gloves when handling heavily exposed materials after very acidic rain events.",
        ],
        "Air Quality": [
            "Keep windows closed, reduce outdoor exercise, and use HEPA filtration or a clean-air room if available.",
            "People with asthma, COPD, heart disease, or high sensitivity should follow their care plan and carry medication.",
            "Use recirculation mode in cars when traffic and PM2.5 are high.",
        ],
    },
    "Local Government": {
        "Flood": [
            "Pre-position drainage crews, barricades, pumps, and shelter resources near the highest-risk district.",
            "Push multilingual flood alerts with road-closure guidance and farm-access information.",
            "Coordinate public works, emergency management, and agriculture extension teams for post-event damage assessment.",
        ],
        "Extreme Heat": [
            "Open cooling centers, extend library/community-center hours, and prioritize senior outreach lists.",
            "Coordinate heat-health messaging with schools, farms, employers, and health clinics.",
            "Prepare hydration stations and check power-grid contingency plans for critical facilities.",
        ],
        "Extreme Cold": [
            "Prepare warming centers, transportation options, and wellness checks for seniors and unhoused residents.",
            "Coordinate road treatment, shelter staffing, and backup power for critical public services.",
            "Send pipe-freeze, safe-heating, and carbon-monoxide prevention guidance before the coldest hours.",
        ],
        "Acid Rain": [
            "Publish rain pH and soil pH advisories for farmers, gardeners, schools, and water managers.",
            "Coordinate additional sampling near industrial corridors and high-traffic areas.",
            "Prepare extension-service guidance on soil amendments and seedbed protection.",
        ],
        "Air Quality": [
            "Issue clean-air guidance, reduce outdoor municipal work, and coordinate school/activity advisories.",
            "Deploy mobile monitoring or community sensors near traffic hot spots and senior housing.",
            "Consider traffic-flow or idling-reduction measures during persistent high PM2.5/ozone periods.",
        ],
    },
}


def normalize_user_type(user_type: str) -> str:
    value = user_type.strip().lower()
    if value.startswith("farm"):
        return "Farmer"
    if value.startswith("gov") or "government" in value:
        return "Local Government"
    return "Resident"


def score_to_band(score: float) -> str:
    if score >= 75:
        return "severe"
    if score >= 55:
        return "high"
    if score >= 35:
        return "moderate"
    return "low"


def ranked_hazards(row: pd.Series, use_predicted: bool = True) -> list[tuple[str, float]]:
    if use_predicted and all(column in row.index for column in PREDICTED_RISK_COLUMNS):
        hazard_scores = [(PREDICTED_TO_HAZARD[column], float(row[column])) for column in PREDICTED_RISK_COLUMNS]
    else:
        hazard_scores = [(HAZARD_LABELS[column], float(row[column])) for column in RISK_COLUMNS if column in row.index]
    return sorted(hazard_scores, key=lambda item: item[1], reverse=True)


def build_recommendations(row: pd.Series, user_type: str = "Farmer", max_actions: int = 6) -> list[str]:
    """Return actionable suggestions, prioritizing the highest-risk hazards."""
    audience = normalize_user_type(user_type)
    hazards = ranked_hazards(row, use_predicted=True)
    actions: list[str] = []

    for hazard, score in hazards[:3]:
        if score < 35 and actions:
            continue
        hazard_actions = ACTION_LIBRARY[audience].get(hazard, [])
        prefix = f"[{hazard} | {score_to_band(score).title()} risk]"
        for action in hazard_actions[:2]:
            actions.append(f"{prefix} {action}")

    traffic = float(row.get("traffic_congestion_idx", 0))
    rainfall = float(row.get("rainfall_mm", 0))
    if traffic >= 75:
        actions.append("[Traffic] Congestion is high; plan alternate routes for emergency access, farm logistics, and resident travel.")
    if rainfall >= 40 and audience in {"Farmer", "Local Government"}:
        actions.append("[Heavy Rain] Confirm drainage and road-access readiness because rainfall is above the prototype heavy-rain threshold.")

    unique_actions = list(dict.fromkeys(actions))
    return unique_actions[:max_actions]


def explain_prediction(row: pd.Series) -> str:
    hazards = ranked_hazards(row, use_predicted=True)[:3]
    hazard_text = ", ".join(f"{hazard}: {score:.1f}" for hazard, score in hazards)
    level = row.get("pred_risk_level", row.get("risk_level", "unknown"))
    district = row.get("district", "selected district")
    return f"For {district}, the model estimates {level} overall risk. Top drivers are {hazard_text}."


def make_action_table(row: pd.Series, user_types: Iterable[str] = ("Farmer", "Resident", "Local Government")) -> pd.DataFrame:
    records = []
    for user_type in user_types:
        for rank, action in enumerate(build_recommendations(row, user_type), start=1):
            records.append({"user_type": user_type, "rank": rank, "recommendation": action})
    return pd.DataFrame(records)

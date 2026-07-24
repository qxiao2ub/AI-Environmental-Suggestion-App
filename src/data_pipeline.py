"""Data generation and API-normalization helpers for the Environmental Suggestion App.

The prototype runs without paid APIs by generating realistic demo data. In production,
replace the generate_environmental_data call with API fetchers that return the same schema.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

RISK_COLUMNS = [
    "flood_risk_score",
    "heat_risk_score",
    "cold_risk_score",
    "acid_rain_risk_score",
    "air_quality_risk_score",
]

HAZARD_LABELS = {
    "flood_risk_score": "Flood",
    "heat_risk_score": "Extreme Heat",
    "cold_risk_score": "Extreme Cold",
    "acid_rain_risk_score": "Acid Rain",
    "air_quality_risk_score": "Air Quality",
}

DISTRICT_METADATA = {
    "North Valley": {"lat": 40.733, "lon": -73.995, "flood_sensitivity": 0.55, "urban_factor": 0.30, "senior_density": 0.18},
    "River Bend": {"lat": 40.712, "lon": -74.020, "flood_sensitivity": 1.10, "urban_factor": 0.60, "senior_density": 0.20},
    "East Orchard": {"lat": 40.724, "lon": -73.965, "flood_sensitivity": 0.40, "urban_factor": 0.25, "senior_density": 0.15},
    "South Fields": {"lat": 40.691, "lon": -74.010, "flood_sensitivity": 0.75, "urban_factor": 0.45, "senior_density": 0.23},
    "Hill Market": {"lat": 40.747, "lon": -73.985, "flood_sensitivity": 0.25, "urban_factor": 0.80, "senior_density": 0.17},
}

CROP_TYPES = ["corn", "soybean", "rice", "wheat", "vegetable"]
CROP_STAGES = ["seeding", "vegetative", "flowering", "harvest", "dormant"]


def _sigmoid(value: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(value, -35, 35)))


def _risk_level(score: float) -> str:
    if score >= 75:
        return "Severe"
    if score >= 55:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def crop_stage_for_date(date: pd.Timestamp) -> str:
    """Simple crop-stage calendar for a northern-hemisphere temperate farming region."""
    month = int(date.month)
    if month in (3, 4):
        return "seeding"
    if month in (5, 6):
        return "vegetative"
    if month in (7, 8):
        return "flowering"
    if month in (9, 10):
        return "harvest"
    return "dormant"


def generate_environmental_data(
    n_days: int = 540,
    start_date: str = "2025-01-01",
    districts: Iterable[str] | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a realistic local-environment dataset for prototype training and demos.

    The schema is designed to match future API payloads: weather forecasts, local sensors,
    air-quality feeds, crop metadata, resident vulnerability indicators, and traffic signals.
    Risk columns are synthetic labels that let students build a supervised-learning prototype
    before real historical labels are available.
    """
    rng = np.random.default_rng(seed)
    chosen_districts = list(districts or DISTRICT_METADATA.keys())
    dates = pd.date_range(start=start_date, periods=n_days, freq="D")
    rows: list[dict[str, object]] = []

    for district in chosen_districts:
        meta = DISTRICT_METADATA[district]
        district_temp_shift = rng.normal(0, 1.2)
        district_pollution_shift = 5 * meta["urban_factor"] + rng.normal(0, 2)
        district_soil_shift = rng.normal(0, 0.18)
        district_crop_bias = rng.choice(CROP_TYPES)

        for t, date in enumerate(dates):
            day = int(date.dayofyear)
            seasonal_temp = 14 + 13 * np.sin(2 * np.pi * (day - 80) / 365)
            rainy_season = 0.55 + 0.45 * np.sin(2 * np.pi * (day - 35) / 365) ** 2
            crop_stage = crop_stage_for_date(date)
            crop_type = district_crop_bias if rng.random() < 0.48 else rng.choice(CROP_TYPES)

            heat_wave = rng.random() < 0.035
            cold_snap = rng.random() < 0.025
            storm_event = rng.random() < (0.035 + 0.025 * rainy_season)

            temperature_c = seasonal_temp + district_temp_shift + rng.normal(0, 3.4)
            if heat_wave:
                temperature_c += rng.uniform(5.5, 9.5)
            if cold_snap:
                temperature_c -= rng.uniform(6.0, 11.0)

            rainfall_mm = rng.gamma(shape=1.5 + rainy_season, scale=4.0)
            if storm_event:
                rainfall_mm += rng.uniform(25, 85)

            humidity_pct = np.clip(52 + 0.62 * rainfall_mm + rng.normal(0, 11), 18, 100)
            wind_speed_kph = np.clip(rng.gamma(2.5, 5.0) + 0.05 * rainfall_mm, 1, 80)
            river_level_m = np.clip(
                1.4 + 0.020 * rainfall_mm + 0.012 * t % 0.5 + rng.normal(0, 0.18) + 0.55 * meta["flood_sensitivity"],
                0.2,
                6.5,
            )
            soil_moisture_pct = np.clip(32 + 0.55 * rainfall_mm + rng.normal(0, 9) - 0.35 * max(temperature_c - 25, 0), 4, 100)
            soil_ph = np.clip(6.55 + district_soil_shift - 0.012 * rainfall_mm + rng.normal(0, 0.18), 4.4, 8.0)
            rain_ph = np.clip(5.7 - 0.012 * rainfall_mm - 0.010 * meta["urban_factor"] * 100 + rng.normal(0, 0.25), 3.8, 7.1)

            traffic_congestion_idx = np.clip(35 + 52 * meta["urban_factor"] + 8 * np.sin(2 * np.pi * (date.dayofweek) / 7) + rng.normal(0, 12), 0, 100)
            pm25_ugm3 = np.clip(7 + district_pollution_shift + 0.18 * traffic_congestion_idx + 0.35 * max(temperature_c - 27, 0) + rng.normal(0, 6), 1, 160)
            ozone_ppb = np.clip(25 + 1.5 * max(temperature_c - 22, 0) + 0.12 * traffic_congestion_idx + rng.normal(0, 8), 2, 170)
            no2_ppb = np.clip(9 + 0.34 * traffic_congestion_idx + rng.normal(0, 5), 1, 120)
            so2_ppb = np.clip(2 + 0.08 * traffic_congestion_idx + 0.16 * rainfall_mm + rng.normal(0, 3), 0, 80)
            visibility_km = np.clip(16 - 0.045 * pm25_ugm3 - 0.040 * rainfall_mm + rng.normal(0, 1.8), 0.5, 25)

            flood_risk = 100 * _sigmoid(
                -5.9
                + 0.078 * rainfall_mm
                + 0.82 * (river_level_m - 2.6)
                + 0.024 * soil_moisture_pct
                + 0.60 * meta["flood_sensitivity"]
                + 0.003 * traffic_congestion_idx
            )
            heat_risk = 100 * _sigmoid(
                -7.8 + 0.25 * temperature_c + 0.018 * humidity_pct + 0.010 * ozone_ppb + 1.45 * meta["senior_density"]
            )
            cold_risk = 100 * _sigmoid(
                -3.1 + 0.42 * (2 - temperature_c) + 0.022 * wind_speed_kph + 1.25 * meta["senior_density"]
            )
            acid_rain_risk = 100 * _sigmoid(
                -6.9
                + 4.7 * (5.6 - rain_ph)
                + 0.030 * rainfall_mm
                + 0.030 * no2_ppb
                + 0.025 * so2_ppb
                + 0.45 * (6.1 - soil_ph)
            )
            air_quality_risk = 100 * _sigmoid(
                -5.2 + 0.060 * pm25_ugm3 + 0.018 * ozone_ppb + 0.026 * no2_ppb + 0.005 * traffic_congestion_idx
            )

            raw_scores = {
                "flood_risk_score": float(np.clip(flood_risk + rng.normal(0, 3), 0, 100)),
                "heat_risk_score": float(np.clip(heat_risk + rng.normal(0, 3), 0, 100)),
                "cold_risk_score": float(np.clip(cold_risk + rng.normal(0, 3), 0, 100)),
                "acid_rain_risk_score": float(np.clip(acid_rain_risk + rng.normal(0, 3), 0, 100)),
                "air_quality_risk_score": float(np.clip(air_quality_risk + rng.normal(0, 3), 0, 100)),
            }
            primary_risk_column = max(raw_scores, key=raw_scores.get)
            overall_risk = float(np.clip(max(raw_scores.values()) * 0.82 + np.mean(list(raw_scores.values())) * 0.18 + rng.normal(0, 2.5), 0, 100))

            crop_vulnerability = {
                "corn": 0.95,
                "soybean": 0.88,
                "rice": 0.72,
                "wheat": 0.83,
                "vegetable": 1.05,
            }[crop_type]
            stage_vulnerability = {
                "seeding": 1.10,
                "vegetative": 0.85,
                "flowering": 1.18,
                "harvest": 0.80,
                "dormant": 0.45,
            }[crop_stage]
            crop_damage_pct = float(
                np.clip(
                    crop_vulnerability
                    * stage_vulnerability
                    * (0.34 * raw_scores["flood_risk_score"] + 0.24 * raw_scores["heat_risk_score"] + 0.18 * raw_scores["acid_rain_risk_score"] + 0.12 * raw_scores["cold_risk_score"])
                    / 100,
                    0,
                    100,
                )
            )

            rows.append(
                {
                    "timestamp": date,
                    "district": district,
                    "lat": meta["lat"],
                    "lon": meta["lon"],
                    "temperature_c": round(float(temperature_c), 2),
                    "humidity_pct": round(float(humidity_pct), 2),
                    "rainfall_mm": round(float(rainfall_mm), 2),
                    "wind_speed_kph": round(float(wind_speed_kph), 2),
                    "river_level_m": round(float(river_level_m), 2),
                    "soil_moisture_pct": round(float(soil_moisture_pct), 2),
                    "soil_ph": round(float(soil_ph), 2),
                    "rain_ph": round(float(rain_ph), 2),
                    "pm25_ugm3": round(float(pm25_ugm3), 2),
                    "ozone_ppb": round(float(ozone_ppb), 2),
                    "no2_ppb": round(float(no2_ppb), 2),
                    "so2_ppb": round(float(so2_ppb), 2),
                    "visibility_km": round(float(visibility_km), 2),
                    "traffic_congestion_idx": round(float(traffic_congestion_idx), 2),
                    "senior_density": round(float(meta["senior_density"]), 2),
                    "crop_type": crop_type,
                    "crop_stage": crop_stage,
                    **{name: round(score, 2) for name, score in raw_scores.items()},
                    "overall_risk_score": round(overall_risk, 2),
                    "risk_level": _risk_level(overall_risk),
                    "primary_hazard": HAZARD_LABELS[primary_risk_column],
                    "observed_crop_damage_pct": round(crop_damage_pct, 2),
                }
            )

    return pd.DataFrame(rows).sort_values(["timestamp", "district"]).reset_index(drop=True)


def apply_what_if_controls(
    df: pd.DataFrame,
    temp_delta_c: float = 0.0,
    rainfall_multiplier: float = 1.0,
    pm25_delta: float = 0.0,
    traffic_delta: float = 0.0,
) -> pd.DataFrame:
    """Create an adjusted scenario without changing the original dataframe."""
    scenario = df.copy()
    scenario["temperature_c"] = scenario["temperature_c"] + temp_delta_c
    scenario["rainfall_mm"] = np.clip(scenario["rainfall_mm"] * rainfall_multiplier, 0, None)
    scenario["pm25_ugm3"] = np.clip(scenario["pm25_ugm3"] + pm25_delta, 0, None)
    scenario["traffic_congestion_idx"] = np.clip(scenario["traffic_congestion_idx"] + traffic_delta, 0, 100)
    scenario["humidity_pct"] = np.clip(scenario["humidity_pct"] + 0.08 * temp_delta_c + 0.12 * (rainfall_multiplier - 1.0) * 100, 0, 100)
    scenario["river_level_m"] = np.clip(scenario["river_level_m"] + 0.025 * scenario["rainfall_mm"] * max(rainfall_multiplier - 1.0, 0), 0, None)
    scenario["visibility_km"] = np.clip(scenario["visibility_km"] - 0.035 * pm25_delta, 0.3, 25)
    return scenario


def expected_api_schema() -> pd.DataFrame:
    """Return a compact table explaining the fields external APIs should provide."""
    return pd.DataFrame(
        [
            ("timestamp", "datetime", "Observation/forecast timestamp"),
            ("district", "string", "Local area, farm zone, or neighborhood"),
            ("temperature_c", "float", "Weather API or local station"),
            ("humidity_pct", "float", "Weather API or local station"),
            ("rainfall_mm", "float", "Weather forecast, radar, or rain gauge"),
            ("wind_speed_kph", "float", "Weather API or local station"),
            ("river_level_m", "float", "Flood sensor / hydrology API"),
            ("soil_moisture_pct", "float", "Farm sensor / extension service"),
            ("soil_ph", "float", "Farm sensor / soil test"),
            ("rain_ph", "float", "Precipitation chemistry sensor or lab feed"),
            ("pm25_ugm3", "float", "Air-quality API"),
            ("ozone_ppb", "float", "Air-quality API"),
            ("no2_ppb", "float", "Air-quality API / traffic proxy"),
            ("so2_ppb", "float", "Air-quality API / industrial proxy"),
            ("traffic_congestion_idx", "float", "Traffic API / road sensors"),
            ("crop_type", "category", "Farmer profile or extension dataset"),
            ("crop_stage", "category", "Crop calendar or farmer input"),
        ],
        columns=["field", "type", "source_hint"],
    )


@dataclass(frozen=True)
class ApiEndpointSpec:
    name: str
    purpose: str
    required_fields: tuple[str, ...]
    api_key_needed: bool = False


def prototype_api_contracts() -> list[ApiEndpointSpec]:
    """Document the API adapters expected in a production implementation."""
    return [
        ApiEndpointSpec("weather_forecast", "Hourly or daily weather forecast", ("temperature_c", "humidity_pct", "rainfall_mm", "wind_speed_kph"), False),
        ApiEndpointSpec("local_environment_sensors", "Farm, river, rain pH, and soil sensors", ("river_level_m", "soil_moisture_pct", "soil_ph", "rain_ph"), True),
        ApiEndpointSpec("air_quality", "PM2.5, ozone, NO2, SO2 measurements or forecasts", ("pm25_ugm3", "ozone_ppb", "no2_ppb", "so2_ppb"), True),
        ApiEndpointSpec("traffic", "Road congestion and closure information", ("traffic_congestion_idx",), True),
    ]

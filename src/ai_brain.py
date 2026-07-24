"""Machine-learning, neural-network, and clustering components for the prototype."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data_pipeline import HAZARD_LABELS, RISK_COLUMNS

NUMERIC_FEATURES = [
    "temperature_c",
    "humidity_pct",
    "rainfall_mm",
    "wind_speed_kph",
    "river_level_m",
    "soil_moisture_pct",
    "soil_ph",
    "rain_ph",
    "pm25_ugm3",
    "ozone_ppb",
    "no2_ppb",
    "so2_ppb",
    "visibility_km",
    "traffic_congestion_idx",
    "senior_density",
]

CATEGORICAL_FEATURES = ["district", "crop_type", "crop_stage"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


@dataclass
class EnvironmentalAIModelBundle:
    """Container for trained models and evaluation outputs."""

    hazard_classifier: Pipeline
    risk_regressor: Pipeline
    dnn_regressor: Pipeline
    cluster_model: Pipeline
    metrics: dict[str, Any]
    cluster_profiles: pd.DataFrame
    feature_columns: list[str]
    risk_columns: list[str]


def build_preprocessor() -> ColumnTransformer:
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_FEATURES),
            ("cat", categorical_pipe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def _risk_level(score: float) -> str:
    if score >= 75:
        return "Severe"
    if score >= 55:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def _cluster_name(row: pd.Series) -> str:
    risk_values = {column: row[column] for column in RISK_COLUMNS if column in row.index}
    primary_risk_col = max(risk_values, key=risk_values.get)
    return f"Cluster {int(row['cluster'])}: {HAZARD_LABELS[primary_risk_col]} dominant"


def make_cluster_profiles(df: pd.DataFrame, cluster_labels: np.ndarray) -> pd.DataFrame:
    prof = df.copy()
    prof["cluster"] = cluster_labels
    mean_cols = [
        "temperature_c",
        "rainfall_mm",
        "river_level_m",
        "soil_ph",
        "rain_ph",
        "pm25_ugm3",
        "traffic_congestion_idx",
        "overall_risk_score",
        *RISK_COLUMNS,
    ]
    profiles = prof.groupby("cluster", as_index=False)[mean_cols].mean().round(2)
    size_table = prof.groupby("cluster", as_index=False).size().rename(columns={"size": "records"})
    district_mode = prof.groupby("cluster")["district"].agg(lambda x: x.mode().iat[0] if not x.mode().empty else "mixed").reset_index(name="most_common_district")
    crop_mode = prof.groupby("cluster")["crop_type"].agg(lambda x: x.mode().iat[0] if not x.mode().empty else "mixed").reset_index(name="most_common_crop")
    profiles = profiles.merge(size_table, on="cluster", how="left").merge(district_mode, on="cluster", how="left").merge(crop_mode, on="cluster", how="left")
    profiles["cluster_name"] = profiles.apply(_cluster_name, axis=1)
    return profiles


def train_ai_brain(
    df: pd.DataFrame,
    random_state: int = 42,
    n_clusters: int = 4,
) -> EnvironmentalAIModelBundle:
    """Train supervised ML, DNN, and clustering models for the prototype AI brain."""
    missing = [column for column in FEATURE_COLUMNS + RISK_COLUMNS + ["primary_hazard"] if column not in df.columns]
    if missing:
        raise ValueError(f"Training data is missing required columns: {missing}")

    X = df[FEATURE_COLUMNS].copy()
    y_class = df["primary_hazard"].copy()
    y_risk = df[RISK_COLUMNS].copy()

    stratify = y_class if y_class.value_counts().min() >= 2 else None
    X_train, X_test, y_class_train, y_class_test, y_risk_train, y_risk_test = train_test_split(
        X,
        y_class,
        y_risk,
        test_size=0.22,
        random_state=random_state,
        stratify=stratify,
    )

    hazard_classifier = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=160,
                    min_samples_leaf=4,
                    class_weight="balanced_subsample",
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    risk_regressor = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=180,
                    min_samples_leaf=3,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    dnn_regressor = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            (
                "model",
                MLPRegressor(
                    hidden_layer_sizes=(96, 48, 24),
                    activation="relu",
                    solver="adam",
                    learning_rate_init=0.002,
                    max_iter=220,
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=15,
                    random_state=random_state,
                ),
            ),
        ]
    )

    cluster_model = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("model", KMeans(n_clusters=n_clusters, n_init="auto", random_state=random_state)),
        ]
    )

    hazard_classifier.fit(X_train, y_class_train)
    risk_regressor.fit(X_train, y_risk_train)
    dnn_regressor.fit(X_train, y_risk_train)
    cluster_model.fit(X)

    class_pred = hazard_classifier.predict(X_test)
    rf_pred = np.clip(risk_regressor.predict(X_test), 0, 100)
    dnn_pred = np.clip(dnn_regressor.predict(X_test), 0, 100)

    metrics = {
        "classification_accuracy": round(float(accuracy_score(y_class_test, class_pred)), 3),
        "classification_weighted_f1": round(float(f1_score(y_class_test, class_pred, average="weighted")), 3),
        "rf_multi_risk_mae": round(float(mean_absolute_error(y_risk_test, rf_pred)), 2),
        "dnn_multi_risk_mae": round(float(mean_absolute_error(y_risk_test, dnn_pred)), 2),
        "training_records": int(len(X_train)),
        "test_records": int(len(X_test)),
        "dnn_architecture": "MLPRegressor hidden layers: 96 -> 48 -> 24, ReLU, Adam, early stopping",
        "supervised_ml_model": "RandomForestClassifier + RandomForestRegressor",
        "clustering_model": f"KMeans with {n_clusters} clusters",
    }

    cluster_labels = cluster_model.predict(X)
    profiles = make_cluster_profiles(df, cluster_labels)

    return EnvironmentalAIModelBundle(
        hazard_classifier=hazard_classifier,
        risk_regressor=risk_regressor,
        dnn_regressor=dnn_regressor,
        cluster_model=cluster_model,
        metrics=metrics,
        cluster_profiles=profiles,
        feature_columns=FEATURE_COLUMNS,
        risk_columns=RISK_COLUMNS,
    )


def predict_environmental_risk(bundle: EnvironmentalAIModelBundle, scenario_df: pd.DataFrame) -> pd.DataFrame:
    """Predict risk scores, primary hazard, risk level, and cluster for new scenarios."""
    X = scenario_df[bundle.feature_columns].copy()
    rf_scores = np.clip(bundle.risk_regressor.predict(X), 0, 100)
    dnn_scores = np.clip(bundle.dnn_regressor.predict(X), 0, 100)
    blended_scores = np.clip(0.60 * rf_scores + 0.40 * dnn_scores, 0, 100)
    classifier_labels = bundle.hazard_classifier.predict(X)
    clusters = bundle.cluster_model.predict(X)

    output = scenario_df.copy()
    for idx, column in enumerate(bundle.risk_columns):
        output[f"pred_{column}"] = np.round(blended_scores[:, idx], 2)

    pred_cols = [f"pred_{column}" for column in bundle.risk_columns]
    output["pred_overall_risk_score"] = np.round(np.max(blended_scores, axis=1) * 0.82 + np.mean(blended_scores, axis=1) * 0.18, 2)
    output["pred_risk_level"] = output["pred_overall_risk_score"].apply(_risk_level)
    dominant_indices = np.argmax(blended_scores, axis=1)
    dominant_score_cols = [bundle.risk_columns[int(i)] for i in dominant_indices]
    output["primary_hazard_score_based"] = [HAZARD_LABELS[col] for col in dominant_score_cols]
    output["primary_hazard_classifier"] = classifier_labels
    output["cluster"] = clusters
    output["model_agreement"] = output["primary_hazard_score_based"] == output["primary_hazard_classifier"]
    output["top_predicted_risk_score"] = output[pred_cols].max(axis=1).round(2)
    return output


def save_model_bundle(bundle: EnvironmentalAIModelBundle, output_path: str | Path) -> Path:
    """Persist the trained model bundle using joblib."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, output_path)
    return output_path


def load_model_bundle(path: str | Path) -> EnvironmentalAIModelBundle:
    return joblib.load(path)

"""Frozen GradientBoosting inference service used directly by FastAPI."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_RUNTIME = PROJECT_ROOT / "server" / "model_runtime"
ARTIFACTS = MODEL_RUNTIME / "artifacts"
if str(MODEL_RUNTIME) not in sys.path:
    sys.path.insert(0, str(MODEL_RUNTIME))

from app.core.final_contract import FEATURE_NAMES, RAW_COLUMNS  # noqa: E402


ARTIFACTS_V25 = MODEL_RUNTIME / "artifacts_v25"
MODEL_PATH_V25 = ARTIFACTS_V25 / "best_carbon_model_v25.joblib"
FEATURES_PATH_V25 = ARTIFACTS_V25 / "feature_names_v25.joblib"
METADATA_PATH_V25 = ARTIFACTS_V25 / "model_metadata_v25.json"
MANIFEST_PATH_V25 = ARTIFACTS_V25 / "manifest_v25.json"

GRID_FACTORS = {"india": 0.67013, "us": 0.38440, "uk": 0.21741}
RENEWABLE_GRID = {"india": 0.147, "us": 0.085, "uk": 0.048}
GROCERY_FACTORS = {"india": 0.11, "us": 0.36, "uk": 0.44}

MODEL_PATH = ARTIFACTS / "best_carbon_model.joblib"
PREPROCESSOR_PATH = ARTIFACTS / "preprocessor_10k_final.joblib"
METADATA_PATH = ARTIFACTS / "model_metadata.json"
MANIFEST_PATH = ARTIFACTS / "manifest.json"

LABELS = {
    "monthly_grocery_bill": "Monthly grocery spending",
    "vehicle_monthly_distance_km": "Vehicle distance",
    "waste_bag_weekly_count": "Weekly waste volume",
    "how_long_tv_pc_daily_hour": "TV and computer time",
    "how_many_new_clothes_monthly": "New clothing frequency",
    "how_long_internet_daily_hour": "Internet time",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    file_hashes = manifest.get("files", manifest)
    for name in ("best_carbon_model.joblib", "preprocessor_10k_final.joblib", "model_metadata.json"):
        if _sha256(ARTIFACTS / name) != file_hashes[name]:
            raise RuntimeError(f"Artifact integrity check failed for {name}")
    return manifest


FEATURE_GROUPS_V25 = [
    ("grid_factor", "home_energy", "Home energy (grid intensity)"),
    ("household_size", "home_energy", "Home energy (shared per person)"),
    ("vehicle_monthly_distance_km", "transport_and_distance", "Transport and distance"),
    ("monthly_grocery_bill", "diet_and_grocery", "Diet and grocery"),
    ("how_long_tv_pc_daily_hour", "digital_use", "Digital use"),
    ("how_long_internet_daily_hour", "digital_use", "Digital use"),
    ("how_many_new_clothes_monthly", "new_clothing", "New clothing purchases"),
    ("waste_bag_weekly_count", "waste_and_recycling", "Waste and recycling"),
    ("grocery_factor", "diet_and_grocery", "Diet and grocery (country price level)"),
]


def _v25_group(feature: str) -> tuple[str, str]:
    for prefix, key, label in FEATURE_GROUPS_V25:
        if feature == prefix:
            return key, label
    if feature.startswith("transport_"):
        return "transport_and_distance", "Transport and distance"
    if feature.startswith("vehicle_type_"):
        return "vehicle_type", "Vehicle type"
    if feature.startswith("air_"):
        return "air_travel_frequency", "Air travel frequency"
    if feature.startswith("heating_"):
        return "home_energy", "Home energy"
    if feature.startswith("diet_"):
        return "diet_and_grocery", "Diet and grocery"
    if feature.startswith("waste_bag_size_"):
        return "waste_and_recycling", "Waste and recycling"
    if feature.startswith("recycle_"):
        return "waste_and_recycling", "Waste and recycling"
    if feature.startswith("cook_"):
        return "cooking_equipment", "Cooking equipment"
    return feature, feature.replace("_", " ").title()


@lru_cache(maxsize=1)
def _v25_explainer():
    import shap
    _meta, model, _features = get_runtime_v25()
    return shap.TreeExplainer(model)


@lru_cache(maxsize=1)
def get_runtime_v25() -> tuple[dict[str, Any], Any, list[str]]:
    manifest = json.loads(MANIFEST_PATH_V25.read_text())
    for name, expected in manifest["files"].items():
        if _sha256(ARTIFACTS_V25 / name) != expected:
            raise RuntimeError(f"v2.5 artifact integrity check failed for {name}")
    metadata = json.loads(METADATA_PATH_V25.read_text())
    model = joblib.load(MODEL_PATH_V25)
    features = joblib.load(FEATURES_PATH_V25)
    if len(features) != metadata["n_features"]:
        raise RuntimeError("v2.5 feature contract mismatch")
    return metadata, model, features


def build_v25_features(payload: dict[str, Any]) -> dict[str, float]:
    """Expand a schema-valid survey payload into the v2.5 feature vector.

    Mirrors scripts/train_v25.py exactly: numeric grid/grocery factors from
    the country, per-person division by household size, one-hots (drop-first),
    and recycling/cooking binaries.
    """
    country = payload.get("country", "india")
    grid = RENEWABLE_GRID.get(country, GRID_FACTORS[country]) if payload.get("region") == "renewable_heavy" else GRID_FACTORS.get(country, GRID_FACTORS["india"])
    hh = max(1, int(payload.get("household_size", 2)))
    f: dict[str, float] = {
        "grid_factor": grid,
        "grocery_factor": GROCERY_FACTORS.get(country, 0.11),
        "household_size": float(hh),
        "vehicle_monthly_distance_km": float(payload.get("vehicle_monthly_distance_km", 0)),
        "monthly_grocery_bill": float(payload.get("monthly_grocery_bill", 0)),
        "how_long_tv_pc_daily_hour": float(payload.get("how_long_tv_pc_daily_hour", 0)),
        "how_long_internet_daily_hour": float(payload.get("how_long_internet_daily_hour", 0)),
        "how_many_new_clothes_monthly": float(payload.get("how_many_new_clothes_monthly", 0)),
        "waste_bag_weekly_count": float(payload.get("waste_bag_weekly_count", 0)),
        "transport_public": 0.0, "transport_walk/bicycle": 0.0,
        "vehicle_type_diesel": 0.0, "vehicle_type_electric": 0.0, "vehicle_type_hybrid": 0.0,
        "vehicle_type_lpg": 0.0, "vehicle_type_none": 0.0, "vehicle_type_petrol": 0.0,
        "air_often": 0.0, "air_rarely": 0.0, "air_very_frequently": 0.0,
        "heating_natural_gas": 0.0, "heating_wood": 0.0,
        "diet_omnivore": 0.0, "diet_pescatarian": 0.0, "diet_vegan": 0.0, "diet_vegetarian": 0.0,
        "waste_bag_size_large": 0.0, "waste_bag_size_medium": 0.0, "waste_bag_size_small": 0.0,
        "recycle_paper": 0.0, "recycle_plastic": 0.0, "recycle_metal": 0.0, "recycle_glass": 0.0,
        "cook_stove": 0.0, "cook_oven": 0.0, "cook_microwave": 0.0, "cook_grill": 0.0, "cook_airfryer": 0.0,
    }
    mode = payload.get("transport", "private")
    if mode == "public":
        f["transport_public"] = 1.0
    elif mode == "walk/bicycle":
        f["transport_walk/bicycle"] = 1.0
    vt = payload.get("vehicle_type", "petrol")
    if vt in ("diesel", "electric", "hybrid", "lpg", "none", "petrol"):
        f[f"vehicle_type_{vt}"] = 1.0
    air = payload.get("frequency_of_traveling_by_air", "never")
    # Air-band and heating keys must match the training contract exactly:
    # get_dummies prefixes carry no spaces, so "very frequently" -> air_very_frequently
    # and "natural gas" -> heating_natural_gas. Space-named keys are silently
    # dropped by the strict column reindex in run_prediction_v25.
    if air in ("often", "rarely", "very frequently"):
        f[f"air_{air.replace(' ', '_')}"] = 1.0
    heat = payload.get("heating_energy_source", "electricity")
    if heat in ("natural gas", "wood"):
        f[f"heating_{heat.replace(' ', '_')}"] = 1.0
    d = payload.get("diet", "omnivore")
    if d in ("vegan", "vegetarian", "pescatarian", "omnivore"):
        f[f"diet_{d}"] = 1.0
    bs = payload.get("waste_bag_size", "medium")
    if bs in ("small", "medium", "large"):
        f[f"waste_bag_size_{bs}"] = 1.0
    for it in payload.get("recycling", []) or []:
        if it in ("paper", "plastic", "metal", "glass"):
            f[f"recycle_{it}"] = 1.0
    for it in payload.get("cooking_with", []) or []:
        if it in ("stove", "oven", "microwave", "grill", "airfryer"):
            f[f"cook_{it}"] = 1.0
    return f


def run_prediction_v25(payload: dict[str, Any]) -> dict[str, Any]:
    import pandas as pd
    metadata, model, features = get_runtime_v25()
    feats = build_v25_features(payload)
    row = pd.DataFrame([feats])[features]
    prediction = max(0.0, float(model.predict(row)[0]))
    q_hat = float(metadata["conformal_prediction"]["quantile_90"])

    import shap
    explainer = _v25_explainer()
    shap_values = explainer.shap_values(row)[0]
    base_value = float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0])
    groups: dict[str, dict[str, Any]] = {}
    for idx, name in enumerate(features):
        key, label = _v25_group(name)
        groups.setdefault(key, {"feature": key, "label": label, "shapValue": 0.0})
        groups[key]["shapValue"] += float(shap_values[idx])
    items = [{"feature": g["feature"], "label": g["label"], "shapValue": round(g["shapValue"], 3),
              "direction": "increases" if g["shapValue"] >= 0 else "decreases"}
             for g in sorted(groups.values(), key=lambda g: abs(g["shapValue"]), reverse=True)]
    items = [i for i in items if abs(i["shapValue"]) >= 0.001]

    return {
        "predictedKg": round(prediction, 1),
        "submittedAnswers": payload,
        "modelVersion": metadata["model_version"],
        "datasetVersion": metadata["dataset_version"],
        "uncertaintyRange": {"low": round(max(0.0, prediction - q_hat), 1),
                             "high": round(prediction + q_hat, 1)},
        "runtime": {"engine": metadata["best_model"], "transformedFeatureCount": len(features)},
        "conformal": {"quantile90": q_hat,
                      "empiricalCoverage": metadata["conformal_prediction"]["empirical_test_coverage"]},
        "explanation": {
            "baseValue": round(base_value, 3),
            "predictedValue": round(prediction, 1),
            "contributions": items,
            "reconciliation": round(base_value + sum(i["shapValue"] for i in items), 3),
            "note": "Grid-factor model contributions recalculated from the values submitted in this survey response. They describe model behavior, not causal environmental impact.",
        },
        "country": payload.get("country", "india"),
        "gridFactorKgPerKwh": feats["grid_factor"],
        "householdSize": int(payload.get("household_size", 2)),
        "disclaimer": "Factor-formula-based model estimate on the cited v2.5 dataset; "
                      "not a direct emissions measurement.",
    }


@lru_cache(maxsize=1)
def get_runtime() -> tuple[dict[str, Any], dict[str, Any], Any, Any]:
    manifest = _verify_manifest()
    metadata = json.loads(METADATA_PATH.read_text())
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    names = list(preprocessor.get_feature_names_out())
    # Dynamic feature count - must match the frozen 44-feature contract exactly
    if len(names) != 44:
        raise RuntimeError(f"Persisted preprocessor does not match the frozen 44-feature contract: got {len(names)} features")
    return manifest, metadata, model, preprocessor


def _feature_label(feature: str) -> str:
    if feature in LABELS:
        return LABELS[feature]
    if feature.startswith("recycle_"):
        return f"Recycling: {feature.removeprefix('recycle_')}"
    if feature.startswith("cook_"):
        return f"Cooking: {feature.removeprefix('cook_')}"
    return feature.replace("_", " ").replace("x ", "× ").title()


def _contribution_group(feature: str) -> tuple[str, str]:
    if feature in {"monthly_grocery_bill"} or feature.startswith("diet_"):
        return "diet_and_grocery", "Diet and grocery"
    if feature in {"vehicle_monthly_distance_km"} or feature.startswith("transport_"):
        return "transport_and_distance", "Transport and distance"
    if feature.startswith("heating_energy_source_"):
        return "home_energy", "Home energy"
    if feature.startswith("frequency_of_traveling_by_air_"):
        return "air_travel_frequency", "Air travel frequency"
    if feature == "waste_bag_weekly_count" or feature.startswith("waste_bag_size_") or feature.startswith("recycle_"):
        return "waste_and_recycling", "Waste and recycling"
    if feature in {"how_long_tv_pc_daily_hour", "how_long_internet_daily_hour"}:
        return "digital_use", "Digital use"
    if feature == "how_many_new_clothes_monthly":
        return "new_clothing", "New clothing purchases"
    if feature.startswith("cook_"):
        return "cooking_equipment", "Cooking equipment"
    if feature.startswith("vehicle_type_"):
        return "vehicle_type", "Vehicle type"
    if feature.startswith("energy_efficiency_"):
        return "energy_efficiency", "Energy efficiency"
    if feature.startswith("how_often_shower_"):
        return "shower_frequency", "Shower frequency"
    if feature.startswith("social_activity_"):
        return "social_activity", "Social activity"
    if feature.startswith("body_type_") or feature == "sex_male":
        return "profile_fields", "Profile fields"
    return feature, _feature_label(feature)


def model_info() -> dict[str, Any]:
    manifest, metadata, _, preprocessor = get_runtime()
    feature_names = list(preprocessor.get_feature_names_out())
    return {
        "modelVersion": manifest["model_version"],
        "datasetVersion": metadata["dataset_version"],
        "targetDefinition": metadata["target_definition"],
        "rawFeatureCount": len(RAW_COLUMNS),
        "transformedFeatureCount": len(feature_names),
        "rawColumns": RAW_COLUMNS,
        "metrics": metadata["metrics"],
        "limitations": metadata["data_limitations"],
    }


def run_prediction(payload: dict[str, Any]) -> dict[str, Any]:
    manifest, metadata, model, preprocessor = get_runtime()
    feature_names = list(preprocessor.get_feature_names_out())
    df = pd.DataFrame([payload])
    transformed = preprocessor.transform(df)
    expected_features = len(feature_names)
    if transformed.shape != (1, expected_features) or not np.isfinite(transformed).all():
        raise RuntimeError(f"Submitted survey did not produce a finite 1x{expected_features} model input")
    import shap
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(transformed)
    contributions = shap_values[0]
    prediction = max(0.0, float(model.predict(transformed)[0]))
    base_value = float(explainer.expected_value) if np.isscalar(explainer.expected_value) else float(explainer.expected_value[0])
    groups: dict[str, dict[str, Any]] = {}
    for index, feature in enumerate(feature_names):
        key, label = _contribution_group(feature)
        groups.setdefault(key, {"feature": key, "label": label, "shapValue": 0.0})
        groups[key]["shapValue"] += float(contributions[index])
    items = []
    for item in sorted(groups.values(), key=lambda value: abs(value["shapValue"]), reverse=True):
        rounded = round(item["shapValue"], 3)
        if abs(rounded) >= 0.001:
            items.append({**item, "shapValue": rounded, "direction": "increases" if rounded >= 0 else "decreases"})
    q_hat = float(metadata["conformal_prediction"]["quantile_90"])
    return {
        "predictedKg": round(prediction, 1),
        "submittedAnswers": payload,
        "modelVersion": manifest["model_version"],
        "datasetVersion": metadata["dataset_version"],
        "targetDefinition": metadata["target_definition"],
        "uncertaintyRange": {"low": round(max(0.0, prediction - q_hat), 1), "high": round(prediction + q_hat, 1)},
        "metrics": metadata["metrics"],
        "runtime": {"engine": metadata.get("best_model", "ensemble"), "rawFeatureCount": len(RAW_COLUMNS), "transformedFeatureCount": len(feature_names)},
        "explanation": {
            "baseValue": round(base_value, 3),
            "predictedValue": round(prediction, 1),
            "contributions": items,
            "reconciliation": round(base_value + sum(item["shapValue"] for item in items), 3),
            "note": "Gradient Boosting tree contributions recalculated from the values submitted in this survey response. They describe model behavior, not causal environmental impact.",
        },
        "disclaimer": "This is an indicative model estimate from a formula-derived synthetic training target, not a direct emissions measurement or verified reduction result.",
    }

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
sys.path.insert(0, str(ROOT))

from app.core.final_contract import FEATURE_NAMES

MODEL_PATH = ARTIFACTS / "best_carbon_model.joblib"
PREPROCESSOR_PATH = ARTIFACTS / "preprocessor_10k_final.joblib"
METADATA_PATH = ARTIFACTS / "model_metadata.json"
MANIFEST_PATH = ARTIFACTS / "manifest.json"
RUNTIME: tuple[dict[str, Any], dict[str, Any], Any, Any] | None = None

LABELS = {
    "monthly_grocery_bill": "Monthly grocery spending",
    "vehicle_monthly_distance_km": "Vehicle distance",
    "waste_bag_weekly_count": "Weekly waste volume",
    "how_long_tv_pc_daily_hour": "TV and computer time",
    "how_many_new_clothes_monthly": "New clothing frequency",
    "how_long_internet_daily_hour": "Internet time",
}


def contribution_group(feature: str) -> tuple[str, str]:
    if feature in {"monthly_grocery_bill"} or feature.startswith("diet_"):
        return "diet_and_grocery", "Diet and grocery"
    if feature in {"vehicle_monthly_distance_km"} or feature.startswith("transport_"):
        return "transport_and_distance", "Transport and distance"
    if feature.startswith("heating_energy_source_"):
        return "home_energy", "Home energy"
    if feature.startswith("frequency_of_traveling_by_air_"):
        return "air_travel_frequency", "Air travel frequency"
    if feature in {"waste_bag_weekly_count"} or feature.startswith("waste_bag_size_") or feature.startswith("recycle_"):
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
    return feature, feature_label(feature)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    file_hashes = manifest.get("files", manifest)
    for name in ("best_carbon_model.joblib", "preprocessor_10k_final.joblib", "model_metadata.json"):
        actual = sha256(ARTIFACTS / name)
        if actual != file_hashes[name]:
            raise RuntimeError(f"Artifact integrity check failed for {name}")
    return manifest


def feature_label(feature: str) -> str:
    if feature in LABELS:
        return LABELS[feature]
    if feature.startswith("recycle_"):
        return f"Recycling: {feature.removeprefix('recycle_')}"
    if feature.startswith("cook_"):
        return f"Cooking: {feature.removeprefix('cook_')}"
    return feature.replace("_", " ").replace("x ", "× ").title()


def get_runtime() -> tuple[dict[str, Any], dict[str, Any], Any, Any]:
    global RUNTIME
    if RUNTIME is not None:
        return RUNTIME
    manifest = verify_manifest()
    metadata = json.loads(METADATA_PATH.read_text())
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    names = list(preprocessor.get_feature_names_out())
    if len(names) != len(FEATURE_NAMES):
        raise RuntimeError(f"Persisted preprocessor emits {len(names)} features but contract requires {len(FEATURE_NAMES)}")
    RUNTIME = (manifest, metadata, model, preprocessor)
    return RUNTIME


def result_for(payload: dict[str, Any]) -> dict[str, Any]:
    import pandas as pd

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
    grouped: dict[str, dict[str, Any]] = {}
    for index, feature in enumerate(feature_names):
        key, label = contribution_group(feature)
        if key not in grouped:
            grouped[key] = {"feature": key, "label": label, "shapValue": 0.0}
        grouped[key]["shapValue"] += float(contributions[index])
    items = []
    for item in sorted(grouped.values(), key=lambda value: abs(value["shapValue"]), reverse=True):
        rounded = round(item["shapValue"], 3)
        if abs(rounded) >= 0.001:
            items.append({**item, "shapValue": rounded, "direction": "increases" if rounded >= 0 else "decreases"})
    reconciliation = round(base_value + sum(item["shapValue"] for item in items), 3)
    metrics = metadata.get("metrics", {})
    rmse = float(metrics.get("rmse", 196.38))
    return {
        "predictedKg": round(prediction, 1),
        "modelVersion": manifest["model_version"],
        "datasetVersion": metadata.get("dataset_version", "kaggle-carbon-emission-v1"),
        "targetDefinition": metadata.get("target_definition", "Formula-derived synthetic monthly kgCO2e estimate"),
        "uncertaintyRange": {"low": round(max(0.0, prediction - rmse), 1), "high": round(prediction + rmse, 1)},
        "metrics": {"r2": metrics.get("r2_test"), "mae": metrics.get("mae"), "rmse": rmse},
        "runtime": {"engine": metadata.get("best_model", "gradient_boosting"), "rawFeatureCount": len(FEATURE_NAMES), "transformedFeatureCount": len(feature_names)},
        "explanation": {
            "baseValue": round(base_value, 3),
            "predictedValue": round(prediction, 1),
            "contributions": items,
            "reconciliation": reconciliation,
            "note": "Gradient Boosting tree contributions recalculated from the values submitted in this survey response. They describe model behavior, not causal environmental impact.",
        },
        "disclaimer": "This is an indicative model estimate from a formula-derived synthetic training target, not a direct emissions measurement or verified reduction result.",
    }


def main() -> None:
    payload = json.loads(sys.stdin.read())
    print(json.dumps(result_for(payload), separators=(",", ":")))


def worker() -> None:
    for line in sys.stdin:
        try:
            payload = json.loads(line)
            print(json.dumps(result_for(payload), separators=(",", ":")), flush=True)
        except Exception as error:
            print(json.dumps({"error": str(error)}, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    try:
        worker() if "--worker" in sys.argv else main()
    except Exception as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        raise

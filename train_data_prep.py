"""Batch-wise training: preprocess data once, save for per-model training runs."""

from __future__ import annotations

import ast
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = PROJECT_ROOT / "server" / "model_runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from app.core.final_contract import (  # noqa: E402
    DEFAULTS,
    FEATURE_NAMES,
    FinalPreprocessor,
)

DATA_DIR = PROJECT_ROOT / "data" / "raw"
EXPERIMENT_DIR = PROJECT_ROOT / "models" / "trained" / "experiments" / datetime.now().strftime("%Y-%m-%d")
EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

SHOWER_MAP = {"less frequently": "rarely", "more frequently": "often"}
HEATING_MAP = {"coal": "electricity"}
AIR_TRAVEL_MAP = {"frequently": "often"}
VEHICLE_TYPE_MAP = {"": "none"}
RECYCLING_MAP = {"paper": "paper", "plastic": "plastic", "metal": "metal", "glass": "glass", "none": "none"}
COOKING_MAP = {"stove": "stove", "oven": "oven", "microwave": "microwave", "grill": "grill", "airfryer": "airfryer", "none": "none"}


def _parse_list(v, item_map):
    if isinstance(v, list):
        return [item_map.get(x.lower(), x.lower()) for x in v]
    try:
        parsed = ast.literal_eval(str(v))
        if isinstance(parsed, list):
            return [item_map.get(x.lower().strip(), x.lower().strip()) for x in parsed]
    except (ValueError, SyntaxError):
        pass
    return []


def main():
    print("=" * 60)
    print("Step 1: Load and preprocess data, save for batch training")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "individual_carbon_footprint.csv")
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

    target_col = "carbonemission" if "carbonemission" in df.columns else "carbon_emission"
    y = df[target_col].copy()
    X = df.drop(columns=[target_col])
    X.drop(columns=["currency", "age"], errors="ignore", inplace=True)
    X["region"] = "mixed"

    X["how_often_shower"] = X["how_often_shower"].map(lambda v: SHOWER_MAP.get(v, v))
    X["heating_energy_source"] = X["heating_energy_source"].map(lambda v: HEATING_MAP.get(v, v))
    X["frequency_of_traveling_by_air"] = X["frequency_of_traveling_by_air"].map(lambda v: AIR_TRAVEL_MAP.get(v, v))
    X["vehicle_type"] = X["vehicle_type"].fillna("").map(lambda v: VEHICLE_TYPE_MAP.get(v, v))
    for col in ["body_type", "sex", "diet", "transport", "social_activity", "waste_bag_size"]:
        X[col] = X[col].str.lower()

    X["recycling"] = X["recycling"].apply(lambda v: _parse_list(v, RECYCLING_MAP))
    X["cooking_with"] = X["cooking_with"].apply(lambda v: _parse_list(v, COOKING_MAP))

    for col in ["monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count",
                "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour"]:
        X[col] = X[col].astype(float).fillna(DEFAULTS[col])

    X.dropna(subset=[
        "body_type", "sex", "diet", "how_often_shower", "heating_energy_source",
        "transport", "vehicle_type", "social_activity", "frequency_of_traveling_by_air",
        "waste_bag_size", "energy_efficiency", "region",
    ], inplace=True)
    y = y.loc[X.index]

    print(f"Rows: {len(X)}")

    preprocessor = FinalPreprocessor(feature_names=list(FEATURE_NAMES))
    X_np = preprocessor.transform(X)
    feature_names = list(preprocessor.get_feature_names_out())

    assert len(feature_names) == 55, f"Expected 55 features, got {len(feature_names)}"
    assert feature_names == FEATURE_NAMES, "Feature names do not match contract"
    print(f"Features: {X_np.shape[1]} — contract validated")

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_np, y.values, test_size=0.2, random_state=42)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    np.save(EXPERIMENT_DIR / "X_train.npy", X_train)
    np.save(EXPERIMENT_DIR / "X_test.npy", X_test)
    np.save(EXPERIMENT_DIR / "y_train.npy", y_train)
    np.save(EXPERIMENT_DIR / "y_test.npy", y_test)

    # Save the raw DataFrame rows for SHAP smoke test (need the original row)
    X_train_df = X.iloc[:len(X_train)].copy()
    X_train_df.to_csv(EXPERIMENT_DIR / "X_train_df_sample.csv", index=False)

    # Save results accumulator
    results_file = EXPERIMENT_DIR / "results.json"
    if results_file.exists():
        results_file.unlink()
    with open(results_file, "w") as f:
        json.dump([], f)

    print(f"\nData saved to: {EXPERIMENT_DIR}")
    print("Run: python train_model_batch.py <model_name>")


if __name__ == "__main__":
    main()

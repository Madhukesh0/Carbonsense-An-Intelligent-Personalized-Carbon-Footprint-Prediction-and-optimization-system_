"""Candidate training experiment: train 5 regressors using the frozen 55-feature contract."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.svm import SVR
from xgboost import XGBRegressor

# ---------------------------------------------------------------------------
# Contract imports
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = PROJECT_ROOT / "server" / "model_runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from app.core.final_contract import (  # noqa: E402
    DEFAULTS,
    FEATURE_NAMES,
    RAW_COLUMNS,
    SUPPORTED,
    FinalPreprocessor,
    engineer_features,
)

# Directories
DATA_DIR = PROJECT_ROOT / "data" / "raw"
EXPERIMENT_DIR = PROJECT_ROOT / "models" / "trained" / "experiments"
TODAY = datetime.now().strftime("%Y-%m-%d")
EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Value mapping: Kaggle dataset → contract-supported values
# ---------------------------------------------------------------------------
SHOWER_MAP = {
    "less frequently": "rarely",
    "more frequently": "often",
    "rarely": "rarely",
    "daily": "daily",
    "often": "often",
    "twice a day": "twice a day",
}

HEATING_MAP = {
    "coal": "electricity",
    "electricity": "electricity",
    "natural gas": "natural gas",
    "wood": "wood",
}

AIR_TRAVEL_MAP = {
    "never": "never",
    "rarely": "rarely",
    "frequently": "often",
    "often": "often",
    "very frequently": "very frequently",
}

VEHICLE_TYPE_MAP = {
    "": "none",
    "none": "none",
    "petrol": "petrol",
    "diesel": "diesel",
    "electric": "electric",
    "hybrid": "hybrid",
    "lpg": "lpg",
}

RECYCLING_ITEM_MAP = {
    "paper": "paper",
    "plastic": "plastic",
    "metal": "metal",
    "glass": "glass",
    "none": "none",
}

COOKING_ITEM_MAP = {
    "stove": "stove",
    "oven": "oven",
    "microwave": "microwave",
    "grill": "grill",
    "airfryer": "airfryer",
    "none": "none",
}


def _parse_multi_field(value, item_map):
    """Parse a string representation of a list into a list of mapped values."""
    if isinstance(value, list):
        return [item_map.get(v.lower(), v.lower()) for v in value]
    if pd.isna(value) or value == "[]":
        return []
    try:
        parsed = ast.literal_eval(str(value))
        if isinstance(parsed, list):
            return [item_map.get(item.lower().strip(), item.lower().strip()) for item in parsed]
    except (ValueError, SyntaxError):
        pass
    return []


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_and_prepare_data():
    """Load raw Kaggle dataset and convert to survey-compatible format for the contract."""
    print("Loading dataset...")
    df = pd.read_csv(DATA_DIR / "individual_carbon_footprint.csv")

    # Normalize column names
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

    # Drop columns not in the contract
    for col in ["currency", "age"]:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Add region if missing
    if "region" not in df.columns:
        df["region"] = "mixed"

    # Target column
    target_col = "carbonemission" if "carbonemission" in df.columns else "carbon_emission"
    if target_col not in df.columns:
        raise RuntimeError(f"Target column not found. Available: {list(df.columns)}")

    y = df[target_col].copy()

    # Drop target from features
    feature_df = df.drop(columns=[target_col])

    # --- Map categorical values to contract-supported values ---
    feature_df["how_often_shower"] = feature_df["how_often_shower"].map(SHOWER_MAP)
    feature_df["heating_energy_source"] = feature_df["heating_energy_source"].map(HEATING_MAP)
    feature_df["frequency_of_traveling_by_air"] = feature_df["frequency_of_traveling_by_air"].map(AIR_TRAVEL_MAP)
    feature_df["vehicle_type"] = feature_df["vehicle_type"].fillna("").map(VEHICLE_TYPE_MAP)

    # Lowercase categorical values that already match SUPPORTED
    for col in ["body_type", "sex", "diet", "transport", "social_activity", "waste_bag_size"]:
        if col in feature_df.columns:
            feature_df[col] = feature_df[col].str.lower()

    # Parse recycling and cooking_with from string-lists to Python lists
    feature_df["recycling"] = feature_df["recycling"].apply(lambda v: _parse_multi_field(v, RECYCLING_ITEM_MAP))
    feature_df["cooking_with"] = feature_df["cooking_with"].apply(lambda v: _parse_multi_field(v, COOKING_ITEM_MAP))

    # Drop rows with unmapped NaN in critical categorical fields
    critical_cats = [
        "body_type", "sex", "diet", "how_often_shower", "heating_energy_source",
        "transport", "vehicle_type", "social_activity", "frequency_of_traveling_by_air",
        "waste_bag_size", "energy_efficiency", "region",
    ]
    before = len(feature_df)
    feature_df.dropna(subset=[c for c in critical_cats if c in feature_df.columns], inplace=True)
    dropped = before - len(feature_df)
    if dropped:
        print(f"Dropped {dropped} rows with unmappable categorical values")

    # Fill remaining NaN in numeric fields with defaults
    for col in ["monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count",
                "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour"]:
        if col in feature_df.columns:
            feature_df[col] = feature_df[col].fillna(DEFAULTS[col])

    # Convert numeric columns to float
    numeric_cols = ["monthly_grocery_bill", "vehicle_monthly_distance_km", "waste_bag_weekly_count",
                    "how_long_tv_pc_daily_hour", "how_many_new_clothes_monthly", "how_long_internet_daily_hour"]
    for col in numeric_cols:
        if col in feature_df.columns:
            feature_df[col] = feature_df[col].astype(float)

    print(f"Dataset shape: {feature_df.shape}, Target shape: {y.shape}")
    print(f"Target range: {y.min():.1f} - {y.max():.1f} kg CO2e/month")

    return feature_df, y


# ---------------------------------------------------------------------------
# Model definitions (same as original, 5 regressors)
# ---------------------------------------------------------------------------
def define_models():
    """Define 5 models with hyperparameter search spaces."""
    return {
        "Gradient Boosting": {
            "model": GradientBoostingRegressor(random_state=42),
            "params": {
                "model__n_estimators": [100, 200, 300],
                "model__learning_rate": [0.01, 0.05, 0.1],
                "model__max_depth": [3, 5, 7],
                "model__subsample": [0.8, 0.9, 1.0],
            },
        },
        "XGBoost": {
            "model": XGBRegressor(random_state=42, enable_categorical=True),
            "params": {
                "model__n_estimators": [100, 200, 300],
                "model__learning_rate": [0.01, 0.05, 0.1],
                "model__max_depth": [3, 5, 7],
                "model__subsample": [0.8, 0.9],
                "model__colsample_bytree": [0.8, 0.9],
            },
        },
        "Random Forest": {
            "model": RandomForestRegressor(random_state=42, n_jobs=-1),
            "params": {
                "model__n_estimators": [100, 200, 300],
                "model__max_depth": [10, 20, 30, None],
                "model__min_samples_split": [2, 5, 10],
                "model__min_samples_leaf": [1, 2, 4],
            },
        },
        "Linear Regression": {
            "model": LinearRegression(),
            "params": {},
        },
        "SVR": {
            "model": SVR(),
            "params": {
                "model__C": [0.1, 1, 10, 100],
                "model__epsilon": [0.01, 0.1, 0.2],
                "model__kernel": ["rbf", "linear"],
            },
        },
    }


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def train_and_evaluate(X_train_df, X_test_df, y_train, y_test, preprocessor):
    """Train all 5 models and return results.

    The FinalPreprocessor is applied *before* training so it is not inside the
    sklearn Pipeline (its ``fit`` signature is not Pipeline-compatible).
    """
    # Transform once through the frozen 55-feature preprocessor
    print("\nTransforming data through FinalPreprocessor...")
    X_train_np = preprocessor.transform(X_train_df)
    X_test_np = preprocessor.transform(X_test_df)
    print(f"  X_train: {X_train_np.shape}, X_test: {X_test_np.shape}")
    assert X_train_np.shape[1] == 55, f"Expected 55 features, got {X_train_np.shape[1]}"

    models = define_models()
    results = []

    for name, config in models.items():
        print(f"\n{'=' * 60}")
        print(f"Training: {name}")
        print("=" * 60)

        model = config["model"]

        if config["params"]:
            print(f"Running RandomizedSearchCV ({len(config['params'])} params)...")
            # Map param names from model__X to just X (no pipeline prefix)
            flat_params = {}
            for k, v in config["params"].items():
                flat_params[k.replace("model__", "")] = v
            search = RandomizedSearchCV(
                model,
                flat_params,
                n_iter=20,
                cv=5,
                scoring="r2",
                random_state=42,
                n_jobs=-1,
                verbose=1,
            )
            search.fit(X_train_np, y_train)
            best_estimator = search.best_estimator_
            print(f"Best params: {search.best_params_}")
        else:
            print("Training baseline model (no hyperparameter tuning)...")
            model.fit(X_train_np, y_train)
            best_estimator = model

        y_pred = best_estimator.predict(X_test_np)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        print(f"\n{name} Results:")
        print(f"  R²:  {r2:.4f}")
        print(f"  MAE: {mae:.2f} kg CO2e/month")
        print(f"  RMSE: {rmse:.2f} kg CO2e/month")

        results.append({
            "model_name": name,
            "estimator": best_estimator,
            "r2": r2,
            "mae": mae,
            "rmse": rmse,
        })

    return results


# ---------------------------------------------------------------------------
# Candidate saving
# ---------------------------------------------------------------------------
def save_candidate(results, X_train_df, y_train, preprocessor):
    """Save the best model as a dated candidate under experiments/."""
    # Sort by RMSE (primary), then MAE (secondary), then R² (tertiary)
    results_sorted = sorted(results, key=lambda r: (r["rmse"], -r["mae"], -r["r2"]))
    best = results_sorted[0]

    print(f"\n{'=' * 60}")
    print(f"BEST CANDIDATE: {best['model_name']}")
    print(f"  RMSE = {best['rmse']:.2f}, MAE = {best['mae']:.2f}, R² = {best['r2']:.4f}")
    print("=" * 60)

    exp_dir = EXPERIMENT_DIR / TODAY
    exp_dir.mkdir(parents=True, exist_ok=True)

    # --- Enforce 55-feature contract ---
    feature_names = list(preprocessor.get_feature_names_out())
    if len(feature_names) != 55:
        raise RuntimeError(
            f"CONTRACT VIOLATION: preprocessor produced {len(feature_names)} features, expected exactly 55"
        )
    if feature_names != FEATURE_NAMES:
        mismatched = [i for i, (a, b) in enumerate(zip(feature_names, FEATURE_NAMES)) if a != b]
        raise RuntimeError(
            f"CONTRACT VIOLATION: feature names do not match FEATURE_NAMES in order. "
            f"First {len(mismatched)} mismatches at indices: {mismatched[:10]}"
        )
    print(f"Feature count: {len(feature_names)} — PASS (exactly 55)")

    # --- SHAP smoke test ---
    print("\nRunning SHAP smoke test on one row...")
    try:
        import shap
        sample = X_train_df.iloc[:1]
        transformed = preprocessor.transform(sample)
        explainer = shap.TreeExplainer(best["estimator"])
        shap_values = explainer.shap_values(transformed)
        shap_arr = np.asarray(shap_values)
        if shap_arr.ndim == 3:
            shap_arr = shap_arr[0]
        assert shap_arr.shape == (1, 55), f"SHAP output shape {shap_arr.shape}, expected (1, 55)"
        assert np.isfinite(shap_arr).all(), "SHAP values contain non-finite entries"
        print("SHAP smoke test — PASS")
    except Exception as exc:
        print(f"SHAP smoke test — FAILED: {exc}")
        print("Aborting save. Investigate SHAP compatibility before retrying.")
        return None

    # --- Conformal prediction interval (90%) ---
    X_train_np = preprocessor.transform(X_train_df)
    residuals = y_train.values - best["estimator"].predict(X_train_np)
    conformal_quantile = float(np.percentile(np.abs(residuals), 90))

    # --- Comparison table ---
    comparison_df = pd.DataFrame([
        {"model_name": r["model_name"], "r2": r["r2"], "mae": r["mae"], "rmse": r["rmse"]}
        for r in results_sorted
    ])
    comparison_df.to_csv(exp_dir / "model_comparison_results.csv", index=False)

    # --- Metadata ---
    metadata = {
        "best_model": best["model_name"],
        "dataset_version": "individual-10k-regional-v1",
        "target_definition": "formula-derived synthetic monthly kgCO2e estimate",
        "raw_feature_count": 34,
        "transformed_feature_count": 55,
        "model_type": type(best["estimator"]).__name__,
        "metrics": {
            "r2": float(best["r2"]),
            "mae": float(best["mae"]),
            "rmse": float(best["rmse"]),
        },
        "conformal_quantile_90": conformal_quantile,
        "training_date": TODAY,
        "feature_contract": "55-feature frozen contract (final_contract.py)",
        "preprocessing": "FinalPreprocessor from server/model_runtime/app/core/final_contract.py",
        "data_limitations": "The target is synthetic and formula-derived; metrics measure agreement with generated targets, not verified personal emissions.",
        "is_candidate": True,
    }
    with open(exp_dir / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # --- Save artifacts ---
    joblib.dump(best["estimator"], exp_dir / "best_candidate_model.joblib")
    joblib.dump(preprocessor, exp_dir / "preprocessor.joblib")
    np.save(exp_dir / "conformal_quantile.npy", conformal_quantile)

    # --- SHA-256 manifest ---
    def sha256(path):
        digest = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    manifest = {
        "source": "candidate-experiment",
        "dataset_version": "individual-10k-regional-v1",
        "model_version": f"{best['model_name'].lower().replace(' ', '-')}-candidate-v1",
        "feature_contract": "55-feature frozen contract",
        "feature_count": 55,
        "artifacts": {
            "best_candidate_model.joblib": sha256(exp_dir / "best_candidate_model.joblib"),
            "preprocessor.joblib": sha256(exp_dir / "preprocessor.joblib"),
            "model_metadata.json": sha256(exp_dir / "model_metadata.json"),
        },
    }
    with open(exp_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nCandidate saved to: {exp_dir}")
    print("\n--- MODEL COMPARISON (sorted by RMSE → MAE → R²) ---")
    print(comparison_df.to_string(index=False))
    print(f"\n--- VERIFICATION ---")
    print(f"  Feature count: 55 — PASS")
    print(f"  Feature names match contract: PASS")
    print(f"  SHAP smoke test: PASS")
    print(f"  Conformal quantile (90%): ±{conformal_quantile:.2f} kg CO2e")
    print(f"\n--- PRODUCTION FILES NOT MODIFIED ---")
    print(f"  server/model_runtime/artifacts/ — untouched")
    print(f"  backend/app/services/prediction.py — untouched")
    print(f"  server/model_runtime/infer.py — untouched")
    print(f"\nThis is a CANDIDATE. Promote only after explicit approval.")

    return exp_dir


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("CarbonSense — Candidate Training Experiment (55-Feature Contract)")
    print("=" * 60)

    # Load and prepare data
    X, y = load_and_prepare_data()

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTrain: {len(X_train)} samples, Test: {len(X_test)} samples")

    # Create the frozen 55-feature preprocessor
    preprocessor = FinalPreprocessor(feature_names=list(FEATURE_NAMES))

    # Train all 5 models
    results = train_and_evaluate(X_train, X_test, y_train, y_test, preprocessor)

    # Save best as candidate
    save_candidate(results, X_train, y_train, preprocessor)


if __name__ == "__main__":
    main()

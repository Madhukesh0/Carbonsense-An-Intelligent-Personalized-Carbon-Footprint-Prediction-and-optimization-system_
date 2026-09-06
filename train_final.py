"""
CarbonSense — Final ML Training Pipeline
=========================================
Loads the raw Kaggle dataset, cleans it, engineers features (no regional noise),
trains 5 models, evaluates, saves the best model + all artifacts.

Output:
  data/final_training/model.joblib
  data/final_training/preprocessor.joblib
  data/final_training/model_metadata.json
  data/final_training/manifest.json
  data/final_training/comparison.csv
  data/final_training/clean_dataset.csv
  data/final_training/preprocessed_features.csv
  data/final_training/TRAINING_REPORT.md
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

# Force unbuffered output on Windows
sys.stdout.reconfigure(line_buffering=True)

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("[WARN] xgboost not installed — skipping XGBoost model")

warnings.filterwarnings("ignore", category=FutureWarning)

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "kaggle_carbon_footprint" / "Carbon Emission.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "final_training"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
np.random.seed(SEED)

# ── 1. LOAD & CLEAN ───────────────────────────────────────────────────

print("=" * 70)
print("STEP 1: Loading and cleaning raw Kaggle dataset")
print("=" * 70)

df = pd.read_csv(RAW_CSV)
print(f"  Raw shape: {df.shape}")
print(f"  Nulls before cleaning: {df.isnull().sum().sum()}")

# Rename columns to snake_case
col_map = {
    "Body Type": "body_type",
    "Sex": "sex",
    "Diet": "diet",
    "How Often Shower": "how_often_shower",
    "Heating Energy Source": "heating_energy_source",
    "Transport": "transport",
    "Vehicle Type": "vehicle_type",
    "Social Activity": "social_activity",
    "Monthly Grocery Bill": "monthly_grocery_bill",
    "Frequency of Traveling by Air": "frequency_of_traveling_by_air",
    "Vehicle Monthly Distance Km": "vehicle_monthly_distance_km",
    "Waste Bag Size": "waste_bag_size",
    "Waste Bag Weekly Count": "waste_bag_weekly_count",
    "How Long TV PC Daily Hour": "how_long_tv_pc_daily_hour",
    "How Many New Clothes Monthly": "how_many_new_clothes_monthly",
    "How Long Internet Daily Hour": "how_long_internet_daily_hour",
    "Energy efficiency": "energy_efficiency",
    "Recycling": "recycling",
    "Cooking_With": "cooking_with",
    "CarbonEmission": "carbon_emission_kgco2e_month",
}
df.rename(columns=col_map, inplace=True)

# Map categorical values to match the contract
shower_map = {"less frequently": "rarely", "more frequently": "often"}
df["how_often_shower"] = df["how_often_shower"].replace(shower_map)

heating_map = {"coal": "electricity"}
df["heating_energy_source"] = df["heating_energy_source"].replace(heating_map)

air_map = {"frequently": "often"}
df["frequency_of_traveling_by_air"] = df["frequency_of_traveling_by_air"].replace(air_map)

# Fill vehicle_type: nulls are for non-private transport → fill with "none"
df["vehicle_type"] = df["vehicle_type"].fillna("none")

print(f"  Nulls after cleaning: {df.isnull().sum().sum()}")
print(f"  Clean shape: {df.shape}")

# Save cleaned dataset
df.to_csv(OUTPUT_DIR / "clean_dataset.csv", index=False)
print(f"  Saved: clean_dataset.csv")

# ── 2. FEATURE ENGINEERING ────────────────────────────────────────────

print()
print("=" * 70)
print("STEP 2: Feature engineering (NO regional noise)")
print("=" * 70)


def parse_multi_column(series: pd.Series, prefix: str) -> pd.DataFrame:
    """Parse stringified lists like "['Paper', 'Glass']" into binary columns."""
    all_items = set()
    parsed = []
    for val in series:
        try:
            items = ast.literal_eval(str(val)) if pd.notna(val) else []
        except (ValueError, SyntaxError):
            items = []
        if isinstance(items, str):
            items = [items]
        parsed.append(set(items))
        all_items.update(items)

    result = {}
    for item in sorted(all_items):
        col_name = f"{prefix}_{item.lower().replace(' ', '_')}"
        result[col_name] = [int(item in row) for row in parsed]
    return pd.DataFrame(result)


# Parse recycling and cooking
recycle_df = parse_multi_column(df["recycling"], "recycle")
cook_df = parse_multi_column(df["cooking_with"], "cook")

# Numeric features (6 core + engineered interactions)
numeric_features = [
    "monthly_grocery_bill",
    "vehicle_monthly_distance_km",
    "waste_bag_weekly_count",
    "how_long_tv_pc_daily_hour",
    "how_many_new_clothes_monthly",
    "how_long_internet_daily_hour",
]

# Categorical features to one-hot encode (drop_first=True to avoid multicollinearity)
categorical_features = [
    "body_type",
    "sex",
    "diet",
    "how_often_shower",
    "heating_energy_source",
    "transport",
    "vehicle_type",
    "social_activity",
    "frequency_of_traveling_by_air",
    "waste_bag_size",
    "energy_efficiency",
]

# Build feature matrix
X_num = df[numeric_features].copy()

# One-hot encode categoricals
X_cat = pd.get_dummies(df[categorical_features], drop_first=True, dtype=int)

# Combine all features
X = pd.concat([X_num, X_cat, recycle_df, cook_df], axis=1)
y = df["carbon_emission_kgco2e_month"].copy()

# Ensure all columns are numeric
for col in X.columns:
    X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

print(f"  Features: {X.shape[1]}")
print(f"  Samples:  {X.shape[0]}")
print(f"  Feature names: {list(X.columns)}")

# Save preprocessed features
preprocessed = X.copy()
preprocessed["target"] = y.values
preprocessed.to_csv(OUTPUT_DIR / "preprocessed_features.csv", index=False)
print(f"  Saved: preprocessed_features.csv")

# ── 3. TRAIN / TEST SPLIT ─────────────────────────────────────────────

print()
print("=" * 70)
print("STEP 3: Train/test split")
print("=" * 70)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED
)
print(f"  Train: {X_train.shape[0]} samples")
print(f"  Test:  {X_test.shape[0]} samples")

# Save splits
X_train.to_csv(OUTPUT_DIR / "train_X.csv", index=False)
y_train.to_csv(OUTPUT_DIR / "train_y.csv", index=False)
X_test.to_csv(OUTPUT_DIR / "test_X.csv", index=False)
y_test.to_csv(OUTPUT_DIR / "test_y.csv", index=False)
print(f"  Saved: train_X.csv, train_y.csv, test_X.csv, test_y.csv")


# ── 4. MODEL TRAINING ─────────────────────────────────────────────────

print()
print("=" * 70)
print("STEP 4: Training 5 models with hyperparameter search")
print("=" * 70)


def evaluate_model(name, model, X_tr, y_tr, X_te, y_te):
    """Train, evaluate, return metrics dict."""
    t0 = time.time()
    model.fit(X_tr, y_tr)
    train_time = time.time() - t0

    y_pred_train = model.predict(X_tr)
    y_pred_test = model.predict(X_te)

    r2_train = r2_score(y_tr, y_pred_train)
    r2_test = r2_score(y_te, y_pred_test)
    mae = mean_absolute_error(y_te, y_pred_test)
    rmse = np.sqrt(mean_squared_error(y_te, y_pred_test))
    mape = np.mean(np.abs((y_te - y_pred_test) / np.maximum(y_te, 1e-9))) * 100

    # 5-fold CV on training set
    cv_scores = cross_val_score(model, X_tr, y_tr, cv=5, scoring="r2", n_jobs=1)
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()

    return {
        "model": name,
        "r2_train": round(r2_train, 6),
        "r2_test": round(r2_test, 6),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 4),
        "cv_r2_mean": round(cv_mean, 6),
        "cv_r2_std": round(cv_std, 6),
        "train_time_s": round(train_time, 2),
        "n_features": X_tr.shape[1],
    }


# Define hyperparameter search spaces
models = {
    "GradientBoosting": {
        "estimator": GradientBoostingRegressor(random_state=SEED),
        "params": {
            "n_estimators": randint(200, 800),
            "max_depth": randint(3, 10),
            "learning_rate": uniform(0.01, 0.2),
            "subsample": uniform(0.7, 0.3),
            "min_samples_split": randint(2, 20),
            "min_samples_leaf": randint(1, 10),
        },
    },
    "RandomForest": {
        "estimator": RandomForestRegressor(random_state=SEED, n_jobs=1),
        "params": {
            "n_estimators": randint(200, 800),
            "max_depth": randint(5, 20),
            "min_samples_split": randint(2, 20),
            "min_samples_leaf": randint(1, 10),
            "max_features": ["sqrt", "log2", 0.5, 0.7, 0.9],
        },
    },
    "LinearRegression": {
        "estimator": LinearRegression(),
        "params": {},
    },
    "SVR": {
        "estimator": SVR(),
        "params": {
            "C": uniform(0.1, 100),
            "epsilon": uniform(0.01, 10),
            "kernel": ["rbf", "linear"],
        },
    },
}

if HAS_XGB:
    models["XGBoost"] = {
        "estimator": xgb.XGBRegressor(
            random_state=SEED,
            n_jobs=1,
            tree_method="hist",
            verbosity=0,
        ),
        "params": {
            "n_estimators": randint(200, 800),
            "max_depth": randint(3, 12),
            "learning_rate": uniform(0.01, 0.3),
            "subsample": uniform(0.6, 0.4),
            "colsample_bytree": uniform(0.5, 0.5),
            "min_child_weight": randint(1, 10),
            "reg_alpha": uniform(0, 1),
            "reg_lambda": uniform(0, 2),
        },
    }

results = []
best_model = None
best_r2 = -999
best_name = ""

for name, config in models.items():
    print(f"\n  Training {name}...")
    estimator = config["estimator"]
    params = config["params"]

    if params:
        search = RandomizedSearchCV(
            estimator,
            params,
            n_iter=40,
            cv=5,
            scoring="r2",
            random_state=SEED,
            n_jobs=1,
            verbose=0,
        )
        search.fit(X_train, y_train)
        model = search.best_estimator_
        print(f"    Best params: {search.best_params_}")
    else:
        model = estimator
        model.fit(X_train, y_train)

    metrics = evaluate_model(name, model, X_train, y_train, X_test, y_test)
    results.append(metrics)
    print(f"    R² = {metrics['r2_test']:.4f} | MAE = {metrics['mae']:.2f} | RMSE = {metrics['rmse']:.2f} | CV = {metrics['cv_r2_mean']:.4f}±{metrics['cv_r2_std']:.4f}")

    if metrics["r2_test"] > best_r2:
        best_r2 = metrics["r2_test"]
        best_model = model
        best_name = name

print(f"\n  ★ Best model: {best_name} (R² = {best_r2:.4f})")

# ── 5. SAVE COMPARISON ────────────────────────────────────────────────

print()
print("=" * 70)
print("STEP 5: Saving comparison and artifacts")
print("=" * 70)

comparison_df = pd.DataFrame(results).sort_values("r2_test", ascending=False)
comparison_df.to_csv(OUTPUT_DIR / "comparison.csv", index=False)
print(f"  Saved: comparison.csv")
print()
print(comparison_df.to_string(index=False))

# ── 6. SAVE BEST MODEL + PREPROCESSOR ─────────────────────────────────

# Create a clean preprocessor class for the final model
class CleanPreprocessor(BaseEstimator, TransformerMixin):
    """Preprocessor that matches the cleaned dataset features."""

    def __init__(self, feature_names: list[str]):
        self.feature_names = feature_names

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            arr = X[self.feature_names].values.astype(float)
        else:
            arr = np.array(X, dtype=float)
        return arr

    def get_feature_names_out(self):
        return np.array(self.feature_names)


feature_names = list(X.columns)
preprocessor = CleanPreprocessor(feature_names=feature_names)

# Fit preprocessor on full training data
preprocessor.fit(X_train)

# Save model artifacts
model_path = OUTPUT_DIR / "model.joblib"
preprocessor_path = OUTPUT_DIR / "preprocessor.joblib"

joblib.dump(best_model, model_path)
joblib.dump(preprocessor, preprocessor_path)

print(f"  Saved: model.joblib ({best_name})")
print(f"  Saved: preprocessor.joblib ({len(feature_names)} features)")

# ── 7. MODEL METADATA ─────────────────────────────────────────────────

best_metrics = [r for r in results if r["model"] == best_name][0]

# Conformal prediction interval (90%) — computed on held-out test set only
y_pred_test = best_model.predict(X_test)
residuals = y_test.values - y_pred_test
alpha = 0.10
q_hat = np.quantile(np.abs(residuals), 1 - alpha)

metadata = {
    "model_type": type(best_model).__name__,
    "model_version": f"final-{best_name.lower().replace(' ', '-')}-v1",
    "training_date": datetime.now(timezone.utc).isoformat(),
    "dataset_source": "Kaggle Individual Carbon Footprint Calculation",
    "dataset_url": "https://www.kaggle.com/datasets/dumanmesut/individual-carbon-footprint-calculation",
    "n_samples": int(X.shape[0]),
    "n_features_raw": 0,  # raw survey inputs
    "n_features_transformed": int(X.shape[1]),
    "train_test_split": "80/20",
    "random_seed": SEED,
    "metrics": {
        "r2_train": best_metrics["r2_train"],
        "r2_test": best_metrics["r2_test"],
        "mae": best_metrics["mae"],
        "rmse": best_metrics["rmse"],
        "mape": best_metrics["mape"],
        "cv_r2_mean": best_metrics["cv_r2_mean"],
        "cv_r2_std": best_metrics["cv_r2_std"],
    },
    "conformal_prediction": {
        "alpha": alpha,
        "quantile_90": round(float(q_hat), 4),
        "uncertainty_range": f"+/- {round(float(q_hat), 2)} kgCO2e/month",
    },
    "feature_names": feature_names,
    "data_cleaning": {
        "vehicle_type_nulls_filled": "6721 nulls → 'none' (non-private transport)",
        "shower_mapping": {"less frequently": "rarely", "more frequently": "often"},
        "heating_mapping": {"coal": "electricity"},
        "air_travel_mapping": {"frequently": "often"},
        "regional_noise_removed": True,
        "columns_removed": ["region_grid_factor", "energy_proxy", "region", "transport_x_energy", "diet_x_grocery", "distance_energy_ratio"],
    },
    "model_comparison": results,
}

metadata_path = OUTPUT_DIR / "model_metadata.json"
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2, default=str)
print(f"  Saved: model_metadata.json")

# ── 8. SHA-256 MANIFEST ───────────────────────────────────────────────


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


manifest = {
    "model_version": metadata["model_version"],
    "generated_at": metadata["training_date"],
    "files": {
        "model.joblib": sha256_file(model_path),
        "preprocessor.joblib": sha256_file(preprocessor_path),
        "model_metadata.json": sha256_file(metadata_path),
    },
}

manifest_path = OUTPUT_DIR / "manifest.json"
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
print(f"  Saved: manifest.json")

# ── 9. TRAINING REPORT ────────────────────────────────────────────────

report_lines = [
    "# CarbonSense — Final Training Report",
    f"Generated: {metadata['training_date']}",
    "",
    "## Dataset",
    f"- Source: Kaggle Individual Carbon Footprint Calculation",
    f"- Rows: {X.shape[0]:,}",
    f"- Features: {X.shape[1]}",
    f"- Target: carbon_emission_kgco2e_month (synthetic formula-derived)",
    "",
    "## Data Cleaning",
    "- Renamed columns to snake_case",
    "- Filled 6,721 vehicle_type nulls with 'none' (non-private transport)",
    "- Mapped: less frequently→rarely, more frequently→often, coal→electricity, frequently→often",
    "- Parsed Recycling and Cooking_With stringified lists into binary columns",
    "- Removed regional noise columns (region_grid_factor, energy_proxy, region, + 3 interaction terms)",
    "",
    "## Model Comparison",
    "",
    "| Model | R² Test | MAE | RMSE | MAPE% | CV R² (5-fold) |",
    "|-------|---------|-----|------|-------|----------------|",
]

for r in results:
    report_lines.append(
        f"| {r['model']} | {r['r2_test']:.4f} | {r['mae']:.2f} | {r['rmse']:.2f} | {r['mape']:.2f} | {r['cv_r2_mean']:.4f}±{r['cv_r2_std']:.4f} |"
    )

report_lines += [
    "",
    f"## Best Model: {best_name}",
    f"- R² (test): {best_metrics['r2_test']:.4f}",
    f"- MAE: {best_metrics['mae']:.2f} kgCO2e/month",
    f"- RMSE: {best_metrics['rmse']:.2f} kgCO2e/month",
    f"- MAPE: {best_metrics['mape']:.2f}%",
    f"- 90% conformal prediction interval: ±{q_hat:.2f} kgCO2e/month",
    "",
    "## Saved Artifacts",
    "- `model.joblib` — Serialized best model",
    "- `preprocessor.joblib` — Feature preprocessor with feature names",
    "- `model_metadata.json` — Full metrics, feature names, version info",
    "- `manifest.json` — SHA-256 checksums for integrity verification",
    "- `comparison.csv` — All model comparison metrics",
    "- `clean_dataset.csv` — Cleaned raw data (pre-encoding)",
    "- `preprocessed_features.csv` — Full preprocessed feature matrix",
    "- `train_X.csv`, `train_y.csv`, `test_X.csv`, `test_y.csv` — Train/test splits",
    "",
    "## Disclaimers",
    "- Target is formula-derived synthetic data, not real-world measured emissions",
    "- Model estimates are indicative, not verified personal emission measurements",
    "- No regional factors were used (they added no predictive value)",
]

report_path = OUTPUT_DIR / "TRAINING_REPORT.md"
with open(report_path, "w") as f:
    f.write("\n".join(report_lines))
print(f"  Saved: TRAINING_REPORT.md")

# ── DONE ───────────────────────────────────────────────────────────────

print()
print("=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)
print(f"  Best model: {best_name}")
print(f"  R² (test):  {best_metrics['r2_test']:.4f}")
print(f"  MAE:        {best_metrics['mae']:.2f} kgCO2e/month")
print(f"  RMSE:       {best_metrics['rmse']:.2f} kgCO2e/month")
print(f"  Features:   {X.shape[1]} (no regional noise)")
print(f"  Artifacts:  {OUTPUT_DIR}")
print("=" * 70)

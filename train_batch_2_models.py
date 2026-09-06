"""
CarbonSense — Batch Step 2: Train Models (one at a time)
=========================================================
Loads preprocessed data from Batch 1, trains 5 models sequentially.
Each model saves its own joblib + metrics JSON. Picks the best at the end.
"""
import sys
sys.stdout.reconfigure(line_buffering=True)

import json
import hashlib
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score, RandomizedSearchCV
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from scipy.stats import randint, uniform
import joblib

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "final_training"
SEED = 42
np.random.seed(SEED)

# ── Load data ──
print("Loading preprocessed data...")
X_train = pd.read_csv(DATA_DIR / "train_X.csv")
y_train = pd.read_csv(DATA_DIR / "train_y.csv").squeeze()
X_test = pd.read_csv(DATA_DIR / "test_X.csv")
y_test = pd.read_csv(DATA_DIR / "test_y.csv").squeeze()
with open(DATA_DIR / "feature_names.json") as f:
    feature_names = json.load(f)

print(f"Train: {X_train.shape}, Test: {X_test.shape}, Features: {len(feature_names)}")

# ── Model definitions ──
MODEL_DEFS = {
    "GradientBoosting": {
        "class": GradientBoostingRegressor,
        "default_kwargs": {"random_state": SEED},
        "param_space": {
            "n_estimators": randint(200, 600),
            "max_depth": randint(3, 8),
            "learning_rate": uniform(0.02, 0.15),
            "subsample": uniform(0.7, 0.3),
            "min_samples_split": randint(2, 15),
            "min_samples_leaf": randint(1, 8),
        },
        "n_iter": 30,
    },
    "XGBoost": {
        "class": xgb.XGBRegressor if HAS_XGB else None,
        "default_kwargs": {"random_state": SEED, "verbosity": 0, "tree_method": "hist"},
        "param_space": {
            "n_estimators": randint(200, 600),
            "max_depth": randint(3, 10),
            "learning_rate": uniform(0.02, 0.2),
            "subsample": uniform(0.6, 0.4),
            "colsample_bytree": uniform(0.5, 0.5),
            "min_child_weight": randint(1, 8),
        },
        "n_iter": 30,
    },
    "RandomForest": {
        "class": RandomForestRegressor,
        "default_kwargs": {"random_state": SEED},
        "param_space": {
            "n_estimators": randint(200, 600),
            "max_depth": randint(5, 18),
            "min_samples_split": randint(2, 15),
            "min_samples_leaf": randint(1, 8),
        },
        "n_iter": 30,
    },
    "LinearRegression": {
        "class": LinearRegression,
        "default_kwargs": {},
        "param_space": {},
        "n_iter": 0,
    },
    "SVR": {
        "class": SVR,
        "default_kwargs": {},
        "param_space": {
            "C": uniform(1, 50),
            "epsilon": uniform(0.1, 5),
        },
        "n_iter": 20,
    },
}

# ── Train each model one at a time ──
all_results = []
best_r2 = -999
best_name = None

for name, mdef in MODEL_DEFS.items():
    print()
    print("=" * 60)
    print(f"  Training: {name}")
    print("=" * 60)

    if mdef["class"] is None:
        print(f"  SKIPPED — dependency not installed")
        continue

    t0 = time.time()

    if mdef["param_space"] and mdef["n_iter"] > 0:
        print(f"  Running RandomizedSearchCV ({mdef['n_iter']} iterations, 3-fold CV)...")
        search = RandomizedSearchCV(
            mdef["class"](**mdef["default_kwargs"]),
            mdef["param_space"],
            n_iter=mdef["n_iter"],
            cv=3,
            scoring="r2",
            random_state=SEED,
            n_jobs=1,
            verbose=0,
        )
        search.fit(X_train, y_train)
        model = search.best_estimator_
        print(f"  Best params: {search.best_params_}")
    else:
        print(f"  Training with defaults...")
        model = mdef["class"](**mdef["default_kwargs"])
        model.fit(X_train, y_train)

    train_time = time.time() - t0

    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    mae = mean_absolute_error(y_test, y_pred_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mape = np.mean(np.abs((y_test - y_pred_test) / np.maximum(y_test.values, 1e-9))) * 100

    cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring="r2", n_jobs=1)
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()

    result = {
        "model": name,
        "r2_train": round(r2_train, 6),
        "r2_test": round(r2_test, 6),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 4),
        "cv_r2_mean": round(cv_mean, 6),
        "cv_r2_std": round(cv_std, 6),
        "train_time_s": round(train_time, 2),
    }
    all_results.append(result)

    print(f"  R² train: {r2_train:.4f}")
    print(f"  R² test:  {r2_test:.4f}")
    print(f"  MAE:      {mae:.2f}")
    print(f"  RMSE:     {rmse:.2f}")
    print(f"  MAPE:     {mape:.2f}%")
    print(f"  CV R²:    {cv_mean:.4f} ± {cv_std:.4f}")
    print(f"  Time:     {train_time:.1f}s")

    # Save individual model
    model_path = DATA_DIR / f"model_{name.lower()}.joblib"
    joblib.dump(model, model_path)
    print(f"  Saved: {model_path.name}")

    if r2_test > best_r2:
        best_r2 = r2_test
        best_name = name

    # Save progress so far
    with open(DATA_DIR / "results_progress.json", "w") as f:
        json.dump(all_results, f, indent=2)

print()
print("=" * 60)
print(f"  ALL MODELS TRAINED — Best: {best_name} (R² = {best_r2:.4f})")
print("=" * 60)

# ── Save best model as the final artifact ──
print()
print("Saving final artifacts...")

# Load best model
best_model = joblib.load(DATA_DIR / f"model_{best_name.lower()}.joblib")

# Conformal prediction interval (90%)
y_pred_all = best_model.predict(X_train)
residuals = y_train.values - y_pred_all
q_hat = np.quantile(np.abs(residuals), 0.90)

best_metrics = [r for r in all_results if r["model"] == best_name][0]

metadata = {
    "model_type": type(best_model).__name__,
    "model_version": f"final-{best_name.lower().replace(' ', '-')}-v1",
    "training_date": datetime.now(timezone.utc).isoformat(),
    "dataset_source": "Kaggle Individual Carbon Footprint Calculation",
    "dataset_url": "https://www.kaggle.com/datasets/dumanmesut/individual-carbon-footprint-calculation",
    "n_samples": int(X_train.shape[0] + X_test.shape[0]),
    "n_features": int(X_train.shape[1]),
    "train_test_split": "80/20",
    "random_seed": SEED,
    "metrics": best_metrics,
    "conformal_prediction": {
        "alpha": 0.10,
        "quantile_90": round(float(q_hat), 4),
        "uncertainty_range": f"+/- {round(float(q_hat), 2)} kgCO2e/month",
    },
    "feature_names": feature_names,
    "all_model_results": all_results,
    "data_cleaning": {
        "vehicle_type_nulls_filled": "6721 nulls -> 'none' (non-private transport)",
        "shower_mapping": {"less frequently": "rarely", "more frequently": "often"},
        "heating_mapping": {"coal": "electricity"},
        "air_travel_mapping": {"frequently": "often"},
        "regional_noise_removed": True,
        "columns_removed": [
            "region_grid_factor", "energy_proxy", "region",
            "transport_x_energy", "diet_x_grocery", "distance_energy_ratio",
        ],
    },
}

# Save final model + preprocessor
joblib.dump(best_model, DATA_DIR / "model.joblib")
joblib.dump(feature_names, DATA_DIR / "feature_names.joblib")

with open(DATA_DIR / "model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2, default=str)

# Save comparison CSV
pd.DataFrame(all_results).sort_values("r2_test", ascending=False).to_csv(
    DATA_DIR / "comparison.csv", index=False
)

# SHA-256 manifest
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    "model_version": metadata["model_version"],
    "generated_at": metadata["training_date"],
    "files": {
        "model.joblib": sha256_file(DATA_DIR / "model.joblib"),
        "feature_names.joblib": sha256_file(DATA_DIR / "feature_names.joblib"),
        "model_metadata.json": sha256_file(DATA_DIR / "model_metadata.json"),
    },
}
with open(DATA_DIR / "manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

# Training report
report = [
    "# CarbonSense — Final Training Report",
    f"Generated: {metadata['training_date']}",
    "",
    "## Dataset",
    f"- Source: Kaggle Individual Carbon Footprint Calculation",
    f"- Rows: {metadata['n_samples']:,} (80% train / 20% test)",
    f"- Features: {metadata['n_features']} (no regional noise)",
    "",
    "## Data Cleaning",
    "- Columns renamed to snake_case",
    "- 6,721 vehicle_type nulls filled with 'none' (non-private transport)",
    "- Mapped: less frequently -> rarely, more frequently -> often, coal -> electricity, frequently -> often",
    "- Recycling and Cooking_With parsed from stringified lists into binary columns",
    "- Regional columns REMOVED (region_grid_factor, energy_proxy, region + 3 interactions)",
    "",
    "## Model Comparison",
    "",
    "| Model | R² Test | MAE | RMSE | MAPE% | CV R² (3-fold) | Time |",
    "|-------|---------|-----|------|-------|----------------|------|",
]
for r in all_results:
    report.append(
        f"| {r['model']} | {r['r2_test']:.4f} | {r['mae']:.2f} | {r['rmse']:.2f} "
        f"| {r['mape']:.2f} | {r['cv_r2_mean']:.4f}±{r['cv_r2_std']:.4f} | {r['train_time_s']:.1f}s |"
    )
report += [
    "",
    f"## Best Model: {best_name}",
    f"- R² = {best_metrics['r2_test']:.4f}",
    f"- MAE = {best_metrics['mae']:.2f} kgCO2e/month",
    f"- RMSE = {best_metrics['rmse']:.2f} kgCO2e/month",
    f"- 90% prediction interval: ±{q_hat:.2f} kgCO2e/month",
    "",
    "## Artifacts",
    "- model.joblib — Final best model",
    "- feature_names.joblib — Ordered feature list",
    "- model_metadata.json — Full metrics + version info",
    "- manifest.json — SHA-256 checksums",
    "- comparison.csv — All model results",
    "- train_X/test_X/train_y/test_y — Splits",
    "",
    "## Disclaimer",
    "- Target is formula-derived synthetic data, not real emissions",
    "- Model estimates are indicative, not verified measurements",
]
with open(DATA_DIR / "TRAINING_REPORT.md", "w") as f:
    f.write("\n".join(report))

print()
print("=" * 70)
print("  TRAINING COMPLETE — ALL ARTIFACTS SAVED")
print(f"  Best model: {best_name}")
print(f"  R² test:    {best_metrics['r2_test']:.4f}")
print(f"  MAE:        {best_metrics['mae']:.2f} kgCO2e/month")
print(f"  RMSE:       {best_metrics['rmse']:.2f} kgCO2e/month")
print(f"  Features:   {metadata['n_features']}")
print(f"  Location:   {DATA_DIR}")
print("=" * 70)

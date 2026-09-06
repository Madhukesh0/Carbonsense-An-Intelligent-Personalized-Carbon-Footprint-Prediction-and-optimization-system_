"""
CarbonSense — Batch 2b: Train remaining 3 models
==================================================
GradientBoosting (R²=0.9629) and XGBoost (R²=0.9602) are already done.
This trains RandomForest, LinearRegression, SVR with reduced search spaces.
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

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score, RandomizedSearchCV
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from scipy.stats import randint, uniform
import joblib

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

# ── Load previous results ──
with open(DATA_DIR / "results_progress.json") as f:
    all_results = json.load(f)
print(f"Loaded {len(all_results)} previous results")

def train_and_evaluate(name, model, X_tr, y_tr, X_te, y_te):
    t0 = time.time()
    model.fit(X_tr, y_tr)
    train_time = time.time() - t0

    y_pred_train = model.predict(X_tr)
    y_pred_test = model.predict(X_te)

    r2_train = r2_score(y_tr, y_pred_train)
    r2_test = r2_score(y_te, y_pred_test)
    mae = mean_absolute_error(y_te, y_pred_test)
    rmse = np.sqrt(mean_squared_error(y_te, y_pred_test))
    mape = np.mean(np.abs((y_te - y_pred_test) / np.maximum(y_te.values, 1e-9))) * 100

    cv_scores = cross_val_score(model, X_tr, y_tr, cv=3, scoring="r2", n_jobs=1)
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

    print(f"  R² train: {r2_train:.4f}")
    print(f"  R² test:  {r2_test:.4f}")
    print(f"  MAE:      {mae:.2f}")
    print(f"  RMSE:     {rmse:.2f}")
    print(f"  MAPE:     {mape:.2f}%")
    print(f"  CV R²:    {cv_mean:.4f} ± {cv_std:.4f}")
    print(f"  Time:     {train_time:.1f}s")

    return result, model

# ── 3. RandomForest (smaller search) ──
print()
print("=" * 60)
print("  Training: RandomForest (reduced search)")
print("=" * 60)

rf_params = {
    "n_estimators": randint(200, 400),
    "max_depth": randint(8, 16),
    "min_samples_split": randint(2, 10),
    "min_samples_leaf": randint(1, 5),
}

search_rf = RandomizedSearchCV(
    RandomForestRegressor(random_state=SEED),
    rf_params,
    n_iter=15,
    cv=3,
    scoring="r2",
    random_state=SEED,
    n_jobs=1,
    verbose=0,
)
result_rf, model_rf = train_and_evaluate(
    "RandomForest", search_rf, X_train, y_train, X_test, y_test
)
print(f"  Best params: {search_rf.best_params_}")
all_results.append(result_rf)
joblib.dump(model_rf, DATA_DIR / "model_randomforest.joblib")
print(f"  Saved: model_randomforest.joblib")

# ── 4. LinearRegression ──
print()
print("=" * 60)
print("  Training: LinearRegression")
print("=" * 60)

result_lr, model_lr = train_and_evaluate(
    "LinearRegression", LinearRegression(), X_train, y_train, X_test, y_test
)
all_results.append(result_lr)
joblib.dump(model_lr, DATA_DIR / "model_linearregression.joblib")
print(f"  Saved: model_linearregression.joblib")

# ── 5. SVR ──
print()
print("=" * 60)
print("  Training: SVR")
print("=" * 60)

svr_params = {
    "C": uniform(1, 30),
    "epsilon": uniform(0.1, 3),
}

search_svr = RandomizedSearchCV(
    SVR(),
    svr_params,
    n_iter=10,
    cv=3,
    scoring="r2",
    random_state=SEED,
    n_jobs=1,
    verbose=0,
)
result_svr, model_svr = train_and_evaluate(
    "SVR", search_svr, X_train, y_train, X_test, y_test
)
print(f"  Best params: {search_svr.best_params_}")
all_results.append(result_svr)
joblib.dump(model_svr, DATA_DIR / "model_svr.joblib")
print(f"  Saved: model_svr.joblib")

# ── Save all results ──
with open(DATA_DIR / "results_progress.json", "w") as f:
    json.dump(all_results, f, indent=2)

# ── Pick best ──
best_r2 = -999
best_name = ""
best_model = None
for r in all_results:
    if r["r2_test"] > best_r2:
        best_r2 = r["r2_test"]
        best_name = r["model"]

model_map = {
    "GradientBoosting": DATA_DIR / "model_gradientboosting.joblib",
    "XGBoost": DATA_DIR / "model_xgboost.joblib",
    "RandomForest": DATA_DIR / "model_randomforest.joblib",
    "LinearRegression": DATA_DIR / "model_linearregression.joblib",
    "SVR": DATA_DIR / "model_svr.joblib",
}
best_model = joblib.load(model_map[best_name])

print()
print("=" * 70)
print("  ALL 5 MODELS TRAINED")
print("=" * 70)

# ── Save comparison CSV ──
pd.DataFrame(all_results).sort_values("r2_test", ascending=False).to_csv(
    DATA_DIR / "comparison.csv", index=False
)

for r in sorted(all_results, key=lambda x: x["r2_test"], reverse=True):
    print(f"  {r['model']:25s}  R²={r['r2_test']:.4f}  MAE={r['mae']:.1f}  RMSE={r['rmse']:.1f}")

print()
print(f"  ★ BEST: {best_name} (R² = {best_r2:.4f})")

# ── Save final artifacts ──
print()
print("Saving final artifacts...")

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
    },
}

# Copy best as final
import shutil
shutil.copy2(model_map[best_name], DATA_DIR / "model.joblib")
joblib.dump(feature_names, DATA_DIR / "feature_names.joblib")

with open(DATA_DIR / "model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2, default=str)

# Manifest
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

# ── Training Report ──
report = [
    "# CarbonSense — Final Training Report",
    f"Generated: {metadata['training_date']}",
    "",
    "## Dataset",
    "- Source: Kaggle Individual Carbon Footprint Calculation",
    f"- Rows: {metadata['n_samples']:,} (80/20 train/test split)",
    f"- Features: {metadata['n_features']} (NO regional noise)",
    "- Target: carbon_emission_kgco2e_month (formula-derived synthetic)",
    "",
    "## Data Cleaning",
    "- Columns renamed to snake_case",
    "- 6,721 vehicle_type nulls filled with 'none' (non-private transport only)",
    "- Mapped: less frequently->rarely, more frequently->often, coal->electricity, frequently->often",
    "- Recycling and Cooking_With parsed from stringified lists into binary columns",
    "- Regional columns REMOVED: region_grid_factor, energy_proxy, region (correlation ~0 with target)",
    "- Interaction terms on regional data REMOVED: transport_x_energy, diet_x_grocery, distance_energy_ratio",
    "",
    "## Model Comparison",
    "",
    "| Rank | Model | R² Test | MAE | RMSE | MAPE% | CV R² | Time |",
    "|------|-------|---------|-----|------|-------|-------|------|",
]

for i, r in enumerate(sorted(all_results, key=lambda x: x["r2_test"], reverse=True), 1):
    report.append(
        f"| {i} | {r['model']} | {r['r2_test']:.4f} | {r['mae']:.2f} | {r['rmse']:.2f} "
        f"| {r['mape']:.2f} | {r['cv_r2_mean']:.4f}±{r['cv_r2_std']:.4f} | {r['train_time_s']:.1f}s |"
    )

report += [
    "",
    f"## Winner: {best_name}",
    f"- R² = {best_metrics['r2_test']:.4f}",
    f"- MAE = {best_metrics['mae']:.2f} kgCO2e/month",
    f"- RMSE = {best_metrics['rmse']:.2f} kgCO2e/month",
    f"- MAPE = {best_metrics['mape']:.2f}%",
    f"- 90% prediction interval: ±{q_hat:.2f} kgCO2e/month",
    "",
    "## Artifacts",
    "- model.joblib — Final best model",
    "- feature_names.joblib — Ordered feature list",
    "- model_metadata.json — Full metrics, version, feature names",
    "- manifest.json — SHA-256 checksums",
    "- comparison.csv — All model results",
    "- model_gradientboosting.joblib / model_xgboost.joblib / model_randomforest.joblib / model_linearregression.joblib / model_svr.joblib",
    "- clean_dataset.csv, preprocessed_features.csv, train_X/y.csv, test_X/y.csv",
    "",
    "## Disclaimer",
    "- Target is formula-derived synthetic data, not real-world measured emissions",
    "- Model estimates are indicative, not verified personal emission measurements",
    "- No regional/location factors were used (they added no predictive value)",
]
with open(DATA_DIR / "TRAINING_REPORT.md", "w") as f:
    f.write("\n".join(report))

print()
print("=" * 70)
print("  ALL ARTIFACTS SAVED")
print(f"  Best model: {best_name} (R² = {best_r2:.4f})")
print(f"  Location:   {DATA_DIR}")
print("=" * 70)

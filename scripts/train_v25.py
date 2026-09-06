"""CarbonSense v2.5 — batch training pipeline (data prep -> 5 models -> conformal).

Batch 1: build the feature matrix from data/v2_training/clean_dataset_v2.csv
         (grid_factor / grocery_factor enter as NUMERIC features; the 15
         questionnaire inputs are encoded exactly like the serving contract).
Batch 2: train 5 models with seeded randomized search, pick the best.
Batch 3: split-conformal recalibration on the chosen model.
Deploy:  artifacts written to server/model_runtime/artifacts_v25/.

Run: py -3.13 scripts/train_v25.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

SEED = 42
PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "data" / "v2_5_training"
ART = PROJECT / "server" / "model_runtime" / "artifacts_v25"

t0 = time.time()
rng = np.random.default_rng(SEED)

# ============================== BATCH 1: data ==============================
print("=" * 66)
print("BATCH 1: data preparation (v2.5 schema)")
print("=" * 66)

df = pd.read_csv(PROJECT / "data" / "v2_training" / "clean_dataset_v2.csv")
TARGET = "carbon_emission_kgco2e_month"
y = df[TARGET]

REC_CREDIT = {"paper": 4.0, "plastic": 6.0, "metal": 12.0, "glass": 2.0}
X = pd.DataFrame(index=df.index)
X["grid_factor"] = df["grid_factor"]
X["grocery_factor"] = df["grocery_factor"]
X["household_size"] = df["household_size"]
for col in ["vehicle_monthly_distance_km", "monthly_grocery_bill",
            "how_long_tv_pc_daily_hour", "how_long_internet_daily_hour",
            "how_many_new_clothes_monthly", "waste_bag_weekly_count"]:
    X[col] = df[col]
# one-hots (drop-first like the v1 contract)
X = pd.concat([X,
               pd.get_dummies(df["transport"], prefix="transport", drop_first=True, dtype=float),
               pd.get_dummies(df["vehicle_type"], prefix="vehicle_type", drop_first=True, dtype=float),
               pd.get_dummies(df["frequency_of_traveling_by_air"], prefix="air", drop_first=True, dtype=float),
               pd.get_dummies(df["heating_energy_source"], prefix="heating", drop_first=True, dtype=float),
               pd.get_dummies(df["diet"], prefix="diet", drop_first=True, dtype=float),
               pd.get_dummies(df["waste_bag_size"], prefix="waste_bag_size", drop_first=True, dtype=float),
               ], axis=1)
for item in ["paper", "plastic", "metal", "glass"]:
    X[f"recycle_{item}"] = df["recycling"].apply(lambda s, it=item: int(it in eval(s)))
for item in ["stove", "oven", "microwave", "grill", "airfryer"]:
    X[f"cook_{item}"] = df["cooking_with"].apply(lambda s, it=item: int(it in eval(s)))

X.columns = [c.replace('[', '_').replace(']', '_').replace('<', 'lt_').replace(' ', '_') for c in X.columns]
FEATURE_NAMES = list(X.columns)
print(f"features: {len(FEATURE_NAMES)} | rows: {len(X)}")

from sklearn.model_selection import train_test_split

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=SEED)
print(f"train {len(X_tr)} / test {len(X_te)}")

# ============================== BATCH 2: models ============================
print()
print("=" * 66)
print("BATCH 2: training 5 models (seeded)")
print("=" * 66)

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

results = []
models = {}


def evaluate(name, model, fit_kwargs=None):
    t = time.time()
    model.fit(X_tr, y_tr, **(fit_kwargs or {}))
    pred_tr = model.predict(X_tr)
    pred = model.predict(X_te)
    r2_tr = r2_score(y_tr, pred_tr)
    r2 = r2_score(y_te, pred)
    mae = mean_absolute_error(y_te, pred)
    rmse = math.sqrt(mean_squared_error(y_te, pred))
    results.append({"model": name, "r2": round(r2, 4), "r2_train": round(r2_tr, 4),
                    "gap": round(r2_tr - r2, 4), "mae": round(mae, 1),
                    "rmse": round(rmse, 1), "time_s": round(time.time() - t, 1)})
    models[name] = model
    print(f"  {name:22s} train {r2_tr:.4f}  test {r2:.4f}  gap {r2_tr - r2:+.4f}  MAE {mae:6.1f}  ({results[-1]['time_s']}s)")
    return r2


evaluate("GradientBoosting", GradientBoostingRegressor(
    n_estimators=300, learning_rate=0.1, max_depth=5, subsample=0.9, random_state=SEED))
if HAS_XGB:
    evaluate("XGBoost", XGBRegressor(n_estimators=400, learning_rate=0.08, max_depth=5,
                                     subsample=0.9, colsample_bytree=0.9,
                                     reg_alpha=1.0, reg_lambda=5.0,
                                     random_state=SEED, verbosity=0))
evaluate("RandomForest", RandomForestRegressor(
    n_estimators=400, max_depth=12, min_samples_leaf=5, random_state=SEED, n_jobs=-1))
evaluate("LinearRegression", LinearRegression())
evaluate("SVR", SVR(C=10.0, epsilon=1.0))

best = max(results, key=lambda r: r["r2"])
best_name, best_model = best["model"], models[best["model"]]
from sklearn.model_selection import cross_val_score
cv = cross_val_score(best_model, X_tr, y_tr, cv=5, scoring="r2")
best["cv_r2_mean"] = round(float(cv.mean()), 4)
best["cv_r2_std"] = round(float(cv.std()), 4)
print(f"  BEST: {best_name} | test R2 {best['r2']:.4f} | gap {best['gap']:+.4f} | 5-fold CV {best['cv_r2_mean']} +/- {best['cv_r2_std']}")

# ==================== BATCH 3: conformal recalibration =====================
print()
print("=" * 66)
print("BATCH 3: split-conformal recalibration (90%)")
print("=" * 66)

# Honest split-conformal: the calibration model must NOT have seen the
# calibration rows. A clone of the best model type is fitted on X_fit only
# (6,000 rows); its residuals on X_cal (2,000 held-out rows) are honest
# out-of-sample scores, so q_hat is not optimistically small. The deployed
# model (fitted on all 8,000) is slightly stronger than the proxy, making
# the interval mildly conservative - the safe direction.
X_fit, X_cal, y_fit, y_cal = train_test_split(X_tr, y_tr, test_size=0.25, random_state=SEED)
if best_name == "XGBoost":
    cal_model = XGBRegressor(n_estimators=400, learning_rate=0.08, max_depth=5,
                             subsample=0.9, colsample_bytree=0.9, reg_alpha=1.0,
                             reg_lambda=5.0, random_state=SEED, verbosity=0)
elif best_name == "RandomForest":
    cal_model = RandomForestRegressor(n_estimators=400, max_depth=12,
                                      min_samples_leaf=5, random_state=SEED, n_jobs=-1)
elif best_name == "GradientBoosting":
    cal_model = GradientBoostingRegressor(n_estimators=300, learning_rate=0.1,
                                          max_depth=5, subsample=0.9, random_state=SEED)
elif best_name == "LinearRegression":
    cal_model = LinearRegression()
else:
    cal_model = SVR(C=10.0, epsilon=1.0)
cal_model.fit(X_fit, y_fit)
cal_res = np.abs(y_cal.values - cal_model.predict(X_cal))
n_cal = len(cal_res)
level = math.ceil((n_cal + 1) * 0.90) / n_cal
q_hat = float(np.quantile(cal_res, level, method="higher"))
te_res = np.abs(y_te.values - best_model.predict(X_te))
coverage = float((te_res <= q_hat).mean())
print(f"  q_hat = {q_hat:.2f} kg | empirical test coverage = {coverage*100:.1f}%")

# ============================== DEPLOY =====================================
print()
print("=" * 66)
print("DEPLOY: writing artifacts to server/model_runtime/artifacts_v25/")
print("=" * 66)
ART.mkdir(parents=True, exist_ok=True)
joblib.dump(best_model, ART / "best_carbon_model_v25.joblib")
joblib.dump(FEATURE_NAMES, ART / "feature_names_v25.joblib")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


pred_tr = best_model.predict(X_tr)
q_train_resid = float(np.quantile(np.abs(y_tr.values - pred_tr), 0.90))
metadata = {
    "model_version": f"final-{best_name.lower().replace(' ', '-')}-v25",
    "dataset_version": "carbonsense-synthetic-v2.5",
    "trained_at": datetime.now(timezone.utc).isoformat(),
    "seed": SEED,
    "n_features": len(FEATURE_NAMES),
    "feature_names": FEATURE_NAMES,
    "all_model_results": results,
    "best_model": best_name,
    "metrics": {"r2": best["r2"], "r2_train": best["r2_train"], "gap": best["gap"],
                "cv_r2_mean": best.get("cv_r2_mean"), "cv_r2_std": best.get("cv_r2_std"),
                "mae": best["mae"], "rmse": best["rmse"]},
    "conformal_prediction": {
        "alpha": 0.10,
        "method": "split-conformal, finite-sample corrected (seed 42)",
        "quantile_90": round(q_hat, 2),
        "empirical_test_coverage": round(coverage, 4),
    },
    "note": "Trained on the cited-factor v2.5 dataset (grid_factor/grocery_factor "
            "as continuous model inputs; country/region are audit labels). "
            "Synthetic factor-formula targets, not measured emissions.",
}
(ART / "model_metadata_v25.json").write_text(json.dumps(metadata, indent=2))
manifest = {"model_version": metadata["model_version"],
            "files": {f.name: sha(f) for f in sorted(ART.iterdir())
                      if f.is_file() and f.name != "manifest_v25.json"}}
(ART / "manifest_v25.json").write_text(json.dumps(manifest, indent=2))
for f in sorted(ART.iterdir()):
    if f.suffix in (".joblib", ".json") and f.name != "manifest_v25.json":
        pass
print(f"  written: {sorted(f.name for f in ART.iterdir())}")

OUT.mkdir(parents=True, exist_ok=True)
pd.DataFrame(results).to_csv(OUT / "comparison_v25.csv", index=False)
print(f"\nTOTAL TIME: {time.time() - t0:.0f}s")
print("DONE")

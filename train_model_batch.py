"""Train a single model as a batch step. Run: python train_model_batch.py <model_name>"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import SVR
from xgboost import XGBRegressor

PROJECT_ROOT = Path(__file__).resolve().parent
EXPERIMENT_DIR = PROJECT_ROOT / "models" / "trained" / "experiments" / datetime.now().strftime("%Y-%m-%d")

MODELS = {
    "gradient_boosting": {
        "model": GradientBoostingRegressor(random_state=42),
        "params": {
            "n_estimators": [100, 200, 300],
            "learning_rate": [0.01, 0.05, 0.1],
            "max_depth": [3, 5, 7],
            "subsample": [0.8, 0.9, 1.0],
        },
    },
    "xgboost": {
        "model": XGBRegressor(random_state=42, enable_categorical=True),
        "params": {
            "n_estimators": [100, 200, 300],
            "learning_rate": [0.01, 0.05, 0.1],
            "max_depth": [3, 5, 7],
            "subsample": [0.8, 0.9],
            "colsample_bytree": [0.8, 0.9],
        },
    },
    "random_forest": {
        "model": RandomForestRegressor(random_state=42, n_jobs=1),
        "params": {
            "n_estimators": [100, 200, 300],
            "max_depth": [10, 20, 30, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
        },
    },
    "linear_regression": {
        "model": LinearRegression(),
        "params": {},
    },
    "svr": {
        "model": SVR(),
        "params": {
            "C": [0.1, 1, 10, 100],
            "epsilon": [0.01, 0.1, 0.2],
            "kernel": ["rbf"],
        },
    },
}


def train(model_name: str):
    if model_name not in MODELS:
        print(f"Unknown model: {model_name}. Available: {list(MODELS.keys())}")
        sys.exit(1)

    config = MODELS[model_name]
    X_train = np.load(EXPERIMENT_DIR / "X_train.npy")
    X_test = np.load(EXPERIMENT_DIR / "X_test.npy")
    y_train = np.load(EXPERIMENT_DIR / "y_train.npy")
    y_test = np.load(EXPERIMENT_DIR / "y_test.npy")

    print(f"Training {model_name}...")
    print(f"  X_train: {X_train.shape}, X_test: {X_test.shape}")

    model = config["model"]

    if config["params"]:
        print(f"  RandomizedSearchCV ({len(config['params'])} param groups, n_iter=20, cv=5)...")
        search = RandomizedSearchCV(
            model,
            config["params"],
            n_iter=20,
            cv=5,
            scoring="r2",
            random_state=42,
            n_jobs=1,
            verbose=1,
        )
        search.fit(X_train, y_train)
        best = search.best_estimator_
        print(f"  Best params: {search.best_params_}")
    else:
        print("  Baseline (no tuning)...")
        model.fit(X_train, y_train)
        best = model

    y_pred = best.predict(X_test)
    r2 = float(r2_score(y_test, y_pred))
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    print(f"\n  {model_name}:")
    print(f"    R²:  {r2:.4f}")
    print(f"    MAE: {mae:.2f} kg CO2e/month")
    print(f"    RMSE: {rmse:.2f} kg CO2e/month")

    # Save model
    model_path = EXPERIMENT_DIR / f"{model_name}.joblib"
    joblib.dump(best, model_path)
    print(f"  Saved: {model_path}")

    # Append to results
    results_file = EXPERIMENT_DIR / "results.json"
    results = json.loads(results_file.read_text()) if results_file.exists() else []
    results.append({
        "model_name": model_name,
        "model_type": type(best).__name__,
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "params": config["params"],
    })
    results_file.write_text(json.dumps(results, indent=2))
    print(f"  Results appended to: {results_file}")
    print(f"\nDone. {len(results)}/5 models trained.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_model_batch.py <model_name>")
        print(f"  Available: {list(MODELS.keys())}")
        sys.exit(1)
    train(sys.argv[1])

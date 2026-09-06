"""Finalize candidate: pick best model, verify contract, test SHAP, save artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = PROJECT_ROOT / "server" / "model_runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from app.core.final_contract import (  # noqa: E402
    FEATURE_NAMES,
    FinalPreprocessor,
)

EXPERIMENT_DIR = PROJECT_ROOT / "models" / "trained" / "experiments" / datetime.now().strftime("%Y-%m-%d")


def main():
    results_file = EXPERIMENT_DIR / "results.json"
    if not results_file.exists():
        print("No results.json found. Run train_model_batch.py for each model first.")
        sys.exit(1)

    results = json.loads(results_file.read_text())
    if len(results) == 0:
        print("results.json is empty. Run train_model_batch.py first.")
        sys.exit(1)

    # Sort by RMSE → MAE → R²
    results_sorted = sorted(results, key=lambda r: (r["rmse"], -r["mae"], -r["r2"]))
    best = results_sorted[0]

    print("=" * 60)
    print("CANDIDATE EXPERIMENT RESULTS")
    print("=" * 60)
    print(f"\n--- ALL MODELS (sorted by RMSE → MAE → R²) ---")
    for i, r in enumerate(results_sorted):
        marker = " <-- BEST" if r["model_name"] == best["model_name"] else ""
        print(f"  {i+1}. {r['model_name']:25s}  RMSE={r['rmse']:8.2f}  MAE={r['mae']:8.2f}  R²={r['r2']:.4f}{marker}")

    print(f"\n--- BEST: {best['model_name']} ---")
    print(f"  Model type: {best['model_type']}")
    print(f"  RMSE: {best['rmse']:.2f}")
    print(f"  MAE:  {best['mae']:.2f}")
    print(f"  R²:   {best['r2']:.4f}")

    # --- Verify 55-feature contract ---
    preprocessor = FinalPreprocessor(feature_names=list(FEATURE_NAMES))
    feature_names = list(preprocessor.get_feature_names_out())

    print(f"\n--- CONTRACT VERIFICATION ---")
    if len(feature_names) != 55:
        print(f"  FAIL: feature count is {len(feature_names)}, expected 55")
        sys.exit(1)
    if feature_names != FEATURE_NAMES:
        print(f"  FAIL: feature names do not match FEATURE_NAMES")
        sys.exit(1)
    print(f"  Feature count: 55 — PASS")
    print(f"  Feature names match contract: PASS")

    # --- SHAP smoke test ---
    print(f"\n--- SHAP SMOKE TEST ---")
    model_path = EXPERIMENT_DIR / f"{best['model_name']}.joblib"
    model = joblib.load(model_path)

    try:
        import shap
        X_test = np.load(EXPERIMENT_DIR / "X_test.npy")
        sample = X_test[:1]
        print(f"  Sample shape: {sample.shape}")

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(sample)
        shap_arr = np.asarray(shap_values)
        if shap_arr.ndim == 3:
            shap_arr = shap_arr[0]

        if shap_arr.shape != (1, 55):
            print(f"  FAIL: SHAP output shape {shap_arr.shape}, expected (1, 55)")
            sys.exit(1)
        if not np.isfinite(shap_arr).all():
            print(f"  FAIL: SHAP values contain non-finite entries")
            sys.exit(1)
        print(f"  SHAP shape: {shap_arr.shape} — PASS")
        print(f"  SHAP all finite: PASS")
    except Exception as exc:
        print(f"  FAIL: {exc}")
        print(f"  Aborting. Investigate SHAP compatibility.")
        sys.exit(1)

    # --- Conformal prediction interval ---
    y_train = np.load(EXPERIMENT_DIR / "y_train.npy")
    residuals = y_train - model.predict(X_train := np.load(EXPERIMENT_DIR / "X_train.npy"))
    conformal_quantile = float(np.percentile(np.abs(residuals), 90))

    # --- Save final candidate artifacts ---
    preprocessor_path = EXPERIMENT_DIR / "preprocessor.joblib"
    joblib.dump(preprocessor, preprocessor_path)

    metadata = {
        "best_model": best["model_name"],
        "dataset_version": "individual-10k-regional-v1",
        "target_definition": "formula-derived synthetic monthly kgCO2e estimate",
        "raw_feature_count": 34,
        "transformed_feature_count": 55,
        "model_type": best["model_type"],
        "metrics": {"r2": best["r2"], "mae": best["mae"], "rmse": best["rmse"]},
        "conformal_quantile_90": conformal_quantile,
        "training_date": datetime.now().strftime("%Y-%m-%d"),
        "feature_contract": "55-feature frozen contract (final_contract.py)",
        "preprocessing": "FinalPreprocessor from server/model_runtime/app/core/final_contract.py",
        "data_limitations": "The target is synthetic and formula-derived; metrics measure agreement with generated targets, not verified personal emissions.",
        "is_candidate": True,
    }
    metadata_path = EXPERIMENT_DIR / "model_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    def sha256(path):
        digest = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    manifest = {
        "source": "candidate-experiment",
        "dataset_version": "individual-10k-regional-v1",
        "model_version": f"{best['model_name']}-candidate-v1",
        "feature_contract": "55-feature frozen contract",
        "feature_count": 55,
        "artifacts": {
            f"{best['model_name']}.joblib": sha256(model_path),
            "preprocessor.joblib": sha256(preprocessor_path),
            "model_metadata.json": sha256(metadata_path),
        },
    }
    (EXPERIMENT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))

    comparison_df = pd.DataFrame(results_sorted)
    comparison_df.to_csv(EXPERIMENT_DIR / "model_comparison_results.csv", index=False)

    np.save(EXPERIMENT_DIR / "conformal_quantile.npy", conformal_quantile)

    print(f"\n--- CANDIDATE SAVED ---")
    print(f"  Directory: {EXPERIMENT_DIR}")
    print(f"  Best model: {best['model_name']}.joblib")
    print(f"  Preprocessor: preprocessor.joblib")
    print(f"  Metadata: model_metadata.json")
    print(f"  Manifest: manifest.json")
    print(f"  Conformal quantile (90%): ±{conformal_quantile:.2f} kg CO2e")
    print(f"\n--- PRODUCTION FILES NOT MODIFIED ---")
    print(f"  server/model_runtime/artifacts/ — untouched")
    print(f"  backend/app/services/prediction.py — untouched")
    print(f"  server/model_runtime/infer.py — untouched")
    print(f"\nThis is a CANDIDATE. Promote only after explicit approval.")


if __name__ == "__main__":
    main()

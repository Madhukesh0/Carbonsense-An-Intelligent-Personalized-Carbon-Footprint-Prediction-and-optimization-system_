# Final dataset and training-artifact audit

**Audit date:** 20 August 2026  
**Deployed artifact:** `xgb-final-54f-v2`  
**Result:** **Model artifact execution is internally consistent, but a material dataset-provenance mismatch was found in the previous freeze documentation.**

## What was verified successfully

| Verification | Result |
|---|---|
| Artifact SHA-256 manifest | All deployed model, preprocessor, and metadata hashes matched. |
| Runtime contract | Persisted preprocessor exposes the exact 54 expected feature names in the frozen order. |
| Deployed model shape | Persisted artifact is an `XGBRegressor` with 54 input features. |
| User input route | Submitted answers transform into a finite `1 × 54` vector and produce finite non-negative predictions. |
| Original generated training package | 10,000 rows replayed through the deployed preprocessor to a `10,000 × 54` matrix. |
| Recorded held-out metrics | Replayed **exactly**: R² = 0.9912465992, MAE = 19.60003595, RMSE = 25.62709881. |

The exact replay used the retained generated training source `carbon_training_dataset_package/individual_10k_regional_augmented_engineered.csv`, an 80/20 split with random seed 42, and the deployed persisted model. This confirms that the saved artifact and its metadata are consistent with that generated training population.

## Material provenance issue found

The prior dataset-freeze record named:

1. `individual_10k_regional_engineered.csv`; and
2. `preprocessed_full_10k.csv`

as the current model’s source/preprocessed pair. Those retained copies are structurally clean—10,000 rows each, no missing values, no duplicates, exact 34/54 schema alignment, and matching target rows with a mean target of **2269.1473**. However, when the deployed XGBoost artifact was replayed on that preprocessed CSV using the documented 80/20 split, it produced:

| Metric | Recorded metadata | Replay against `preprocessed_full_10k.csv` |
|---|---:|---:|
| R² | 0.9912 | −3.1159 |
| MAE | 19.6000 | 1834.6997 |
| RMSE | 25.6271 | 2068.6572 |

This is not a small numerical variation. It proves that the retained `preprocessed_full_10k.csv` is **not the exact training matrix for the deployed artifact**.

In contrast, the retained generated training package has a target mean of **943.7136**, and replaying it through the persisted preprocessor reproduced every recorded held-out metric exactly. The deployed model’s usual output range is also consistent with this latter training package, not the 2269-mean preprocessed CSV.

## Correct interpretation

> The live prediction system is **working correctly for the persisted XGBoost artifact and its matching generated training population**. The error is a **dataset lineage/documentation mismatch**, not a failure in the live inference code.

The model should therefore not be described as trained directly on the retained `preprocessed_full_10k.csv` until a model is retrained on that file and independently validated. Similarly, the previously named `individual_10k_regional_engineered.csv` / `preprocessed_full_10k.csv` pair remains useful for data governance and reference analysis, but it cannot currently be claimed as the exact artifact-training pair.

## What can and cannot be claimed

| Claim | Status |
|---|---|
| The live app executes a real persisted 54-feature XGBoost artifact | Verified |
| The preprocessor/model contract is internally consistent | Verified |
| Metadata metrics reproduce on the retained generated training package | Verified |
| The artifact was trained on the retained `preprocessed_full_10k.csv` | **Not supported; disproved by replay** |
| The model measures real personal emissions | Not supported; target is formula-derived synthetic data |
| The original model’s generated-target held-out score is high | Verified, with the synthetic-target limitation |

## Safe next step

No silent retraining or artifact replacement was performed. To fully correct provenance, the project owner should choose one controlled path:

1. **Preserve the deployed artifact:** treat the retained generated training package as the artifact’s authoritative provenance and export/version its matching 54-feature matrix; or
2. **Adopt the documented `preprocessed_full_10k.csv` pair:** retrain a new model on that exact file, compare it against the current artifact, version it separately, and only then deploy it.

Until that decision, CarbonSense can safely continue using the live artifact for demonstration, provided its documentation states that it is a **frozen XGBoost model trained on a formula-derived generated dataset** and does not name the mismatched preprocessed CSV as its exact training matrix.

## Owner decision — 20 August 2026

The project owner explicitly chose to **preserve the current deployed 34-input / 54-feature XGBoost artifact**. No retraining, feature reduction, dataset merge, preprocessing change, artifact replacement, or questionnaire reduction is authorized by this decision.

CarbonSense will therefore continue to use the working `xgb-final-54f-v2` runtime unchanged. The required correction is limited to provenance language: the project must refer to the retained generated training package as the artifact-matching training population and must not claim that the separate `preprocessed_full_10k.csv` trained this artifact.

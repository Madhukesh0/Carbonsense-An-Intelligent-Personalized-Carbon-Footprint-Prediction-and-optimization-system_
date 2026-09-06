# CarbonSense Prediction Runtime Audit

**Audit updated:** 31 August 2026  
**Runtime status:** GradientBoostingRegressor artifact deployed for authenticated inference.

## Direct answer

The live CarbonSense application now executes a **GradientBoostingRegressor** model and its persisted `preprocessor_10k_final.joblib` for every submitted prediction. The application transforms the submitted 26-input profile into the exact frozen 44-feature vector, then returns the model prediction, 90% conformal prediction interval, and model-native SHAP contribution values in real time.

| Question | Verified answer |
|---|---|
| Are submitted survey values used? | Yes. The submitted profile is transformed through the exact persisted preprocessor for that request. The model does not substitute default values. |
| Do defaults apply? | Only as editable starting values in the survey. The server predicts from the values submitted by the user. |
| Is the live result a genuine ML prediction? | Yes. The active response identifies `final-gradientboosting-v1`, checks the artifact manifest, and runs the persisted GradientBoostingRegressor artifact. |
| What is the training dataset? | The frozen training contract: 10,000 formula-derived synthetic rows from the Kaggle dataset, 8,000 used to train and 2,000 used to evaluate the model. |
| Why is there a range? | The response applies the 90% conformal prediction interval of ±255.58 kgCO₂e/month around the current prediction as an indicative comparison range. |
| Are contribution bars real time? | Yes. They come from the model's SHAP TreeExplainer output and are regrouped into 14 understandable input drivers. They describe model behavior, not causal environmental impact. |

## Artifact integrity and contract

The deployed runtime bundles and hashes `best_carbon_model.joblib`, `preprocessor_10k_final.joblib`, and `model_metadata.json`. Before the first prediction, it validates all SHA-256 values and confirms that the preprocessor emits the documented 44 feature names in the frozen order. A submitted profile that cannot produce a finite 1×44 vector fails instead of silently falling back to another formula.

## Model scope

The model target remains formula-derived and synthetic. The GradientBoostingRegressor runtime is real model inference, but it does not turn the output into a direct personal-emission measurement, nor does it retrain on sign-ups, activity entries, or new survey submissions. Dataset and model changes remain frozen through May 2027 unless approved under the documented change-control process.

## Interface verification

The linked in-app `/about` methodology page was rechecked after model deployment. It visibly states the live artifact, exact 26-input / 44-feature preprocessing contract, artifact-hash check, model-native contribution interpretation, and prediction interval boundary without exposing the model artifacts to the browser.

## Key metrics

| Metric | Value |
|---|---|
| Model type | GradientBoostingRegressor (sklearn) |
| Feature count | 44 (6 numeric + 38 one-hot) |
| R² | 0.9629 |
| RMSE | 196.38 kgCO₂e/month |
| MAE | 156.96 kgCO₂e/month |
| 90% prediction interval | ±255.58 kgCO₂e/month |

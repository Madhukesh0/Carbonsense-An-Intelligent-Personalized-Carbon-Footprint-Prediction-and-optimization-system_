# CarbonSense model runtime notes

CarbonSense now executes a **GradientBoostingRegressor** model for every authenticated prediction, baseline comparison, what-if scenario, and per-prediction contribution request. It uses the persisted `preprocessor_10k_final.joblib` and verifies that its output has the frozen 44-feature order before inference.

The server runtime holds a single serialized Python worker for the Node process. The worker integrity-checks the bundled model, preprocessor, and metadata SHA-256 values before first use, loads the artifacts once, and transforms only the submitted survey profile. It does not use another user's profile as model input and does not retrain the model at request time.

The runtime returns gradient boosting tree contribution values using SHAP `TreeExplainer`. CarbonSense groups related transformed features, such as the one-hot air-travel or recycling terms, into 14 understandable profile drivers before displaying the ranked breakdown. Contributions explain how the trained model reached this particular prediction relative to its base value; they do not establish causal environmental impact.

The model was trained on the frozen 26-input / 44-feature contract. Regional noise columns (`region_grid_factor`, `energy_proxy`, `region`, and three interaction terms) were removed after correlation and cross-validation analysis showed no predictive value (~0.0004 correlation with target). Its target is formula-derived synthetic monthly kgCO₂e, so the held-out R², MAE, and RMSE describe agreement with that generated target rather than verified personal-emission measurement accuracy. The live range is prediction ± 90% conformal interval (±255.58 kgCO₂e/month).

The production image adds Python, NumPy, joblib, and scikit-learn through the root `Dockerfile`. The model artifacts reside in the server runtime directory and are never sent to the browser.

## Key metrics

| Metric | Value |
|---|---|
| Model | GradientBoostingRegressor (sklearn) |
| Version | final-gradientboosting-v1 |
| Training set | 8,000 rows (80/20 split of Kaggle synthetic dataset) |
| Features | 44 (6 numeric + 38 one-hot encoded) |
| R² | 0.9629 |
| RMSE | 196.38 kgCO₂e/month |
| MAE | 156.96 kgCO₂e/month |

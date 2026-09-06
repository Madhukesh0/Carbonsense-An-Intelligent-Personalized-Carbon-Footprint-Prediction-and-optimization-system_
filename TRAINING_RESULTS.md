# CarbonSense Training Results

## Training Date
**2026-08-31** (final retrain)

## Dataset
- **Source:** Kaggle Individual Carbon Footprint Calculation dataset
- **Total Samples:** 10,000
- **Train/Test Split:** 8,000 / 2,000 (80/20)
- **Target Range:** 306 - 8,377 kg CO₂e/month
- **Features:** 26 raw inputs → 44 engineered features after preprocessing

## Model Comparison Results

All 5 models were trained with hyperparameter tuning (except Linear Regression baseline):

| Rank | Model | R² Score | MAE (kg CO₂e/month) | RMSE (kg CO₂e/month) |
|------|-------|----------|---------------------|----------------------|
| 🏆 1 | **Gradient Boosting** | **0.9629** | **156.96** | **196.38** |
| 2 | XGBoost | 0.9602 | 163.53 | 203.36 |
| 3 | Linear Regression | 0.9141 | 220.12 | 298.82 |
| 4 | Random Forest | 0.9068 | 243.51 | 311.32 |
| 5 | SVR (RBF) | 0.3656 | 630.03 | 812.16 |

## Winner: Gradient Boosting 🏆

### Performance Metrics
- **R² Score:** 0.9629 (explains 96.29% of variance)
- **Mean Absolute Error:** 156.96 kg CO₂e/month
- **Root Mean Squared Error:** 196.38 kg CO₂e/month
- **90% Prediction Interval:** ±330.96 kg CO₂e (split-conformal, recalibrated 2026-09-03)

### Prediction Interval Method (updated 2026-09-03)

The interval was originally calibrated from training residuals (±255.58), which under-estimates
error because the model fit those points; measured test coverage was 80.5%. It was recalibrated
with split-conformal prediction: the 8,000 training rows were split 6,000 fit / 2,000 calibration
(random_state=42), a GradientBoosting proxy fit with the production hyperparameters was fitted on
the 6,000, and the 90% residual quantile was taken on the 2,000 calibration rows with the
finite-sample correction ceil((n+1)(1-α))/n, giving **q̂ = 330.96 kg**. On the untouched 2,000-row
test set the frozen production model's interval covers **91.7%** of outcomes (nominal 90%). The
served `uncertaintyRange` is now prediction ± q̂ (see `scripts/recalibrate_conformal.py`).

### Best Hyperparameters
```python
{
  'n_estimators': 300,
  'learning_rate': 0.1,
  'max_depth': 5,
  'subsample': 0.9
}
```

### Why Gradient Boosting Won
1. **Highest R² score** - Best overall fit to the data
2. **Lowest MAE** - Most accurate predictions on average
3. **Lowest RMSE** - Best handling of prediction errors
4. **Better than XGBoost** - Slightly outperformed XGBoost despite similar architecture
5. **Robust to overfitting** - Subsample parameter prevents overfitting

## Deployment Status

✅ **Production artifacts deployed to:**
- `server/model_runtime/artifacts/best_carbon_model.joblib`
- `server/model_runtime/artifacts/preprocessor_10k_final.joblib`
- `server/model_runtime/artifacts/model_metadata.json`
- `server/model_runtime/artifacts/manifest.json` (with SHA256 checksums)

✅ **Research artifacts saved to:**
- `data/final_training/` (complete training package with all model variants, splits, and reports)

## Feature Engineering

The preprocessing pipeline transforms 26 raw survey fields into 44 features:

### Numerical Features (6)
- monthly_grocery_bill
- vehicle_monthly_distance_km
- waste_bag_weekly_count
- how_long_tv_pc_daily_hour
- how_many_new_clothes_monthly
- how_long_internet_daily_hour

### Categorical Features (11) → One-Hot Encoded
- body_type → 3 features (reference: normal)
- sex → 1 feature (reference: female)
- diet → 3 features (reference: omnivore)
- how_often_shower → 3 features (reference: daily)
- heating_energy_source → 2 features (reference: electricity)
- transport → 2 features (reference: private)
- vehicle_type → 5 features (reference: diesel)
- social_activity → 2 features (reference: never)
- frequency_of_traveling_by_air → 3 features (reference: never)
- waste_bag_size → 3 features (reference: extra large)
- energy_efficiency → 2 features (reference: No)

### Binary Flags (9)
- recycling: recycle_glass, recycle_metal, recycle_paper, recycle_plastic (4)
- cooking: cook_airfryer, cook_grill, cook_microwave, cook_oven, cook_stove (5)

### Total: 44 Transformed Features

## Data Limitations

⚠️ **Important:** The training target is **formula-derived and synthetic**, not measured emissions. The model learns to predict this synthetic target with high accuracy, but metrics measure agreement with the formula, not real-world emissions validation.

Regional noise columns (`region_grid_factor`, `energy_proxy`, `region`, and three interaction terms) were removed after analysis showed ~0.0004 correlation with the target and cross-validation R² of 0.0033.

## Next Steps

1. ✅ Model trained and deployed
2. ✅ Production artifacts verified with SHA256 checksums
3. ✅ Conformal prediction intervals calibrated
4. ✅ Server loads the Gradient Boosting model
5. 📋 **Future:** Consider collecting real user feedback to validate predictions

## Training Environment

- **Python:** 3.13
- **scikit-learn:** GradientBoostingRegressor
- **pandas/numpy:** Latest
- **joblib:** Latest

---

**Training completed successfully! The Gradient Boosting model is now in production.** 🎉

# CarbonSense Forecasting Method Audit

**Status:** Implemented on 21 August 2026  
**Scope:** Personal, account-scoped activity-ledger forecasting only

## Finding from the uploaded paper draft

The uploaded draft states that CarbonSense uses “Prophet/ETS models” for monthly forecasting and refers to a dedicated `/forecast` model path. Before this implementation, the application did **not** contain Prophet, the legacy package name `fbprophet`, ETS, or another fitted time-series model. Its live forecast was a fixed **1.8% month-over-month directional planning trajectory** based on activity entries from the latest 42 days, with an illustrative widening range.

Therefore, the old paper claim was not supported by the deployed code. The deployed XGBoost predictor remains a separate, static lifestyle-survey predictor and must not be described as the time-series forecast engine.

## Implemented method

CarbonSense now includes a **conditionally enabled Prophet 1.4.0** path for an authenticated user’s own activity ledger. The server groups recorded transport, electricity, diet, and fuel entry emissions into UTC monthly totals, excludes the unfinished current month, and fits a non-seasonal linear Prophet model for a six-month horizon. Prophet’s Python API takes a data frame with a timestamp column named `ds` and a numeric measurement column named `y`; it returns `yhat`, `yhat_lower`, and `yhat_upper` forecast fields.[1]

| Control | Implemented CarbonSense policy | Why it matters |
|---|---|---|
| Scope | One authenticated user’s activity ledger only | Prevents organization data or other users’ records from entering a personal forecast. |
| Training observations | At least **12 completed consecutive calendar months** | Avoids fitting the model to a few scattered entries. |
| Recording density | At least **90 distinct recorded activity days** | Prevents a month total from being treated as representative when it comes from only a few entries. |
| Current month | Excluded from fitting | Prevents a partial month from being used as a full monthly observation. |
| Seasonality | Disabled | The minimum history is only one year; this conservative setting avoids claiming stable personal seasonality from a limited series. Prophet’s guidance notes that yearly seasonal components need at least a year of history.[2] |
| Horizon | Six future months | Keeps the personal planning horizon short and visible. |
| Interval | Prophet’s 80% predictive interval | This is model uncertainty, not a guarantee or a verified emissions range.[1] |
| Fallback | Existing directional activity-ledger view | Used when the evidence threshold is not met or the Prophet worker is unavailable; it is labelled as a planning fallback, not a fitted model. |

## Honest interpretation boundary

The Prophet result forecasts **recorded ledger totals**, not actual verified household or personal emissions. It does not prove that a recommendation caused a future decrease, does not predict emissions not entered into the ledger, and should not be used to make a verified-reduction claim. The predictor uses user-entered activity records; it is independent of the frozen `individual_10k_regional_augmented_engineered.csv` XGBoost training dataset.

Prophet provides built-in historical cross-validation and error metrics such as RMSE, MAE, MAPE, and interval coverage.[2] CarbonSense does **not** show a performance number for an individual until sufficient real historical data exists to run a meaningful back-test. No accuracy percentage has been fabricated for the new forecast path.

## Required correction to the paper

Replace generic references to “Prophet/ETS models” with the following accurate wording:

> **CarbonSense conditionally fits a Prophet-based, non-seasonal monthly activity-ledger forecast when an authenticated user has at least 12 consecutive completed months and 90 distinct days of recorded activity. Before that evidence threshold is met, the interface presents a clearly labelled directional planning fallback. ETS is not deployed in the current implementation.**

The paper should also update the system-architecture description to distinguish the current React 19 + Express + tRPC application from the earlier FastAPI/MongoDB-only draft architecture. MongoDB Atlas stores native account credentials; the managed relational application database stores activity, results, and planning records.

## Verification recorded

The worker was tested with a deterministic monthly-history fixture and returned six finite Prophet 1.4.0 forecast points with 80% intervals. The complete non-network suite passed with **25 files and 79 tests**. Regression tests cover completed-month aggregation, exclusion of the live month, the 12-month/90-day evidence gate, interrupted-month rejection, and fallback-mode labelling.

## References

[1] [Prophet Quick Start — Meta Open Source](https://facebook.github.io/prophet/docs/quick_start.html)  
[2] [Prophet Diagnostics — Meta Open Source](https://facebook.github.io/prophet/docs/diagnostics.html)  
[3] [Prophet Installation — Meta Open Source](https://facebook.github.io/prophet/docs/installation.html)

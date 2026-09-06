# XGBoost Deterministic 100-Scenario QA Audit

> This is non-user QA evidence generated from bounded test inputs. It does not create user records and must not be interpreted as an emissions distribution or real-person outcome set.

## Validation Result

All **100** deterministic scenarios executed through the persisted `xgb-final-54f-v2` runtime. Every output was finite, used the frozen 34-to-54 feature contract, returned a ranked contribution explanation, and reconciled its grouped contribution total to the prediction within **0.2 kgCO₂e**.

## Matrix Summary

| Summary measure | Result (kgCO₂e/month) |
|---|---:|
| Lowest deterministic test result | 176.8 |
| Highest deterministic test result | 2102.1 |
| Matrix mean | 1019.2 |
| Matrix median | 913.5 |

## Profile Bands

| Test band | Scenarios | Mean | Minimum–maximum |
|---|---:|---:|---:|
| Low Impact | 34 | 265.0 | 176.8–358.3 |
| Typical | 33 | 906.4 | 405.0–1219.8 |
| High Impact | 33 | 1909.2 | 1723.5–2102.1 |

## Representative Live Explanations

| Case | Result | Top live model drivers |
|---|---:|---|
| lowestPrediction | 176.8 | Digital use (decreases -229.0); Air travel frequency (decreases -162.3); Diet and grocery (decreases -94.5) |
| closestToMatrixMean | 1013.1 | Air travel frequency (decreases -159.0); Diet and grocery (increases +88.1); New clothing purchases (increases +64.7) |
| highestPrediction | 2102.1 | Transport and distance (increases +317.2); Air travel frequency (increases +260.2); Digital use (increases +209.4) |

## Interpretation Boundary

The results show that the live persisted model responds to controlled changes in submitted survey inputs and that its grouped XGBoost contributions reconcile to each prediction. They do **not** prove a real person’s emissions, causal environmental effects, or a population distribution; the model target remains formula-derived and synthetic.

Detailed machine-readable scenario evidence: `server/model_runtime/audits/xgb_deterministic_100_scenario_audit.json`.

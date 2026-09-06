# CarbonSense Model Feature-Importance Note

## What the preprocessor does

`preprocessor_10k_final.joblib` does **not** rank or dominate features. It converts the frozen 34 raw inputs into the exact 54 transformed features that the trained model expects, preserving training-time feature order and categorical encoding.

The persisted XGBoost model (`best_carbon_model.joblib`) determines global feature importance.

## Globally dominant model feature groups

| Rank | Feature group | Global total-gain share |
|---:|---|---:|
| 1 | Air-travel frequency | 35.604% |
| 2 | Digital use | 24.190% |
| 3 | Transport and distance | 20.965% |
| 4 | Waste and recycling | 7.496% |
| 5 | New clothing purchases | 5.189% |
| 6 | Diet and grocery | 5.033% |
| 7 | Home energy and region | 1.502% |

The first three groups account for **80.759%** of the frozen model’s total split gain.

## Most dominant exact transformed features

| Rank | Exact model feature | Questionnaire field | Global importance |
|---:|---|---|---:|
| 1 | `frequency_of_traveling_by_air_very frequently` | Air travel = very frequently | 27.950% |
| 2 | `how_long_tv_pc_daily_hour` | TV / PC hours per day | 24.006% |
| 3 | `vehicle_monthly_distance_km` | Vehicle distance per month | 18.388% |
| 4 | `how_many_new_clothes_monthly` | New clothing per month | 5.189% |
| 5 | `frequency_of_traveling_by_air_never` | Air travel = never | 4.345% |
| 6 | `waste_bag_weekly_count` | Waste bags per week | 4.015% |
| 7 | `frequency_of_traveling_by_air_rarely` | Air travel = rarely | 3.310% |

> The globally dominant user-input families are **air-travel frequency, TV/PC time, vehicle distance, new-clothing frequency, and weekly waste-bag count**.

## Interpretation

This is **global XGBoost total-gain importance**: it shows which transformed features the model relied on most across its saved training trees. It is different from the user-specific live breakdown. A particular prediction can have another top contribution because that contribution depends on all of that user’s submitted answers together.

Feature importance and individual contribution values describe model behavior. They are not direct causal measurements of environmental impact.

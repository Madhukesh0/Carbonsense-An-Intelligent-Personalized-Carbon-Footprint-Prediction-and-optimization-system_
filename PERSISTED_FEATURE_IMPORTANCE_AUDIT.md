# Persisted XGBoost feature-importance audit

## Important correction

`preprocessor_10k_final.joblib` does **not** decide which features are dominant. Its job is to transform the frozen 34 raw columns into the 54 columns expected by the model: it preserves numeric values, creates categorical one-hot columns, and maintains the exact training-time order.

Dominance comes from the persisted `best_carbon_model.joblib` XGBoost tree ensemble. This audit extracted the model’s **global total-gain importance** for every one of the 54 transformed features and grouped related transformed features using the same labels displayed in CarbonSense.

## Dominant global model groups

| Rank | Group | Total-gain share | Main related user answers |
|---:|---|---:|---|
| 1 | Air travel frequency | 35.604% | Air travel frequency |
| 2 | Digital use | 24.190% | TV/PC hours per day; internet hours per day |
| 3 | Transport and distance | 20.965% | Transport; vehicle distance; heating/region interaction |
| 4 | Waste and recycling | 7.496% | Waste bag count/size; recycling selections |
| 5 | New clothing purchases | 5.189% | New clothing items per month |
| 6 | Diet and grocery | 5.033% | Diet; grocery spend; diet × grocery interaction |
| 7 | Home energy and region | 1.502% | Heating source; regional grid factor |
| — | All remaining groups | 0.021% | Vehicle type, profile fields, cooking, social activity, efficiency, shower frequency |

The top three global groups account for **80.759%** of the model’s total split gain. For the frozen model artifact, air-travel frequency, digital use, and transport/distance are therefore the most dominant input families.

## Top transformed features in the saved model

| Rank | Exact transformed feature | Global total-gain share | Questionnaire mapping |
|---:|---|---:|---|
| 1 | `frequency_of_traveling_by_air_very frequently` | 27.950% | Air travel = very frequently |
| 2 | `how_long_tv_pc_daily_hour` | 24.006% | TV / PC hours per day |
| 3 | `vehicle_monthly_distance_km` | 18.388% | Vehicle distance per month |
| 4 | `how_many_new_clothes_monthly` | 5.189% | New clothing items per month |
| 5 | `frequency_of_traveling_by_air_never` | 4.345% | Air travel = never |
| 6 | `waste_bag_weekly_count` | 4.015% | Waste bags per week |
| 7 | `frequency_of_traveling_by_air_rarely` | 3.310% | Air travel = rarely |
| 8 | `diet_x_grocery` | 2.846% | Calculated diet × grocery interaction |
| 9 | `transport_x_energy` | 2.159% | Calculated transport × energy interaction |
| 10 | `waste_bag_size_small` | 1.912% | Waste bag size = small |

## Global importance versus the user’s live breakdown

Global importance tells us which feature families the model relied on most **across its training trees overall**. It does not say that every user will have the same top contribution.

For the previously verified submitted profile, **digital use** was the largest *user-specific contribution* at −114.066 kgCO₂e/month, followed by air travel frequency at −97.371 kgCO₂e/month. This is compatible with the global audit: both fields are globally dominant, but the exact contribution value depends on the particular answers submitted together.

> A total-gain share measures the model’s internal use of a feature when splitting its training trees. It is not a causal estimate of real-world emissions impact.

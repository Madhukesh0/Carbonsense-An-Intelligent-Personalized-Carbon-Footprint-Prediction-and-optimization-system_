# Submitted-profile inference verification

**Verified:** 20 August 2026  
**Model:** `xgb-final-54f-v2`  
**Dataset contract:** `individual-10k-regional-v1`

## Short answer

The **709.295 kgCO₂e/month** shown in the supplied result screenshot is a genuine output from the deployed frozen **XGBoost model**, not a new hand-written formula. The application does use deterministic mathematics first to transform the questionnaire answers into the frozen 34-column input contract. It then applies the persisted 54-feature preprocessor and asks the trained XGBoost tree ensemble to score that vector.

> The main result is **trained-model inference**. The deterministic calculations prepare the model input; they do not replace the trained XGBoost prediction.

## Reconstructed submitted answers

The following values were reconstructed from the supplied screenshots and submitted to the exact deployed artifact runner. The reconstruction deliberately excludes no observed answer.

| Questionnaire area | Submitted value | How it is used |
|---|---:|---|
| Age | 18 | Survey context only; **not used as an XGBoost feature** in this frozen contract. |
| Profile | Male; normal body type | Encoded into profile columns. |
| Diet and showering | Omnivore; daily | Encoded into categorical columns; diet also contributes to a deterministic grocery interaction. |
| Heating and efficiency | Electricity; Sometimes | Encoded; heating and region create energy-derived columns. |
| Transport | Private; petrol; 259 km/month | Encoded; distance and travel mode create transport-derived columns. |
| Air travel and region | Rarely; mixed | Encoded; region produces the regional grid factor. |
| Consumption | Grocery 200; clothing 2 | Grocery contributes directly and to the diet × grocery interaction; clothing is direct. |
| Waste and digital activity | Medium bag; 3 bags/week; TV/PC 4 h/day; internet 4 h/day | Direct numeric/category inputs. |
| Social activity | Sometimes | Encoded into categorical columns. |
| Recycling | Paper, plastic | Generates paper=1, plastic=1, metal=0, glass=0, none=0. |
| Cooking | Stove, oven | Generates stove=1, oven=1, microwave=0, grill=0, airfryer=0, none=0. |

## How 21 controls become 34 frozen raw columns

The user sees 21 controls because this is the useful number of answers to collect. The model’s **34 raw columns** are not 34 unrelated questions.

| Stage | Count | What happens for this profile |
|---|---:|---|
| Direct numeric and categorical model values | 18 | Six numeric values plus twelve selected categories are passed into the fixed contract. |
| Survey context | 1 | Age is validated and retained in the submitted survey, but is not used by this model artifact. |
| Multi-select source controls | 2 | Recycling and cooking are converted into 11 binary flags. |
| Deterministic engineered columns | 5 | The server computes regional/energy/transport/diet relationships from the selected answers. |
| **Frozen raw model columns** | **34** | 18 direct model values + 11 flags + 5 engineered values. |
| Preprocessed model vector | **54** | The persisted preprocessor keeps numeric/binary columns and one-hot encodes categorical columns in its saved training-time order. |

For the reconstructed profile, the five deterministic engineered values are:

| Frozen raw column | Formula | Verified value |
|---|---|---:|
| `region_grid_factor` | mixed regional factor | 0.475 |
| `energy_proxy` | `region_grid_factor × electricity multiplier` | 0.475 |
| `transport_x_energy` | `private transport multiplier × energy_proxy` | 0.475 |
| `diet_x_grocery` | `omnivore multiplier × grocery spend` | 200.000 |
| `distance_energy_ratio` | `259 km ÷ energy_proxy` | 545.263 |

These calculations are deterministic and use the frozen code contract. The persisted preprocessor then creates the 54-feature vector expected by the model artifact. It does not estimate missing fields or replace submitted answers with browser defaults.

## Verified live XGBoost result

The same reconstructed payload was passed to `server/model_runtime/infer.py`, which first verified the SHA-256 manifest and then loaded the persisted `best_carbon_model.joblib` and `preprocessor_10k_final.joblib` files.

| Result element | Verified value | Meaning |
|---|---:|---|
| XGBoost output displayed in the app | 709.295 kgCO₂e/month | The unrounded model output. The result card may display a rounded value. |
| Displayed prediction | 709.3 kgCO₂e/month | Rounded to one decimal place by the runtime. |
| RMSE comparison range | 683.7–734.9 kgCO₂e/month | Prediction ± the held-out RMSE of 25.627 kgCO₂e/month. |
| Model version | `xgb-final-54f-v2` | Exact deployed GitHub artifact version. |
| Feature contract | 34 → 54 | Exact persisted preprocessing path. |

The artifact hashes calculated during this check matched the frozen manifest:

| Artifact | SHA-256 status |
|---|---|
| `best_carbon_model.joblib` | Matched |
| `preprocessor_10k_final.joblib` | Matched |
| `model_metadata.json` | Matched |

## Why the live XGBoost breakdown adds up exactly

The model runtime uses XGBoost’s `pred_contribs=True` output. This returns a base value plus a contribution from each of the 54 transformed features for **this exact submitted vector**. CarbonSense groups related transformed features into understandable categories before displaying them.

| Group shown in the app | Contribution (kgCO₂e/month) | Direction |
|---|---:|---|
| Digital use | −114.066 | Lowers the model result relative to its base value. |
| Air travel frequency | −97.371 | Lowers the model result. |
| New clothing purchases | −64.388 | Lowers the model result. |
| Home energy and region | +61.169 | Raises the model result. |
| Waste and recycling | −50.285 | Lowers the model result. |
| Diet and grocery | +46.625 | Raises the model result. |
| Transport and distance | −16.506 | Lowers the model result. |
| All remaining grouped effects | +0.378 | Small net effect across efficiency, profile, vehicle, cooking, social, and shower groups. |

The exact reconciliation is:

```text
XGBoost base value                         943.739
+ all grouped contributions               −234.444
--------------------------------------------------
= reconstructed model output               709.295 kgCO₂e/month
```

This is why the screenshot’s **Model reconciliation = 709.295 kg** is correct. It is an internal consistency check on the real tree-model calculation.

## What is mathematical and what is trained

| Part of the system | Is it mathematics? | Is it trained XGBoost inference? |
|---|---|---|
| Converting recycling/cooking selections into 0/1 flags | Yes, deterministic | No |
| Computing regional, energy, transport, and diet interaction columns | Yes, deterministic | No |
| Mapping 34 raw columns into the saved 54-feature vector | Yes, deterministic preprocessing | No |
| Producing 709.295 from the 54-feature vector | Yes, tree arithmetic | **Yes, the trained XGBoost ensemble** |
| Contribution breakdown | Yes, sums of per-tree feature contributions | **Yes, derived from the trained XGBoost ensemble** |
| RMSE comparison range | Yes, fixed ±25.627 calculation | No; it uses the model’s held-out evaluation metric |
| Separate transparent baseline tab | Yes, documented factor-based calculation | No; it is intentionally a different comparison lens |

## Important interpretation boundary

The live breakdown is valid as an explanation of **how this frozen model behaved for these answers**. For example, a negative “Digital use” contribution means those submitted digital-use values pushed this model’s result below its base value; it does **not** prove that changing internet use alone will cause exactly 114.066 kgCO₂e/month of real-world change.

The model was trained on a formula-derived synthetic target. Therefore, this is a scientifically useful **model-based estimate and comparison tool**, not a direct physical measurement or a causal environmental-impact claim.

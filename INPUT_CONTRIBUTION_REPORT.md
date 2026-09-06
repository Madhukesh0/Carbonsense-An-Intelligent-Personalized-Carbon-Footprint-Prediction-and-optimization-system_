# Do All User Inputs Contribute to the Carbon Estimate?

**Question:** Does every input the user gives directly contribute to the carbon emission estimate?

**Short answer:** **No — and by design, not every question on the form is meant to.**
All 15 interactive answers shape the estimate, but in different ways and to very different
degrees. The AI model weights them according to what it learned from training data; the
transparent baseline converts a subset of them with published emission factors; and five
contract fields (body type, sex, shower frequency, social activity, energy-efficiency
attitude) are deliberately held at dataset reference values because they have no defensible
emission mechanism.

This report documents, field by field, exactly how each input moves the number.

---

## 1. The two estimates side by side

CarbonSense produces two numbers from the same 15 answers, and "contribution" means
something different in each:

| | **AI prediction** (XGBoost, v2.5) | **Transparent baseline** (formula) |
|---|---|---|
| Method | Gradient-boosted trees trained on the `carbonsense-synthetic-v2.5` dataset | Published emission factors multiplied by reported activity |
| How an input contributes | Trees split on the input's encoded value; the effect is learned, non-linear, and interacts with other answers | The input appears directly in an arithmetic line: `activity × factor = kg` |
| Which inputs move it | 31 of the 36 model features are set by the user; the other 5 are country-derived factors | 11 of the 15 questions appear in the formula; 4 are not in it at all |
| Per-input attribution shown to the user | Live SHAP contributions per feature group | Line-by-line arithmetic per category |
| Uncertainty | ±71.3 kg (split-conformal 90% interval, 91.4% empirical coverage) | Not modeled — the formula is deterministic |
| Model accuracy on held-out data | R² 0.951, MAE 32.2 kg, RMSE 44.6 kg | n/a (it is the reference calculation) |

A run is only complete when both exist together — that pairing is what the recommendations
page (see §7) and the optimizer are built on.

---

## 2. What the user is actually asked

The questionnaire (`client/src/utils/predictSurvey.ts`) asks **15 interactive questions**,
grouped into steps. Two of them are compound multi-selects that expand into several model
columns. The form also derives `country` (grid selection) and sends `region` and the five
no-mechanism fields at dataset reference values to keep the frozen 26-column payload valid
(`client/src/utils/predictContract.ts`, `backend/app/core/final_contract.py`).

| # | Question | Field | Expands into model columns |
|---|---|---|---|
| 1 | Main travel mode | `transport` | `transport_public`, `transport_walk/bicycle` (drop-one vs private) |
| 2 | Vehicle fuel | `vehicle_type` | 5 one-hot columns (drop-one vs diesel) |
| 3 | Distance driven / month | `vehicle_monthly_distance_km` | numeric |
| 4 | Flights | `frequency_of_traveling_by_air` | 3 one-hot columns (drop-one vs never) |
| 5 | People in your home | `household_size` | numeric |
| 6 | Heating fuel | `heating_energy_source` | 2 one-hot columns (drop-one vs electricity) |
| 7 | TV / PC hours / day | `how_long_tv_pc_daily_hour` | numeric |
| 8 | Internet hours / day | `how_long_internet_daily_hour` | numeric |
| 9 | Diet pattern | `diet` | 3 one-hot columns (drop-one vs omnivore) |
| 10 | Grocery spend / month | `monthly_grocery_bill` | numeric |
| 11 | New clothing / month | `how_many_new_clothes_monthly` | numeric |
| 12 | Waste bag size | `waste_bag_size` | 3 one-hot columns (drop-one vs extra large) |
| 13 | Waste bags / week | `waste_bag_weekly_count` | numeric |
| 14 | Recycling (multi-select) | `recycling` | 4 binary columns |
| 15 | Cooking appliances (multi-select) | `cooking_with` | 5 binary columns |

Plus two page-level selections: **country** (India / US / UK — sets the grid and grocery
factors) and the retired **region** grid-mix field (sent at reference value).

---

## 3. How each input feeds the AI model (v2.5)

The deployed XGBoost model consumes a **36-feature vector** built from the answers
(`backend/app/services/prediction.py::build_v25_features`). 31 features are set directly by
the user. The remaining 5 — `grid_factor`, `renewable grid override`, `grocery_factor`,
plus the country selection behind them — come from the country/renewable selections.

Global importance of the deployed model (total gain across trees, computed from
`best_carbon_model_v25.joblib`):

| Rank | Input family | Global importance | Fields involved |
|---:|---|---:|---|
| 1 | Air travel | **50.6%** | flight frequency (all 3 one-hots: 35.1 + 11.9 + 3.7) |
| 2 | Diet & grocery | 24.2% | grocery spend (7.3), diet pattern (13.8), country grocery factor (3.1) |
| 3 | Waste | 12.9% | bag size (10.1), bags per week (2.8) |
| 4 | Home energy | 4.5% | household size (3.4), heating fuel (0.4), grid factor (0.7) |
| 5 | New clothing | 2.9% | clothing count |
| 6 | Vehicle type | 2.2% | fuel type (distance adds 0.5 via transport) |
| 7 | Cooking | 0.9% | appliance multi-select |
| 8 | Recycling | 0.8% | material multi-select |
| 9 | Digital use | 0.2% | TV/PC hours (0.10), internet hours (0.11) |

**Reading this correctly.** These are *model* weights, not physical emissions. Three
caveats matter:

1. **Global ≠ personal.** A single prediction's dominant driver can differ — the results
   page shows each user's live SHAP group contributions. For the verified test account
   (UK, omnivore, electricity heating), the model's biggest positive contributor was the
   diet group (+291.7 kg), not air travel.
2. **The one-hot encoding splits a single answer's weight** across its non-reference
   columns; family totals above sum them.
3. **Drop-one encoding hides the reference class.** `vehicle_type_none`, `diet_vegan`, etc.
   carry the effect of *not* being the reference (diesel / omnivore). An omnivore user's
   omnivore-ness is real but encoded as zeros elsewhere — its effect shows up in SHAP, not
   in a named feature's importance.

### Fields the model does NOT use

The v2.5 build removed these from the feature vector (they are accepted by the API schema
for compatibility, then ignored by `build_v25_features`):

| Field | Why it is excluded |
|---|---|
| `sex` | No defensible emission mechanism; dataset reference value sent |
| `body_type` | Same — no causal pathway to household emissions |
| `how_often_shower` | No water-heating energy data behind it |
| `social_activity` | Proxy for nothing measurable in the dataset |
| `energy_efficiency` | Self-reported attitude, no activity data behind it |
| `age` | Not in the v2.5 feature contract |
| `currency` | Display only; the country factor, not the currency code, prices groceries |

The results page is explicit about this: the plain-language "your answers" card filters out
the `profile_fields`, `shower_frequency`, `social_activity`, and `energy_efficiency` groups
(`PredictionResults.tsx` `notAsked` set), so users are never told these fields drove their
result.

---

## 4. How each input feeds the transparent baseline

The baseline (`backend/app/services/baseline.py`) uses only inputs that map to a published
factor. Each line is visible arithmetic:

| Baseline line | Formula | Inputs used |
|---|---|---|
| Electricity | `220 kWh (shared ref) × grid factor ÷ household` | **country, household_size** |
| Transport | `km × vehicle kg/km` (petrol 0.162, diesel 0.173, hybrid 0.130, LPG 0.196, electric 0.027, public transit 0.102 kg/pkm) | **transport, vehicle_type, vehicle_monthly_distance_km** |
| Diet | screening band (vegan 95, vegetarian 130, pescatarian 175, omnivore 240 kg) | **diet** |
| Waste | `bags × 4.3 weeks × bag-size factor ÷ household` | **waste_bag_size, waste_bag_weekly_count, household_size** |
| Air travel | band proxy (never 0, rarely 60, often 180, very frequently 420 kg) | **frequency_of_traveling_by_air** |
| Consumption | `grocery spend × country price factor + clothing × 18 kg` | **monthly_grocery_bill, how_many_new_clothes_monthly, country** |

Factor sources: Ember 2025 grid factors (India 0.670, US 0.384) with a DESNZ 2026 UK
reporting-basis factor (0.131), DESNZ 2026 vehicle and bus factors, and disclosed screening
proxies for diet, waste, air, and clothing.

**Four questions do not enter the baseline at all:** TV/PC hours, internet hours, cooking
appliances, and recycling. They are real questions with real model weight (digital use
0.2%, cooking 0.9%, recycling 0.8% globally) — but no published factor converts "hours of
streaming" into kg CO₂e at estimate time, so the transparent method declines to pretend
otherwise.

---

## 5. Field-by-field: the full picture

Merging both views — **=** modelled and shown in the baseline, **AI** model-only:

| Input | AI model weight | Baseline line | Verdict |
|---|---|---|---|
| Flight frequency | 50.6% (largest single driver) | ✈ air band | **Highest-impact answer in the survey** for both methods |
| Grocery spend | 7.3% + factor 3.1% | consumption | Strong in both |
| Diet pattern | 13.8% | diet band | Strong in both |
| Waste bag size | 10.1% | waste | Size matters to the model more than the count |
| Waste bags/week | 2.8% | waste | Both |
| Household size | 3.4% | electricity + waste (÷) | Both (divides shared lines) |
| Vehicle distance | 0.5% model / direct in baseline | transport | **Model-weak, baseline-strong** — the formula is linear in km; the learned model barely uses it because air travel dominates the synthetic target |
| Vehicle type | 2.2% | transport (factor choice) | Both |
| Heating fuel | 0.4% | — (baseline: only via grid for electric) | Minor in both |
| Country/grid | 0.7% + grocery factor 3.1% | electricity + consumption | Both (scales two lines) |
| New clothing/month | 2.9% | consumption (18 kg/item) | Both |
| TV/PC hours | 0.10% | not in baseline | **Model-only, near-zero** |
| Internet hours | 0.11% | not in baseline | **Model-only, near-zero** |
| Cooking appliances | 0.9% | not in baseline | Model-only, minor |
| Recycling | 0.8% | not in baseline | Model-only, minor |

The surprises worth knowing: **vehicle distance — the answer most users assume matters
most — carries only 0.5% of the model's split gain**, while the flight-frequency answer
carries half the model. That asymmetry is a property of the v2.5 synthetic training target,
and it is exactly why the app shows *two* methods: the baseline keeps physical proportion
(`1200 km × 0.162 = 194 kg`) when the model's learned weighting does not.

---

## 6. How this maps to recommendations

The dynamic recommendation engine (`/recommendations/result-led`, added 2026-09-06) uses
the same principle: every approved action is re-scored against the **submitted answers** of
the newest run using the transparent factor set, and ranked by estimated planning impact:

- Flight frequency `rarely → often → very frequently` yields band deltas of 60 / 120 / 240
  kg — so a "very frequently" flyer sees *Cut back one air-travel band* ranked first.
- An omnivore sees ~110 kg for the diet band shift; a vegan sees no diet action at all.
- The cleaner-energy estimate uses the actual country grid gap (India 0.523 kg/kWh of
  headroom vs UK 0.083) and divides by household size — a UK user sees 9.1 kg, not a
  static 44.
- Transit and fuel actions scale with actual reported km and vehicle factor.
- Every action shows its arithmetic basis ("estimate basis: …") and its share of the
  user's baseline, and each is annotated with the run's live SHAP contribution for its
  feature group.

Actions with sub-1 kg planning estimates, and actions whose gating fails (no vehicle, no
flights, zero clothing), are not shown — the engine never suggests a lever the user's data
says they do not have.

---

## 7. Where the numbers come from (traceability)

| Claim | Source in repo |
|---|---|
| 15 interactive questions | `client/src/utils/predictSurvey.ts` (`fieldGroups`) |
| 26-column → 44-feature frozen contract (v1 runtime) | `backend/app/core/final_contract.py` |
| 36-feature v2.5 vector builder | `backend/app/services/prediction.py::build_v25_features` |
| Model metrics (R² 0.951, MAE 32.2, conformal ±71.3) | `server/model_runtime/artifacts_v25/model_metadata_v25.json` |
| Global importance table (§3) | Computed from `best_carbon_model_v25.joblib` feature importances |
| Baseline factors and formulas | `backend/app/services/baseline.py` (`FACTOR_SET`, `SCREENING`) |
| Excluded no-mechanism fields | `client/src/utils/predictContract.ts` header comment; `PredictionResults.tsx` `notAsked` |
| Dynamic recommendation scoring | `backend/app/routers/recommendations.py::estimate_profile_actions` |

**Standing caveat, as stated throughout the product:** feature importances and SHAP
contributions describe *model behavior*; the baseline is a *screening calculation* from
declared proxies. Neither is a direct emissions measurement, and estimates are indicative,
not verified reductions.

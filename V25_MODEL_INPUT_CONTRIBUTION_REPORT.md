# XGBoost v2.5 Production Model — Input Contribution Report

**Model under analysis:** `final-xgboost-v25` (`best_carbon_model_v25.joblib`) — the deployed
production runtime behind `POST /api/v1/model/predict` and `/api/v1/model/baseline`
(`backend/app/services/prediction.py::run_prediction_v25`).

**Question answered:** Does every input the user gives directly contribute to the v2.5
model's carbon estimate — and by how much?

**Short answer:** **No.** The v2.5 model consumes 36 engineered features, of which **31 are
set directly by the user's 15 questionnaire answers** (the other 5 are country-derived
factors). Seven additional fields the API accepts — `age`, `sex`, `body_type`,
`how_often_shower`, `social_activity`, `energy_efficiency`, `currency` — have **exactly zero
contribution**: they never reach the feature builder. And among the inputs that *do* reach
the model, contribution ranges from ~0.3% (TV/PC time) to ~21% (grocery spend) of the
average absolute SHAP mass.

Everything below was measured on the live production artifacts, not estimated.

---

## 1. Method — two independent measurements on the deployed model

1. **One-at-a-time sensitivity sweep.** A fixed reference profile (India, household 2,
   petrol 300 km, omnivore, 200 grocery, 2 clothes, medium/3 waste bags, 4h screens,
   rarely flights) was held constant while each field was swept across its full legal
   range (`reports/v25_input_sensitivity.json`). This shows the *practical range* each
   answer can swing the prediction across, including non-linear behavior.

2. **Mean |SHAP| over 800 random profiles** (seed 42), sampled across all legal values of
   every field (`reports/v25_shap_by_field.json`). This shows each field's *average
   contribution to the model's output* across realistic input space, correctly attributing
   one-hot columns back to their single questionnaire field.

The two methods agree on the ordering of the top inputs; the SHAP table is the primary
measure of "how much does this input contribute."

Reference prediction for the fixed profile: **450.0 kg CO₂e** (the model's uncertainty on
any single estimate is ±71.3 kg at 90% conformal coverage).

---

## 2. Headline result: average contribution share per input

Mean absolute SHAP share across 800 random profiles. This is "of all the explaining the
model does, how much rests on this answer":

| Rank | Input (questionnaire field) | Avg \|SHAP\| share | Avg \|contribution\| | Verdict |
|---:|---|---:|---:|---|
| 1 | **Grocery spend / month** | **20.8%** | ≈199 kg | Dominant driver |
| 2 | **New clothing / month** | **16.3%** | ≈155 kg | Dominant driver |
| 3 | Flight frequency | 8.8% | ≈84 kg | Strong |
| 4 | Country (grid + grocery factor) | 8.3% | ≈79 kg | Strong context |
| 5 | Household size | 8.2% | ≈78 kg | Strong context |
| 6 | Diet pattern | 8.1% | ≈78 kg | Strong |
| 7 | Waste bags / week | 8.1% | ≈77 kg | Strong |
| 8 | Vehicle distance / month | 6.5% | ≈63 kg | Moderate |
| 9 | Waste bag size | 5.9% | ≈56 kg | Moderate |
| 10 | Vehicle fuel type | 3.7% | ≈36 kg | Minor-moderate |
| 11 | Cooking appliances | 1.4% | ≈13 kg | Minor |
| 12 | Region (grid mix) | 1.3% | ≈12 kg | Minor |
| 13 | Recycling | 1.2% | ≈12 kg | Minor |
| 14 | Internet hours / day | 0.45% | ≈4 kg | Near-zero |
| 15 | Heating fuel | 0.4% | ≈4 kg | Near-zero |
| 16 | TV / PC hours / day | 0.35% | ≈3 kg | Near-zero |
| 17 | Main travel mode (private/public/walk) | 0.34% | ≈3 kg | Near-zero |

**Zero-contribution fields** (accepted by the API schema, never enter the model):
`age`, `sex`, `body_type`, `how_often_shower`, `social_activity`, `energy_efficiency`,
`currency`. The v2.5 feature builder (`build_v25_features`) silently ignores them; the UI
sends them only to keep the frozen payload schema valid.

---

## 3. Practical swing range per answer (sensitivity sweep)

Starting from the 450 kg reference profile, how far can one answer move the prediction
across its full legal range (all else fixed)?

| Input | Sweep (value → predicted kg) | Total swing |
|---|---|---:|
| **New clothing / month** | 0→401, 2→450, 5→497, 10→589, 25→988, 50→**1,095** | **+694 kg** |
| **Grocery spend / month** | 0→417, 200→450, 500→520, 1000→588, 2000→667, 5000→**1,006** | **+589 kg** |
| Waste bags / week | 0→414, 3→450, 5→476, 10→619, 20→**836** | +421 kg |
| Vehicle distance / month | 0→429, 300→450, 1200→563, 3000→**837**, 5000→837 (saturates) | +409 kg |
| Flight frequency | never→406, rarely→450, often→574, very frequently→**406** | 168 kg |
| Diet | vegan→309, vegetarian→335, pescatarian→353, omnivore→450 | 141 kg |
| Household size | 1→511, 2→450, 4→413, 10→382 | 129 kg |
| Waste bag size | small→421, medium→450, large→503, extra large→538 | 117 kg |
| Country | india→450, us→507, uk→508 | 58 kg |
| Vehicle type | none→422, electric→430, hybrid→445, petrol→450, diesel→452 | 31 kg |
| Region | mixed→450, renewable_heavy→421 | 29 kg |
| Cooking appliances | none→450, stove only→471, all five→474 | 24 kg |
| Heating fuel | wood→438, gas→450, electricity→450 | 12 kg |
| Recycling | none→450, all four→431 | 19 kg |
| Main travel mode | walk/bicycle→444, public→450, private→450 | 7 kg |
| TV / PC hours | 0→445, 4→450, 24→448 | 6 kg |
| Internet hours | 0→451, 8→449, 24→455 | 5 kg |

### Non-linear behaviors worth knowing (the model is not a formula)

- **Vehicle distance saturates at 3,000 km.** Predicted impact stops growing beyond it:
  3,000, 5,000, and 10,000 km all yield 837.3 kg. The trees never learned a higher-distance
  split. The transparent baseline keeps growing linearly where the model has stopped.
- **Flight frequency is U-shaped, not monotone.** "very frequently" (406 kg) scores the
  same as "never" (406 kg), *below* "rarely" (450) and "often" (574). Only the "often"
  band pushes predictions up in the region sampled; the strongest flight signal in the
  training-data direction appears only in combination with other high-spend answers.
- **Grocery spend is flat at the bottom.** 0 and 100 both give 416.8 — the model's first
  grocery split sits between 100 and 200 (in the reference currency scale).
- **Travel mode barely matters on its own.** Switching private → public → walk/bicycle
  moves the prediction by 6.5 kg total, because with the reference distance of 300 km the
  distance feature dominates whatever mode split exists.
- **Interaction effects are strong.** Every number above is conditional on the reference
  profile; a UK household of 5 with a vegan diet will see different deltas. The user-facing
  SHAP breakdown on the results page shows each individual's actual contributions.

---

## 4. Feature-level detail (before grouping)

Per-engineered-feature mean |SHAP| (kg) across the 800-profile sample — showing how the
drop-one encoding distributes each answer's weight:

| Model feature | Avg \|SHAP\| | Model feature | Avg \|SHAP\| |
|---|---:|---|---:|
| `monthly_grocery_bill` | 195.6 | `vehicle_type_none` | 14.9 |
| `how_many_new_clothes_monthly` | 155.3 | `waste_bag_size_large` | 12.9 |
| `air_often` | 48.9 | `cook_stove` | 8.6 |
| `waste_bag_weekly_count` | 46.9 | `grid_factor` | 7.6 |
| `vehicle_monthly_distance_km` | 39.0 | `heating_wood` | 2.6 |
| `waste_bag_size_medium` | 27.2 | `recycle_metal` | 2.5 |
| `grocery_factor` | 25.2 | `heating_natural_gas` | 2.4 |
| `diet_vegetarian` | 21.5 | `recycle_plastic` | 2.2 |
| `diet_pescatarian` | 21.3 | `recycle_glass` | 2.1 |
| `diet_vegan` | 20.7 | `vehicle_type_petrol` | 2.1 |
| `household_size` | 19.5 | `recycle_paper` | 2.0 |
| `waste_bag_size_small` | 15.8 | `transport_public` | 1.7 |
| `air_very_frequently` | 19.0 | `cook_oven` | 1.7 |
| `air_rarely` | 15.8 | `transport_walk/bicycle` | 1.5 |
| `vehicle_type_electric` | 15.3 | `how_long_internet_daily_hour` | 1.3 |
| `vehicle_type_hybrid` | 3.2 | `cook_microwave` | 1.3 |
| `vehicle_type_lpg` | 3.2 | `how_long_tv_pc_daily_hour` | 1.1 |

(Numbers do not sum to the field table's "avg contribution" column because the SHAP base
value and reference-class zeros distribute the remainder.)

---

## 5. What this means for the product

1. **Five answers do ~70% of the explanatory work:** grocery spend, clothing count, flight
   frequency, country, and household size. A user changing those five will see the estimate
   move a lot; changing screen time or travel mode will barely move it.
2. **The model is spend- and consumption-weighted, not distance-weighted.** Grocery and
   clothing — both *spend* proxies — outweigh physical activity (km driven) roughly 6:1.
   This mirrors the synthetic v2.5 training target's construction, and it is the reason the
   transparent baseline exists alongside: the formula keeps `km × factor` physically
   proportional where the learned model does not.
3. **The near-zero fields are still worth asking** (screen time, heating fuel, travel mode)
   — but the UI should not imply they strongly drive the estimate. The results page's
   live SHAP card already shows each user their true top contributors, which is the
   product's honest answer to this question.
4. **Recommendations stay factor-led, not model-led.** The dynamic recommendation engine
   ranks actions by transparent factor arithmetic from the submitted answers — so a
   high-distance driver still gets transit/fuel advice even though the model weights
   distance modestly. SHAP values annotate, never rank.

---

## 6. Traceability

| Artifact | Path |
|---|---|
| Deployed model + metadata (R² 0.951, MAE 32.2, conformal ±71.3 @ 90%) | `server/model_runtime/artifacts_v25/` |
| Feature builder (36 features; excludes the 7 zero-contribution fields) | `backend/app/services/prediction.py::build_v25_features` |
| Sensitivity sweep (reference profile, per-value predictions) | `reports/v25_input_sensitivity.json` |
| SHAP field analysis (800 profiles, seed 42) | `reports/v25_shap_by_field.json` |
| API schema accepting all fields | `backend/app/schemas/model.py::SurveyPayload` |
| Model cards & global gain importance (training-time view) | `MODEL_FEATURE_IMPORTANCE_NOTE.md`, `TRAINING_RESULTS.md` |

**Standing caveat:** SHAP values and sensitivity deltas describe *model behavior* on the
frozen v2.5 artifact. The training target is a formula-derived synthetic estimate, so these
contributions reflect learned patterns in that dataset — not direct causal measurements of
environmental impact.

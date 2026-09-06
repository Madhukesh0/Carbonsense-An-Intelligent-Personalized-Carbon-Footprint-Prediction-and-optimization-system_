# CarbonSense Dataset v2.5 — Correctness Audit, Prediction Walkthrough & Creation Record

**Date:** 2026-09-06 · **Scope:** `carbonsense-synthetic-v2.5` (`data/v2_training/clean_dataset_v2.csv`),
the deployed `final-xgboost-v25` runtime (`server/model_runtime/artifacts_v25/`), and the serving encoder
(`backend/app/services/prediction.py`).

**Verdict up front:**

| Question | Verdict |
|---|---|
| Is dataset v2.5 actually correct? | **Yes — every audit check passes.** 10,000 rows, zero nulls/duplicates, factors match the documented lookups exactly, target re-derives from the cited factor formula within the documented noise, and all behavior bands are monotone. |
| Is the deployed model correct? | **Yes — R² 0.976 against the dataset** when features are encoded as at training time. |
| Was the *serving* path correct? | **No — one real bug found and fixed on 2026-09-06** (see §5): multi-word one-hot values (`very frequently`, `natural gas`) were silently dropped, underpredicting very-frequent flyers by ~422 kg. Fixed, verified end-to-end via the live API. |

---

## 1. How the dataset was created

`scripts/generate_dataset_v2.py` (seed 42, deterministic) builds all 10,000 rows from scratch —
it is **not** real-world measurement data, and the app says so everywhere.

### 1.1 Input sampling

Each of the 10,000 rows samples the 15 questionnaire fields from declared distributions:
country (India 40% / US 30% / UK 30%), transport mode (private 62% / public 26% / walk-bicycle 12%),
diet, air frequency, waste, and lognormal-drawn numerics (distance clipped to 0–10,000 km,
grocery bill drawn per-country in local currency, clothing 0–50, waste bags 0–20, TV/internet hours).
Household size is geometric (1–10). 25–28% of rows get the `renewable_heavy` region override.
The five no-mechanism fields (sex, body type, shower, social activity, energy efficiency) are
**not in the v2.5 dataset at all**.

### 1.2 Two derived numeric features carry the country signal

Instead of country one-hots, each row carries:

- `grid_factor` — kgCO₂e/kWh from Ember 2025 (fetched 2026-09-03, data year 2025):
  India 0.67013, US 0.38440, UK 0.21741; the renewable-heavy override applies 0.147 / 0.085 / 0.048.
  (India cross-referenced against CEA v21.0.)
- `grocery_factor` — price-level-calibrated kgCO₂e per unit of local currency:
  India 0.11, US 0.36, UK 0.44.

This design (verified superior to country one-hots during training: R² 0.9462 vs 0.9450 with fewer
features) means the model extends to a new country by adding a lookup entry, without re-encoding.

### 1.3 The target: a cited factor formula + noise

`carbon_emission_kgco2e_month` is computed row by row from `citations/factor-sheet.md` sources
(IPCC fuel chemistry, Scarborough diet bands, OWID flight bands, EEA clothing, IPCC waste), line by line:

| Line | Formula (per row) |
|---|---|
| Transport | petrol/diesel: `km × fuel kgCO₂e/L (2.31 / 2.68) ÷ sampled km/L`; electric: `km × 0.18 kWh/km × grid`; hybrid: petrol ÷ 0.8 economy; LPG: IPCC stoichiometry; public: `km × 1.15 × 0.02` (CNG/metro band); walk/bicycle: 0 |
| Home energy | `(TV 75 W + internet 40 W-equiv hours × 30 + base 40–90 kWh + electric-heat 60–140 kWh) × grid ÷ household`; gas heating flat 20 kg, wood 8 kg |
| Food | diet band (vegan 90 / vegetarian 115 / pescatarian 120 / omnivore 215, Scarborough 2023) + `grocery bill × grocery_factor` |
| Waste | `bags × 4.3 weeks × bag mass (5/10/20/30 kg) × 0.65 kg/kg ÷ household − recycling credits (4/6/12/2)` |
| Clothing | `items × 18 kg` (EEA-derived) |
| Cooking | appliance kWh (stove 12 / oven 9 / microwave 5 / grill 7 / airfryer 8) × grid + partial LPG 15 kg |
| Air travel | band (never 0 / rarely 60 / often 180 / very frequently 420 kg, OWID) |

Finally `× lognormal(0, 0.05)` — ±5% multiplicative noise so the model must **learn the
relationship** instead of memorizing a lookup table.

---

## 2. Correctness audit — dataset (all checks pass)

Reproduce with `py -3.12 scripts/audit_v25_dataset.py` (results cached in
`reports/v25_dataset_audit.json`):

| # | Check | Result |
|---|---|---|
| 1 | Rows / columns | **10,000 × 20** — matches the freeze record |
| 2 | Missing values / duplicate rows | **0 / 0** |
| 3 | Ranges within API schema limits (distance ≤ 10,000; bill ≤ 5,000; clothes ≤ 50; bags ≤ 20; hours ≤ 24; household 1–10; target > 0) | **all pass** |
| 4 | `transport` ∈ {public, walk/bicycle} ⇒ `vehicle_type = none` | **0 violations in 10,000 rows** |
| 5 | `grid_factor` exactly equals the country × region lookup | **10,000 / 10,000 rows** |
| 6 | `grocery_factor` exactly equals the country lookup | **10,000 / 10,000 rows** |
| 7 | Target re-derivation: stored ÷ deterministic-formula ratio | **median 1.018, log-σ 0.058** — i.e. the stored target *is* the formula plus the documented ±5% noise (the +1.8% median shift comes from the audit using mid-range fuel-economy draws where the generator samples per-row) |
| 8 | Diet bands monotone (vegan 567.9 < vegetarian 590.3 < pescatarian 593.5 < omnivore 689.0 mean target) | **pass** |
| 9 | Air bands monotone (never 553.3 < rarely 611.5 < often 735.1 < very frequently 969.9 mean target) | **pass** |
| 10 | Model trained on it reproduces it (all 10k rows, training-style encoding) | **R² 0.9762, MAE 23.9 kg** |

**Conclusion: the v2.5 dataset is internally correct and matches its own documented construction.**

---

## 3. Worked example — one sample input, factor combination to prediction

Sample profile: **India, household of 3, petrol car 450 km/month, natural-gas heating,
omnivore, ₹400 grocery, 3 new clothes/month, 4 medium waste bags/week, recycles paper+plastic,
cooks with stove+oven, 4 h TV/PC + 5 h internet daily, flies "often".**

### 3.1 Emission factors combine (the dataset target's formula)

| Line | Arithmetic | kg |
|---|---|---:|
| Transport | 450 km × 2.31 kg/L ÷ 20 km/L (mid-range petrol economy) | 52.0 |
| Home electricity | (4 h × 75 W + 5 h × 40 W) × 30 d + 65 kWh base + 100 kWh electric-boost = 179.9 kWh × **0.67013 grid** ÷ 3 people | 40.2 |
| Gas heating | flat factor | 20.0 |
| Food | omnivore band 215 + ₹400 × **0.11 grocery factor** | 259.0 |
| Waste | 4 bags × 4.3 wk × 10 kg × 0.65 = 111.8 ÷ 3 − recycling credits (4 + 6) | 27.3 |
| Clothing | 3 × 18 kg | 54.0 |
| Cooking | (stove 12 + oven 9) kWh × grid + LPG 15 kg | 29.1 |
| Flights | "often" band | 180.0 |
| **Total** | | **661.5 kg** |

The stored dataset row would be this × lognormal noise (±5%).

### 3.2 Prediction: how the model combines the same factors

The serving path (`POST /api/v1/model/predict`) does:

1. **Validate** the payload against `SurveyPayload` (pydantic; ranges, enums, list rules).
2. **Encode 36 features** (`build_v25_features`): 6 numerics pass through, `grid_factor` /
   `grocery_factor` / `household_size` become numeric features, and every categorical becomes
   drop-first one-hots (reference classes: private, diesel, never-fly, electric heating,
   omnivore, extra-large bags). For this sample: `air_often=1`, `heating_natural_gas=1`,
   `recycle_paper=1`, `recycle_plastic=1`, `cook_stove=1`, `cook_oven=1`, `grid_factor=0.67013`,
   `grocery_factor=0.11`.
3. **Predict** with XGBoost (400 trees, depth 5, seed 42): **647.1 kg**.
4. **Explain** with TreeSHAP: base 639.7 + Σ contributions = 647.0 (reconciles to the prediction).
   Top groups for this sample: air +92.1, grocery −89.1 (₹400 is modest for India), diet +49.7,
   household −48.3, grocery factor −46.1, distance +20.2.
5. **Quantify uncertainty**: split-conformal 90% interval = ±71.26 kg → **[575.9, 718.4] kg**.
6. **Persist** the run (`footprint_runs`) with the top-6 SHAP groups as `dominant_factors` —
   this is what drives the impact-ranked recommendations.

The model (647.1) sits 2.2% below the deterministic formula (661.5) — exactly the ±5% noise band
it was trained on. Verified live over HTTP: the API returns the identical 647.1 kg with the same
contribution ranking.

---

## 4. Where the model departs from the factors (by design or by learning)

- **The model learned the formula, not the factor table.** MAE 23.9 kg (≈3% of mean target)
  against a target that already contains ±5% noise — it captured the relationship, not row values.
- **It treats factors as interacting features, not lines.** The grid factor enters both the
  electricity line and cooking; the model can (and does) learn interaction effects the linear
  formula cannot express.
- **Rare high bands are learned with less precision.** "Very frequently" flights are only 7% of
  rows; per-band mean errors remain ≤ 9 kg after the §5 fix, but individual estimates there are
  the model's least-precise region.
- **The transparent baseline uses different (newer/official) factors.** Deliberately: the serving
  baseline uses DESNZ 2026 vehicle factors (petrol 0.162 kg/km), a UK DESNZ grid factor (0.131 vs
  the dataset's Ember 0.217), bus 0.102 kg/pkm (vs the dataset's CNG band 0.02), and screening
  diet bands (95/130/175/240). The app presents both numbers side by side and never averages them.

---

## 5. Bug found during this audit — serving encoder dropped multi-word one-hot values (fixed)

**Symptom.** The deployed model scored R² 0.68 against its own dataset through the serving path,
and a "very frequently" flyer predicted the same 405.8 kg as a "never" flyer (data says ≈ +360 kg).

**Root cause.** `build_v25_features()` built one-hot keys with raw value strings:

```python
f[f"air_{air}"] = 1.0        # "very frequently" -> key "air_very frequently" (space)
f[f"heating_{heat}"] = 1.0   # "natural gas"      -> key "heating_natural gas" (space)
```

Training-time encoding (`scripts/train_v25.py`) sanitizes column names
(`' '` → `_`), so the contract columns are `air_very_frequently` / `heating_natural_gas`.
The space-named keys created **new dict entries** that the strict reindex
`pd.DataFrame([feats])[features]` silently discarded — leaving the true columns at 0.0.
Every very-frequent flyer was therefore encoded as the "never" reference class, and every
natural-gas home as electric heating.

**Impact.** ~7% of profiles (very-frequent flyers) were underpredicted by ~422 kg on average;
natural-gas heating lost its (small, ≈2–3 kg) signal. The conformal interval shown to users was
not honored for those profiles.

**Fix (2026-09-06).** Normalize the key: `f[f"air_{air.replace(' ', '_')}"] = 1.0` and
`f[f"heating_{heat.replace(' ', '_')}"] = 1.0` in `backend/app/services/prediction.py`.

**Verification.**

| Check | Before fix | After fix |
|---|---|---|
| All-10k-row R² / MAE (serving encoding, parsed lists) | 0.6817 / 55.3 kg | **0.9762 / 23.9 kg** — byte-identical to the training encoding |
| "very frequently" band mean error | +421.9 kg | **+8.0 kg** |
| `air_very_frequently` / `heating_natural_gas` set correctly | 0.0 | **1.0** |
| Live API (`POST /model/predict`, worked sample) | — | 647.1 kg, correct ranking, reconciling SHAP |

---

## 6. Traceability

| Item | Location |
|---|---|
| Dataset generator (seed 42) | `scripts/generate_dataset_v2.py` |
| Dataset file | `data/v2_training/clean_dataset_v2.csv` |
| Factor sources | `citations/factor-sheet.md`, `citations/country-factors.md` |
| Training pipeline (5 models → best → conformal) | `scripts/train_v25.py` |
| Model artifacts + manifest (SHA-256 verified at load) | `server/model_runtime/artifacts_v25/` |
| Serving encoder + SHAP + conformal | `backend/app/services/prediction.py` |
| Audit script (reproducible) | `scripts/audit_v25_dataset.py` |
| Audit results | `reports/v25_dataset_audit.json` |
| Freeze record / data card | `DATASET_FREEZE.md`, `data/DATA_CARD.md` |

**Standing caveat:** the dataset and target are synthetic, formula-derived constructions, as
recorded in `DATASET_FREEZE.md` and the model metadata. Predictions are indicative model
estimates on that construction — not measurements of real-world personal emissions.

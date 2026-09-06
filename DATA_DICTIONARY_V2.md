# Data Dictionary — CarbonSense v2 dataset (`clean_dataset_v2.csv`)

**Version:** `carbonsense-synthetic-v2.4` (17-country + household; corrected LPG factor + rule-based renewable proxies) · **Generated:** 2026-09-03 ·
**Generator:** `scripts/generate_dataset_v2.py` (seed 42, deterministic —
byte-identical on re-run) · **Rows:** 10,000 · **Columns:** 19 (15 questions + grid_factor + grocery_factor + household_size + country/region labels) + 1 target.
Design: the model receives the NUMERIC grid factor (kgCO2e/kWh) and grocery
spend factor directly - verified superior to country one-hots (R2 0.9462 vs
0.9450, 59 vs 74 features) and instantly extensible: any new country = one
lookup-table entry, zero retraining. Active countries: India (0.67013/0.147),
US (0.38440/0.085), UK (0.21741/0.048) with the renewable-heavy modifier at
25% of rows. The `country`/`region` columns are labels for audit, not model
features.

**Provenance:** the schema is the 15-question frontend questionnaire
(`client/src/utils/predictSurvey.ts`) plus a `country` field (India/US/UK —
to be added to the form as a select with India default in the next frontend
pass). All factors updated to the latest published editions (grid fetched
2026-09-03 via Ember/OWID CSV, data through 2025). The target is computed by a transparent factor formula whose
every coefficient is cited in `citations/` (factor-sheet.md,
india-values.md, india-latest.md). This replaces the v1 Kaggle target
(authored by that dataset's owner with uncitable weights; v1 remains
frozen under DATASET_FREEZE.md as the reproducibility anchor).

---

## Columns

| Column | Type / values | Distribution sampled (seed 42) | Target contribution (per month) |
|---|---|---|---|
| `transport` | private / public / walk-bicycle | 62/26/12% | private: km × fuel factor; public: transit km × 0.02 kg/pkm; walk/bicycle: ≈0 |
| `vehicle_type` | none/petrol/diesel/electric/hybrid/lpg | conditional on transport=private | petrol/diesel: litres = km ÷ efficiency × 2.31/2.68 kg/L (IPCC); hybrid ×0.8 economy; LPG 2.16 kg/kg; **electric: 18 kWh/100km × grid factor** |
| `vehicle_monthly_distance_km` | 0–10,000 | lognormal(5.2, 0.9) | multiplies the fuel factor |
| `frequency_of_traveling_by_air` | never/rarely/often/very-frequently | 35/40/18/7% | bands 0/60/180/420 kg (OWID pkm × typical Indian routes) |
| `region` | mixed / renewable_heavy | 72/28% | grid multiplier within country: national average vs rule-based renewable proxy max(0.02, round(0.22 × national, 2)) — realised ratios ≈18–48% across the 17 countries |
| `household_size` | 1–10 people | geometric(0.42): 1-person 42%, long tail | divides shared home-energy kWh and household waste per person — a 4-person home halves each member's home/waste lines |
| `country` | 17 countries: india, china, us, germany, japan, uk, france, canada, brazil, australia, russia, south_korea, saudi_arabia, indonesia, uae, singapore, netherlands | weights: india 0.35, china/us 0.10 each, germany/japan/uk 0.05 each, 0.03-0.04 others | **grid factor per country (Ember 2025, fetched): saudi 0.692, indonesia 0.680, india 0.670, australia 0.525, china 0.525, singapore 0.497, japan 0.477, uae 0.468, russia 0.450, south_korea 0.417, us 0.384, germany 0.330, netherlands 0.254, uk 0.217, canada 0.191, brazil 0.110, france 0.041 kg/kWh** |
| `heating_energy_source` | electricity/natural gas/wood | 55/35/10% | electric: +60–140 kWh on grid line; gas: 20 kg; wood: 8 kg |
| `how_long_tv_pc_daily_hour` | 0–24, step 0.5 | normal(4.2, 2.4) | × 75 W × 30 d × grid → ≈1.24 kg/h/day (avg grid) |
| `how_long_internet_daily_hour` | 0–24, step 0.5 | normal(5.0, 2.6) | × 40 W-equiv × 30 d × grid → ≈0.66 kg/h/day |
| `diet` | vegan/vegetarian/pescatarian/omnivore | 10/32/8/50% | bands 90/115/120/215 kg (Scarborough 2023) |
| `monthly_grocery_bill` | local currency 0–5,000 | lognormal per country (per-country median lognormal table) | × spend factor per country (price-level calibrated so the median food basket lands ≈120–180 kg/month everywhere) |
| `how_many_new_clothes_monthly` | 0–50 | lognormal(0.4, 0.9) | × 18 kg/item (EEA) |
| `waste_bag_size` | small/medium/large/extra-large | 25/40/25/10% | mass 5/10/20/30 kg per bag |
| `waste_bag_weekly_count` | 0–20 | lognormal(0.9, 0.6) | × 4.3 weeks × mass × 0.65 kg/kg (IPCC Vol.5) − recycling credit |
| `recycling` | list: paper/plastic/metal/glass/none | 30% none | credit −4/−6/−12/−2 kg per material (avoided virgin production) |
| `cooking_with` | list: stove/oven/microwave/grill/airfryer/none | 4% none | appliance kWh × grid; +5 kg partial LPG when stove |
| `carbon_emission_kgco2e_month` | **target** | — | sum of all contributions × lognormal(1, 0.05) noise |

Base household electricity load (lights, fridge, fans): uniform 40–90 kWh;
electric-heating households add uniform 60–140 kWh (geysers/winter
heaters) — both on the grid line, so `region` scales them.

---

## Target statistics

- Range: **157 – 1,871 kg/month**, mean **614** (LPG combustion corrected to ~3.0 kgCO₂e/kg — IPCC stoichiometry; the 1.5 previously used was the per-litre value)
- household_size effect verified: means fall 666.6 (1 person) → ~520–545 (5–10 people), corr −0.206
- 17-country coverage; country means correlate with grid factors
  (positive relationship, modulated by per-country sampling of other
  answers) — the model must learn the country-grid relationship.
- Scale note: v2 targets are ≈3× smaller than v1 (Kaggle mean 2,269) —
  MAE/RMSE are **not comparable across versions**; compare R², CV, and
  feature-importance structure instead.
- Sanity signals (verified on the generated file):
  - region effect live: mixed 781.9 vs renewable_heavy 700.2 (grid factor in target)
  - diet ordering: vegan 685 < vegetarian 702 < pescatarian 716 < omnivore 814
  - coefficient recovery at N=200k: grocery 0.110 (gen 0.11), clothing
    17.89 (gen 18.0), TV 1.227 (gen ≈1.24), internet 0.688 (gen ≈0.66) —
    the model recovers the generating factors.
  - **No artifact columns** (sex/body_type/shower/social/efficiency/age do not exist).

## Freeze / governance

- v1 pair stays frozen (DATASET_FREEZE.md) as the reproducibility anchor.
- v2 is the owner-approved new dataset version per the freeze doc's
  change-control rule; review boundary and retraining record to follow in
  DATASET_V2_COMPARISON.md.
- Still synthetic: targets are factor-formula estimates, not measured
  emissions — the app disclaimer remains required.

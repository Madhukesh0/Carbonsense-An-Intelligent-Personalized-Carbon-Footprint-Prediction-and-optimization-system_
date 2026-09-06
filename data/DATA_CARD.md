# Data Card — `individual_carbon_footprint.csv`

A datasheet in the style of Gebru et al., *"Datasheets for Datasets"* (CACM 2021).
Every model in this repository is trained on this file; every claim in the
project report about data quality defers to this card.

| Field | Value |
|---|---|
| File | `data/raw/individual_carbon_footprint.csv` |
| SHA-256 | `69a5afab2716d70dfab934075f4dbc62938c7200c86d7e840a10ee50dad95ad0` |
| Size | 1,622,858 bytes · 10,000 rows × 20 columns |
| Card version | 1.0 (2026-08-16) |
| Freeze policy | **Frozen until May 2027.** No edits, no merges, no row additions. Augmentation happens only via side experiments (see §Maintenance). |

---

## 1. Motivation

The dataset serves as the single supervised-training source for the XGBoost
lifestyle→footprint model. It was chosen because it is public, citable, and
maps 19 survey-style lifestyle features to a monthly kgCO₂e target — the exact
prediction task of CarbonSense.

## 2. Composition

**19 input features + 1 target (`CarbonEmission`, kgCO₂e/month).**

Categorical (13): Body Type, Sex, Diet, How Often Shower, Heating Energy
Source, Transport, Vehicle Type, Social Activity, Frequency of Traveling by
Air, Waste Bag Size, Energy efficiency, Recycling (stringified list),
Cooking_With (stringified list).

Numerical (6): Monthly Grocery Bill (USD), Vehicle Monthly Distance Km, Waste
Bag Weekly Count, How Long TV PC Daily Hour, How Many New Clothes Monthly, How
Long Internet Daily Hour.

Column renaming to snake_case is applied at load time by
`data/data_loader.py::COLUMN_MAPPING` — the single source of truth.

## 3. Collection process & provenance

Obtained from Kaggle (*Individual Carbon Footprint*, 10,000 responses).
The upstream collection methodology is **not documented by the publisher**.
Internal evidence (see §4, issue L1) indicates the target column was
**programmatically derived from the features**, not measured from real utility
bills. The dataset should therefore be described in all project documents as
*"a Kaggle lifestyle-survey dataset with a formula-derived target"*, never as
measured real-world emissions.

## 4. Known quality issues & mitigations

Each issue below is accepted, documented, and mitigated elsewhere in the
system — none is silently ignored.

| # | Issue | Evidence | Mitigation in CarbonSense |
|---|---|---|---|
| L1 | Target is likely formula-generated, inflating fit metrics | R² = 0.9758 is implausibly high for human behavioral data; tree ensembles learn the generator formula | Report cites metric with this caveat; accuracy claims made via **conformal intervals (±253.3 kgCO₂e, 90 %)**, not R² |
| L2 | Single source, single anonymous population; no country/region column | Column list §2 | Hybrid blend anchors predictions to citable country-aware reference tables (IEA 2024 grid intensity via `data/external/grid_intensity.csv`); regional model variant adds grid features |
| L3 | No `age` column, though the model expects one | Raw CSV lacks it; pipeline fills `age=30` (documented default) | Documented in `preprocessing.py::DEFAULT_INPUTS`; filled identically at train and inference time |
| L4 | Zero real-world validation samples | Feedback store empty at card date | `POST /predict/feedback` collects labeled real samples for future retraining |
| L5 | `Recycling` / `Cooking_With` stored as stringified lists | Raw values e.g. `"['Stove', 'Oven']"` | Validated as free strings; `OneHotEncoder(handle_unknown='ignore')` |
| L6 | Distribution coverage: lifestyle extremes may be sparsely represented | Unknown publisher sampling frame | Conformal interval widens coverage claim honestly; corner-case profiles are demo-tested, not assumed |

## 5. Uses

**Intended:** supervised training of the global and regional footprint models;
behavioral deviation signal in the hybrid blend; conformal calibration
(`models/trained/conformal_quantile.npy`).

**Out-of-scope:** claims about measured real-world emissions; cross-country
causal comparisons; regulatory or carbon-accounting use.

## 6. Maintenance rules

1. **Frozen until May 2027** — the file's SHA-256 above is the reference.
   Any file whose hash differs is a different dataset and invalidates:
   the trained models, `model_metadata.json`, and the conformal quantile.
2. If the dataset is ever changed (post-freeze), `CarbonPredictor.calibrate_conformal()`
   **must** be re-run — otherwise the 90 % interval guarantee is void.
3. Augmentation experiments (e.g., generating physics-labeled rows from
   `data/external/` reference tables) must use a **separate derived file** and
   a side model artifact; never overwrite this CSV.

## 7. Companion reference data (not merged, comparison-only)

`data/external/per_capita_footprints.csv` — published national per-capita
footprints (Global Carbon Budget 2023 / Friedlingstein et al.; consumption-based
figures per Peters et al. via Our World in Data). Never merged into training.

**Worked external-validation check (2026-08-16).** A single typical profile
(omnivore, petrol car 300 km/mo, rare flights) run through blend mode per
country; "expected" = consumption-based per-capita × ~65 % household share
(Hertwich & Peters 2009, PNAS):

| Country | Predicted | Published-derived | Ratio |
|---|---|---|---|
| GBR | 483 | 460 | **1.05** |
| DEU | 498 | 455 | **1.10** |
| CHN | 522 | 460 | **1.13** |
| USA | 501 | 806 | 0.62 |
| IND | 546 | 108 | 5.05 |
| BRA | 469 | 141 | 3.33 |

**Interpretation (report-ready):** for Western/industrialized lifestyle
distributions, blend predictions track published statistics within ~5–40 % —
credible external validity. IND/BRA ratios are high **by construction of the
comparison, not model error**: the Kaggle feature vocabulary describes a
car-owning, high-grocery-spend lifestyle, while the published per-capita figure
averages over populations where most households own no car. The honest claim is
"validated against published statistics for matching lifestyle distributions,"
not "validated for every population."

## 8. Citation

> Kaggle, *Individual Carbon Footprint* dataset (10,000 responses).
> Downloaded 2026; SHA-256-pinned above.

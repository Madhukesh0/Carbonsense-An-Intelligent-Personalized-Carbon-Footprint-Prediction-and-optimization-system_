# Country-wise emission factors — all 17 dataset countries

Country-specific factors for every country in `clean_dataset_v2.csv`
(v2.3), matched to the frontend inputs, with source links. Grid factors
fetched live from Ember/OWID (data year 2025; SAU/IDN/ARE 2024 as latest
published) on 2026-09-03. The dataset's `country` column selects the grid
factor; `region` (mixed/renewable-heavy) applies the within-country
modifier; `household_size` divides shared home energy and waste per
person.

---

## 1. Grid electricity factor by country (the anchor per country)

| Country | Mixed-grid factor (kgCO₂e/kWh) | Renewable-heavy proxy | Data year | Source link | Status |
|---|---|---|---|---|---|
| Saudi Arabia | 0.69195 | 0.16 | 2024 | https://ourworldindata.org/grapher/carbon-intensity-electricity.csv | Fetched |
| Indonesia | 0.68025 | 0.15 | 2024 | same | Fetched |
| **India** | **0.67013** | **0.15** | **2025** | https://cea.nic.in/cdm-co2-baseline-database/?lang=en (official) · https://ourworldindata.org/grapher/carbon-intensity-electricity.csv?country=~IND (CSV) | Fetched ✅ |
| Australia | 0.52518 | 0.12 | 2025 | same CSV | Fetched |
| China | 0.52534 | 0.12 | 2025 | same CSV | Fetched |
| Singapore | 0.49709 | 0.11 | 2025 | same CSV | Fetched |
| Japan | 0.47726 | 0.11 | 2025 | same CSV | Fetched |
| UAE | 0.46751 | 0.10 | 2024 | same CSV | Fetched |
| Russia | 0.44973 | 0.10 | 2025 | same CSV | Fetched |
| South Korea | 0.41706 | 0.09 | 2025 | same CSV | Fetched |
| United States | 0.38440 | 0.10 | 2025 | same CSV · cross-check EPA https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator | Fetched |
| Germany | 0.32965 | 0.08 | 2025 | same CSV | Fetched |
| Netherlands | 0.25356 | 0.06 | 2025 | same CSV | Fetched |
| United Kingdom | 0.21741 | 0.05 | 2025 | same CSV · DESNZ 2026 official: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026 (app's deployed 0.13096 is the DESNZ factor — see note below) | Fetched |
| Canada | 0.19072 | 0.04 | 2025 | same CSV | Fetched |
| Brazil | 0.10995 | 0.03 | 2025 | same CSV | Fetched |
| France | 0.04144 | 0.02 | 2025 | same CSV (nuclear-dominant grid) | Fetched |

**Note on the UK:** the dataset's grid factors come from the Ember/OWID
dataset (generation-based, 2025) while the app's deployed `baseline.py`
uses DESNZ 2026 (0.13096 — consumption/reporting basis). Both are citable;
the difference is methodology (generation vs reporting convention), not
error. State this if asked.

## 2. Fuel & travel factors — country-independent (chemistry / international)

Same factors for all 17 countries:

| Frontend input | Factor | Source link |
|---|---|---|
| Vehicle fuel = petrol | 2.31 kgCO₂e/L ÷ real km/L | https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf |
| Vehicle fuel = diesel | 2.68 kgCO₂e/L ÷ real km/L | same |
| Vehicle fuel = electric | **18 kWh/100km × the country's grid factor above** (this is where country matters!) | grid links in §1 |
| Flights | 246 g/pkm domestic · 154 g/pkm short-haul (international dataset) | https://ourworldindata.org/travel-carbon-footprint |
| Aviation non-CO₂ | ×2–3 | https://doi.org/10.1016/j.atmosenv.2020.117834 |
| Public transport | 0.02–0.10 kg/pkm by country bus/metro mix | consumption.md §6.4 / travel.md |

## 3. Food — diet bands international, spend factor per currency

| Frontend input | Factor | Source link |
|---|---|---|
| Diet bands (vegan→omnivore) | 90/115/120/215 kg/month | Scarborough 2023, BMJ: https://www.bmj.com/content/381/bmj-2022-097913 · per-kg: https://ourworldindata.org/food-choice-vs-eating-local |
| Grocery spend (per country currency) | India ₹0.11 · US $0.36 · UK £0.44 · China ¥0.14 · Japan ¥0.50 · Germany €0.40 · France €0.42 · Canada C$0.34 · Brazil R$0.28 · Australia A$0.33 · Russia ₽0.20 · South Korea ₩0.42 · Saudi ﷼0.18 · Indonesia Rp0.012 · UAE د.إ0.13 · Singapore S$0.24 · Netherlands €0.40 kg/unit | price-level calibrated conventions (median food basket ≈120–180 kg/month in every country); currency conversions per-app display |

## 4. Consumption & waste — country-independent conventions

| Frontend input | Factor | Source link |
|---|---|---|
| New clothing | 18 kg/item (EEA ≈17 kg/kg) | https://www.eea.europa.eu/en/topics/in-depth/textiles |
| Waste bags | bag mass 5/10/20/30 kg × **0.65 kg/kg landfilled** | https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol5.html · https://en.wikipedia.org/wiki/Landfill_gas |
| Recycling credits | paper −4 · plastic −6 · metal −12 · glass −2 kg/month | https://en.wikipedia.org/wiki/Recycling (Al −95%, plastics −70%, steel −60%, paper −40%) |
| Cooking appliances | appliance kWh × **country grid factor** + LPG 1.5 kg/kg where stove | §1 grid + IPCC |

## 5. household_size — divides shared lines per person (all countries)

Home-energy kWh and household waste are divided by household size
(geometric distribution, 1–10). The mechanism is country-independent;
typical household sizes differ by country (documented as a v3 refinement:
country-specific household-size distributions).

## 6. How a row computes (recap)

```
target = transport(km × fuel ÷ efficiency, or transit, by country-agnostic chemistry)
        + (screens + base + heating kWh) × GRID_BY_COUNTRY[country][region] ÷ household_size
        + heating direct (gas/wood)
        + diet band + grocery × GROCERY_FACTOR_BY_COUNTRY[country]
        + waste(bags × mass × 0.65 ÷ household_size) − recycling credits
        + clothing × 18 + cooking(appliance kWh × country grid + LPG)
        + flight band
        × lognormal(1, 0.05) noise
```

Dataset implementation: `scripts/generate_dataset_v2.py` (seed 42,
deterministic). Master per-question table: `citations/factor-sheet.md`.

## 7. Update rule

When Ember publishes 2026 data or CEA/DESNZ release new editions: update
§1 grid factors here, the `GRID_BY_COUNTRY` table in
`scripts/generate_dataset_v2.py`, regenerate the dataset, and retrain —
one commit, version bump.

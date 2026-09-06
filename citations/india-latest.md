# India — latest available data (2025/2026 refresh)

New companion file to `citations/india-values.md`. This file carries the
**newest published numbers** for the India-specific factors behind the 14
carbon-emitter questions, fetched on 2026-09-03. Where a newer figure
exists, it supersedes the value in india-values.md; the older file is kept
as the audit trail (viva answer: "we tracked the factor revisions").

Headline change vs the earlier file: **India's grid carbon intensity fell
to 670 gCO₂e/kWh in 2025** (from 705–727 in 2021–24) as coal's share
dropped below 71% for the first time — the renewable transition is now
visible in the data, which strengthens the case for the grid-mix question.

---

## 1. Grid electricity — newest national figures (fetched live, Ember via OWID)

CSV endpoint: https://ourworldindata.org/grapher/carbon-intensity-electricity.csv?country=~IND
(dataset "Carbon intensity of electricity generation", Ember + Energy
Institute, major processing by Our World in Data; page last updated
2026-06-30, data through 2025)

| Year | Carbon intensity (gCO₂e/kWh) | Coal share of generation |
|---|---|---|
| 2021 | 715.3 | — |
| 2022 | 705.8 | 74.5% |
| 2023 | 713.4 | 75.4% |
| 2024 | 705.4 | 74.5% |
| **2025 (latest)** | **670.1** | **70.8%** |

2025 generation mix (same CSV family, share-elec-by-source):
coal 70.8% · gas 2.3% · hydro 8.5% · wind+solar ≈ 9.4+5.0% · nuclear 2.6%
· bioenergy 1.1% · other 4.995%.

**Effect on the app:** every electric line in the India equivalents drops
by ≈5% — e.g. TV/PC 4h/day: 9 kWh × 0.67013 ≈ **6.0 kg/month** (was 6.4);
EV per km: 18 kWh/100km × 0.67013 ≈ **0.121 kg/km** (was 0.128).

**CEA cross-reference:** the official government source (CO₂ Baseline
Database **v21.0**, uploaded Dec 2025, https://cea.nic.in/cdm-co2-baseline-database/?lang=en)
is the fiscal-year equivalent (its FY 2024-25 weighted average ≈ 0.71
kg/kWh, matching the fetched 2024 figure of 705.4 g in calendar-year
terms). Use CEA for official/fiscal reporting, Ember/OWID for the newest
calendar year.

## 2. Travel factors — unchanged (chemistry + international aviation)

| Question | Latest value | Source | Status |
|---|---|---|---|
| Petrol combustion | 2.31 kgCO₂e/L → ≈0.115 kg/km @ ~20 km/L | IPCC 2006 Vol.2 Ch.3: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf | Convention |
| Diesel | 2.68 kgCO₂e/L → ≈0.149 kg/km @ ~18 km/L | same | Convention |
| EV @ 2025 grid (18 kWh/100km) | **≈0.121 kg/km** | Ember/OWID grid above | Derived from fetched |
| CNG car (~30 km/kg) | ≈0.06–0.07 kg/km | IPCC chemistry | Derived |
| Flights: domestic 246 g/pkm · short-haul 154 g/pkm | unchanged (global aviation dataset) | OWID: https://ourworldindata.org/travel-carbon-footprint | Fetched earlier |
| Aviation non-CO₂ multiplier | ≈2–3× CO₂-only | Lee et al. 2021: https://doi.org/10.1016/j.atmosenv.2020.117834 | Cited |

## 3. Home energy — device and fuel factors unchanged; grid down 5%

| Question | Latest value | Source | Status |
|---|---|---|---|
| TV/PC 4 h/day | ≈**6.0 kg/month** (was 6.4) | Ember grid × 9 kWh | Derived from fetched |
| Internet 4 h/day | ≈**8.0 kg/month** (was 8.5) | same + IEA data-centre trend https://www.iea.org/reports/electricity-2024/executive-summary | Derived from fetched |
| Electric heating 100 kWh | ≈**67.0 kg** (was 71.0) | same | Derived from fetched |
| Gas heating 100 kWh | ≈**20 kg** (≈0.20 kg/kWh net CV) | DESNZ 2025 xlsx: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025 | Convention |

IEA context (from the fetched executive summary): global data-centre +
AI + crypto demand ≈ Japan's electricity consumption; India-specific AC
growth is named by the IEA as a major demand driver — reinforcing the v2
"AC hours" question.

## 4. Food — factors unchanged; India context as fetched

| Question | Latest value | Source | Status |
|---|---|---|---|
| Beef / poultry / pork / peas | 60 / 6 / 7 / 1 kgCO₂e/kg | OWID: https://ourworldindata.org/food-choice-vs-eating-local | Fetched |
| Diet bands | vegan 2.9 → high-meat 7.2 kg/day | Scarborough 2023, BMJ 381:e097913: https://www.bmj.com/content/381/bmj-2022-097913 | Cited |
| India vegetarian share | 20–39% | https://en.wikipedia.org/wiki/Vegetarianism_in_India | Fetched |
| Grocery spend proxy | 0.11 kg/₹ (app) | baseline.py | App-declared |

## 5. Consumption & waste — unchanged conventions

| Question | Latest value | Source | Status |
|---|---|---|---|
| Textiles | ≈17 kgCO₂e/kg (EEA 2020 data — still the latest published) | https://www.eea.europa.eu/en/topics/in-depth/textiles | Fetched |
| Landfilled waste | ≈0.5–0.8 kgCO₂e/kg; gas 40–60% CH₄ | IPCC Vol.5: https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol5.html · https://en.wikipedia.org/wiki/Landfill_gas | Convention / Fetched |
| Recycling credits | Al 95% / plastics 70% / steel 60% / paper 40% energy saved | https://en.wikipedia.org/wiki/Recycling | Fetched |
| LPG cooking | ≈21 kgCO₂e per 14.2 kg cylinder | IPCC chemistry | Derived |

## 6. What changed vs india-values.md (one-page diff)

| Item | india-values.md | this file (latest) | Change |
|---|---|---|---|
| Grid intensity | 0.710 kg/kWh (CEA FY 2024-25) | **0.670 kg/kWh (Ember 2025)** | **−5.6%** |
| Coal share | ~73% | **70.8%** | −2.2 pts |
| EV per km | 0.128 kg | **0.121 kg** | −5.6% |
| TV/PC month | 6.4 kg | **6.0 kg** | −5.6% |
| All fuel-chemistry, aviation, food, waste, clothing factors | unchanged | unchanged | no new editions |

## 7. Links used in this file (all fetched 2026-09-03 unless noted)

1. https://ourworldindata.org/grapher/carbon-intensity-electricity.csv?country=~IND — India grid intensity CSV (Ember/OWID, data through 2025)
2. https://ourworldindata.org/grapher/share-electricity-coal.csv?country=~IND — coal share CSV
3. https://ourworldindata.org/grapher/share-elec-by-source.csv?country=~IND — 2025 generation mix
4. https://cea.nic.in/cdm-co2-baseline-database/?lang=en — CEA database index (v21.0, Dec 2025)
5. https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025 — DESNZ 2025 xlsx index
6. https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf — IPCC fuel chemistry
7. https://ourworldindata.org/travel-carbon-footprint — aviation pkm
8. https://www.eea.europa.eu/en/topics/in-depth/textiles — textiles
9. https://en.wikipedia.org/wiki/Landfill_gas · https://en.wikipedia.org/wiki/Recycling — waste conventions
10. https://en.wikipedia.org/wiki/Vegetarianism_in_India — diet context
11. https://doi.org/10.1016/j.atmosenv.2020.117834 — aviation non-CO₂

**Status legend:** Fetched = verified live 2026-09-03 · Derived =
computed from fetched values · Convention = standard published estimate ·
Cited = peer-reviewed, verify decimals in the paper.

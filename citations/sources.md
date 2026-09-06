# Source link index — every URL used in the citations folder

Companion index for travel.md, home.md, food.md, consumption.md, and
india-equivalents.md. Fetch status is recorded per link (verified live on
2026-09-03 vs cited-but-not-fetched). Values in the section files should be
quoted together with the link on this page.

---

## Government / official statistics

| # | Source | URL | Used for | Fetched |
|---|---|---|---|---|
| 1 | DESNZ — GHG conversion factors 2026 (publication page; factor values live in the downloadable xlsx) | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026 | UK grid electricity 0.13096 kg/kWh; car per-km factors; local bus 0.10151 kg/pkm (as encoded in backend/app/services/baseline.py) | ✅ landing page (values read from the repo's own FACTOR_SET which cites this release) |
| 2 | DESNZ — conversion factors 2025 (same structure; use for edition-exact gas/biomass decimals) | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025 | natural gas ≈0.20 kg/kWh, wood ≈0.06–0.09 kg/kWh, waste-disposal worksheet factors | ✅ landing page — decimals flagged as to-verify in xlsx |
| 3 | US EPA — Greenhouse gas emissions from a typical passenger vehicle | https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle | 400 g CO₂/mile; 4.6 t CO₂/yr (22.2 mpg, 11,500 mi) | ✅ |
| 4 | CEA — CO₂ Baseline Database for the Indian Power Sector (index page, v1.0–v21.0) | https://cea.nic.in/cdm-co2-baseline-database/?lang=en | India grid factor source database | ✅ index (v21.0 files Dec 2025) |
| 5 | Electricity sector in India — CEA FY-wise grid factors table | https://en.wikipedia.org/wiki/Electricity_sector_in_India | India grid 0.710 kg CO₂/kWh FY 2024-25; FY22–25 table; 0.477 FY29-30 projection; ~73% coal | ✅ |
| 6 | Vegetarianism in India — survey compendium | https://en.wikipedia.org/wiki/Vegetarianism_in_India | India vegetarian share 20–39% (Pew 2021: 39%; GoI survey 28–29%; CNN-IBN 31%; EPW 2018 ~20%) | ✅ |
| 7 | Our World in Data — travel carbon footprint (UK Gov data) | https://ourworldindata.org/travel-carbon-footprint | domestic flight 246 g/pkm; short-haul 154 g/pkm; national rail 35 g/pkm; Eurostar 4 g/pkm; petrol car 170 g/pkm; cycling 16–50 g/km | ✅ |
| 8 | Our World in Data — food choice vs eating local | https://ourworldindata.org/food-choice-vs-eating-local | beef 60 kg/kg; lamb & cheese >20; pork 7; poultry 6; peas 1; avocados ~2.5 | ✅ |
| 9 | Our World in Data — food methane page | https://ourworldindata.org/carbon-footprint-food-methane | beef (beef herd) 100 kg/kg total, 51 excl-methane, 36 average excl-methane; beef 5× tofu / 10× beans / 20× peas per protein | ✅ |
| 10 | Our World in Data — carbon opportunity costs of food | https://ourworldindata.org/carbon-opportunity-costs-food | food system 13.7 Gt CO₂e/yr = 26% of global; vegan transition potential | ✅ |
| 11 | US EPA — passenger vehicle page (duplicate guard for #3) | https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle | cross-check of #3 | ✅ |

## Energy systems / aviation

| # | Source | URL | Used for | Fetched |
|---|---|---|---|---|
| 12 | IEA — Electricity 2024 report | https://www.iea.org/reports/electricity-2024/executive-summary | data centres 460 TWh (2022) → possibly >1,000 TWh (2026); AI+crypto+DC ≈ Japan's consumption | ✅ |
| 13 | Lee, D.S. et al. (2021), Atmospheric Environment — aviation forcing | https://doi.org/10.1016/j.atmosenv.2020.117834 | aviation non-CO₂ multiplier ≈ 2–3× CO₂-only (contrails + NOₓ) | 📄 cited (paywalled) |

## Wikipedia references (fetched, for mechanisms & savings tables)

| # | Source | URL | Used for | Fetched |
|---|---|---|---|---|
| 14 | Recycling | https://en.wikipedia.org/wiki/Recycling | energy savings vs virgin: Al 95%, plastics 70%, steel 60%, paper 40%, cardboard 24%, glass 5–30% (EPA/EIA-cited) | ✅ |
| 15 | Landfill gas | https://en.wikipedia.org/wiki/Landfill_gas | landfill gas 40–60% CH₄; GWP 27 (GHG Protocol); gen. starts ~6 months, peaks ~20 yrs; 3rd-largest US CH₄ source | ✅ |
| 16 | Exhaust gas | https://en.wikipedia.org/wiki/Exhaust_gas | US car 415 g/mi (2000, EPA); EU new-car 145.6 g/km (2010) — context only | ✅ |

## Industry / agency reports

| # | Source | URL | Used for | Fetched |
|---|---|---|---|---|
| 17 | EEA — Textiles topic page | https://www.eea.europa.eu/en/topics/in-depth/textiles | EU textiles ≈270 kg CO₂e/person (2020) at ~16 kg consumed → ~17 kg/kg derived; <1% recycled (EMF 2017) | ✅ |
| 18 | ICCT — real-world fuel consumption program | https://theicct.org/real-world-fuel-consumption/ | type-approval vs on-road gap ≈20–40% | 📄 cited (program page) |
| 19 | Quantis / Ellen MacArthur Foundation apparel LCA lineage | https://www.ellenmacarthurfoundation.org/a-new-textiles-economy | per-garment conventions (jeans ≈20–33 kg; ≈20 kg/kg apparel) | 📄 cited (report) |

## Country-wise factors (multi-country v2.3 dataset)

| # | Source | URL | Used for | Fetched |
|---|---|---|---|---|
| 23 | Ember/OWID carbon-intensity CSV (17 countries, data year 2025) | https://ourworldindata.org/grapher/carbon-intensity-electricity.csv | grid factors for all 17 dataset countries (see citations/country-factors.md §1) | ✅ |
| 24 | CEA CO₂ Baseline Database v21.0 index | https://cea.nic.in/cdm-co2-baseline-database/?lang=en | India official fiscal-year grid factor | ✅ index |

## App-internal factor sources (the deployed numbers)

| # | Source | Location | Values |
|---|---|---|---|
| 20 | FACTOR_SET (DESNZ 2026 UK reference) | backend/app/services/baseline.py | electricity 0.13096; petrol 0.16152; diesel 0.17265; hybrid 0.12961; LPG 0.19553; EV 0.02686 kg/km; bus 0.10151 kg/pkm; 220 kWh reference |
| 21 | SCREENING proxies (declared, not official factors) | backend/app/services/baseline.py | diet 95/130/175/240; waste 1.8/3.5/5.5/8 kg/bag; air 0/60/180/420; grocery 0.11; clothing 18 |
| 22 | Conformal interval (split-conformal, seed 42) | scripts/recalibrate_conformal.py; data/final_training/model_metadata.json | q̂ = 330.96 kg (90%), empirical coverage 91.7% |

## Honesty ledger — which numbers are verified vs hedged

- **Fetched and quoted from source:** EPA 400 g/mi · OWID travel figures ·
  OWID beef figures · EEA 270 kg textiles · IEA data-centre TWh · CEA
  India grid table · recycling savings table · landfill gas composition ·
  India vegetarian-share surveys.
- **Encoded in the app and attributed to DESNZ 2026 (values not
  re-fetched from the xlsx):** the FACTOR_SET decimals (0.13096, 0.16152,
  0.17265, 0.12961, 0.19553, 0.02686, 0.10151). These are the deployed
  contract; if you ever need edition-exact decimals for print, download
  the conversion-factors xlsx from link #1.
- **Hedged estimates (ranges, source family named):** natural gas
  ≈0.20 kg/kWh, wood 0.06–0.09, waste 0.5–0.8 kg/kg, LPG 1.5 kg/kg,
  petrol 2.31 / diesel 2.68 kg/L, per-garment 5–33 kg, streaming
  0.06 kWh/GB (Aslan 2018), device wattages, EV 18 kWh/100km,
  renewable-heavy proxy 0.15 kg/kWh.
- **Scarborough 2023 diet figures:** values as reproduced from the BMJ
  study's public coverage (BMJ blocked direct fetch); verify the decimals
  against BMJ 381:e097913 before quoting in print.

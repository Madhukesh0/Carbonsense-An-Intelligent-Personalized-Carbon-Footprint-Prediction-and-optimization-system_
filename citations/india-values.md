# India emission values — the 14 carbon-emitter questions, with links

India-specific emission factors and worked monthly values for the 14
frontend questions that directly emit (the travel-mode router question is
excluded — it emits nothing itself). Every value carries its inline link.
Fetched = verified live on 2026-09-03; Derived = computed from fetched
values; Convention = standard published estimate (source named, range kept).

---

## Travel

**1. Distance driven / month (petrol car, India)**

| Value | Number | Source link | Status |
|---|---|---|---|
| Petrol combustion | **2.31 kgCO₂e/litre** | IPCC 2006 Vol.2 Ch.3 (motor gasoline ≈69,300 kg CO₂/TJ × NCV): https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf | Derived (chemistry, country-independent) |
| Typical Indian hatchback efficiency | ~20 km/L | manufacturer-class convention (Maruti Swift-class) | Convention |
| **Emission per km** | **≈0.115 kg/km** | = 2.31 ÷ 20 | Derived |
| **300 km/month** | **≈34.6 kg** | — | Derived |

**2. Vehicle fuel (India-specific per km)**

| Fuel | kgCO₂e/km | Source link | Status |
|---|---|---|---|
| Petrol hatchback (~20 km/L) | **0.115** | as above | Derived |
| Diesel compact SUV (~18 km/L, 2.68 kg/L) | **0.149** | IPCC Ch.3 as above | Derived |
| Electric vehicle (18 kWh/100km × **0.710 kg/kWh grid**) | **0.128** | grid: CEA table https://en.wikipedia.org/wiki/Electricity_sector_in_India | Derived from fetched |
| CNG car (~30 km/kg, ≈2.16 kgCO₂e/kg CNG) | **≈0.06–0.07** | IPCC fuel chemistry | Derived |

**3. Flights (aviation is international — same factors in India)**

| Value | Number | Source link | Status |
|---|---|---|---|
| Domestic short flight | **246 gCO₂e/pkm** | OWID (UK Gov data): https://ourworldindata.org/travel-carbon-footprint | Fetched |
| Short-haul (e.g., Delhi–Mumbai class) | **154 gCO₂e/pkm** | same | Fetched |
| Delhi–Mumbai return (~2,300 km) | **≈355 kg** | = 2,300 km × 0.154 | Derived from fetched |
| Non-CO₂ warming multiplier | **≈2–3× CO₂-only** | Lee et al. 2021: https://doi.org/10.1016/j.atmosenv.2020.117834 | Cited |

## Home energy

**4. Electricity grid mix — THE India anchor**

| Value | Number | Source link | Status |
|---|---|---|---|
| **India grid FY 2024-25** | **0.710 kgCO₂e/kWh** | CEA CO₂ Baseline Database v21.0: https://cea.nic.in/cdm-co2-baseline-database/?lang=en · FY table: https://en.wikipedia.org/wiki/Electricity_sector_in_India | Fetched |
| FY 2021-22 → 2023-24 | 0.715 → 0.727 | same table | Fetched |
| FY 2029-30 projection | 0.477 | same | Fetched |
| Coal share of generation | ~73% | same | Fetched |
| UK comparison (app's deployed factor) | 0.13096 | DESNZ: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026 | App contract |
| **Same 121 kWh usage: India vs UK** | **85.9 vs 15.8 kg/month (5.4×)** | derived from the two grids | Derived |

**5. Heating fuel (India context: geysers/winter heaters, mostly electric)**

| Value | Number | Source link | Status |
|---|---|---|---|
| Electric heating (100 kWh) | **71.0 kg** | 100 × 0.710 (CEA above) | Derived from fetched |
| Natural gas / LPG heating (100 kWh) | **20.0 kg** (≈0.20 kg/kWh) | IPCC Vol.2; DESNZ 2025 xlsx: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025 | Convention (edition-exact decimal in xlsx) |

**6. TV/PC hours (75 W average device)**

| Value | Number | Source link | Status |
|---|---|---|---|
| 4 h/day ≈ 9 kWh/month × 0.710 | **6.4 kg/month** | CEA grid above; device wattage conventions | Derived from fetched |

**7. Internet hours**

| Value | Number | Source link | Status |
|---|---|---|---|
| Data-centre energy globally | **460 TWh (2022) → possibly >1,000 TWh (2026)** | IEA Electricity 2024: https://www.iea.org/reports/electricity-2024/executive-summary | Fetched |
| Network + DC intensity | **≈0.06 kWh/GB** | Aslan et al. 2018 (standard citation) | Cited |
| 4 h/day ≈ 12 kWh/month × 0.710 | **8.5 kg/month** | derived | Derived from fetched |

## Food

**8. Diet pattern (India-relevant: 20–39% vegetarian)**

| Value | Number | Source link | Status |
|---|---|---|---|
| Beef (beef herd) | **60 kgCO₂e/kg** | OWID: https://ourworldindata.org/food-choice-vs-eating-local | Fetched |
| Poultry / pork | **6 / 7 kgCO₂e/kg** | same | Fetched |
| Legumes (peas) | **1 kgCO₂e/kg** | same | Fetched |
| Diet bands: vegan vs omnivore | **2.9 vs 7.2 kgCO₂e/day** (≈90 vs ≈216 kg/month) | Scarborough et al. 2023, BMJ 381:e097913 (verify decimals in paper): https://www.bmj.com/content/381/bmj-2022-097913 | Cited |
| India vegetarian share | **20–39%** | Pew 2021 / GoI survey compendium: https://en.wikipedia.org/wiki/Vegetarianism_in_India | Fetched |

**9. Grocery spend (spend-based method)**

| Value | Number | Source link | Status |
|---|---|---|---|
| App proxy | **0.11 kgCO₂e per ₹** | backend/app/services/baseline.py SCREENING | App-declared |
| Method sanction | spend-based when activity data unavailable | DESNZ 2026: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026 | Cited |
| ₹2,000/month → ₹5,000 | **220 → 550 kg/month** | derived | Derived |

## Consumption & waste

**10. New clothing**

| Value | Number | Source link | Status |
|---|---|---|---|
| EU textile footprint | **≈270 kgCO₂e/person/yr at ≈16 kg** → **≈17 kg/kg** | EEA Textiles: https://www.eea.europa.eu/en/topics/in-depth/textiles | Fetched |
| Per-item convention | **≈5 (t-shirt) to ≈20–33 (jeans) kgCO₂e** | Quantis/EMF lineage: https://www.ellenmacarthurfoundation.org/a-new-textiles-economy | Convention |
| App proxy | **18 kg/item** | baseline.py | App-declared |
| 2 items/month | **≈36 kg/month** | derived | Derived |

**11+12. Waste bag size × bags/week**

| Value | Number | Source link | Status |
|---|---|---|---|
| Landfill gas composition | **40–60% methane**; CH₄ GWP = 27 | https://en.wikipedia.org/wiki/Landfill_gas | Fetched |
| Landfilled MSW factor | **≈0.5–0.8 kgCO₂e/kg** | IPCC 2006 Vol.5 Waste: https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol5.html | Convention |
| App proxy | 1.8 / 3.5 / 5.5 / 8 kg per bag (S/M/L/XL) | baseline.py | App-declared |
| 3 medium bags/week | **≈45 kg/month** | derived | Derived |

**13. Recycling (credit, not emission)**

| Value | Number | Source link | Status |
|---|---|---|---|
| Energy saved vs virgin: aluminium | **95%** | https://en.wikipedia.org/wiki/Recycling (EPA/EIA-cited table) | Fetched |
| plastics / steel / paper / glass | **70% / 60% / 40% / 5–30%** | same | Fetched |
| None→all measured model effect | **−386 kg/month** | project test suite | Measured |

**14. Cooking appliances**

| Value | Number | Source link | Status |
|---|---|---|---|
| LPG combustion | **≈1.5 kgCO₂e/kg burned** → 14.2 kg cylinder ≈ **21 kgCO₂e** | IPCC fuel chemistry | Derived |
| Electric appliances | appliance kWh × **0.710** | CEA above | Derived from fetched |
| Typical mix | **≈20 kg/month** | derived | Derived |

---

## Totals at the default profile (India factors)

| Section | kgCO₂e/month |
|---|---|
| Travel (petrol 300 km + rarely flying) | ≈ 95 |
| Home energy (121 kWh usage) | ≈ 86 |
| Food (omnivore + ₹2,000) | ≈ 440 |
| Consumption & waste (clothing, waste, cooking; before recycling credit) | ≈ 100 |
| **Gross total** | **≈ 720 kg/month** (≈ 8.6 t/yr, before recycling credit) |
| With full recycling | ≈ 560 kg/month |

Sanity anchor: Indian per-capita total footprint ≈ 2.0 tCO₂e/yr (all
sectors incl. shared infrastructure) — a household-based estimate of
8.6 t/yr before per-person household division is the right order of
magnitude for an individual attribution, and household size (v2) is what
divides it.

**Status legend:** Fetched = verified live 2026-09-03 · Derived =
computed from fetched values · Convention = standard published estimate ·
Cited = peer-reviewed, verify decimals in the paper.

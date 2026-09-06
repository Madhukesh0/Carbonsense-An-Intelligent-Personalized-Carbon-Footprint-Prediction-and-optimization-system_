# Travel carbon emission factors — citations & worked examples

Reference document for the travel section of the CarbonSense questionnaire.
Every number below is either encoded in `backend/app/services/baseline.py`
(DESNZ 2026 factor set, id `desnz-2026-uk-reference-v1`) or cross-verified
from the cited external source on 2026-09-03.

---

## 1. Car — emission per km by fuel

Source: **DESNZ 2026 GHG conversion factors**, Department for Energy Security
& Net Zero, gov.uk — the factor set encoded in `baseline.py`.

| Fuel | kgCO₂e/km | At 250 km/month | Per year (×12) |
|---|---|---|---|
| Petrol | 0.16152 | 40.4 kg | 485 kg |
| Diesel | 0.17265 | 43.2 kg | 518 kg |
| Hybrid | 0.12961 | 32.4 kg | 389 kg |
| LPG | 0.19553 | 48.9 kg | 587 kg |
| Electric (UK grid) | 0.02686 | 6.7 kg | 80 kg |

Cross-checks:

- **US EPA** — *Greenhouse gas emissions from a typical passenger vehicle*
  (epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle):
  "the average passenger vehicle emits about **400 grams of CO2 per mile**"
  (≈ 0.249 kg/km) and "**about 4.6 metric tons of CO2 per year**" (assumes
  22.2 mpg, 11,500 mi/yr). Higher than DESNZ petrol because it mixes the US
  fleet (SUVs/trucks) and real-world driving — consistent, not contradictory.
- **Our World in Data** (UK Gov data) — *Which form of transport has the
  smallest carbon footprint?* (ourworldindata.org/travel-carbon-footprint):
  **170 g CO₂/pkm for an average petrol car** — matches DESNZ petrol within
  rounding once occupancy is considered.

Caveat: factors are type-approval-derived; real-world fuel consumption runs
roughly **20–40% higher** than test figures (ICCT real-world studies). One
sentence in limitations covers this.

EV-grid nuance (strong viva point): the EV factor 0.02686 kg/km =
≈ 20.5 kWh/100km × UK grid factor 0.13096 kg/kWh. The same EV on India's
grid (~0.71 kg/kWh) would emit ≈ **0.15 kg/km — nearly petrol-level**. This
is why the questionnaire asks for the electricity grid mix.

---

## 2. Mode — public transport & active travel

| Mode | kgCO₂e/passenger-km | Source |
|---|---|---|
| Local bus | **0.10151** | DESNZ 2026, business-travel land (encoded in `baseline.py`) |
| National rail | **0.035** | UK Gov via Our World in Data (fetched) |
| Eurostar / international rail | **0.004** | Our World in Data (fetched) |
| Cycling | 0.016–0.050 | Our World in Data — not strictly zero: extra food calories, diet-dependent |
| Walking | ~0 | Our World in Data, negligible |

Same 250 km by different mode: car solo 40.4 kg → bus 25.4 kg → rail 8.8 kg
→ bicycle ~4–12 kg (food). One question, four different emission answers.

---

## 3. Flights — per flight, not per km

| Flight type | kgCO₂e/passenger-km | Worked example |
|---|---|---|
| Domestic (UK) | **0.246** | 500 km return ≈ 245 kg |
| Short-haul | **0.154** | London–Madrid return (~2,300 km) ≈ 355 kg |
| Long-haul | ~0.15 | London–New York return (~11,100 km) ≈ 1,600 kg economy |

Non-CO₂ multiplier: aviation's total warming effect exceeds its CO₂ alone
(contrails + NOₓ); effective multiplier ≈ **2–3× CO2-only**. Standard
citation: **Lee, D.S. et al. (2021), "The contribution of global aviation to
anthropogenic climate forcing", Atmospheric Environment**. One long-haul
return ≈ 3+ tonnes warming-equivalent — why the "very frequently" flight
option moves the model by ~1,239 kg.

---

## 4. Worked example — the app's travel profile

250 km/month petrol, rarely flying:

- Driving: 250 × 0.16152 = **40.4 kg/month** (~485 kg/year)
- Flights "rarely": declared screening value ≈ 60 kg/month
- Travel ≈ **100 kg of the ~957 kg total estimate**

The travel section is the most factor-exact part of the app because it uses
real activity data (km) rather than screening proxies.

---

## 5. Citation list

1. **DESNZ (2026).** *Greenhouse gas reporting: conversion factors 2026*,
   gov.uk — primary factor set (`baseline.py`, id `desnz-2026-uk-reference-v1`).
2. **US EPA.** *Greenhouse gas emissions from a typical passenger vehicle* —
   400 g CO₂/mile, 4.6 t/yr. (fetched 2026-09-03)
3. **Our World in Data / UK Gov.** *Which form of transport has the smallest
   carbon footprint?* — 246 g/pkm domestic flight, 154 g/pkm short-haul,
   35 g/pkm rail, 170 g/pkm petrol car. (fetched 2026-09-03)
4. **Lee, D.S. et al. (2021).** *The contribution of global aviation to
   anthropogenic climate forcing*, Atmospheric Environment — aviation
   non-CO₂ effects (≈2–3× CO2-only).
5. **ICCT.** Real-world fuel-consumption studies — type-approval vs on-road
   gap (~20–40%).

General caveat: factors are UK/EU-flavoured — exact for the DESNZ reference
case, approximate elsewhere. The app's grid-mix question and baseline
assumptions disclose this boundary.

---

## 6. India-specific factors (project author is based in India)

### 6.1 Grid electricity — the anchor factor (verified live)

**India average grid emission factor ≈ 0.71 kgCO₂e/kWh** (FY 2024-25).
Source: **CEA (Central Electricity Authority), *CO₂ Baseline Database for
the Indian Power Sector*** — weighted-average emission intensity of
electricity generated, as tabulated in *Electricity sector in India*
(en.wikipedia.org/wiki/Electricity_sector_in_India, fetched 2026-09-03):

| Fiscal year | Generation (Mt CO₂) | Factor (kg CO₂/kWh) |
|---|---|---|
| 2021-22 | 1,002 | 0.715 |
| 2022-23 | 1,108 | 0.716 |
| 2023-24 | 1,203 | 0.727 |
| **2024-25** | **1,234** | **0.710** |

For viva: CEA publishes this annually (v21.0 current, Dec 2025 files at
cea.nic.in/cdm-co2-baseline-database); the factor is the official basis for
India's carbon-market baselines. Compare: UK 0.13096 (DESNZ 2026) — India's
grid is ≈ **5.4× more carbon-intensive per kWh**.

### 6.2 Fuels — combustion chemistry (country-independent)

CO₂ per litre depends on fuel chemistry, not country, so these factors are
valid for India and globally (DEFRA/IPCC 2006 Tier-1 combustion values;
approximations commonly cited ≈2.31/2.68; derived from IPCC 2006 Vol.2
Ch.3 — https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf
— motor gasoline ≈69,300 kg CO₂/TJ, gas/diesel oil ≈74,100 kg CO₂/TJ ×
NCV; see citations/sources.md #19):

- **Petrol (motor gasoline): ≈ 2.31 kgCO₂e/litre**
- **Diesel: ≈ 2.68 kgCO₂e/litre**

Worked Indian examples (typical real-world efficiency):

| Vehicle | Efficiency | kgCO₂/km | 250 km/month |
|---|---|---|---|
| Petrol hatchback (Maruti Swift-class) | ~20 km/L | 0.115 | 28.9 kg |
| Petrol sedan / SUV (low 20s mpg) | ~12 km/L | 0.19 | 48.1 kg |
| Diesel compact SUV | ~18 km/L | 0.149 | 37.2 kg |
| CNG car (well-maintained) | ~30 km/kg | ≈ 0.06 (2.16 kg/kg CNG) | 15 kg |

Two ways to compute — both citable:

- **Per litre** (fuel-based, most accurate): litre × 2.31 (petrol)
- **Per km** (distance-based): km ÷ efficiency × 2.31

Cross-check vs the app's DESNZ per-km factors: DESNZ petrol 0.16152 kg/km
assumes ~14.3 km/L — a mid-size car, slightly thirstier than an Indian
hatchback. Same chemistry, different fleet mix. State this if asked why
numbers differ.

### 6.3 EV in India — the grid-mix question made concrete

EV consumption ≈ 15–20 kWh/100 km. On India's 0.71 kg/kWh grid:

- 18 kWh/100km × 0.71 = **≈ 0.128 kgCO₂/km** (~1.4× *better* than the petrol
  hatchback, not 6× as in the UK)
- Same EV on the UK grid (0.13096): **≈ 0.024 kgCO₂/km**

This single worked example justifies the "Electricity grid mix" question:
same vehicle, ~5× different emissions, decided entirely by the grid.

### 6.4 Public transport in India (per passenger-km, indicative)

Exact official per-passenger-km factors are less standardized in India than
the UK; the citable order-of-magnitude figures from peer-reviewed/agency
studies:

| Mode | gCO₂/passenger-km | Basis |
|---|---|---|
| Delhi Metro | ≈ 8–30 | Metro rail studies; runs on grid (0.71) with very high ridership |
| Indian Railways (electric) | ≈ 5–15 | Grid-powered, ~64,000 km electrified; net-zero-2030 target |
| Indian Railways (diesel) | ≈ 25–50 | Diesel traction, high occupancy |
| City bus (diesel/CNG) | ≈ 20–40 | CNG buses (Delhi) at low end; occupancy-dependent |
| Private car (petrol, 1–2 occupants) | ≈ 115–190 | Derived from 6.2 at realistic occupancy |

Conservative viva wording: *"India-specific per-passenger-km factors vary by
study and occupancy; the app therefore uses the versioned DESNZ local-bus
proxy (0.10151 kg/pkm) as its declared screening value, which sits at the
conservative end for Indian CNG buses and metro."*

### 6.5 What changes vs the app's current factors (summary)

| Travel question | App factor (DESNZ) | India-specific equivalent | Impact if swapped in |
|---|---|---|---|
| Vehicle fuel + distance (car) | 0.16152 (petrol), 0.17265 (diesel) kg/km | 0.115–0.19 petrol, ~0.15 diesel (via 2.31/2.68 kg/L ÷ real km/L) | Small for cars (chemistry same); matters via vehicle size |
| Vehicle fuel = electric | 0.02686 kg/km (UK grid) | ≈ 0.13 kg/km (0.71 grid) | **5× higher EV line — biggest correction** |
| Mode = public transport | 0.10151 kg/pkm (UK local bus) | ≈ 0.02–0.04 metro/rail, 0.02–0.04 CNG bus | App is conservative (over-counts) for Indian transit |
| Flights | DESNZ/OWID pkm factors | Same (aviation is international; domestic Indian routes match short-haul 0.154 g pkm) | No change needed |

Bottom line: fuel chemistry factors transfer directly; the grid factor and
transit factors are the India-specific corrections, and the grid-mix
question is exactly the hook where CEA 0.71 plugs in.

### 6.6 India citation list

1. **CEA (2025).** *CO₂ Baseline Database for the Indian Power Sector*,
   v21.0 — Central Electricity Authority, cea.nic.in (annual grid factor;
   FY 2024-25 ≈ 0.71 kgCO₂/kWh).
2. **MoEFCC.** *India: Third National Communication / GHG Inventory*,
   moef.gov.in — national inventory fuel factors (IPCC 2006 methodology).
3. **IPCC (2006).** *Guidelines for National GHG Inventories, Vol. 2 Energy*,
   Ch. 3 Mobile Combustion — Tier-1 fuel factors (motor gasoline ≈ 69,300
   kg CO₂/TJ; gas/diesel oil ≈ 74,100 kg CO₂/TJ; × NCV → 2.31/2.68 kg/L).
4. **DEFRA/DESNZ conversion factors** — per-litre fuel factors used widely
   for India too (combustion chemistry is country-independent).
5. **Our World in Data / UK Gov** — aviation pkm factors (valid for Indian
   domestic routes; same global aviation dataset).

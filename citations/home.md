# Home-energy carbon emission factors — citations & worked examples

Reference document for the home-energy section of the CarbonSense
questionnaire (grid mix, heating fuel, TV/PC hours, internet hours).
Companion to `citations/travel.md`. Grid factors were verified against
official sources on 2026-09-03; device/fuel figures are standard published
values with sources noted per section.

---

## 1. Grid mix — the multiplier for every electrical line

| Grid | kgCO₂e/kWh | Source | Status |
|---|---|---|---|
| UK (DESNZ 2026) | **0.13096** | gov.uk conversion factors (encoded in `baseline.py`) | app's reference set |
| India (CEA, FY 2024-25) | **0.710** | CEA CO₂ Baseline Database, via *Electricity sector in India* (fetched; FY table 0.715 / 0.716 / 0.727 / 0.710 for FY22–FY25) | verified live |
| CEA projection FY 2029-30 | 0.477 | same source (renewables build-out) | context |

Same 4h TV/PC + 4h internet on the two grids (see §3–4): ≈ **1.2 kg/month
on the UK grid vs ≈ 6.5 kg/month on India's grid** — same user, ~5.4×
difference, decided entirely by the grid-mix answer.

### 1.1 "But users can't know where their electricity comes from"

This is a fair challenge, and the defensible answer is built into the
question design:

1. **Default = national average.** Most users are on the average grid. In
   India that is ~73% coal and 0.71 kg/kWh (CEA) — so "Mixed grid" is the
   correct default for the large majority, and users don't need to research
   anything.
2. **The opt-in is self-evident.** Users who genuinely sit on the renewable
   side know it without research: they pay for a green tariff, or have
   rooftop solar, or live in a state with hydro-heavy supply. Those are the
   "Renewable-heavy" answers.
3. **It is a declared screening proxy, not a claim.** The form says the
   choice is recorded as context; the precise per-state grid factor is a v2
   refinement (CEA publishes state-level factors in the same database).

## 2. Heating fuel — the biggest home end use

| Fuel | Factor | Basis / source |
|---|---|---|
| Natural gas | **≈ 0.20 kgCO₂e/kWh** (net CV); ≈ 2.0 kg per m³ (≈ 11.3 kWh/m³) | DESNZ conversion factors, fuels worksheet — https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025 (≈0.20 stable across recent editions; edition-exact decimal in the xlsx — see citations/sources.md #2) |
| Wood logs | ≈ **0.06–0.09 kgCO₂e/kWh** | DESNZ biomass factors; non-fossil CO₂ treated as biogenic, processing/transport included |
| Electricity heating | **grid factor × usage** (0.13096 UK / 0.710 India) | §1 |
| None / district | varies | screening |

Worked example — heating a small home in winter (≈ 400 kWh/month thermal):
gas ≈ 80 kg vs electric-UK ≈ 52 kg vs electric-India ≈ 284 kg. The fuel
choice and the grid interact — exactly what the two questions capture.

India note: whole-home central heating is rare; the load that exists is
mostly **water heating (geysers)** and winter space heaters — both electric,
so the grid factor governs. Traditional biomass burning is captured by the
wood choice. The heating question stays meaningful in the Indian context
through these end uses.

## 3. TV / PC hours — device electricity

Typical nameplate/running draw (manufacturer specs, standard values):

| Device | Watts (running) |
|---|---|
| 50–55" LED TV | 50–100 W |
| Laptop | 20–50 W |
| Desktop + monitor | 100–250 W |
| Console (gaming) | 100–200 W |

Modelled at ≈ **75 W average** → 4 h/day ≈ 0.3 kWh/day ≈ **9 kWh/month**:

- UK grid: 9 × 0.13096 ≈ **1.2 kg/month**
- India grid: 9 × 0.710 ≈ **6.4 kg/month**

## 4. Internet hours — home equipment + network + data centres

Three electricity draws stack up: (a) your router/modem (6–10 W, always on),
(b) network transmission, (c) the data centre serving you.

- **Data centres consumed ≈ 460 TWh in 2022 and could exceed 1,000 TWh by
  2026** — IEA, *Electricity 2024* report (fetched; the combined data
  centre + AI + crypto demand is "roughly equivalent to the electricity
  consumption of Japan").
- Energy intensity of internet traffic ≈ **0.06 kWh/GB** (Aslan et al. 2018,
  *The unsustainability of popular video streaming* — the standard citation;
  newer studies put it lower, ~0.03–0.08).
- HD video ≈ 2–3 GB/hour → network + data centre ≈ 0.12–0.25 kWh per hour.

Worked example — 4 h/day of mixed use (browsing + ~1 h HD streaming):

- Home side: router ~8 W × 24 h + devices ≈ 0.25–0.4 kWh/day
- Network + data centre: ≈ 0.15–0.5 kWh/day
- Total ≈ **10–15 kWh/month** → UK ≈ **1.3–2.0 kg/month**; India ≈
  **7–11 kg/month**

So the two screen-time questions represent a real, grid-scaled load — small
next to heating and driving, but honest and mechanical.

---

## 5. Worked example — the app's home-energy profile

Grid "mixed", heating "electricity", TV 4 h/day, internet 4 h/day:

| Line | UK grid | India grid |
|---|---|---|
| Appliance + network electricity (§3–4) | ≈ 2.5–3.5 kg | ≈ 14–19 kg |
| Hot water / heating via electricity (small-home reference) | included in a real kWh figure in v2 | same |
| Section total (current model, reference 220 kWh month) | fixed 28.8 kg in baseline | fixed 156 kg if CEA swapped in |

Note the structural point: the current frozen baseline uses a fixed
220 kWh reference, so the grid-mix answer changes nothing today (by design,
disclosed). In dataset v2 the target formula will include
`electricity_kwh × grid_factor ÷ household_size`, which makes every answer
on this screen live.

## 6. Deliberately deferred to v2 (not vague — just not yet wired)

| Missing question | Why it matters | v2 treatment |
|---|---|---|
| Household size | Shared home energy ÷ occupants; can halve/double the section | `electricity × grid ÷ household` in the v2 target |
| Actual electricity kWh (or bill) | Replaces the fixed 220 kWh reference; makes the estimate personal | bill ÷ price × grid factor, or direct kWh field |
| Home size / type | ±20% on heating and cooling | categorical multiplier |
| AC / cooling hours | Often the #1 residential load in India | `hours × 1.2 kWh × grid factor` |

## 7. Citation list

1. **DESNZ (2026).** *GHG reporting: conversion factors 2026*, gov.uk —
   electricity 0.13096 kg/kWh (encoded in `baseline.py`); natural gas
   ≈ 0.20 kg/kWh net CV, biomass factors in the fuels worksheet.
2. **CEA (Central Electricity Authority, India).** *CO₂ Baseline Database
   for the Indian Power Sector* (v21.0, Dec 2025 files), cea.nic.in —
   India grid ≈ 0.710 kg CO₂/kWh FY 2024-25 (table fetched 2026-09-03 via
   *Electricity sector in India*).
3. **IEA (2024).** *Electricity 2024* report — data centres ≈ 460 TWh
   (2022) → possibly >1,000 TWh (2026). (fetched 2026-09-03)
4. **Aslan, J. et al. (2018).** *The unsustainability of popular video
   streaming: a case study of Netflix.* — ≈ 0.06 kWh/GB internet energy
   intensity (standard citation; newer estimates 0.03–0.08).
5. **IPCC (2006).** *Guidelines for National GHG Inventories, Vol. 2* —
   natural gas 56.1 kg CO₂/TJ (basis for the ≈2.0 kg/m³ figure).
6. **Manufacturer specifications** — LED TV / laptop / desktop wattage
   ranges (§3) — typical running values, not a single measured device.

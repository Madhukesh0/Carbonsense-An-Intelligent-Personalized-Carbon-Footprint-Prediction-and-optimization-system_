# Worked example — one person's footprint computed line by line

A complete worked computation of an individual monthly carbon footprint
using the v2 factor formula, with every number traced to either a user
answer, a published (cited) factor, or a documented modeling convention.
This is the reference example for explaining how
`scripts/generate_dataset_v2.py` computes the target and how the app's
estimate maps answers to emissions.

---

## The profile (the 15 answers)

Public transport · no vehicle · 20 km/month · never flies · mixed grid ·
electric heating · 4 h TV/PC · 4 h internet · omnivore · ₹1,200 groceries ·
2 new clothing items · medium waste bags · 2 bags/week · recycles
paper + plastic · cooks with stove.

**Result: ≈ 572 kg CO₂e/month (≈ 6.9 tonnes/year)** — plausible band
±5%: 544–601 kg.

---

## The universal pattern

> **your ACTIVITY (form answer) × EMISSION FACTOR (published number) = kg CO₂e**

## Line 1 — Transport: 0.5 kg

| Number | What it is |
|---|---|
| 20 km | *Your answer* — distance travelled per month |
| × 1.15 | Multiplier — bus/metro riders cover ~15% more km than the direct route (detours, stops) |
| × 0.02 kg | *Factor* — Indian CNG bus/metro per **passenger**-km; one engine's emissions shared across 40+ passengers |

20 × 1.15 × 0.02 = **0.5 kg** — tiny, because shared mode + no flying are
the two lightest travel choices.

## Line 2 — Home energy: 126.9 kg

| Number | What it is |
|---|---|
| 13.8 kWh | *Answers* (4 h TV + 4 h internet) × device wattages (TV 75 W, internet 40 W) × 30 days |
| 65 kWh | Base load — fridge, lights, fans (typical 40–90 range) |
| 100 kWh | Electric heating — geyser + winter heater ("electricity" heating answer; 60–140 range) |
| = 179 kWh | The month's meter reading |
| × 0.710 kg/kWh | *Factor* — India grid carbon intensity (CEA FY 2024-25, verified; see citations/india-latest.md). A ~71% coal grid releases 0.710 kg per kWh |

179 × 0.710 = **126.9 kg**. On a renewable-heavy grid the same appliances
would cost ≈ 27 kg — the grid-mix question in one number.

## Line 3 — Food: 347.0 kg (the biggest line)

| Number | What it is |
|---|---|
| 215 kg | *Band* for omnivore — Scarborough et al. 2023 (BMJ 381:e097913): livestock need land, feed, and emit enteric methane (7.2 kg/day vs vegan 2.9) |
| ₹1,200 × 0.11 kg/₹ | *Answer* (grocery spend) × *spend-based factor* — more spending = more food + packaging + processing + transport (DESNZ-sanctioned method when activity data is unavailable) |

215 + 132 = **347 kg** — 61% of the total footprint is the plate.

## Line 4 — Waste: 45.9 kg

| Number | What it is |
|---|---|
| 2 bags/week | *Answer* — disposal frequency |
| 10 kg | Mass of one medium bag (size question sets mass: small 5 → XL 30) |
| × 4.3 | Weeks per month |
| × 0.65 kg/kg | *Factor* — landfilled waste decomposes into methane (40–60% of landfill gas, GWP 27) + CO₂ (IPCC Vol.5 convention) |
| = 55.9 gross | |
| − 10 credit | *Answer* (recycling paper + plastic) — avoided virgin production (aluminium −95% energy, plastics −70%): paper −4, plastic −6 |

55.9 − 10 = **45.9 kg** — the one line where an answer *reduces* the total.

## Line 5 — Clothing: 36.0 kg

| Number | What it is |
|---|---|
| 2 items | *Answer* — new purchases/month |
| × 18 kg/item | *Factor* — fiber, dyeing, stitching, shipping (EEA-derived ≈17 kg/kg textile, rounded up conservatively) |

2 × 18 = **36 kg** — clothing outweighs this person's entire transport
line by ~70×.

## Line 6 — Cooking: 16.0 kg

| Number | What it is |
|---|---|
| 12 kWh | Stove use — ~30 min/day at 1.2–2 kW |
| × 0.710 | Grid factor again (electric cooking) |
| + ≈5 kg LPG | "Stove" in India typically implies partial LPG cylinder use (1.5 kg CO₂ per kg burned) |

≈ **16 kg** — small but real.

## Line 7 — Flights: 0 kg

| Number | What it is |
|---|---|
| never | *Answer* — the "0" band. Scale: rarely 60 · often 180 · very frequently 420 kg/month; one long-haul return ≈ 1,600 kg |

---

## The three types of numbers

1. **User inputs (10)** — 20 km, 4 h, 4 h, ₹1,200, 2 items, 2 bags,
   recycling list, cooking list, plus the two choices (public, never).
2. **Published factors (7)** — 0.02 kg/pkm, 0.710 kg/kWh, 215 kg band,
   0.11/₹, 0.65 kg/kg, 18 kg/item, 1.5 kg/kg LPG. All cited:
   CEA, Scarborough (BMJ), DESNZ, IPCC, EEA — with links in
   citations/sources.md and section files.
3. **Conventions (4)** — 1.15 transit multiplier, 65 kWh base load,
   100 kWh heating draw, 10 kg medium bag. Documented modeling ranges
   (DATA_DICTIONARY_V2.md).

## Totals

| Line | kg/month |
|---|---|
| Transport | 0.5 |
| Home energy | 126.9 |
| Food | 347.0 |
| Waste (net) | 45.9 |
| Clothing | 36.0 |
| Cooking | 16.0 |
| Flights | 0.0 |
| **Total** | **≈ 572 kg/month (≈ 6.9 t/year)** |

**Insight takeaway:** food (61%) and the grid factor dominate; transport
choices are already near-zero. Surfacing exactly this kind of ranking is
the app's purpose — and every coefficient in the computation is
traceable to citations/.

# India-equivalent emissions per questionnaire question

Per-question carbon mapping for all 15 questions on the CarbonSense form,
expressed as India-equivalent kgCO₂e/month. The anchor factor is India's
grid intensity — **0.710 kgCO₂e/kWh (CEA CO₂ Baseline Database, FY 2024-25)**
— applied to every electrical line; fuel, waste, clothing, and diet factors
come from the section files (travel.md, home.md, food.md,
consumption.md), which carry the full citations.

Verdict summary: **14 of 15 questions have a direct, cited emission
mechanism with an India-computable number.** The 15th (main travel mode) is
the honest exception — it emits nothing by itself; it is the selector that
decides which emission equation the distance question uses.

---

## Per-question table

| # | Question | Mechanism | India number (kgCO₂e/month) |
|---|---|---|---|
| 1 | Main travel mode | ⚠️ No direct emission — the router: decides whether km burn petrol (0.115 kg/km), diesel (0.149), electricity (0.128), shared bus (0.02–0.04), or nothing (cycle) | **0 direct** — changes the same 300 km from **34.6 (car)** to ~9 (bus) to ~0 (cycle) |
| 2 | Vehicle fuel | Petrol burns at 2.31 kg/L (chemistry) → 300 km ≈ 34.6 kg at Indian hatchback efficiency (~20 km/L). EV: 18 kWh/100km × 0.710 grid = 0.128 kg/km | petrol **34.6** · diesel **44.7** · EV **38.3** · hybrid ~**30** |
| 3 | Distance / month | Fuel burn scales linearly: km × fuel factor | 0 km → **0** · 300 km → **34.6** · 1,000 km → **115.5** (petrol) |
| 4 | Flights | Aviation factors are international: 154 g/pkm short-haul, 246 g/pkm domestic (OWID). Screening bands: never 0 / rarely 60 / often 180 / very-frequently 420 | rarely **60** · very frequently **420**; one long-haul return alone ≈ 1,600 |
| 5 | Grid mix | Every kWh multiplied: India 0.710 vs UK 0.13096 vs renewable proxy ~0.15 | ~121 kWh usage: mixed **85.9** vs renewable-heavy **~18** — the 4.7× lever |
| 6 | Heating fuel | Gas ≈ 0.20 kg/kWh combustion (chemistry); electric heating = grid × usage | electric 100 kWh → **71.0** · gas 100 kWh → **20.0** |
| 7 | TV/PC hours | 75 W average × 4 h/day ≈ 9 kWh × 0.710 | **6.4** (UK: 1.2) |
| 8 | Internet hours | Router + network + data centres ≈ 1 kWh/day × 0.710 | **8.5** (UK: 1.6) |
| 9 | Diet | Livestock land + feed + enteric methane (beef 60 kg/kg vs peas 1) | vegan **~90–95** · omnivore **~216–240** (Scarborough 2.9 vs 7.2 kg/day) |
| 10 | Grocery spend | Spend-based method: ₹ × factor (food + packaging + transport) | ₹200 → **22** · ₹5,000 → **550** (app proxy 0.11/kg-spend) |
| 11 | New clothing | Manufacture + dye + ship: EEA ≈ 17 kg/kg textile → 18 kg/item declared | 2 items → **36** · 10 items → **180** |
| 12 | Waste bag size | Sets mass per bag (medium ≈ 10 kg waste) | medium bag ≈ **3.5–6** each |
| 13 | Waste bags/week | Landfill organics → methane (40–60% CH₄, GWP 27) + CO₂; ≈ 0.5–0.8 kg/kg waste | 3 medium bags/week → **≈ 45** |
| 14 | Recycling | Avoids virgin production: aluminium −95% energy, plastics −70%, steel −60%, paper −40% | credit, not emission: none→all ≈ **−386** (measured model effect) |
| 15 | Cooking appliances | Electricity × 0.710 per use, or LPG burned at 1.5 kg/kg | typical mix → **~20**; one LPG cylinder (14.2 kg) ≈ **21** |

---

## Viva takeaways

1. **14/15 direct, cited, India-computable.** The two "engine" questions
   (grid mix, vehicle fuel) are multipliers whose India values (0.710
   kg/kWh; 2.31 kg/L petrol) are the same kind government inventories use.
2. **The one "zero" is by design.** Travel mode emits nothing itself — it
   makes distance interpretable: the same 300 km is 34.6 kg by petrol car,
   ~9 by bus, ~0 by bicycle. No emission factor exists for "a mode"; only
   for mode × distance. Answer if asked: *"Not directly; it selects the
   emission factor for the distance question — without it, '300 km' has no
   emission meaning."*
3. **One question is a credit, not an emission.** Recycling (−386 kg at
   full adoption) reduces rather than emits — still a carbon-linked
   mechanism (avoided production), fully citable.

---

## Transparency note

Numbers above use India-specific factors where they differ from the app's
UK reference set (grid 0.710 kg/kWh; petrol 2.31 kg/L ÷ realistic Indian
efficiency) and the app's declared screening proxies where the form
collects frequency or spend rather than physical activity (flights, diet,
grocery, waste). The strongest guarantees — grid, fuels, clothing, waste,
recycling — are chemistry- or inventory-based, identical in kind to what
CEA, DESNZ, and the IPCC publish.

Full factor citations: see citations/travel.md (§1–3, §6), citations/home.md
(§1–2), citations/food.md (§1–2, §4), citations/consumption.md (§1–4).

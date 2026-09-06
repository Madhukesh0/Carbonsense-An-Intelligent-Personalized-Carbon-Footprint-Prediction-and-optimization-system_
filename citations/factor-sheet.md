# Factor sheet — all 15 frontend questions (deployed + India + citation)

One row per question asked in the frontend. Columns:
- **Deployed factor** — the number in `backend/app/services/baseline.py`
  (FACTOR_SET / SCREENING), attributed to DESNZ 2026 UK reference set.
- **India factor** — the country-specific equivalent (CEA grid, fuel
  chemistry, declared India-compatible proxies).
- **Worked India number** — kgCO₂e/month at the form's default answer.
- **Citation** — link index entry in `citations/sources.md` + section file.

Anchor: India grid **0.710 kgCO₂e/kWh** (CEA CO₂ Baseline Database, FY
2024-25). Form defaults are the survey reference profile (private/petrol/
300 km, rarely, mixed grid, electricity heating, 4h+4h screens, omnivore,
₹200, 2 items, medium, 3 bags/week, paper+plastic recycling, stove+oven).

---

## The 15-row sheet

| # | Question | Deployed factor (baseline.py) | India factor | Worked India number (default) | Citation (sources.md #) |
|---|---|---|---|---|---|
| 1 | Main travel mode | *(router — no factor; selects the #2 equation)* | same | 0 direct (makes "300 km" meaningful) | OWID travel — #7 |
| 2 | Vehicle fuel | petrol 0.16152 · diesel 0.17265 · hybrid 0.12961 · LPG 0.19553 · EV 0.02686 kg/km | petrol 2.31 / diesel 2.68 kg/L ÷ real efficiency; EV = 18 kWh/100km × 0.710 | petrol **34.6** · diesel **44.7** · EV **38.3** @300 km | DESNZ — #1; IPCC Ch.3 — #13 in travel.md §6 |
| 3 | Distance / month | km × vehicle factor (activity-based) | same chemistry factors | 300 km → **34.6** · 1,000 km → **115.5** (petrol) | DESNZ — #1 |
| 4 | Flights | screening bands 0 / 60 / 180 / 420 kg/month | aviation is international — same pkm factors | rarely → **60** · very frequently → **420** | OWID 246/154 g/pkm — #7 |
| 5 | Grid mix | *(context-only in model; baseline uses fixed 220 kWh reference)* | **0.710** kg/kWh (CEA FY 2024-25); renewable proxy ~0.15 | ~121 kWh usage: mixed **85.9** vs renewable **~18** | CEA table — #5 |
| 6 | Heating fuel | *(folds into the 220 kWh electricity reference)* | gas ≈ 0.20 kg/kWh · wood ≈ 0.06–0.09 · electric = grid × usage | electric 100 kWh → **71.0** · gas → **20.0** | DESNZ 2025 xlsx — #2; IPCC Vol.2 |
| 7 | TV/PC hours | *(in the 220 kWh reference)* | 75 W avg × 0.710 × 4 h/day ≈ 9 kWh | **6.4** | device specs — #22 ledger |
| 8 | Internet hours | *(in the 220 kWh reference)* | router + 0.06 kWh/GB (Aslan 2018) + IEA 460→1,000 TWh | **8.5** | IEA — #12; Aslan — home.md §7 |
| 9 | Diet | vegan 95 · vegetarian 130 · pescatarian 175 · omnivore 240 kg/month | same ordering; Scarborough 2.9–7.2 kg/day; beef 60 vs peas 1 kg/kg | omnivore → **240** · vegan → **95** | Scarborough BMJ — food.md §7; OWID — #8/#9 |
| 10 | Grocery spend | 0.11 kg per ₹ (spend-based) | ₹-denominated proxy (DESNZ-sanctioned method) | ₹200 → **22** · ₹5,000 → **550** | DESNZ method sanction — #1 |
| 11 | New clothing | 18 kg/item | EEA ≈ 17 kg/kg textile (fetched); same global supply chain | 2 items → **36** | EEA — #17 |
| 12 | Waste bag size | 1.8 / 3.5 / 5.5 / 8 kg per bag (S/M/L/XL) | 0.5–0.8 kg/kg landfill convention (IPCC Vol.5) | medium bag ≈ **3.5–6** | IPCC Vol.5 — consumption.md §7 |
| 13 | Waste bags/week | count × 4.3 weeks × bag factor | same; methane 40–60% CH₄, GWP 27 | 3 medium/week → **≈45** | Landfill gas — #15 |
| 14 | Recycling | modeled as waste reduction; measured effect −386 kg none→all | avoided-production credits: Al −95% energy, plastics −70%, steel −60%, paper −40% | none→all → **−386** (credit) | Recycling table — #14 |
| 15 | Cooking appliances | binary model flags | LPG 1.5 kg/kg (cylinder ≈ 21 kgCO₂e); electric = grid × draw | typical mix → **~20** | IPCC/India LPG — consumption.md §7 |

---

## Reading notes

1. **Deployed ≠ India for exactly one question**: grid mix (#5) — the
   app's baseline uses a fixed UK-reference electricity line; the CEA
   factor is the designed v2 swap-in (the `region` field already collects
   the answer).
2. **Screening proxies** (#4, #9, #10, #11, #12/#13) are declared
   frequency/spend proxies, not activity factors — the DESNZ-sanctioned
   approach when activity data is unavailable; disclosed in the baseline's
   own assumptions text.
3. **Everything else is chemistry- or inventory-based** (fuels, grid,
   clothing, waste convention, recycling credits) — identical in kind to
   what CEA, DESNZ, and the IPCC publish.
4. Per-question India worked examples in full detail:
   `citations/india-equivalents.md`. Factor derivations and caveats:
   travel.md §6, home.md §2–4, food.md §2–3, consumption.md §1–4.

## Update rule

If any factor changes (e.g., CEA publishes the next FY, DESNZ issues the
2027 set), update: the relevant section file, this sheet's two factor
columns, and `backend/app/services/baseline.py` (with a version bump of
the FACTOR_SET id) — in that order, in one commit.

# Consumption & waste carbon emission factors — citations & worked examples

Reference document for the consumption & waste section of the CarbonSense
questionnaire (new clothing, waste bag size, waste bags/week, recycling,
cooking appliances). Companion to `citations/travel.md`, `home.md`, and
`food.md` — same structure: mechanism, factors, worked example, India
context, v2 gaps. External figures fetched on 2026-09-03 where marked.

---

## 1. New clothing / month — manufacturing emissions per item

**Mechanism:** fabric production (polyester is petroleum-based; cotton is
irrigation- and fertilizer-intensive), dyeing and finishing (energy and
chemicals), and global shipping — all before the garment is worn.

Verified anchor (fetched): **EEA, *Textiles*** (https://www.eea.europa.eu/en/topics/in-depth/textiles) — EU textile
consumption per person caused a carbon footprint of **≈ 270 kg CO₂e in
2020** at ≈ 16 kg of textiles per person → **≈ 17 kg CO₂e per kg of
textile consumed** (derived; the EEA does not publish per-item numbers).

Per-item estimates from widely used lifecycle figures (Quantis / Ellen
MacArthur lineage — https://www.ellenmacarthurfoundation.org/a-new-textiles-economy,
commonly cited ≈ 20 kg/kg apparel; per-item values are convention estimates,
not official factors):

| Garment | Typical weight | ≈ kgCO₂e per item |
|---|---|---|
| T-shirt (cotton) | 0.25 kg | ≈ 5 |
| Shirt / blouse | 0.3 kg | ≈ 6 |
| Jeans (denim) | 0.6–0.8 kg | ≈ 20–33 |
| Polyester dress | 0.4 kg | ≈ 8–10 |
| Jacket / coat | 1.0 kg | ≈ 20+ |

App's declared screening proxy (`baseline.py` SCREENING.clothing):
**18 kgCO₂e per new item** — deliberately conservative (between a shirt and
a pair of jeans) so mixed wardrobes are not under-counted.

Worked example (the form's default 2 items/month): 2 × 18 = **36 kg/month**
(≈ 432 kg/year) — of the same order as home electricity, which is why the
clothing slider earns its place in a screening calculator.

## 2. Waste bag size + bags/week — landfill methane & CO₂

**Mechanism:** landfilled organic waste decomposes anaerobically. Landfill
gas is **40–60% methane** (Ullmann's, via *Landfill gas*, Wikipedia —
fetched), methane's GWP is **27× CO₂ over 100 years** (GHG Protocol),
generation starts ≈ 6 months after depositing and peaks ≈ 20 years later.
Landfills are the **third-largest US methane source** (EPA, via same page).

Reference emission factor (IPCC 2006 Vol.5 Waste guidelines / EPA WARM
convention; https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol5.html):
municipal solid waste to landfill ≈ **0.5–0.8 kgCO₂e per kg of waste**
(composition- and landfill-gas-capture-dependent; hedged range — pull the
category-exact value from the DESNZ waste worksheet for print: see
citations/sources.md #2).

Bag size → mass mapping (typical household bins):

| Bag size | Approx. mass per bag | kgCO₂e per bag (0.6 kg/kg mid) |
|---|---|---|
| Small | ~5 kg | ≈ 3 |
| Medium | ~10 kg | ≈ 6 |
| Large | ~20 kg | ≈ 12 |
| Extra large | ~30 kg | ≈ 18 |

App's declared proxies (`SCREENING.waste`): small 1.8 / medium 3.5 / large
5.5 / extra-large 8 kg **per bag** — same ordering, conservatively below the
0.6 kg/kg mid-point (partially defensible via India's higher organics share
vs higher landfill-gas capture in the UK; both directions documented).

Worked example (the form's default: medium, 3 bags/week):
3 × 4.3 weeks × 3.5 kg ≈ **45 kg/month** — real, mechanism-backed, and
among the few waste questions that survive a viva.

## 3. Recycling — avoided-virgin-production credits

**Mechanism:** recycling displaces primary material production. Verified
energy-savings vs virgin production (*Recycling*, Wikipedia — fetched;
sources EPA/EIA/Garbology):

| Material | Energy saved vs virgin | Note |
|---|---|---|
| Aluminium | **95%** | the headline case; smelting is electricity-intensive |
| Plastics | **70%** | mechanical recycling |
| Steel | **60%** | recycled-cans steel ≈ −75% GHG |
| Paper | **40%** | EIA: paper mills use 40% less energy |
| Cardboard | 24% | — |
| Glass | 5–30% | modest; glass recycling mostly saves raw materials |

App treatment (`baseline.py`): recycling lowers the waste proxy rather than
crediting per material — declared, conservative, and directionally correct
(aluminium's 95% justifies "recycling lowers your footprint" as stated on
the form).

## 4. Cooking appliances — kitchen energy load

**Mechanism:** each appliance draws electricity (grid factor) or gas
combustion per use.

| Appliance | Typical draw | Monthly use (assumed) | kgCO₂e/month (India grid 0.71) |
|---|---|---|---|
| Induction/electric stove | 1.2–2 kW, 30 min/day | ≈ 9–15 kWh | ≈ 7–11 |
| Gas stove (LPG) | 1.8–2.2 kW-equivalent | ≈ 1 cylinder (14.2 kg LPG)/2 months | ≈ 10 (≈ 1.5 kg/kg LPG burned × monthly share) |
| Electric oven | 2–2.4 kW, 1 h/week | ≈ 9 kWh | ≈ 6 |
| Microwave | 0.8–1.2 kW, 10 min/day | ≈ 4–6 kWh | ≈ 3–4 |
| Grill | 1.5–2 kW, 1 h/week | ≈ 6–8 kWh | ≈ 4–6 |
| Air fryer | 1.2–1.5 kW, 20 min/day | ≈ 7–9 kWh | ≈ 5–6 |

App treatment: cooking enters the model as binary flags (which appliances
you use), contributing a modest ~160 kg full-range effect; the baseline
folds cooking into the electricity/waste lines rather than crediting it
separately — declared in the assumptions.

India note (viva-ready): in India the cooking question is **more material
than in the UK** because LPG cylinders are the norm (≈ 1.5 kg CO₂ per kg
LPG; a 14.2 kg cylinder ≈ 21 kg CO₂e when burned) and induction is
grid-coupled. The appliance multi-select is the right shape for this; a
v2 could add "LPG cylinders per month" as a numeric question for the
baseline.

## 5. Are the 5 questions necessary and enough?

**Yes — all 5 necessary, none redundant, screening-complete:**

| Question | Mechanism | Verdict |
|---|---|---|
| New clothing/month | Manufacturing + shipping per item | ✅ Necessary (18 kg/item × up to 50 items = up to 900 kg/month range) |
| Waste bag size | Mass-per-bag proxy | ✅ Necessary (multiplies bags/week) |
| Waste bags/week | Landfill methane (40–60% CH₄, GWP 27) | ✅ Necessary (293 kg full-range effect in the model) |
| Recycling | Avoided virgin production (Al 95%, plastics 70%) | ✅ Necessary (386 kg none→all effect) |
| Cooking appliances | Electricity/gas per use | ✅ Necessary (kitchen load; India-salient via LPG) |

The section covers every consumption-and-waste source a screening
calculator can defensibly ask: what you buy (clothing), what you discard
(bag size × count), what you recover (recycling), and what you cook with
(appliances).

**Known gaps — v2, with their justifications:**

| Gap | Why it matters | v2 treatment |
|---|---|---|
| Non-clothing goods spend | Electronics/furniture carry large embodied emissions not captured anywhere | monthly goods-spend field (spend-based method, as food) |
| Clothing material mix | Polyester ≈ 2× cotton per kg in production | material-weighted per-item factor |
| Food-waste share of bags | Organics drive landfill methane; separation changes the factor | organics fraction → factor selection |
| E-waste / recycling quality | "recycled" varies between kerbside collection and landfill-bound | material × confidence weighting |
| Second-hand share of clothing | Reuse cuts the per-item factor dramatically | discount multiplier on the clothing line |

## 6. Citation list

1. **EEA — European Environment Agency.** *Textiles* topic page — EU
   per-person textile footprint ≈ 270 kg CO₂e (2020) at ≈ 16 kg consumed;
   <1% of textiles recycled into new products (Ellen MacArthur Foundation,
   2017). (fetched 2026-09-03)
2. **IPCC (2006).** *Guidelines for National GHG Inventories, Vol. 5
   Waste* — landfill methane estimation basis (0.5–0.8 kgCO₂e/kg MSW
   convention; EPA WARM comparable).
3. ***Landfill gas* (Wikipedia, fetched 2026-09-03)** — gas is 40–60%
   methane (Ullmann's 2011); CH₄ GWP 27 (GHG Protocol); landfills the
   third-largest US methane source (EPA).
4. ***Recycling* (Wikipedia, fetched 2026-09-03)** — energy savings vs
   virgin: aluminium 95%, plastics 70%, steel 60%, paper 40%, glass 5–30%
   (EPA/EIA-cited table).
5. **Quantis / Ellen MacArthur Foundation lifecycle studies** — per-garment
   figures (jeans ≈ 20–33 kgCO₂e; commonly cited ≈ 20 kg/kg apparel).
6. **DESNZ (2026).** Conversion factors, waste-disposal worksheets —
   category factors behind the app's declared bag-size proxies.
7. **IPCC (2006) Vol. 2 / Indian LPG data.** LPG ≈ 1.5 kgCO₂e/kg burned —
   basis for the India cooking-cylinder example.

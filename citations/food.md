# Food carbon emission factors — citations & worked examples

Reference document for the food section of the CarbonSense questionnaire
(diet pattern, grocery spend). Companion to `citations/travel.md` and
`citations/home.md`. External figures verified on 2026-09-03 (source noted
per section); app screening proxies are the declared values in
`backend/app/services/baseline.py`.

---

## 1. Why diet type is the core food question — the mechanism, quantified

Food emissions are dominated by **production method**, not cooking or
transport. Livestock need land, feed, and time, and ruminants (cattle,
sheep, goats) add methane from enteric fermentation — a greenhouse gas
~80× more potent than CO₂ over 20 years.

Per-kilogram footprints (Poore & Nemecek 2018, via Our World in Data —
*food-choice-vs-eating-local*, fetched 2026-09-03):

| Food | kgCO₂eq per kg |
|---|---|
| Beef (beef herd) | **60** |
| Lamb | **>20** |
| Cheese | **>20** |
| Pork | 7 |
| Poultry | 6 |
| Avocado | ~2.5 |
| **Peas (legume)** | **1** |

Per-unit-of-protein comparisons (same source, quoted on
*carbon-footprint-food-methane*): beef ≈ 5× tofu, ≈ 10× beans, ≈ 20× peas.

Structural conclusion: a plant-based plate is **~10–20× lighter per calorie
or per protein** than a red-meat plate — this is the mechanism the diet
question encodes, and why the description on the form is factual, not
decorative.

## 2. Diet-pattern emissions (screening values, per person)

Peer-reviewed per-person daily footprints by diet type (Scarborough et al.
2023, *BMJ* 381:e097913, EPIC-Oxford ~55,000 participants — values as
widely reported; note the BMJ page itself blocked automated fetching, so
these are the study's headline figures as reproduced in secondary coverage;
verify the decimal against the paper before quoting in print):

| Diet | kgCO₂eq/day | ≈ kgCO₂eq/month |
|---|---|---|
| High meat-eater (≥100 g/day) | **7.2** | 216 |
| Medium meat-eater (50–99 g/day) | 5.6 | 170 |
| Low meat-eater (<50 g/day) | 4.7 | 140 |
| **Pescatarian** (fish, no meat) | 3.9 | 120 |
| **Vegetarian** | 3.8 | 115 |
| **Vegan** | **2.9** | 90 |

App's declared screening proxies (`baseline.py` SCREENING.diet): vegan 95,
vegetarian 130, pescatarian 175, omnivore 240 kg/month — same ordering,
conservative (higher) magnitudes than the UK study, sitting between the
medium and high meat-eater bands.

Two honest notes for the viva:

1. **The app's ordering differs from the study at the bottom end** — the
   study puts vegetarian ≈ pescatarian (3.8 vs 3.9) and the app's proxies
   put vegetarian (130) below pescatarian (175). Defensible either way:
   Indian vegetarian diets are typically dairy-heavy (cheese/paneer >20
   kg/kg), which can push a dairy-rich vegetarian diet above a light-fish
   one. State that this is a modelling choice, not a measured Indian result.
2. **Why the model's diet effect looks small (153 kg spread)** — the frozen
   model learned the Kaggle formula's diet term, not these literature
   values. The *literature* spread (vegan vs high-meat ≈ 126 kg/month,
   ≈ 1.5 t/year) is what a v2 target built from these factors would produce.

## 3. Grocery spend — what a spending proxy can and cannot claim

Spend-based accounting is a recognized method when activity data is absent
(DESNZ explicitly sanctions it, `travel.md` §2): emission = spend ×
industry-average factor. Standard benchmark ≈ **2.0 kgCO₂e per unit
currency of food spend** (UK-focused estimates; varies by diet mix and
prices).

Worked example at the app's proxy (`SCREENING.grocery` = 0.11 kg per ₹/unit
of spend — calibrated conservatively):

- ₹2,000/month food spend → 220 kg/month proxy
- Same spend as ₹5,000 → 550 kg: the slider covers the meaningful range

Strengths: universally answerable (everyone knows their food bill);
correlates with total food consumed, packaging, and processing.

Weaknesses to state: currency- and price-level-dependent (₹5,000 buys
different food in India vs the UK); ignores *composition* (the diet
question supplies that — the two questions work as a pair); does not
capture home-grown food.

## 4. India context (fetched, for the viva)

- **Vegetarian share of India: 20–39%** across surveys — Pew Research 2021
  (39%, ~30,000 respondents), GoI official survey (28–29%), CNN-IBN 2006
  (31% + 9% eggs), EPW 2018 critique (likely closer to 20%).
  (Vegetarianism in India, Wikipedia, fetched 2026-09-03.)
- Consequence: the diet question is **more salient in India than anywhere
  else** — the app's four options map directly onto real Indian dietary
  identities (vegan/vegetarian/pescatarian are rarer categories; most
  Indian users will split between vegetarian and omnivore).
- Rice-heavy diets carry extra methane from paddy cultivation (largest
  methane source after livestock — OWID emissions-by-sector); a possible
  v2 refinement question (rice-dominant vs wheat-dominant staples).

## 5. Are the two questions enough?

**Yes for screening — with one designed-in caveat.** Diet type × grocery
spend covers the production-emission mechanism (composition) and the
quantity/packaging/transport dimension (spend). The known gaps, all v2:

| Gap | Why it matters | v2 fix |
|---|---|---|
| Red-meat meals/week | Explains more variance than the category label; resolves omnivore-vs-omnivore differences | count × beef/lamb kg factors |
| Dairy amount | Paneer/cheese >20 kg/kg; Indian vegetarian diets are dairy-heavy | dairy spend or servings field |
| Food waste share | ~⅓ of food produced is wasted; household-level lever | fraction × spend factor |
| Regional food factor | ₹-denominated factor differs by country/price level | country-specific spend factor (India-specific EF from MoEFCC inventory) |
| Rice vs wheat staple | Paddy methane is India-relevant | categorical adjustment |

## 6. Citation list

1. **Poore, J. & Nemecek, T. (2018).** *Reducing food's environmental
   impacts through producers and consumers.* Science 360(6392) — the
   underlying per-kg dataset (beef 60, poultry 6, peas 1 kg/kg; cheese and
   lamb >20 kg/kg).
2. **Our World in Data.** *Food choice vs eating local* and *Carbon
   footprint of food: methane* — per-kg figures quoted above (fetched
   2026-09-03).
3. **Scarborough, P. et al. (2023).** *Dietary greenhouse gas emissions of
   meat-eaters, fish-eaters, vegetarians and vegans in the UK.* BMJ
   381:e097913 — per-diet daily footprints (§2 table).
4. **DESNZ (2026).** Conversion factors — spend-based method sanction
   (activity-data-unavailable case), as applied to the grocery proxy.
5. **Pew Research Center (2021) / GoI NSS survey / CNN-IBN (2006).** India
   vegetarian-population estimates 20–39% (via *Vegetarianism in India*,
   fetched 2026-09-03).
6. **Aslan et al. / OWID emissions-by-sector** — livestock methane and
   paddy-rice methane as the two largest agricultural methane sources.

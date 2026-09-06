# Frontend coverage — the 14 human-activity carbon emitters

Audit result: **every human-activity carbon emitter is present in the
frontend questionnaire (14/14), plus 1 justified router question, and the
5 mechanism-free model-contract columns are deliberately excluded.**
Verified against the live form (`client/src/utils/predictSurvey.ts`) and
the deployed model contract (`server/model_runtime/app/core/final_contract.py`).

---

## The 14 questions where human activity emits carbon — all present ✅

| # | Emitter (human activity) | Frontend question | Form section | Asked? |
|---|---|---|---|---|
| 1 | Driving a fuel vehicle | Distance driven / month | Travel | ✅ |
| 2 | Choice of fuel (petrol/diesel/EV…) | Vehicle fuel | Travel | ✅ |
| 3 | Flying | Flights | Travel | ✅ |
| 4 | Consuming grid electricity (multiplier) | Electricity grid mix | Home energy | ✅ |
| 5 | Heating the home | Heating fuel | Home energy | ✅ |
| 6 | Screen time on devices | TV / PC hours / day | Home energy | ✅ |
| 7 | Internet use | Internet hours / day | Home energy | ✅ |
| 8 | Diet choice (livestock vs plants) | Diet pattern | Food | ✅ |
| 9 | Buying food (spend-based) | Grocery spend / month | Food | ✅ |
| 10 | Buying new clothing | New clothing / month | Consumption & waste | ✅ |
| 11 | Waste volume per bag | Waste bag size | Consumption & waste | ✅ |
| 12 | Waste disposal frequency | Waste bags / week | Consumption & waste | ✅ |
| 13 | Recycling (avoided production) | Recycling (multi-select) | Consumption & waste | ✅ |
| 14 | Cooking energy use | Cooking appliances (multi-select) | Consumption & waste | ✅ |

## The 15th question — the interpretive router

**Main travel mode** is in the frontend and does not emit directly. It is
the **router**: without it, "300 km" has no emission meaning (car
34.6 kg / bus ~9 kg / cycle ~0 per month). It stays — not as an emitter,
but as the question that makes the distance emitter interpretable.

## Deliberately NOT in the frontend (correct by design)

- **5 model-contract columns** — sex, body type, shower frequency, social
  activity, and the "energy efficiency" scale: no defensible emission
  mechanism (their historical model effects — male +328 kg, obese +532 kg,
  etc. — are artifacts of the synthetic source formula). Sent as silent
  reference values so the frozen 44-feature model contract stays valid;
  the results card labels them "dataset reference profile".
- **Nothing else is missing.** Every carbon-emitting human activity a
  screening calculator can defensibly ask about is on the form.

## The complete chain

```
15 questions asked in frontend
├── 14 = human-activity carbon emitters (all mechanism-backed, cited in citations/)
└──  1 = travel mode (interpretive router, 0 direct emission)

→ 26-column model contract (12 direct + 9 derived binaries + 5 reference defaults)
→ 44 model features → prediction + SHAP + 90% conformal interval
```

**Conclusion:** the frontend covers 100% of the human-activity emitters
(14/14), plus 1 justified router question, and excludes exactly the 5
mechanism-free contract columns. No emitter is un-asked, and no question
on the form fails the emission-mechanism test.

---

Factor evidence per question: see `citations/travel.md` (1–3),
`citations/home.md` (4–7), `citations/food.md` (8–9),
`citations/consumption.md` (10–14), and `citations/india-equivalents.md`
for the per-question India numbers.

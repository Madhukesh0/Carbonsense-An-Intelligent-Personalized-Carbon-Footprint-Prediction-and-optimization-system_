# Reduction Optimizer method audit

## Answer: does it use linear programming?

**Yes.** The original CarbonSense repository contains a PuLP/CBC linear-programming optimizer. It defines continuous decision variables for red-meat reduction, car-distance reduction, electricity reduction, waste diversion, clothing reduction, and renewable switching. It minimizes a weighted effort objective subject to the constraint that total modeled savings meet the user’s target reduction.

The original implementation is located at `backend/app/core/optimization.py`. Its API accepts a current footprint, a target percentage, optional limits, and a reference electricity value. The method therefore starts from a completed footprint result; it is not an independent second prediction model.

## Deployed CarbonSense implementation

The current app now follows the same user workflow:

1. The signed-in user completes an AI prediction and transparent baseline with the same survey answers.
2. The optimizer retrieves the newest matching private result pair for that user.
3. The stored XGBoost prediction becomes the immutable starting footprint.
4. The user selects a target reduction percentage.
5. A continuous linear plan returns the minimum weighted-effort combination of supported actions that meets the target, where feasible.

For this single savings constraint, the deployed implementation solves the same linear-programming formulation by its mathematically equivalent least-effort ordering: actions are ranked by **effort per kgCO₂e saved**, bounded by the user profile and action limits, and allocated until the target is met or all bounds are exhausted.

## Action boundaries

| Action family | Starting limit | Factor boundary |
|---|---|---|
| Diet shift | 8 kg red-meat equivalent/month for omnivore; 3 kg for pescatarian | Original repository planning factor: 27 kgCO₂e/kg. |
| Transport | Up to the stored monthly distance, capped at 800 km | DESNZ 2026 vehicle/public-distance reference factor. |
| Electricity | Up to 150 kWh/month reference activity | DESNZ 2026 UK-grid electricity reference factor. |
| Waste | Up to 30 kg/month | Explicit 0.5 kgCO₂e/kg screening planning factor. |
| Clothing | Up to stored clothing purchases, capped at 6 items/month | Explicit 18 kgCO₂e/item screening factor consistent with the app’s transparent baseline. |

The planner explicitly reports whether the requested target is feasible under these bounds. Its recommendations are **scenario-planning suggestions**, not verified future reductions or causal guarantees.

## Difference from XGBoost and the transparent baseline

The live XGBoost model estimates the submitted lifestyle profile. The transparent baseline applies documented activity factors where compatible input data exist. The optimizer does not retrain or alter either; it uses the stored AI estimate as its starting number, then finds an internally consistent plan under disclosed action factors and limits.

## Verification

At desktop and 390 px mobile widths, the authenticated optimizer rendered the stored **715 kg AI result** and **480 kg transparent baseline** before exposing the target-reduction control. Both layouts retained the linear-method disclosure, starting-value boundary, and clear result-led plan action without clipping or horizontal scrolling. Focused TypeScript and optimizer/profile/interface tests passed after this change.

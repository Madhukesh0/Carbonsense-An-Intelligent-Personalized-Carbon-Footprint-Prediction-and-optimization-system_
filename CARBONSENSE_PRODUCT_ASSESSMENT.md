# CarbonSense web app assessment

## Overall assessment

CarbonSense is a **strong final-year B.E./B.CSE project and a credible prototype**, rather than a production-grade personal-emissions measurement service. Its main strength is the complete, explainable workflow: user inputs lead to a live persisted XGBoost estimate, an independently transparent baseline, contributor analysis, result-led recommendations, What-if comparisons, and a constrained reduction planner. The most important limitation is that both the model target and several baseline components are still **estimation lenses**, not direct measurements of a person’s real emissions.

## Strengths

| Area | Evidence-based strength | Why it matters |
|---|---|---|
| End-to-end product flow | The app supports result capture, comparison, recommendations, What-if scenarios, reduction planning, history, goals, activity tracking, reporting, organization views, and governance. | Demonstrates full-stack engineering, not only an isolated ML notebook. |
| Real deployed model path | The persisted 54-feature XGBoost artifact, 34→54 preprocessor contract, SHA-256 checks, and recorded held-out metrics replayed exactly on the artifact-matching generated training package. | Strong reproducibility and deployment evidence for an academic demonstration. |
| Transparent second lens | The factor-based baseline is shown separately from the XGBoost estimate and identifies its factor set, sources, assumptions, and comparison fields. | Prevents the ML output from being presented as the only truth. |
| Current factor sourcing where compatible | Electricity and travel-distance inputs use the versioned DESNZ 2026 UK reference set, with source links and unit boundaries.[1] | Stronger methodology than unexplained hard-coded factors. |
| Explainability | Live grouped XGBoost contributions reconcile to the prediction and distinguish model behavior from causal environmental claims. | Useful for viva demonstration and user understanding. |
| Result-led decision support | Recommendations, What-if, and Reduction Optimizer now require the authenticated user’s matching completed AI/baseline result. | Avoids generic demo values and makes the planning experience coherent. |
| Privacy and authentication | Native passwords use salted scrypt hashes in Atlas; browser sessions are HTTP-only; Google/Manus sign-in does not expose a Google password to CarbonSense. | Shows appropriate secure-design thinking for a student project. |
| Quality evidence | The latest checkpoint validates 17 test files / 66 tests, production build, and desktop/mobile flows for the major result-led experiences. | Demonstrates regression discipline rather than relying only on screenshots. |

## Limitations and risks

| Area | Current limitation | Honest implication |
|---|---|---|
| Model target | The XGBoost target is formula-derived synthetic data. | The model predicts its generated target pattern; it does not verify a user’s physically measured emissions. |
| Dataset lineage | The retained `preprocessed_full_10k.csv` does not reproduce the deployed artifact’s metrics; the separate generated training package does. | The project must retain the corrected provenance wording and not claim the mismatched preprocessed CSV trained the deployed model. |
| Geographic accuracy | DESNZ factors are a UK reference set, while the survey collects only broad grid categories. | Baseline results are not country- or supplier-specific measurements for every user. |
| Input precision | Air travel is frequency only; diet/grocery, waste, and clothing lack the physical quantities or treatment details required for fully activity-based accounting. | Those components are explicitly screening proxies, not precise official factor calculations. |
| “Real-time” scope | Predictions are recalculated immediately from user-entered survey values, but no meter, utility, GPS, receipt, or flight-distance integration exists. | Say **interactive model-based estimation**, not live measured emissions tracking. |
| Recommendation outcomes | Action estimates and optimizer plans are planning scenarios. | Do not claim a user has achieved a reduction until they record evidence; self-reported completion remains distinct from verified completion. |
| Security hardening | The least-privilege Atlas database user and final personal-browser authenticated checks remain user-controlled unfinished tasks. | Complete these before presenting the app as security-hardened for public deployment. |
| External validation | There is no independent real-world test set, user study, or country-specific calibration. | The strong held-out score applies to the generated target, not proven real-world accuracy. |

## Best project positioning

Use this statement in the methodology or viva:

> CarbonSense is an intelligent carbon-footprint **estimation and decision-support platform**. It combines a frozen XGBoost model trained on a documented formula-derived generated dataset with a transparent factor-based baseline. It supports scenario comparison, recommendations, and reduction planning, but it is not a direct real-time emissions measurement system.

## Prioritized next steps

| Priority | Next step | Value |
|---:|---|---|
| P0 | Create the least-privilege Atlas user, restrict network access appropriately, and complete a real personal-browser authenticated test. | Closes the two remaining security/verification gaps. |
| P0 | Preserve the corrected model-provenance wording in the report and demo. | Avoids a material methodology claim error. |
| P1 | Add optional country, utility electricity, fuel quantity, flight distance, waste mass, and product-detail inputs. | Enables more valid factor calculations and country-specific comparisons. |
| P1 | Export/version the exact artifact-matching transformed matrix or keep a reproducible training script and package manifest. | Strengthens reproducibility. |
| P2 | Validate against an external measured dataset or pilot user records after appropriate consent and governance. | Establishes real-world accuracy evidence. |
| P2 | Add formal security review, performance/load testing, and monitoring before public-scale use. | Moves the prototype toward production readiness. |

## Conclusion

For a final-year major project, CarbonSense is **above average in scope and methodological transparency**. Its strongest defence is not a claim of perfect accuracy; it is the explicit separation between trained-model estimation, transparent factor calculation, scenario planning, verified behavior, and known boundaries. The app is suitable for demonstration and academic evaluation when presented with these limits clearly.

## References

[1] [Department for Energy Security and Net Zero, *Greenhouse gas reporting: conversion factors 2026*](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026)

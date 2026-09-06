# CarbonSense improvement roadmap

## Core recommendation

**Do not rebuild the core model now.** The current 34-input → 54-feature XGBoost contract is deployed, tested, documented, and explicitly chosen by the project owner. Your strongest final-year project is a reliable, explainable system with a clear methodology—not a larger project with unverified late changes.

## Keep as it is

| Area | Keep | Reason |
|---|---|---|
| Frozen ML contract | Keep the 34 raw columns, 54 transformed features, persisted XGBoost artifact, and 21-question user interface. | The artifact and matching generated training package are verified. Feature reduction or retraining now introduces unnecessary risk. |
| Two-lens result | Keep AI prediction and transparent baseline as separate cards. | This is a distinctive and academically strong design: one trained model plus one explainable factor method. |
| Result-led workflow | Keep the flow **result → recommendations → What-if → optimizer → goals**. | It makes planning actions traceable to the user’s own completed profile, rather than generic demo data. |
| Explainability | Keep grouped XGBoost contributions and the “model behavior, not causal proof” boundary. | This is strong viva material and demonstrates responsible AI design. |
| Privacy design | Keep native MongoDB hashed credentials, HTTP-only sessions, Google/Manus alternative sign-in, and private per-user results. | These are practical security strengths for a student project. |
| Design system | Keep the climate-intelligence visual system, semantic result colors, and responsive layouts. | The product already looks cohesive and has desktop/mobile evidence. |

## Improve now — highest value before final submission

| Priority | Improvement | Why it helps | Scope |
|---:|---|---|---|
| P0 | Complete the least-privilege Atlas user and personal-browser authenticated verification. | Converts current security/verification gaps into completed evidence. | User-controlled hardening; no model change. |
| P0 | Prepare a polished 5-minute demo path. | Gives a clean viva story: sign in → submit result → compare baseline → see recommendations → run What-if → build optimizer plan. | Documentation and rehearsal. |
| P0 | Keep the dataset-provenance wording correct everywhere. | Avoids claiming that the mismatched preprocessed CSV trained the deployed artifact. | Methodology/report copy only. |
| P1 | Add a “Why this result?” summary on the result page. | Combine top 3 model contributors, baseline boundary, and next action into one easy explanation. | UI content improvement; no model change. |
| P1 | Expand What-if controls from two fields to a few high-value controls. | Let users test travel distance, air travel, diet, clothing, and digital use while preserving the same completed profile. | Scenario UI and existing inference API. |
| P1 | Add “Save scenario to plan” after a What-if or optimizer result. | Connects experimentation to goals and activity tracking. | Product workflow improvement. |
| P1 | Improve input-quality guidance. | Add short examples such as “use a typical month” and show unit/currency guidance before the form is submitted. | UX copy and validation hints. |

## Good future enhancements — defer until after submission

| Future idea | Why it is valuable | Why defer it now |
|---|---|---|
| Country-specific electricity and vehicle factors | More geographically appropriate baseline estimates. | Requires reliable country data and additional methodological validation. |
| Utility bill, fuel receipt, GPS, flight-distance, and waste-mass integrations | Moves the app closer to measured activity data. | Needs consent, external APIs, data governance, and new security work. |
| External real-world validation study | Tests whether the estimation approach agrees with independent data. | Requires a valid measured dataset or participant study. |
| Adaptive/retrained model | Could improve accuracy for a new, governed dataset. | Needs versioning, reproducibility, approval, evaluation, and deployment control. |
| Full organization reporting exports and notifications | Helpful for enterprise use. | Adds product breadth, but does not improve the core academic methodology as much as validation does. |
| Load testing, monitoring, rate limiting, and formal security review | Important for production rollout. | Valuable later; keep the final-year scope focused. |

## Changes to avoid

| Avoid | Reason |
|---|---|
| Do not reduce the model to a short questionnaire now. | The owner cancelled this path and the current frozen contract is validated. |
| Do not silently replace the model or preprocessor. | It would break reproducibility and your documented evaluation evidence. |
| Do not claim exact real-time personal emissions. | Inputs are user-entered and the model target is formula-derived synthetic data. |
| Do not present contribution bars as causal savings. | They explain model behavior for a submitted profile, not proven physical impact. |
| Do not add fake reviews, rankings, or “user feedback.” | It weakens credibility and creates an unnecessary integrity problem. |
| Do not store passwords or session credentials in local storage. | The current secure boundary is stronger and should be retained. |

## Recommended final-year version

The best submission version is:

> **CarbonSense: an explainable AI-based carbon-footprint estimation and decision-support platform.** Users enter lifestyle data, receive a live XGBoost estimate and transparent factor baseline, understand the result through model contributions, then use profile-matched recommendations, What-if scenarios, and a reduction planner to make and track practical choices.

This scope is complete, impressive, and defendable. First finish the two outstanding hardening checks; then improve **scenario controls** and the **result explanation summary** only if time remains.

# CarbonSense homepage improvement concepts

## Current opportunity

The current landing page has a polished climate-intelligence visual system, but its main message can become more immediately useful for a first-time visitor. The strongest page should answer three questions in the first screen:

1. **What is CarbonSense?** An AI-based carbon-footprint estimation and planning workspace.
2. **What will I get?** A model estimate, a transparent baseline comparison, and actions to explore.
3. **What should I do now?** Start the guided estimate.

## Recommended direction: “Measure → Compare → Act”

Use the existing dark climate-signal hero, but make the first screen a more explicit guided entry point.

| Hero element | Recommended change | Benefit |
|---|---|---|
| Main title | **Understand your carbon estimate. Plan your next move.** | Says the product outcome without claiming direct measurement. |
| Supporting sentence | “Answer guided lifestyle questions, compare a live XGBoost estimate with a transparent baseline, then explore practical next steps.” | Explains the two-lens methodology in plain language. |
| Primary action | **Start my estimate** | Clear first action; routes to the prediction survey. |
| Secondary action | **See how it works** | Scrolls to a concise Measure → Compare → Act explanation. |
| Trust strip | “34-input model contract · Transparent factor baseline · Private result history” | Builds confidence without placing a long disclaimer in the hero. |
| Right-side visual | Replace the abstract-only signal visual with a three-stage active workflow: **1 Answer → 2 Compare → 3 Plan**. | Shows the outcome of the primary action before the user begins. |

## Homepage blocks after the hero

| Order | Section | Content |
|---:|---|---|
| 1 | Three-step workflow | **Measure:** guided source answers. **Compare:** AI prediction + transparent baseline. **Act:** recommendations, What-if, and optimizer. |
| 2 | What makes the result useful | Three evidence cards: live XGBoost model, transparent baseline, and result-led planning. |
| 3 | Example of the planning journey | A non-numeric process preview: “Completed result → relevant recommendation → test a scenario → accept an action.” Avoid invented user emissions values. |
| 4 | Privacy and methodology | Compact links: “Where is my data stored?”, “How does the model work?”, and “What is estimated?” |
| 5 | Final conversion panel | “Ready to understand your pattern?” with the same primary **Start my estimate** action. |

## Signed-out and signed-in behavior

The page should deliberately behave differently for two visitor states.

| Visitor | First-page priority | Best primary action |
|---|---|---|
| Signed out | Explain the product and lower uncertainty before asking for registration. | Start my estimate / Create account |
| Signed in without a completed result | Resume the core measurement flow. | Complete my estimate |
| Signed in with a completed result | Help the user return to useful work. | View my latest result; second action: Explore recommendations |

This avoids showing generic dashboard numbers to a new visitor and avoids making an existing member repeat the onboarding story.

## Three possible visual styles

| Option | Concept | Best for | Recommendation |
|---|---|---|---|
| A | **Guided climate cockpit** | Clear methodology and final-year demo storytelling | **Recommended** — extends the existing visual system without a redesign risk. |
| B | Personal progress journal | Softer habits, streaks, and weekly action feel | Good later, but can distract from the technical AI/baseline core. |
| C | Data laboratory | Dense charts, model metrics, and technical credibility | Useful for an About/Methodology page, not as the first visitor screen. |

## What to avoid

Do not add a large chart before the visitor has any personal result. Do not hard-code example “personal emissions” as if they were a real user result. Do not make the hero lead with model RMSE, feature counts, or a long scientific limitation paragraph. Keep those available through a clear methodology link; the hero should lead with the useful user journey.

## Recommended first implementation slice

Implement **Option A** only:

1. Rewrite the hero message and CTAs around Measure → Compare → Act.
2. Add the visible three-stage workflow preview in the hero/right panel.
3. Add the trust strip below the CTAs.
4. Add a signed-in conditional first action: resume result or start estimate.

This is a high-impact change that improves the first page without touching the frozen model, baseline calculations, privacy architecture, or planning tools.

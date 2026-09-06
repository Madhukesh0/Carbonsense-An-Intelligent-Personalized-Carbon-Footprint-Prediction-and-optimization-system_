# GitHub Interface Reference — CarbonSense

## Source repository

The visual reference is the selected GitHub repository at `Madhukesh0/Carbonsense-An-Intelligent-Personalized-Carbon-Footprint-Prediction-and-optimization-system`, specifically its Wren-inspired React frontend.

## Verified dashboard reference

The reference interface uses a sticky, translucent white navigation bar above a softly glowing, pale-gray page. The brand block has a green circular `C` mark, the `CarbonSense` wordmark, and the micro-label `INTELLIGENT CLIMATE AI`. The public navigation uses `Dashboard` and `About`, while signed-in users see four hubs: `Explore`, `Plan`, `Insights`, and `Progress`.

The dashboard contains a dark forest-to-near-black gradient hero card with a dotted environmental texture, the kicker `POWERED BY XGBOOST + SHAP + PuLP`, the headline `Track your carbon. Reduce with clarity.`, and two primary actions: baseline calculation and AI prediction. Beneath the hero, it uses a three-card climate-action journey (`Discover`, `Reduce`, and `Track`), a snapshot area, a six-card tool grid, and a final trust-metrics bar.

## Interface patterns to recreate

| Pattern | Reference behavior |
|---|---|
| Visual language | Dark forest hero, green `carbon` accent, rounded 24–32 px cards, soft shadows, blurred translucent surfaces, dense but calm typography |
| Navigation | Sticky desktop bar; responsive mobile bottom sheet; active hub chip and role-aware Admin destination |
| Hubs | Explore, Plan, Insights, and Progress group related workflows in a shared page header and tab bar |
| Explore workflow | Multi-step prediction and baseline wizards with chips, selectors, sliders, live estimate panels, result cards, and next-step calls to action |
| Content layout | Max-width 6xl centered container, generous vertical space, three-card story blocks, tool grids, and trust metrics |
| Safety correction | Claims about real training responses, model scores, and user impact must remain replaced with the current CarbonSense synthetic-data disclosure and verified runtime metadata |

## Implementation boundary

The Manus application will reproduce the navigation hierarchy, layouts, visual system, and user interaction patterns. It will retain the existing secured tRPC procedures, Manus OAuth flow, role checks, model contract, and scientific-honesty disclosures rather than copying unsupported claims or the source repository's client-side API behavior.

## Verification note

On 19 August 2026, the rebuilt `/explore` route was opened without an authenticated Manus session. It correctly displayed the protected-workspace gate rather than exposing individual records or organization data. Dedicated repository-style hub components supply the signed-in Explore, Plan, Insights, and Progress layouts after this existing authentication guard succeeds.

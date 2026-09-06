# CarbonSense Feature and Style Roadmap

## Executive recommendation

The running application has a credible, polished foundation. Its strongest qualities are the calm mint and deep-green palette, the high-contrast hero, clear typography, privacy-aware language, and unusually candid model-boundary disclosures. The supplied screens add a second strength: **guided decision flows**, where a user moves through visible steps, meaningful defaults, compact controls, and a single next action.

The highest-value direction is not to add a large number of unrelated tools. It is to turn the existing tools into one coherent, evidence-aware journey:

> **Measure → understand → choose → record → learn.**

This is a hybrid of the two interface directions. Preserve the current product’s composed climate-intelligence visual system and trust language. Borrow the supplied interface’s interaction density, progress cues, and focused forms. Do not reintroduce generic emoji decoration, broad “AI-powered” claims, or implied emissions outcomes.

## What the live review indicates

The public homepage is strong: it explains the product, establishes a distinctive dark signal-led hero, and introduces the major instruments. The responsive implementation also maintains hierarchy on mobile. The authenticated hubs are consistent and easy to scan, but they function mainly as elegant directories. A returning user with no saved data gets little help deciding what to do first, why a tool is unavailable, or what evidence will unlock a more useful result.

The detailed Forecast and Reports views are stronger because they expose a real analytical state. Forecast clearly distinguishes its directional fallback from Prophet readiness, while Reports foregrounds scope, service health, and model boundaries. This is the product’s differentiating asset: **show the evidence and limits, not just a green score**. Planning and progress should adopt this same behavior.

Some direct protected tool links currently resolve to a generic discovery surface when their prerequisite result is missing. That is preferable to exposing an invalid planner, but it loses context. Users should see an explicit, recoverable readiness state such as “Complete an estimate before opening the optimizer,” with one action that preserves the original destination after completion.

## Highest-priority product improvements

| Priority | Improvement | Why it matters now | Scope of the first version | Evidence and safety boundary |
|---|---|---|---|---|
| 1 | **Guided first-result journey** | Converts an elegant directory into a clear first-use path and reduces abandonment before the user receives any personal context. | Add a signed-in “Start here” panel that lets a user choose transparent baseline or model estimate, shows an estimated completion time, and continues to the relevant four-step flow. | Label estimates as indicative; do not prefill or fabricate a result. |
| 2 | **Unified result-to-action cockpit** | The core value is comparison and interpretation, yet estimates, drivers, plans, and recommendations are spread across tools. | After a completed run, show the selected estimate, its range/boundary, transparent baseline comparison, leading non-causal drivers, and one recommended next action. | Keep AI and baseline separate; never average them or present drivers as causal facts. |
| 3 | **Two-minute monthly climate check-in** | Forecasting is currently honest about being history-limited; a low-friction routine is the practical route to usable history, trend, and eventual Prophet eligibility. | Let users record a concise monthly update covering the categories already supported by their data contract, with optional detail only when needed. | Display progress toward recorded-history readiness; do not promise an accurate forecast until the documented thresholds are met. |
| 4 | **Weekly action loop** | Planning becomes useful when an action can be selected, revisited, and honestly recorded. | Introduce a “This week” action card with accept, self-report completion, defer, and why-this-action controls. | Distinguish accepted, self-reported, and verified states. Do not display a quantified reduction as achieved without supporting evidence. |
| 5 | **Prerequisite-aware planning states** | Direct links to What-if, Optimizer, and Net-Zero should never feel broken or silently redirect a user away from their intent. | Replace generic fallback routing with a purpose-built readiness panel, clear prerequisite explanation, and “Complete estimate” CTA that returns the user to the requested planner. | Preserve existing access controls and use only the current authenticated user’s data. |
| 6 | **History that teaches a pattern** | A private history page with no entries is accurate but passive; users need to see how new entries will become insight. | Add an empty-state timeline showing the next three meaningful milestones: first estimate, first monthly check-in, and enough history for a trend/forecast view. | Use illustrative structural states, not example emissions values or fake achievements. |
| 7 | **Organization action programme** | The existing role-aware assignment capability can become a strong differentiator for academic and organization demonstrations. | Give administrators a concise workflow: choose approved action, assign to an eligible member group, monitor accepted/self-reported/verified counts, and view only consent-filtered aggregates. | Do not show individual history in organization analytics; do not infer reductions from assignment status. |

## Recommended build order

The best first build is a **Personal Climate Journey**. It combines priorities 1, 3, 4, and 5 into a single user-facing system rather than adding another isolated page. The work should begin with the empty-data state because the copied database has no user records. A user should be able to complete a baseline or model estimate, receive an honest result, select one action, and understand the next data-recording step in one uninterrupted sequence.

| Release | User-visible outcome | Main screens affected | Expected implementation complexity |
|---|---|---|---|
| **Release A — First signal** | A user knows exactly how to obtain their first estimate and what becomes available afterward. | Signed-in home, Explore, protected planner entry states. | Moderate; primarily existing-route composition and state handling. |
| **Release B — Decision cockpit** | A completed result becomes a legible decision surface instead of an endpoint. | Prediction/baseline result, Plan entry, action recommendations. | Moderate; requires careful result-contract reuse and transparent comparison logic. |
| **Release C — Habit and history** | A user can build history through lightweight periodic records and see why it matters. | Progress, History, Forecast, action follow-up. | Moderate to high; requires a deliberately narrow activity model, migration, and tests. |
| **Release D — Organization programme** | Administrators can run privacy-aware action initiatives with meaningful status tracking. | Organization and Admin routes. | Moderate; builds on the existing assignment and verification infrastructure. |

## Visual direction: climate signal intelligence

The product should move from “clean green SaaS” toward an ownable **climate signal intelligence** system. The concentric CarbonSense mark is the appropriate visual language: a signal is detected, interpreted, compared, then acted upon. Use it consistently in the public hero, authentication, empty states, result headers, and section transitions. The mark can expand into restrained radar rings, contour lines, and soft signal halos; it should not become decorative noise.

The supplied screens demonstrate valuable hierarchy patterns: strong page title, short explanation, visible step/progress status, one primary action, and compact choice controls. Retain those patterns, but use Lucide-style iconography and the current brand motif rather than emoji. The result will feel more considered and more academically credible.

| Design element | Keep or change | Recommendation |
|---|---|---|
| Brand mark | **Keep and extend** | Use the concentric signal/radar mark on all surfaces, including Login and Register, rather than switching to the separate `C` tile. |
| Palette | **Refine** | Retain deep forest and soft mint. Add a semantic teal for evidence/data, amber for uncertainty or missing prerequisites, and clay/red only for review or attention states. Never use color as the only status indicator. |
| Hub layouts | **Recompose** | Replace card-directory-first layouts with a “current signal” or “what unlocks next” module at the top, then reveal tools below it. Each major hub should contain at least one genuine analytical artifact. |
| Cards | **Tighten** | Use larger, richer cards only for the currently recommended decision. Move secondary tools to denser supporting cards to prevent an all-cards-equal hierarchy. |
| Data visuals | **Increase carefully** | Prefer simple range bands, contribution bars, readiness rings, trend sparklines, and action-status timelines. These must be generated from the user’s actual stored data or rendered as explicitly non-data structural empty states. |
| Copy | **Sharpen** | Prefer “Compare the evidence boundary,” “Build the history needed for a forecast,” and “Model a lower-carbon path.” Avoid generic phrases such as “make a difference” and unqualified “AI-powered plan.” |
| Motion | **Use sparingly** | Use 160–240ms opacity/transform transitions for cards, tabs, and progress changes. Respect reduced-motion preferences and do not animate critical numbers as though they are verified outcomes. |

## Page-specific ideas

### Explore: make the first calculation feel purposeful

The current two-lens choice is conceptually sound. Above it, add a compact “Your first signal” panel that explains the trade-off in one sentence: the baseline is transparent and factor-based, while the model estimate is a fixed-contract inference with an explicit boundary. After selection, retain the supplied multi-step pattern: a visible step label, a completion bar, accessible visual choices, and one next button. A small save-and-resume indicator would reduce friction without asserting that a result already exists.

### Results: make interpretation the product moment

Replace any endpoint-like result layout with a composed result cockpit. Its top row should answer four questions: “What is the estimate?”, “What is the documented range or limitation?”, “Which inputs are most influential in this model output?”, and “What can I do next?” A comparison panel may show the transparent baseline beside the model estimate, but must keep their methods distinct. The call to action should route to the most relevant action or planner, rather than a generic tool hub.

### Plan: turn three tools into a sequence

The supplied planning screen’s target controls, percentage shortcuts, and time-horizon selection are useful interaction references. Reframe the current Plan hub around a single decision: “Choose the result you want to plan from.” Then reveal the optimizer for prioritisation, What-if for one-change comparison, and Net-Zero for staged planning. When no result is available, show why planning is blocked and use a return-to-plan flow after the user obtains one.

### Insights and Forecast: make readiness visible

The current forecast screen is exemplary in its honest `0/12` and `0/90` readiness messaging. Improve it with a visual readiness path showing the next user-controllable milestone, such as “Record your first monthly check-in.” When the data is insufficient, present the directional view as a planning aid, not a prediction. When a trend becomes available, show an actual trend line, range band, and source descriptor—not a decorative chart.

### Progress: reward evidence, not claimed impact

Keep CarbonQuest, but center it on verified participation and consistency. A weekly action panel, a habit streak that is tied to genuine check-ins, and transparent status chips (`accepted`, `self-reported`, `verified`) would make it more meaningful. Avoid gamification that awards points for a claimed kilogram reduction, because it would blur participation with proven outcome.

### Reports and organization views: make trust visible

The Report center already succeeds by showing scope, service health, and the model/data boundary. Reuse these trust-building components in summary pages. For organizations, present a programme overview with consent-filtered participation and completion states, a clear aggregate threshold, and an explicit “individual records are not shown here” guardrail.

## What not to add yet

Avoid adding a social feed, public individual leaderboards, offset purchasing, automatic emissions-reduction claims, or a general-purpose chatbot that is not grounded in authenticated user data and approved actions. These additions would dilute the product’s strongest advantage: a careful, explainable, privacy-aware decision-support experience.

## Suggested acceptance criteria for the first build

| Area | Acceptance criterion |
|---|---|
| First-use flow | A signed-in user with no stored entries can complete an estimate and is shown exactly one relevant next action. |
| Planner access | A user who opens a planner without a completed result sees a clear prerequisite state and returns to their intended planner after completing the required step. |
| Data honesty | The interface never represents self-reported or recommended reductions as verified real-world reductions. |
| Forecast integrity | Prophet activation messaging continues to require 12 consecutive completed months and 90 activity days; the fallback remains visibly directional. |
| Privacy | Organization interfaces show only consent-filtered aggregates and never individual histories. |
| Visual system | Login, registration, public, and workspace views use one CarbonSense signal mark and the same semantic color/typography system. |
| Responsive quality | The new journey, prerequisite state, and action loop work at desktop and mobile widths with keyboard-accessible controls. |

## Decision needed

Choose one of these implementation paths for the next change:

1. **Personal Climate Journey** — the recommended option; strongest user value and a coherent foundation for later improvements.
2. **Result cockpit redesign** — best if the immediate goal is a stronger demo after completing the existing questionnaire.
3. **Climate signal visual-system rollout** — best if the immediate goal is a visible design transformation without adding new data workflows.
4. **Organization action programme** — best if the primary audience is administrators or a university/organization deployment.

# CarbonSense product roadmap

## Product direction

CarbonSense is a climate-action platform that begins with individual carbon-footprint tracking and grows into a privacy-scoped organizational planning system. The core loop is: capture activity, estimate emissions, explain the estimate, recommend a practical action, record completion, and compare progress over time.

## MVP sequence

| Phase | Outcome | Primary users |
|---|---|---|
| 1. Measure | Survey estimate, activity ledger, history, assumptions, and privacy boundary | Individuals |
| 2. Act | Approved recommendations, goals, completion tracking, what-if planning, and reduction progress | Individuals |
| 3. Sustain | Directional forecasting, streaks, badges, CarbonQuest score, and grounded assistant | Individuals |
| 4. Coordinate | Regional/country aggregates, organization recommendation assignment, and completion monitoring | Organization viewers and admins |
| 5. Govern | Documentation, reported-query workflows, audit history, moderation, and platform administration | Super administrators |

## Data boundaries

Individual activity entries, goals, and recommendation completion records are private to the authenticated user by default. Organization views should expose only aggregated information for the organization scope, region, or country. Super-admin access should be limited to platform operations and should not become a shortcut around individual privacy controls.

## Product principles

CarbonSense should prefer transparent assumptions over false precision, directional forecasts over unsupported certainty, approved recommendation content over unconstrained advice, and measurable completion over unverified claims of impact. Gamification should reward consistent participation and completed actions, not fabricated emissions reductions.

## Current implementation slice

The Manus project now contains the activity ledger schema and procedures for transport, electricity, diet, and fuel entries; reduction goal persistence with validation; a four-category approved recommendation catalog; user acceptance and completion tracking; organization-scoped recommendation assignment; and responsive workspace panels for activity, goals, and recommendations. The next build phase should add real progress calculations from the ledger, forecast inputs based on stored activity history, and the governed assistant experience.

# CarbonSense GitHub Repository Feature-Parity Audit

**Reference repository:** `CarbonSense` GitHub project selected by the user  
**Comparison target:** Manus-hosted CarbonSense application  
**Audit date:** 19 August 2026

## Scope

The repository contains a React frontend, a FastAPI/Python backend, a MongoDB-oriented account and history layer, a trained Python model artifact, role-aware analytics, CarbonQuest gamification, PDF report export, and an IBM watsonx chat widget. The Manus version uses React, Express, tRPC, a managed SQL database for role-scoped application records, and MongoDB Atlas for native email/password credentials.

## Verified parity matrix

| Repository capability | Manus status | Parity action |
|---|---|---|
| Dashboard, About, Explore, Plan, Insights, and Progress hubs | Implemented in the repository-inspired UI shell | Verify every original hub tool is reachable from its matching hub |
| Native login and registration | Implemented with MongoDB-backed salted scrypt credential records | Keep the GitHub-style pages; retain Manus OAuth as a secure alternative |
| Access/refresh tokens and offline demo login | Deliberately not reproduced | Use secure HTTP-only signed sessions; do not add browser-stored demo credentials |
| Security-question password reset | Deliberately not reproduced | Replace with secure recovery workflow when an email provider is configured; knowledge-based answers are not an acceptable authentication factor |
| Prediction, baseline comparison, and feature explanation | Implemented with frozen 34-source/54-model-feature contract adapter and persistent history | Add any missing repository-style visual presentation and field coverage |
| Original Python joblib/XGBoost model artifact | Not executable in the default Node deployment | Document as a runtime boundary; exact artifact inference requires a Python-compatible deployment path or exported portable model |
| Optimization and what-if planning | Implemented | Direct Optimizer, What-If, and Net-Zero routes now provide repository-style sliders, scenarios, staged pathways, and secured procedure calls |
| Forecast and net-zero planner | Implemented | Activity-ledger directional forecast and staged net-zero pathway remain clearly labeled as estimates |
| Personal history | Implemented and scoped to the authenticated user | Repository-style history remains available; printable report cards now include recent saved estimates |
| Profile editing | Implemented | Name, country, and region controls persist through a scoped authenticated procedure |
| CarbonQuest: streak, score, badges, leaderboard, rank, refresh | Implemented with evidence boundary | Score, streak calendar, badges, and aggregate cohort cards are present; no fabricated individual leaderboard entries are displayed |
| Contributor map, continent picker, country/region detail | Implemented as map-equivalent aggregate view | Country and region bars are derived solely from consented organization records; external map assets are not required |
| Organization/admin dashboard | Implemented with stronger privacy boundaries | Aggregate country, regional, and six-week trend views are available; zero-data states remain explicit |
| Super-admin user management | Implemented | Role and active/inactive account controls are audit logged and prevent self-role-change or self-deactivation |
| PDF report download | Implemented as browser print-to-PDF | The report center provides a private print layout, model metadata, recent records, and synthetic-data disclosure |
| IBM watsonx Assistant widget | Implemented as a role-adaptive secure fallback shell | Live watsonx connectivity still requires a user-supplied authorized IBM Assistant ID and approved integration configuration |
| Health and model-information endpoint | Implemented | The printable report center shows live service and MongoDB credential-store status, the model version, and an explicit unavailable-health state; frozen-dataset disclosure is retained |
| Advanced CarbonSense additions absent from repository | Implemented | Retain activity ledger, goals, verified recommendations, privacy consent, governance reports, and audit history; these strengthen rather than replace repository flows |

## Implementation order

1. Decide whether the trained Python joblib/XGBoost artifact must execute unchanged in production. This is a deployment-runtime decision, not a UI-only change.
2. If live IBM watsonx web chat is required, supply its authorized Assistant ID and approved integration configuration.
3. Replace the temporary Atlas Admin database user with the documented `carbonsense_app` least-privilege account before production publication.

## Validation evidence

The feature-parity implementation has been checked with a complete regression suite, TypeScript validation, production build, and desktop/mobile preview capture for direct planner, profile, user-management, CarbonQuest, contributor, report, and administrator routes. The completed suite contains **49 passing tests** across 12 test files, including deterministic quest-rank behavior, report-health rendering, profile updates, role and active-status governance audits, and report status workflows.

## GitHub source re-validation

On 19 August 2026, the current `main` branch of the selected GitHub repository was rechecked against the Manus route dispatcher and tRPC procedure set. The reference routes—Dashboard, About, Explore, Plan, Insights, Progress, Predict, Baseline, Optimize, What-If, History, Profile, Quests, Contributors, Forecast, Net-Zero, and both administrator routes—are all present in the Manus application or intentionally represented by a stronger privacy/security equivalent. The GitHub API endpoints for prediction, baseline, explanation, planning, history, quest metrics, contributor aggregation, administration, health/meta, reporting, and chat likewise have matching secure procedures.

The only retained differences are deliberate: no browser-stored offline/demo credentials, no security-question recovery, no public individual contributor map, no claim that the Python artifact executes in the Node runtime, and no live IBM watsonx integration without user-supplied authorization. No additional repository-aligned code correction was required by this re-validation.

## Security and scientific integrity boundaries

The parity work will not reintroduce repository offline demo accounts, browser-stored credentials, or security-question-based password recovery. MongoDB stores only native login credential records; the managed application database remains authoritative for roles, OAuth users, private activity records, goals, and governance data. The frozen synthetic-data disclosure and current model-runtime note must remain visible in reports and prediction screens.

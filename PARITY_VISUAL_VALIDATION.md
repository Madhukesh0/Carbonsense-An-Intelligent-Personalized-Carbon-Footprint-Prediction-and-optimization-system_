# Repository-Parity Visual Validation

**Date:** 19 August 2026

The managed project preview rendered the current authenticated CarbonSense session at desktop and mobile widths. The primary parity routes showed the expected repository-style shared shell, account chip, role-aware Admin navigation, and floating role-adaptive assistant launcher.

| Route group | Desktop result | Mobile result |
|---|---|---|
| `/optimize`, `/whatif`, `/netzero` | Dedicated planner cards and direct route layouts rendered | Planner layouts stack correctly at narrow width |
| `/profile`, `/admin/users` | Profile form and audited user management rendered | User roster uses stacked cards rather than a clipped table |
| `/quests` | Score, streak grid, badge card, aggregate leaderboard filter, rank, and refresh control rendered | Score and streak remain readable with a single-column flow |
| `/contributors` | Country and grid-cohort filters render above aggregate bars | Both filters remain reachable and stacked on mobile |
| `/reports` | Print/save-PDF control, recent history, model boundary, and live health metadata render | Report summary remains readable and print action stays available |
| `/admin` | Aggregate metrics, explicit zero-data state, filters, and organization summary surface render | Metric cards stack vertically with no horizontal clipping |

The visual tests also confirmed two important empty states: country/organization aggregate panels state when no consented aggregate data is available, and the administrator trend area does not render non-zero-looking bars when there are no consented records.

The report center was rechecked after the final server restart. Its live health state resolved to **CarbonSense service running** with the MongoDB credential store connected to the `carbonsense` database; its printable boundary text still states that the synthetic contract is not a direct emissions measurement. The corresponding automated render test also covers the explicit unavailable-health presentation.

An attempt to open `/quests` through the enabled **My Browser** connector on 19 August 2026 still reported a Sandbox browser context and showed the protected sign-in screen. Therefore, user-personal-browser evidence remains intentionally unrecorded; managed-preview authenticated evidence and regression coverage are documented above.

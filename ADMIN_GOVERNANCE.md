# CarbonSense administrator governance

CarbonSense separates individual activity records from organization analytics. Organization and contributor views include only members who opt into aggregate sharing through the privacy control. The product exposes region and country aggregates, assigned recommendation completion counts, and verified completion counts; it does not expose an individual’s activity ledger, goals, or personal recommendation details to organization viewers.

Recommendation completion has two states. A user may mark an assigned action as self-reported, but that action does not earn verified gamification credit. An organization administrator or super administrator may review the completion and mark it verified. Every verification writes an immutable governance audit record containing the actor, organization, entity, action, and timestamp.

Report requests cover data questions, privacy concerns, recommendation feedback, technical issues, and other support matters. Administrators can move reports through open, in-review, resolved, and dismissed states within their authorized organization. Each status transition is recorded in the governance audit log. Super administrators can inspect the full audit stream and user roster.

Forecasts and scenario plans are directional decision-support tools. They use stored activity history when available, expose uncertainty ranges, and must not be presented as verified emissions measurements or guaranteed future outcomes. The assistant is grounded in the authenticated user’s activity summary, active goal, recommendation state, and approved recommendation catalog.

## Operational review sequence

1. Confirm that the user or organization has the required role and that organization scope matches.
2. Confirm aggregate-sharing consent before reviewing organization-level analytics.
3. Review the evidence supplied for a completed recommendation.
4. Mark the action verified only when the evidence is sufficient; otherwise leave it self-reported.
5. Record and resolve report requests through the governance queue.
6. Use the audit log to review status changes, verification actions, and accountability.

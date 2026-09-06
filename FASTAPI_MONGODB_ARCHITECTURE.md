# CarbonSense FastAPI + MongoDB Architecture Contract

## Objective

CarbonSense will retain its React/Vite user interface and replace the Node/Express/tRPC backend with a single FastAPI application. The FastAPI service will serve the built React application, expose versioned JSON APIs under `/api/v1`, own JWT-based authentication and role-based access control, persist application data in MongoDB, and run the current Python prediction and baseline logic in-process.

The migration must preserve the current product boundaries: model estimates remain indicative, baselines remain source-and-proxy transparent, forecasts remain eligibility-gated, organization comparisons remain consent-filtered, and individual histories remain private.

## Target deployment shape

```text
Browser
  └─ React + Vite + React Query
       └─ same-origin /api/v1 calls with secure JWT cookies
            └─ FastAPI application
                 ├─ JWT / RBAC / CSRF dependencies
                 ├─ MongoDB repositories
                 ├─ Prediction service: frozen XGBoost + preprocessor + contributions
                 ├─ Baseline service: declared factor set + screening proxies
                 ├─ Planning, history, insight, progress, governance, report services
                 └─ Static React build hosting
                      └─ MongoDB collections and indexes
```

The production image will continue to start from Python 3.12, install Node 22 only to build the React bundle, copy the built Vite output, and run Uvicorn with the platform-provided `PORT`.

## FastAPI module layout

```text
backend/
  app/
    main.py                 # FastAPI lifespan, CORS, static React hosting, router registration
    core/
      config.py             # typed environment settings
      security.py           # JWT issue/verify, Argon2 password hashes, cookie + CSRF policies
      dependencies.py       # current user, current active user, role and organization guards
    db/
      mongo.py              # Motor client lifecycle, collections, indexes
      repositories/         # user, run, activity, goal, recommendation, report, audit access
    schemas/                # Pydantic request/response contracts
    routers/                # auth, profile, model, tools, activity, analytics, organization, admin, reports
    services/
      prediction.py         # frozen artifact verification, preprocessing, XGBoost, grouped contributions
      baseline.py           # declared factors, proxy assumptions, breakdown and sources
      planning.py           # Net-Zero, Optimizer and What-if logic
      forecasting.py        # activity eligibility and Prophet/directional fallback
      governance.py         # consent-filtered aggregates and audit writes
    ml_artifacts/           # read-only model, preprocessor, metadata and manifest
  migration/
    mysql_to_mongo.py       # explicit one-time migration script, dry-run and idempotent modes
```

## Collection and index contract

| MongoDB collection | Replaces | Required fields / indexes |
|---|---|---|
| `users` | `users`, `credential_accounts` | Unique `email`, unique `legacy_user_id` where imported, role, organizationId, active status, consent, Argon2 password hash, timestamps. |
| `sessions` | Express session cookies | Hashed refresh-token identifier, userId, expiry, revokedAt, client metadata; TTL index on expiry. |
| `footprint_runs` | `footprint_runs` | userId + createdAt index; organizationId + createdAt index; runType; inputPayload; results; baseline/reduction values; modelVersion. |
| `activity_ledger` | `activity_ledger` | userId + activityDate index; organizationId + activityDate index; category, quantity, unit, co2Kg, source. |
| `carbon_goals` | `carbon_goals` | userId + status index; baseline, target, deadline, timestamps. |
| `recommendations` | `carbon_recommendations` | Unique recommendation key and approved catalog details. |
| `user_recommendations` | `user_recommendations` | userId + status and organizationId + status indexes; verification provenance. |
| `report_requests` | `carbon_report_requests` | userId + createdAt, organizationId + status, category, resolution workflow. |
| `governance_audit_logs` | `carbon_governance_audit_logs` | actorUserId + createdAt and organizationId + createdAt indexes. |

Every imported row will retain its source primary key in a `legacy_id` field to make the process idempotent and traceable. MongoDB `_id` values will not be exposed as authorization inputs; the authenticated JWT subject remains the primary ownership check.

## JWT and RBAC boundaries

FastAPI will use short-lived access tokens and rotating refresh sessions. Access tokens will be sent in a secure, HTTP-only, same-origin cookie. State-changing requests will require a CSRF token header derived by the application rather than trusting a browser cookie alone. Passwords will be stored only as Argon2 hashes. Logout revokes the server-side refresh session and clears both cookies.

The role vocabulary remains `individual`, `org_viewer`, `org_admin`, and `super_admin`. Dependencies will enforce three separate conditions: an authenticated active user, the required role, and organization membership where applicable. The role of a requester will be read from a fresh user record where authorization affects governance or administration, not trusted blindly from stale display state.

Organization queries must continue to filter member records by `shareAggregates` before calculating country, regional, or average results. No API will return another person’s `inputPayload`, private run history, activity ledger, goals, or individually identifiable recommendation state to an organization viewer.

## API and frontend migration contract

React routes and visual components are retained. `client/src/lib/trpc.ts` is replaced by a typed same-origin API client and React Query hooks. The first FastAPI release uses `/api/v1` resources instead of tRPC procedure calls while preserving response fields needed by the existing UI.

| Current capability | FastAPI route group |
|---|---|
| Account / profile / logout | `/api/v1/auth`, `/api/v1/profile` |
| XGBoost metadata, prediction, explanation, baseline, QA preview | `/api/v1/model` |
| What-if, Net-Zero, Optimizer | `/api/v1/planning` |
| Activity ledger, progress, goals, recommendations | `/api/v1/activity`, `/api/v1/goals`, `/api/v1/recommendations` |
| History, forecast, dashboard | `/api/v1/insights` |
| Contributor coverage, organization recommendations | `/api/v1/organization` |
| Reports, user administration, audit | `/api/v1/reports`, `/api/v1/admin` |

The FastAPI prediction service will directly import the existing frozen Python contract, load the artifact once during the application lifespan, verify SHA-256 manifest hashes, and protect the model with a process-level lock/semaphore. It will not create a Node child process. The baseline service will preserve the exact declared factor set, source links, proxy calculations, and disclaimer fields.

## Data migration safeguards

The one-time migration script must run first in `--dry-run` mode and produce counts by collection and ownership scope. The production mode must upsert by `legacy_id`, never delete source MySQL records, and verify:

1. User, run, activity, goal, recommendation, report, and audit row counts match the scoped source export.
2. A sampled set of prediction/baseline pairs retains identical source payloads, run type, timestamps, and model version.
3. Every migrated object with user scope points to an existing MongoDB user with the matching legacy identifier.
4. Aggregate-consent flags, role values, organization IDs, verification fields, and active-account state are preserved.
5. No password hash is copied from the unconfigured native credential path; new JWT-native credentials are created through controlled account setup or explicit password-reset flow.

The current MySQL/TiDB database remains read-only and available until the FastAPI release has passed feature-parity, privacy, authorization, and recovery checks.

## Definition of safe cutover

FastAPI becomes the production server only after the React client has been switched to the typed REST hooks; all current critical route families pass regression tests; migration reconciliation passes; a fresh JWT user can complete prediction, baseline, planning, history, and sign-out flows; consent filters and role forbiddance are tested; and a rollback checkpoint exists for the current Node/tRPC version.

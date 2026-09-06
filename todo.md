
## CarbonSense definitive scope

- [x] Climate-tech landing page with white/light-gray surfaces, deep navy text, green CTAs, rounded cards, and responsive desktop/mobile layout.
- [x] Manus OAuth authentication with protected and role-specific routing.
- [x] Individual, org_viewer, org_admin, and super_admin role model and enforcement.
- [x] Auth-scoped per-user footprint history and organization-level isolation.
- [x] 34-field AI prediction survey with supported-category validation and visible region selector.
- [x] Serialize recycling and cooking multi-select values as JSON arrays.
- [x] Contract-aware XGBoost-style prediction procedure with model/dataset version, region, target definition, uncertainty range, and synthetic-target disclaimer.
- [x] Real signed SHAP-style feature contributions with labels, directions, base value, and reconciliation.
- [x] Transparent baseline calculator with IPCC and DEFRA factor citations and assumptions.
- [x] ML versus baseline comparison with absolute and relative difference explanations.
- [x] Reduction optimizer, action plan, what-if simulator, and recommendation explanations.
- [x] History, progress, streaks, CarbonQuest badges, score, leaderboard, and rank.
- [x] Forecast, phased net-zero planner, contributor analytics, and PDF report export.
- [x] Individual and organization admin analytics plus super-admin user management.
- [x] Global React error boundary and loading, empty, error, and unauthenticated states.
- [x] Vitest coverage for contract validation, auth scoping, role enforcement, prediction metadata, SHAP reconciliation, and baseline assumptions.
- [x] Responsive visual verification and production build verification.

## Follow-up hardening

- [x] Expose the exact 34-column canonical contract and derived-field preview in the survey and model metadata.
- [x] Make the model implementation boundary explicit and artifact-backed where the Node runtime permits; do not overclaim SHAP/XGBoost semantics.
- [x] Add visible recommendation explanations and dedicated forecast/net-zero/contributor/report states.
- [x] Add consistent loading and error states for all data-fetching pages and mutations.

## Prediction pipeline and contribution clarity

- [x] Audit the active `individual_10k_regional_v1` / frozen-model feature pipeline, including survey defaults and the source of the displayed prediction range.
- [x] Move detailed synthetic-target and non-causal contribution language from the primary result screen into accessible documentation while retaining required source transparency.
- [x] Present real-time ranked feature contributions for each submitted prediction using accurate non-causal terminology and test the visible contract.
- [x] Surface the prediction-runtime audit, synthetic-target boundary, and contribution interpretation on the linked in-app `/about` methodology page.
- [x] Add regression coverage verifying the in-app methodology page contains the moved prediction-boundary documentation.

## Live GitHub XGBoost inference

- [x] Copy and integrity-check the selected GitHub `best_carbon_model.joblib`, persisted 54-feature preprocessor, and model metadata for project runtime use.
- [x] Add an authenticated Python inference bridge that transforms submitted survey data through the exact frozen preprocessor and returns XGBoost predictions.
- [x] Replace adapter-only contributions with model-native per-prediction XGBoost contribution values while retaining non-causal interpretation boundaries.
- [x] Add a deploy-compatible Python/XGBoost runtime, resource-safe model loading, and production build configuration.
- [x] Add artifact-inference parity tests, regression coverage, and desktop/mobile verification of the deployed model result experience.
- [x] Capture desktop and mobile evidence from the secure non-persistent XGBoost QA result, including the live-model label, RMSE range, and grouped contribution breakdown.
- [x] Record route-specific visual verification notes for the deployed prediction result experience.
- [x] Add a super-admin-only non-persistent XGBoost QA preview route for live result-screen verification without writing test data.

## Archived by user — reduced-feature model experiment

- [x] Archived, not implemented: a compact question-count specification was drafted and then withdrawn at the user’s request before any model or production change.
- [x] Archived, not completed: only a read-only artifact-importance check was run; frozen CSV data was unavailable, so coverage, correlation, missingness, leakage, and held-out analysis were not performed.
- [x] Archived, not implemented: no 20-feature or compact XGBoost candidate was trained, compared, or proposed for production.
- [x] Recorded decision: retain the deployed frozen 34-input / 54-feature `xgb-final-54f-v2` model unless the user explicitly reopens a separately scoped experiment with the frozen CSV files.

## User perspective roadmap

- [x] Define the MVP journey from activity capture to footprint result, recommendation, and repeat tracking.
- [x] Add a persistent individual activity ledger for transport, electricity, diet, and fuel inputs.
- [x] Add user goals, reduction targets, and progress-over-time views backed by stored history.
- [x] Add scenario-based forecasting using the user’s stored history and clearly labeled uncertainty.
- [x] Add recommendation delivery, acceptance, completion, and reduction-impact tracking.
- [x] Add gamification that rewards verified completion and consistent tracking without fabricating outcomes.
- [x] Add an AI climate assistant grounded in the user’s own data and approved recommendation catalog.
- [x] Add organization workflows for regional/country aggregation, recommendation assignment, and completion monitoring.
- [x] Add privacy controls separating individual records from organization-level aggregates.
- [x] Add administrator documentation, report/query governance, audit history, and moderation workflows.
- [x] Write product and technical documentation describing roles, data flows, MVP limits, and future phases.

- [x] Implement a real goal-progress calculation from stored activity history and render its trend/progress view.
- [x] Add tests covering goal progress calculations and stored-history-backed progress output.

- [x] Add exact deterministic assertions for weekly progress totals, currentKg, progressPercent, and goal metadata isolation.

- [x] Verify activity progress ignores mixed-user history and goal data at the endpoint contract boundary.

## Final roadmap hardening

- [x] Implement true scenario-based forecasting with user-selectable changes and visible uncertainty bands.
- [x] Add a verification state for completed recommendations before awarding gamification credit.
- [x] Ground assistant responses in the authenticated user’s activity, goals, and accepted actions.
- [x] Add country aggregation and assigned-recommendation completion monitoring for organizations.
- [x] Apply aggregate-sharing consent filtering to every organization analytics endpoint.
- [x] Add audit-log persistence for report status changes and explicit administrator governance documentation.

- [x] Include accepted-but-not-completed recommendations explicitly in assistant context, response, UI, and tests.
- [x] Render organization country aggregates visibly and cover the exposed client contract.

- [x] Surface accepted-but-not-completed actions visibly in the assistant panel with a clear pending-action context summary.

## Bug fix: ProductPage hook order

- [x] Fix `/about` rendered-fewer-hooks error caused by ProductPage early return before all hooks execute.
- [x] Verify `/about`, authenticated workspace routes, tests, TypeScript, and production build after the hook-order fix.

- [x] Gate all protected ProductPage queries and mutations by authentication and role scope after moving route guards below hooks.
- [x] Add regression coverage or focused verification that unauthenticated protected routes do not fire protected queries.
- [x] Re-verify /about and protected routes after auth-gating the ProductPage data layer.

- [x] Add explicit role guards to admin and super-admin ProductPage query enabled conditions.
- [x] Gate the ProductPage admin report-status and recommendation-verification handlers at the UI interaction boundary for authentication and role scope.
- [x] Add focused regression coverage for unauthorized /admin and /admin/users query suppression.

- [x] Add a focused ProductPage source-contract regression test for unauthorized admin query suppression.
- [x] Narrow the completed mutation-gating checklist item to the admin mutation handlers actually hardened.

- [x] Ensure the client route-gating regression test is discovered by Vitest and confirm the test count increases.

## Final dataset selection

- [x] Profile all eight candidate files for row count, columns, types, missingness, duplicates, and target fields.
- [x] Compare candidate datasets against the CarbonSense 34-raw/54-transformed contract.
- [x] Check target leakage, target scale, synthetic-generation indicators, and train/test compatibility.
- [x] Select one final training dataset and document why the others are retained, rejected, or used only for context.
- [x] Prepare a migration plan for the selected dataset, preprocessing, model retraining, metadata, and validation.

## Beginner dataset decision

- [x] Profile the newly uploaded eight files and identify duplicate transformations.
- [x] Give one clear dataset to keep for the current model.
- [x] List files to ignore or retain only as intermediate/source/context data.
- [x] Define the exact fixes needed for the selected dataset and model pipeline.

## Dataset freeze through May 2027

- [x] Freeze `individual_10k_regional_engineered.csv` as the human-readable canonical source baseline.
- [x] Freeze `preprocessed_full_10k.csv` as the current ML model input baseline.
- [x] Verify the uploaded frozen files match the 34-feature source and 54-feature model-ready contract.
- [x] Document that dataset changes require explicit approval and a new version after May 2027.

## Repository-matched interface rebuild

- [x] Inspect the selected GitHub repository’s layouts, screens, components, styling, and interactions.
- [x] Map the reference interface to the existing Manus-hosted routes and data contracts.
- [x] Recreate the reference navigation, page layouts, visual system, and principal user flows.
- [x] Add or update regression tests for the recreated route and interface contract.
- [x] Verify the rebuilt interface visually at desktop and mobile sizes before checkpointing.

## Repository hub parity follow-up

- [x] Rework the Explore hub so prediction and baseline are presented as the reference repository’s focused hub workflows.
- [x] Rework the Plan, Insights, and Progress hubs into reference-style grouped layouts while preserving existing secured data procedures.
- [x] Verify desktop and mobile views for all primary hubs, including the signed-in and role-aware admin states.

## Authenticated interface evidence

- [ ] Record the authenticated desktop and mobile verification evidence for Explore, Plan, Insights, and Progress. **Blocked:** requires a connected personal browser session.
- [ ] Record the super-admin desktop and mobile verification evidence for the Admin interface. **Blocked:** requires a connected super-admin personal browser session.
- [ ] Verify the signed-in CarbonSense routes through the user’s personal browser connector rather than the sandbox browser. **Blocked:** browser actions still report Sandbox.
- [ ] Save the repository-interface checkpoint after the authenticated personal-browser verification is completed.
- [ ] Open the Google sign-in flow through the user’s connected personal browser without handling credentials.

## Clean sandbox restart

- [x] Restart the CarbonSense sandbox development services cleanly at the user’s request.
- [x] Confirm the restarted preview is healthy before retrying the personal-browser connector.

## Repository-style authentication

- [x] Inspect the selected repository’s login, registration, password-reset, and authentication routing patterns.
- [x] Recreate the repository-style authentication screens while retaining secure Manus OAuth session handling.
- [x] Route the existing sign-in and protected-workspace calls to the recreated authentication experience.
- [x] Add regression coverage for login, register, and protected-route authentication behavior.
- [x] Verify authentication screens visually at desktop and mobile sizes.
- [x] Add a prominent sign-up entry point to the sign-in experience and validate its route.
- [x] Display accurate registration and sign-in storage boundaries for MongoDB Atlas, the application database, and browser-local data.
- [x] Add regression coverage and desktop/mobile verification for the sign-up and storage-transparency interface.

## Post-authentication restart

- [x] Restart the CarbonSense development services after the repository-style authentication update.
- [x] Confirm the restarted login preview is reachable and healthy.

## MongoDB-backed authentication

- [x] Compare MongoDB-backed native account storage with the existing managed-database path and document the selected scope.
- [x] Add a secure `MONGODB_URI` configuration only after the user provides the MongoDB connection string.
- [x] Move native credential registration and login lookup to MongoDB without weakening password hashing or session issuance.
- [x] Preserve Manus OAuth and existing role-protected CarbonSense workflows during the MongoDB migration.
- [x] Add MongoDB authentication regression coverage and verify the login interface remains visually consistent.

## MongoDB authentication validation follow-up

- [x] Add an integration test for MongoDB-backed registration, login, duplicate-email protection, and legacy credential migration.
- [x] Re-run desktop and mobile visual verification for login, registration, and protected-route redirect behavior after the MongoDB migration.
- [x] Record the MongoDB credential-storage boundary and managed-database role/OAuth boundary in project documentation.

## MongoDB Atlas provisioning

- [x] Create or access the user’s MongoDB Atlas account and a dedicated CarbonSense project.
- [x] Create a free MongoDB deployment for CarbonSense.
- [ ] Create a least-privilege CarbonSense database user and configure required network access.
- [x] Obtain the MongoDB connection string without exposing its password in chat.
- [ ] Complete Atlas hardening and authenticated verification without temporary-email identities or disposable production accounts.
- [x] Make the non-mutating MongoDB integration test tolerant of observed hosted-Atlas replica-set latency without changing authentication behavior.

## GitHub repository feature parity

- [x] Inventory every GitHub repository frontend route, backend endpoint, data model, role flow, and dependency.
- [x] Produce a feature-by-feature parity matrix against the Manus-hosted CarbonSense application.
- [x] Implement all verified missing or mismatched repository features while preserving security and data-honesty safeguards. The watsonx-style assistant remains securely grounded until IBM credentials are supplied.
- [x] Add regression tests and desktop/mobile visual verification for each feature-parity change.
- [x] Document remaining intentional differences, if any, with their technical or security rationale.

## Repository parity implementation batches

- [x] Add repository-style direct Optimizer, What-If, and Net-Zero route experiences using the existing secure planning procedures.
- [x] Add repository-style Profile editing, country/region fields, account status controls, and audited super-admin role management.
- [x] Expand CarbonQuest with score, streak calendar, badges, rank, country-aware leaderboard, and refresh behavior.
- [x] Expand contributor and administrator analytics with country/region filtering, trend charts, organization summaries, and privacy-scoped map-equivalent views.
- [x] Add repository-style report download, model/health metadata, and clearly labeled synthetic-data boundaries.
- [x] Add the role-adaptive watsonx-style assistant shell and document the IBM credential requirement for live watsonx connectivity.

## Parity visual refinement

- [x] Replace the clipped mobile super-admin roster table with an accessible stacked member-card layout.
- [x] Replace the zero-data administrator trend bars with an explicit no-consented-aggregate empty state.

## Repository parity validation follow-up

- [x] Add CarbonQuest rank, country-filtered aggregate leaderboard, and refresh interaction with behavior-focused tests.
- [x] Add privacy-scoped country/region filters and organization-summary interactions to contributor and administrator analytics.
- [x] Add health and model-status metadata to the printable report center and test its available/unavailable states.
- [x] Add interaction-focused tests for the new planning, profile, admin, quest, contributor, and report procedures.
- [ ] Re-run authenticated desktop/mobile visual verification for all protected repository-parity routes through an attached personal browser session.

## Final parity-test evidence

- [x] Extract and test CarbonQuest rank calculation for eligible and non-eligible aggregate participants.
- [x] Render and test the printable report center's available and unavailable service-health states.
- [x] Add isolated mock-backed success-path assertions for profile updates, audited super-admin changes, and report create/list/status procedures.
- [x] Add mock-backed successful active/inactive account-control coverage with its governance audit record.

## GitHub source re-validation

- [x] Compare the current Manus code against the selected GitHub CarbonSense source and identify any remaining present-code mismatch.
- [x] Implement and test any repository-aligned correction found during the re-validation. No additional safe correction was required; intentional differences are documented in `FEATURE_PARITY_AUDIT.md`.

## Industry-standard visual-system redesign

- [x] Define and apply a cohesive climate-tech color, typography, spacing, radius, elevation, and focus-state token system.
- [x] Refine the shared shell, navigation, buttons, cards, forms, and data surfaces for clearer hierarchy and accessibility.
- [x] Redesign the landing, hub, planning, reporting, and administration views with responsive compositions and purposeful motion.
- [x] Add UI regression coverage and verify the redesigned public and protected routes at desktop and mobile widths.
- [x] Capture post-redesign desktop verification for the direct planner and report-center routes.
- [x] Capture post-redesign mobile verification for a redesigned protected hub route.

## Sustainability-app experience refinement

- [x] Research established carbon-footprint and sustainability-app patterns for onboarding, progress, actions, trust, and data visualization.
- [x] Define an original CarbonSense visual direction with improved typography, eco-aware color grading, and accessible data hierarchy.
- [x] Implement the selected high-value refinement across the landing, prediction, progress, and action experiences.
- [x] Add regression coverage and desktop/mobile verification for the sustainability-app-inspired experience updates.

## Interactive frozen-model questionnaire

- [x] Audit the current prediction survey against all 34 frozen raw input fields and its 34 → 54 XGBoost submission contract.
- [x] Make every frozen model input directly user-editable through a guided, accessible multi-step form with clear labels, units, and allowed choices.
- [x] Add validation and regression coverage that confirms complete 34-input capture and submission without changing model defaults or preprocessing.
- [x] Verify the complete interactive questionnaire at desktop and mobile widths, including the prediction hand-off and error states.

## Submitted-profile inference explanation

- [x] Reconstruct the values visible in the user’s submitted questionnaire screenshots and verify their 34-column feature engineering path.
- [x] Re-run the deployed XGBoost artifact for the reconstructed profile and reconcile the displayed prediction with its grouped tree contributions.
- [x] Explain in plain language which portions are deterministic mathematics, which portion is trained-model inference, and what the live XGBoost contribution values mean.

## Input-to-model presentation slide

- [x] Create a presentation-ready slide explaining the 21 user-entered controls, 20 model-relevant inputs, and the frozen 34 → 54 XGBoost transformation.

## Persisted model feature-importance explanation

- [x] Extract the dominant global XGBoost features from the persisted model and distinguish them from the preprocessor’s transformation role.
- [x] Map the highest-ranked transformed features back to user-facing questionnaire fields and explain their difference from a user-specific contribution breakdown.
- [x] Save the verified persisted-model feature-importance explanation as a reusable project note.

## Final dataset and training-artifact audit

- [x] Verify the frozen dataset governance, artifact hashes, and 34-column / 54-feature contract alignment; the audit found a material provenance mismatch between the retained preprocessed CSV and the deployed artifact.
- [x] Validate live persisted model/preprocessor inference and review the available evaluation metadata for detectable errors or limitations.
- [x] Document the audit findings with a clear conclusion on what is verified, what is limited, and what cannot be claimed from the available artifacts.

## User-approved model preservation decision

- [x] Record the owner decision to preserve the deployed 34-input / 54-feature XGBoost artifact without retraining, feature reduction, or dataset/model replacement.

## Transparent baseline factor refresh

- [x] Audit the current transparent-baseline formulas, input mappings, source citations, and regression tests.
- [x] Research and select current authoritative factor sources compatible with the available transport, energy, diet, waste, and travel inputs.
- [x] Implement a versioned baseline-factor update with source documentation while preserving the frozen XGBoost artifact unchanged.
- [x] Add regression coverage and verify the updated transparent baseline calculation and user-facing source disclosure.

## Result-led What-if Simulator

- [x] Require a completed AI prediction and transparent baseline before opening What-if comparisons.
- [x] Reuse the authenticated user’s completed result profile as the starting scenario without browser-stored credentials or cross-user data exposure.
- [x] Add regression coverage and responsive verification for the result-led scenario workflow.

## Result-led Reduction Optimizer

- [x] Audit the current optimizer method and repository behavior, including whether it is linear programming or a transparent rule-based planner.
- [x] Require a completed AI prediction and transparent baseline before opening the optimizer, and reuse the authenticated result values as its starting point.
- [x] Add method disclosure, regression coverage, and responsive verification for the result-led optimizer workflow.

## Result-led recommendations

- [x] Audit the current recommendation catalog and route against the completed AI prediction and transparent baseline data.
- [x] Require a completed result before recommendations and generate traceable actions from the matched AI/baseline profile.
- [x] Add recommendation provenance, regression coverage, and responsive verification for the result-led workflow.

## CarbonSense product assessment

- [x] Review the implemented capabilities, validation evidence, scientific boundaries, security posture, and outstanding hardening items.
- [x] Produce an evidence-based pros-and-cons assessment with prioritized next steps for final-year project and public demonstration use.

## CarbonSense improvement roadmap

- [x] Create a prioritized roadmap that distinguishes stable features to keep, high-value final-year improvements, deferred production work, and changes to avoid.

## Organization-aware recommendations

- [x] Audit organization membership, administrator assignment, and completed-result recommendation flows.
- [x] Add a combined recommendations section that clearly separates profile-matched AI/baseline actions from organization-assigned actions for registered members.
- [x] Add scope, source-attribution, acceptance, and responsive verification coverage for organization-aware recommendations.

## Homepage improvement direction

- [x] Review the current first-page hierarchy and develop a prioritized homepage improvement direction for user approval.

## Comparable sustainability platform research

- [x] Research comparable carbon-footprint and sustainability platforms, provide direct website links, and identify relevant CarbonSense homepage patterns.

## Additional calculator website research

- [x] Research additional public carbon-footprint calculator websites, their direct links, and their methodology scope for comparison.

## Homepage eco-sustainability hero

- [x] Replace the “Two-Lens Climate Frame” homepage hero treatment with an original eco-sustainability image and validate it responsively.
- [x] Expand the sustainability image into a full-bleed homepage hero background while preserving readable content and responsive composition.
- [x] Increase the full-bleed homepage hero size and refine the responsive content composition.
- [x] Make the sustainability image the dominant homepage-hero focal point with an image-led desktop composition and maintained text contrast.
- [x] Restore the prior image-led homepage hero by removing the later workflow cue and transition-polish adjustments at the user’s request.
- [x] Refine homepage typography hierarchy and eco-sustainability color grading for stronger visual coherence and accessible contrast.

## Documentation-focused homepage simplification

- [x] Add a Docs navigation destination for model contract, methodology, data limitations, and privacy information; remove the duplicate homepage evidence badge, evidence metrics, and baseline callout.

## Hub interface simplification

- [x] Remove the Signal frame metrics block from the Explore, Plan, Insights, and Progress hub header.

## Visual questionnaire redesign

- [x] Redesign the four-step AI prediction questionnaire with clear sliders, segmented choices, visual option cards, and multi-select chips while preserving all 21 controls and validation.
- [x] Reorganize the four-step questionnaire into clear demographic, energy and mobility, routine, and circular-habit sections without changing its 21 source inputs.
- [x] Remove the duplicate `energy_efficiency` field causing a React non-unique key warning on the prediction questionnaire.
- [x] Rename the questionnaire Sex field to Gender, clarify the regional-grid choice in plain language, and label grocery spending in Indian rupees without altering model values.
- [x] Add an optional display-only currency selector for grocery spending without changing the frozen model’s numeric input.
- [x] Run and document 100 deterministic non-user XGBoost scenarios covering low, typical, and high-impact profiles, with contribution reconciliation checks.
- [x] Improve the saved AI result with a clear “What is influencing this result?” explanation based on live XGBoost contributions.
- [x] Export the documented deterministic 100-scenario XGBoost QA matrix to a clearly labeled Excel workbook.
- [x] Export the deterministic 100-scenario XGBoost QA evidence to a clearly labeled Word document.
- [x] Export a plain-language Word guide explaining the plus and minus live XGBoost contribution signs for the 715 kgCO2e result.
- [x] Create a concise PowerPoint presentation explaining the fixed XGBoost base number and changing plus/minus contributions in CarbonSense.
- [x] Compare all model-training and evaluation claims in DraftFinalCopy.docx with the deployed CarbonSense XGBoost runtime and report any mismatch.
- [x] Brighten the homepage sustainability hero while preserving accessible copy and action contrast.
- [x] Align in-app methodology and model claims with the verified deployed XGBoost artifact and distinguish non-ML planning tools from trained models.
- [x] Redesign the transparent-baseline route into an interactive, category-level live estimate inspired by the supplied reference image.
- [x] Expose only verified baseline factor values, units, calculations, and source labels in the revised baseline experience.
- [x] Attribute each transparent-baseline category only to the approved IPCC, DEFRA/DESNZ, GHG Protocol, Poore and Nemecek, or US EPA source that supports its displayed factor.
- [x] Assess the transparent-baseline sources, citations, factor scope, and reporting language for suitability in the CarbonSense major project.
- [x] Remove the “Recommended next move / One profile. Two lenses.” section from the Explore hub.
- [x] Remove the “Recommended next move / Planning works best in small steps.” section from the Planning hub.
- [x] Expand reduction-optimizer output into multiple transparent recommendations prioritized by their contribution to the selected reduction target.
- [x] Remove the “Planning frame / Result / Test / Plan” block from the planning tools.
- [x] Add a “Reduce from” selector allowing optimizer targets to begin from either the AI estimate or the transparent baseline without averaging the methods.
- [x] Remove the optimizer’s Starting AI result and Starting baseline summary cards while keeping the selected start visible.
- [x] Recompose the optimizer to use the full desktop page width for controls and prioritized recommendations while retaining mobile stacking.
- [x] Remove the long optimizer result methodology and planning-limitations paragraph at the user’s request.
- [x] Create a Word guide explaining how optimizer recommendations are assigned, prioritized, bounded, and kept separate from organization assignments.
- [x] Replace the What-if starting AI and baseline summary cards with an optimizer-style “Reduce from” method selector that keeps scenario methods separate.
- [x] Fix the duplicate React key warning in the Net-Zero staged-pathway list and add regression coverage.
- [x] Add an optimizer-style “Reduce from” selector to the Net-Zero planner so the pathway starts from either the AI estimate or transparent baseline without averaging them.
- [x] Remove the “Recommended next move / History stays private by design.” card from the Insights hub.
- [x] Restore removal of the optimizer methodology and limitations paragraph after it was inadvertently reintroduced by the Net-Zero selector refactor.
- [x] Inspect and explain the current CarbonSense forecast method, saved-history inputs, assumptions, and uncertainty boundary.
- [x] Audit the uploaded Prophet/ETS paper claim against the codebase and implement an evidence-limited Prophet forecasting path only where personal-history data and runtime support are sufficient.
- [x] Remove the Forecast page’s right-side “Next best step” and “Role access” panel while retaining the forecast and scenario planner.
- [x] Remove the Forecast page’s What-if scenario planner and retain only the forecast history experience.
- [x] Verify and push the latest CarbonSense checkpoint to the requested GitHub repository.
- [x] Remove the remaining shared workspace “Next best step / Role access” panel and footer text from CarbonSense pages.
- [x] Remove the Progress hub’s “Recommended next move / Progress is built from recorded action” card while retaining progress tools.
- [x] Remove the requested Progress lower summary cards and user-facing Activity ledger panel/navigation while retaining the underlying stored-record and privacy safeguards.
- [x] Add a clear role-aware organization recommendation panel so organization administrators can assign recommendations and track member completion.
- [x] Verify all accessible Admin-panel features, role boundaries, organization recommendation tracking, and rendered states; fix any defect found.

## Independent-copy GitHub publication

- [x] Create a new private GitHub repository for this independent CarbonSense copy and push the current project contents.

## Product experience review

- [x] Review the running CarbonSense experience and supplied interface evidence; produce a prioritized, data-honest feature and visual-style improvement roadmap.

## Progress experience redesign

- [x] Redesign the Progress section with a focused overview, Quests and Contributors modes, responsive score/streak/badge surfaces, and consent-filtered contributor views modeled on the supplied layout without fabricating outcomes.
- [x] Add regression coverage and desktop/mobile visual verification for the redesigned Progress section.
- [x] Show the CarbonQuest introduction only when the Quests and badges mode is selected, not in the shared Progress header.
- [x] Recompose the Progress overview, Quests and badges mode, and Contributors mode to match the supplied reference layout while preserving real score data, consent-filtered aggregates, and data-honesty language.
- [x] Replace the contributor map placeholder with a zoomable world map that updates from consent-filtered country aggregates without exposing individual locations or histories.
- [x] Remove the contributor map’s empty-selection coverage message while retaining the world map and country-level privacy controls.
- [x] Remove the oversized green silhouette overlay from the contributor map empty state while retaining the zoomable map and privacy controls.
- [x] Restore the `/predict` XGBoost inference worker by adding its missing `joblib` dependency to the declared development and production runtime.

## Insights experience redesign

- [x] Redesign Insights with the supplied focused header and Forecast/History switcher while preserving real history, the documented forecast threshold, and truthful empty states.
- [x] Restore the concise prior Forecast empty state while retaining the redesigned Forecast/History switcher.
- [x] Restore the original Forecast method, evidence, uncertainty, and monthly-point presentation inside the redesigned Forecast tab.

## Plan experience redesign

- [x] Restyle the Plan workspace with the supplied soft-mint grading, roadmap callout, and Net-Zero/Optimizer/What-if segmented slider while retaining current planning calculations and boundaries.
- [x] Remove the Net-Zero roadmap callout and its button while retaining the Plan mode switcher and all planning tools.
- [x] Add a reference-inspired Plan Configuration and roadmap-status section using only live CarbonSense inputs, without removing any existing planning controls, modes, or result views.
- [x] Remove the added Plan Configuration and roadmap-status panels, restoring the immediately previous streamlined Plan layout.
- [x] Add a two-column Current Lifestyle and Modified Lifestyle presentation to What-if while retaining the existing Reduce from selector, method boundary, vehicle-distance, clothing-item controls, calculations, and result behavior.
- [x] Remove the What-if Current Lifestyle summary and explanatory copy while retaining Modified Lifestyle controls, calculations, and result behavior.

## Explore baseline experience redesign

- [x] Restyle Explore’s Baseline Calculator with the supplied AI Prediction/Baseline slider, staged input presentation, and soft-mint grading while retaining current formulas, verified source factors, and real result data.

## First-use onboarding path

- [x] Add a real-data four-step onboarding path for first-time users: run an estimate, review a top driver, choose a planning tool, and record a first follow-up without duplicating existing workflows.
- [x] Add regression coverage and desktop/mobile verification for the first-use onboarding completion states.

## Shared workspace mode sliders

- [x] Apply the Explore segmented-slider visual treatment to the existing Insights Forecast/History and Plan Net-Zero/Optimizer/What-if controls without changing labels, calculations, or mode behavior.
- [x] Add focused regression coverage and visual verification for the unified Insights and Plan mode sliders.

## Home hero visual refinement

- [x] Add a CarbonSense-specific, image-led home hero that communicates personal footprint estimation, transparent comparison, and practical planning while preserving existing navigation and entry points.
- [x] Add regression coverage and desktop/mobile verification for the updated home hero.

## Independent GitHub update

- [x] Push the verified independent CarbonSense home-hero update to the configured private GitHub repository.

## Current-product improvement review

- [x] Review the current CarbonSense experience and develop a prioritized, evidence-aware improvement roadmap across onboarding, data capture, trust, retention, collaboration, and project readiness.

## Current interface desktop screenshot set

- [x] Capture and package current desktop screenshots for all main CarbonSense routes, including Home, Explore, Plan, Insights, Progress, direct calculation and planning tools, docs, and administration surfaces.

## Current-page screenshot

- [x] Capture and provide the current CarbonSense page at desktop width.

## CarbonSense documentation guide

- [x] Create a detailed Word guide that explains the current CarbonSense pages, workflows, feature boundaries, privacy safeguards, model limitations, and administration behavior using current screenshots.
- [x] Include a structured manual test-case catalogue covering authentication, estimation, planning, insights, progress, documentation, profile, administration, permissions, and responsive checks.
- [x] Expand the Word guide with a verified frontend-to-backend technical walkthrough of AI prediction, including persistence, frozen preprocessing, inference worker, explanations, safeguards, and backend test cases.
- [x] Create a dedicated Word guide covering prediction frontend/backend flow, XGBoost configuration and behavior, contribution/uncertainty framing, and transparent baseline calculation.

## FastAPI migration assessment

- [ ] Assess and design a safe migration from the current Node/tRPC backend to Python FastAPI while retaining the React frontend, authentication, database records, XGBoost inference, role/consent safeguards, and existing feature behavior.
- [x] Map the selected React–FastAPI–ML-service architecture to CarbonSense modules and confirm whether the existing MySQL/TiDB data store and OAuth sessions are retained or replaced by the attachment’s MongoDB/JWT model.
- [x] Validate the configured MongoDB Atlas target with an authenticated safe ping before starting repository implementation.
- [ ] Replace the backend architecture with FastAPI, MongoDB collections, and JWT/RBAC authentication while retaining the React UI and core CarbonSense feature behavior.
- [x] Superseded by the clean native-account restart: implement the selected password-reset activation path for existing OAuth/MySQL users before switching the React session client to FastAPI.
- [x] Superseded by the clean native-account restart: prepare a safe transfer plan for existing MySQL/TiDB user and application records before switching the production data source to MongoDB.
- [x] Implement a clean MongoDB-native registration and sign-in flow with Argon2 password hashes, FastAPI JWT sessions, CSRF protection, and React integration through the same-origin development bridge.
- [x] Add isolated behavioral FastAPI authentication tests covering registration hashing, duplicate prevention, login rejection, session revocation, CSRF, and disabled users without writing owner data.
- [x] Run FastAPI alongside the legacy development host through a same-origin `/api/v1` bridge, including JSON-body forwarding and local secure-cookie handling for native authentication validation.
- [x] Port the core native-auth React flows plus prediction/baseline, planning, Insights, Progress/CarbonQuest, Profile, Reports, organization recommendation panel, and bounded assistant widget to FastAPI API calls.
- [ ] Port the remaining aggregate administrator dashboard, contributor, and first-use-onboarding React modules; then remove tRPC providers and the legacy Node compatibility bridge. The FastAPI super-admin user-management panel is complete.
- [ ] Complete the controlled FastAPI cutover: migrate remaining React endpoint groups from tRPC, remove the temporary Node development bridge, and switch the production container to Uvicorn static hosting only after behavioral parity is proven.

## Filled prediction questionnaire screenshot set

- [ ] Capture and package desktop screenshots of every AI prediction questionnaire step with its current filled input values visible.
- [ ] Use a temporary account and representative non-personal inputs to capture the filled questionnaire without submitting a prediction result.
- [ ] Use the requested administrator account to capture the filled questionnaire without submitting a prediction result.

## Deployment repair

- [x] Replace the Python dependency pin that is incompatible with the Docker image’s Python 3.11 runtime, then validate a deploy-ready project build.
- [x] Diagnose and resolve the repeat production deployment failure after the initial NumPy compatibility repair.

## Current interface screenshot set

- [x] Superseded by the user’s desktop-only request: capture and package current desktop and mobile screenshots for the main CarbonSense routes: Home, Explore, Plan, Insights, and Progress.

## Attached React/Vite project-structure alignment

- [x] Map the supplied `src/api`, `src/components`, `src/pages`, `src/store`, and `src/utils` structure to the current CarbonSense React modules.
- [x] Create a target React page and component structure with compatibility exports so existing routes continue to work during the FastAPI cutover.
- [x] Move core CarbonSense route composition and shared UI into the aligned React structure without weakening MongoDB/JWT/RBAC, model, forecast, or privacy boundaries.
- [x] Validate the reorganized React structure with TypeScript, focused tests, FastAPI health, and route screenshots before a production checkpoint.

## Existing repository frontend refactor into supplied structure

- [ ] Relocate the current CarbonSense repository frontend's reusable layout, maps, charts, authentication guards, and page composition into the supplied `src/components`, `src/pages`, `src/api`, `src/store`, and `src/utils` layout.
- [ ] Preserve every current route and FastAPI contract while replacing temporary page compatibility exports with the existing frontend implementations in their target modules.
- [x] Validate each adopted route with strict TypeScript, FastAPI-focused tests, full regression coverage, bridge health checks, and desktop screenshots before publishing.
- [x] Move the real FastAPI-backed onboarding, super-admin user management, consent-filtered aggregate admin dashboard, planning workspace, root dashboard, and Insights history/forecast route implementations into the requested target modules with compatibility exports where existing imports still depend on them.
- [x] Extract the real Explore hub and public About/Docs methodology content from the legacy `Home.tsx` multiplexer, preserving their existing navigation, model-boundary language, and visual workflows.
- [x] Move the reusable workspace tool navigation into `components/navigation/WorkspaceTabs.tsx` while preserving its existing route grouping and active-state behavior.
- [x] Move the frozen-model survey defaults and reset-safe survey state hook into `store/survey.ts` without changing the exact submitted answer shape.
- [x] Move the frozen 34-column contract metadata and entered-versus-derived boundary into `utils/predictContract.ts` without changing the displayed model contract.
- [x] Move the four staged Predict survey headings and descriptions into `utils/predictSurvey.ts` without changing their order or source-factor guidance.
- [x] Move the Predict field groups, choice visuals, display currencies, and formatting logic into `utils/predictSurvey.ts` without changing the frozen answer options or interaction semantics.
- [x] Move frozen-model contribution ranking, scale, and direction interpretation into `utils/predictionResults.ts` without changing the result disclosure language.
- [x] Remove the unreferenced legacy source-baseline calculator from `Home.tsx`, leaving the relocated Baseline page as the single active calculator implementation.
- [x] Adopt `/predict` through `pages/Predict.tsx` while retaining the exact existing frozen-model implementation pending its coupled source relocation.
- [x] Extract the coupled Predict questionnaire and result workflow from the legacy `Home.tsx` multiplexer, preserving the frozen 34-input → 54-feature contract, FastAPI model/baseline calls, contribution disclosure, and baseline comparison.
- [x] Migrate the super-admin-only non-persistent model QA preview from tRPC to the existing FastAPI `/model/preview` route without creating a footprint run.
- [x] Move the retained super-admin model QA preview into `pages/admin` and register its direct route without weakening its FastAPI role gate or non-persistence guarantee.
- [x] Move the consent-preserving privacy aggregate-sharing control into a direct FastAPI-backed target page without exposing individual activity or member identities.
- [x] Move the authenticated goals workflow into a direct FastAPI-backed target page while retaining history-linked targets and the existing 90-day goal default.
- [x] Move the authenticated assistant workflow into a direct FastAPI-backed target page while preserving its private-data and non-verified-reduction boundaries.
- [x] Port the completed-result recommendation selector to FastAPI and move the direct Recommendations route into the target page structure without replacing it with a generic catalog.
- [x] Move the role-gated, consent-filtered organization summary into a direct FastAPI-backed page without exposing individual records.
- [x] Move the account-scoped activity route and administrator-only report queue into direct FastAPI-backed target pages before removing the legacy Home fallback runtime.
- [x] Remove the active React tRPC provider and Node tRPC transport after direct-route parity, while retaining the temporary Node-to-FastAPI same-origin bridge pending production-hosting cutover.
- [x] Add the useful reference-structure UI modules—visual progress, contribution, and interaction components—and integrate them without exposing individual contributor data.
- [x] Compare the submitted final project document against the current CarbonSense implementation and identify feature, architecture, evidence, and presentation gaps before making further changes.
- [x] Fix Windows local development so the Node host launches the FastAPI bridge successfully and registration can reach `127.0.0.1:8015`.
- [x] Diagnose and fix the invalid Predict response after form submission without changing the frozen XGBoost input contract or account-scoped persistence rules.
- [x] Add the supplied `data` and `models` research assets plus a documented original CarbonSense layout compatibility tree without replacing the active `client`/`backend` application.
- [ ] Remove remaining active React tRPC consumers and the temporary provider/Node bridge only after the replacement FastAPI route groups have proven behavioral parity.

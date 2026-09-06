# CarbonSense research and legacy-layout guide

The repository now retains the requested original research-project structure while preserving the active React, FastAPI, MongoDB, JWT, CSRF, and role-based application. The added research folders are deliberately separate from the active runtime so that a model experiment cannot silently change the deployed prediction behavior.

| Requested location | Present location | Purpose and boundary |
|---|---|---|
| `CarbonSense/backend/` | `backend/` | Active FastAPI service; it remains the only backend runtime. |
| `CarbonSense/data/` | `data/` | User-supplied research factors, raw/processed datasets, splits, and preprocessing artifacts. |
| `CarbonSense/models/` | `models/trained/` | User-supplied research model artifacts for controlled evaluation. |
| `CarbonSense/reports/` | `reports/` | Safe location for experiment and evaluation documentation. |
| `CarbonSense/retrain.py` | `retrain.py` | Non-destructive research entrypoint; it performs no model replacement. |
| Regional retraining support | `retrain_regional.py` | Non-destructive regional research entrypoint. |
| Wren-inspired frontend | `carbonsense-frontend-wren-inspired/carbonsense-frontend/` | Compatibility layout whose aliases point to the maintained active `client/` source. |

## Active application boundary

The running frontend is `client/`. The running API is `backend/`. The current production path continues to use the transitional Node host solely as a same-origin launcher and proxy for FastAPI; it has not been replaced by the legacy compatibility tree.

The live predictor continues to use its existing frozen artifact and 34-source-to-54-feature contract. The `models/trained/` research artifacts are **not** automatically loaded by `/api/v1/model/predict`, and no prediction result has been recalculated from these files.

## Windows workflow

Use the repository root as the working directory. Keep your own `.env` outside source control, install the project dependencies, and run the current application from the root as described in `WINDOWS_LOCAL_SETUP.md`. The nested compatibility folder is a structural map for older tooling and should not be installed or launched as a separate frontend.

For research exploration only, you may run:

```powershell
py -3.12 retrain.py
py -3.12 retrain_regional.py
```

Both commands only report their intended directories. They do not train, write, or replace any deployment artifact.

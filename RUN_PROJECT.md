# Run CarbonSense Locally

This guide starts the CarbonSense web application and its FastAPI prediction service on Windows.

## Prerequisites

Install the following:

- Node.js 22 or later
- Python 3.12
- Corepack, included with supported Node.js installations
- MongoDB Atlas access, or another MongoDB instance configured for the project

Verify the installations from PowerShell:

```powershell
node --version
py -3.12 --version
corepack --version
```

## First-time setup

Open PowerShell in the repository root (`D:\proj`) and install the dependencies:

```powershell
py -3.12 -m pip install -r requirements.txt
corepack enable
corepack pnpm install
```

Create a `.env` file beside `package.json` with real, local values:

```env
MONGODB_URI=mongodb+srv://USERNAME:URL_ENCODED_PASSWORD@CLUSTER/carbonsense_fastapi?retryWrites=true&w=majority
JWT_SECRET=replace_with_a_long_random_secret
```

Do not commit `.env` or use placeholder credentials. URL-encode special characters in the MongoDB password. In MongoDB Atlas, confirm that the database user has access to `carbonsense_fastapi` and that your current IP address is allowed under Network Access.

## Start the development server

From the repository root, run:

```powershell
$env:NODE_ENV="development"
pnpm exec tsx watch server/_core/index.ts
```

You can also start the same server with:

```powershell
.\start_dev.bat
```

The Node server automatically starts the FastAPI service. Wait until the terminal reports that FastAPI is running on `127.0.0.1:8015`, then open:

<http://localhost:3000>

Keep the terminal open while using the application. Press `Ctrl+C` to stop both services.

## Service URLs

| Service               | URL                                   | Purpose                 |
| --------------------- | ------------------------------------- | ----------------------- |
| CarbonSense web app   | <http://localhost:3000>               | Main browser interface  |
| FastAPI service       | <http://127.0.0.1:8015>               | Internal prediction API |
| FastAPI documentation | <http://127.0.0.1:8015/api/docs>      | Interactive API docs    |
| FastAPI health check  | <http://127.0.0.1:8015/api/v1/health> | Service status          |

The web server searches for an available port starting at `3000` if that port is already occupied. Check the terminal output for the actual URL in that case.

## Verify the setup

After the application opens:

1. Sign in with a configured test account or create an account.
2. Open the Predict page.
3. Complete and submit the questionnaire.
4. Confirm that a footprint estimate, category breakdown, and prediction interval are displayed.

To test the MongoDB connection without writing test data:

```powershell
py -3.12 scripts\validate_mongodb_connection.py
```

## Troubleshooting

### Python cannot be launched

Confirm that Python 3.12 is available through the launcher:

```powershell
py -3.12 --version
```

If the launcher is unavailable, install Python 3.12 with Add Python to PATH enabled. Alternatively, set the full executable path before starting the app:

```powershell
$env:PYTHON_EXECUTABLE="C:\Path\To\python.exe"
```

### FastAPI connection refused

The FastAPI process may still be starting or may have exited. Read the `[FastAPI]` traceback in the terminal, then verify the Python dependencies:

```powershell
py -3.12 -m pip install -r requirements.txt
```

### MongoDB authentication or timeout errors

Check `MONGODB_URI`, URL-encode special password characters, verify the Atlas credentials, and allow your current public IP address in MongoDB Atlas Network Access.

### Port already in use

The web server can select another available port automatically. FastAPI uses `8015`; set a different internal port if needed:

```powershell
$env:FASTAPI_INTERNAL_PORT="8016"
```

### Dependency or type errors after pulling changes

Reinstall JavaScript dependencies and run the available checks:

```powershell
corepack pnpm install
pnpm run check
pnpm test
```

## Production build

To build and run the production bundle:

```powershell
pnpm run build
$env:NODE_ENV="production"
pnpm start
```

Open the URL printed by the server. Production mode requires the same MongoDB configuration and Python dependencies as development mode.

# 🚀 Start CarbonSense Project

## Quick Start (Windows PowerShell)

Open PowerShell in the project root and run:

```powershell
$env:NODE_ENV="development"
pnpm exec tsx watch server/_core/index.ts
```

**Or** use the batch file:
```cmd
start_dev.bat
```

## Expected Output

Wait for both these lines:
```
[FastAPI] INFO:     Uvicorn running on http://127.0.0.1:8015 (Press CTRL+C to quit)
Server running on http://localhost:3000/
```

Then open: **http://localhost:3000**

## What Just Happened

✅ **GradientBoostingRegressor model loaded from artifacts!**
- **R² = 0.9629** (96.29% variance explained)
- **MAE = 156.96 kg CO₂e/month** (average error)
- **RMSE = 196.38 kg CO₂e/month**
- **44 features** from 26 raw survey inputs

The model:
- Uses **Gradient Boosting** (scikit-learn GradientBoostingRegressor)
- Loads from `server/model_runtime/artifacts/`
- Serves predictions via FastAPI on port 8015
- Returns predictions through the React UI on port 3000

## If It Doesn't Start

### Python Missing
```powershell
py -3.12 --version
# If this fails, install Python 3.12 from python.org
```

### Missing Packages
```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 -m pip install python-dotenv
```

### Node/pnpm Missing
```powershell
node --version
pnpm --version
# If missing: install Node.js 22 from nodejs.org
# Then: corepack enable
# Then: corepack pnpm install
```

### MongoDB Connection Issues
Check `.env` file:
```env
MONGODB_URI=mongodb+srv://USER:PASSWORD@cluster/carbonsense_fastapi?retryWrites=true
JWT_SECRET=your_long_random_secret_32_chars_minimum
```

Test MongoDB:
```powershell
py -3.12 scripts\validate_mongodb_connection.py
```

## Port Reference

| Port | Service | URL | Notes |
|------|---------|-----|-------|
| 3000 | Full App | http://localhost:3000 | **Open this in your browser** |
| 8015 | FastAPI Backend | http://127.0.0.1:8015 | API only (not for browser) |

### API Documentation
- FastAPI Docs: http://127.0.0.1:8015/api/docs
- Health Check: http://127.0.0.1:8015/api/v1/health

## Test the Prediction

After logging in, go to the **Predict** page and fill out the questionnaire.

You should now see:
- ✅ A carbon footprint estimate
- ✅ Breakdown by category
- ✅ Prediction interval

---

**Everything is ready! Start the server and test the predictions.** 🎉

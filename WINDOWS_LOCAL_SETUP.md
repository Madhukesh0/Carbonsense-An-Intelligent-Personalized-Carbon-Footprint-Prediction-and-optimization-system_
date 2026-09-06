# CarbonSense local setup on Windows

## 1. Install prerequisites

Install Node.js 22 and Python 3.12. Then confirm that the Windows Python launcher can find Python 3.12:

```powershell
node --version
py -3.12 --version
```

## 2. Install dependencies

Open PowerShell in the project root and run:

```powershell
py -3.12 -m pip install -r requirements.txt
corepack enable
corepack pnpm install
```

## 3. Configure `.env`

Create a `.env` file beside `package.json` using your own values:

```env
MONGODB_URI=mongodb+srv://YOUR_USER:YOUR_URL_ENCODED_PASSWORD@YOUR_CLUSTER/carbonsense_fastapi?retryWrites=true&w=majority
JWT_SECRET=your_long_random_secret
```

Do not leave placeholder values such as `your_mongodb_atlas_connection_string`. In Atlas, ensure the database user password is correct and your current public IP address is allowed under **Network Access**. If the password contains `@`, `:`, `/`, `?`, `#`, or `%`, URL-encode it in the connection string.

## 4. Start the project

```powershell
$env:NODE_ENV="development"
pnpm exec tsx watch server/_core/index.ts
```

Open `http://localhost:3000` after the console shows that Uvicorn is running on `127.0.0.1:8015`.

## Troubleshooting

| Error | Meaning | Fix |
|---|---|---|
| `connect ECONNREFUSED 127.0.0.1:8015` | FastAPI has not started or exited. | Read the FastAPI console traceback immediately above this error. |
| `bad auth : authentication failed` | MongoDB Atlas rejected `MONGODB_URI`. | Correct the Atlas username/password, URL-encode special password characters, and verify the user has read/write access to `carbonsense_fastapi`. |
| `unable to launch py` | Python launcher is unavailable. | Reinstall Python 3.12 and select **Add Python to PATH**, or set `PYTHON_EXECUTABLE` to your `python.exe` path. |
| Atlas timeout | Your device IP is not allowed by Atlas. | Add your current IP under Atlas **Network Access**. |

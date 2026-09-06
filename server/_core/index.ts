import "dotenv/config";
import { spawn } from "child_process";
import express from "express";
import { createServer, request as httpRequest } from "http";
import net from "net";
import { registerOAuthRoutes } from "./oauth";
import { registerStorageProxy } from "./storageProxy";
import { serveStatic, setupVite } from "./vite";

const fastApiPort = parseInt(process.env.FASTAPI_INTERNAL_PORT || "8015", 10);

function startFastApiBridge() {
  const isWindows = process.platform === "win32";
  const pythonCommand = process.env.PYTHON_EXECUTABLE || (isWindows ? "py" : "python3");
  const pythonArgs = process.env.PYTHON_EXECUTABLE
    ? ["-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", String(fastApiPort)]
    : isWindows
      ? ["-3.12", "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", String(fastApiPort)]
      : ["-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", String(fastApiPort)];
  const child = spawn(pythonCommand, pythonArgs, {
    cwd: process.cwd(),
    env: { ...process.env, COOKIE_SECURE: process.env.NODE_ENV === "development" ? "false" : "true" },
    stdio: ["ignore", "pipe", "pipe"],
  });
  child.stdout.on("data", chunk => console.log(`[FastAPI] ${String(chunk).trim()}`));
  child.stderr.on("data", chunk => console.error(`[FastAPI] ${String(chunk).trim()}`));
  child.on("error", error => console.error(`[FastAPI] unable to launch ${pythonCommand}. Install Python 3.12 and dependencies, or set PYTHON_EXECUTABLE. ${error.message}`));
  child.on("exit", code => console.error(`[FastAPI] stopped with code ${code ?? "unknown"}`));
  const stop = () => { if (!child.killed) child.kill("SIGTERM"); };
  process.once("exit", stop);
  process.once("SIGINT", stop);
  return child;
}

function proxyFastApi(req: express.Request, res: express.Response) {
  const hasJsonBody = !["GET", "HEAD"].includes(req.method) && req.is("application/json") && req.body !== undefined;
  const serializedBody = hasJsonBody ? JSON.stringify(req.body) : undefined;
  const proxy = httpRequest({
    hostname: "127.0.0.1",
    port: fastApiPort,
    path: req.originalUrl,
    method: req.method,
    headers: { ...req.headers, host: `127.0.0.1:${fastApiPort}`, ...(serializedBody ? { "content-length": Buffer.byteLength(serializedBody) } : {}) },
  }, upstream => {
    res.status(upstream.statusCode || 502);
    for (const [key, value] of Object.entries(upstream.headers)) {
      if (value !== undefined) res.setHeader(key, value);
    }
    upstream.pipe(res);
  });
  proxy.on("error", error => {
    if (!res.headersSent) res.status(503).json({ detail: `FastAPI service is starting or unavailable: ${error.message}` });
  });
  if (serializedBody !== undefined) proxy.end(serializedBody);
  else req.pipe(proxy);
}

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function startServer() {
  const app = express();
  const server = createServer(app);
  // Configure body parser with larger size limit for file uploads
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  registerStorageProxy(app);
  registerOAuthRoutes(app);
  startFastApiBridge();
  app.use("/api/v1", proxyFastApi);
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);

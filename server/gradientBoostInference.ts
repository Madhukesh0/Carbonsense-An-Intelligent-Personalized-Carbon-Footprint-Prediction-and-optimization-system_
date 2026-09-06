import { ChildProcessWithoutNullStreams, spawn } from "node:child_process";
import { resolve } from "node:path";

type Contribution = { feature: string; label: string; shapValue: number; direction: "increases" | "decreases" };

export type GradientBoostInference = {
  predictedKg: number;
  modelVersion: "gradient-boosting-v1";
  datasetVersion: "individual-10k-regional-v1";
  targetDefinition: string;
  uncertaintyRange: { low: number; high: number };
  metrics: { r2: number; mae: number; rmse: number };
  runtime: { engine: "gradient_boosting"; rawFeatureCount: number; transformedFeatureCount: number };
  explanation: { baseValue: number; predictedValue: number; contributions: Contribution[]; reconciliation: number; note: string };
  disclaimer?: string;
};

let queue = Promise.resolve();
let worker: ChildProcessWithoutNullStreams | null = null;
let stdoutBuffer = "";
let workerError = "";
let pending: { resolve: (value: GradientBoostInference) => void; reject: (reason: Error) => void; timer: NodeJS.Timeout } | null = null;

function resetWorker(reason?: Error) {
  if (worker) worker.kill("SIGKILL");
  worker = null;
  stdoutBuffer = "";
  if (pending) {
    clearTimeout(pending.timer);
    pending.reject(reason || new Error("Model inference worker stopped."));
    pending = null;
  }
}

function getWorker() {
  if (worker && !worker.killed) return worker;
  const isWindows = process.platform === "win32";
  const pythonCommand = process.env.PYTHON_EXECUTABLE || (isWindows ? "py" : "python3");
  const script = resolve(process.cwd(), "server/model_runtime/infer.py");
  worker = spawn(pythonCommand, isWindows ? ["-3.12", script, "--worker"] : [script, "--worker"], { cwd: process.cwd(), stdio: ["pipe", "pipe", "pipe"] });
  worker.stdout.on("data", chunk => {
    stdoutBuffer += chunk.toString("utf8");
    const newline = stdoutBuffer.indexOf("\n");
    if (newline < 0 || !pending) return;
    const line = stdoutBuffer.slice(0, newline);
    stdoutBuffer = stdoutBuffer.slice(newline + 1);
    const current = pending;
    pending = null;
    clearTimeout(current.timer);
    try {
      const result = JSON.parse(line) as GradientBoostInference & { error?: string };
      if (result.error) throw new Error(result.error);
      if (!Number.isFinite(result.predictedKg) || !result.runtime?.engine) throw new Error("Invalid model inference response.");
      current.resolve(result);
    } catch (error) {
      current.reject(error instanceof Error ? error : new Error("Invalid model inference response."));
    }
  });
  worker.stderr.on("data", chunk => { workerError = `${workerError}${chunk.toString("utf8")}`.slice(-1200); });
  worker.once("error", error => resetWorker(error));
  worker.once("close", () => resetWorker(new Error(`Model inference worker stopped: ${workerError}`)));
  return worker;
}

function invoke(payload: Record<string, unknown>): Promise<GradientBoostInference> {
  return new Promise((resolvePromise, reject) => {
    const process = getWorker();
    const timer = setTimeout(() => resetWorker(new Error("Model inference timed out.")), 30_000);
    pending = { resolve: resolvePromise, reject, timer };
    process.stdin.write(`${JSON.stringify(payload)}\n`);
  });
}

/** Serialize model loads so the 512 MiB autoscale runtime does not spawn concurrent inference workers. */
export function runGradientBoostInference(payload: Record<string, unknown>) {
  const task = queue.then(() => invoke(payload));
  queue = task.then(() => undefined, () => undefined);
  return task;
}

import { spawn } from "node:child_process";
import { describe, expect, it } from "vitest";

const isWin = process.platform === "win32";
const pyCmd = isWin ? "py" : "python3";
const pyArgs = isWin ? ["-3.12"] : [];

function validateMongoConnection() {
  return new Promise<{ code: number | null; stderr: string }>((resolve, reject) => {
    const child = spawn(pyCmd, [...pyArgs, "scripts/validate_mongodb_connection.py"], {
      cwd: process.cwd(),
      env: process.env,
      stdio: ["ignore", "ignore", "pipe"],
    });
    let stderr = "";
    child.stderr.on("data", chunk => { stderr += chunk.toString("utf8"); });
    child.once("error", reject);
    child.once("close", code => resolve({ code, stderr }));
  });
}

describe("MongoDB migration configuration", () => {
  it("can authenticate and ping the configured MongoDB target without exposing the URI", async () => {
    const result = await validateMongoConnection();
    expect(result.code, result.stderr).toBe(0);
  }, 45_000);
});

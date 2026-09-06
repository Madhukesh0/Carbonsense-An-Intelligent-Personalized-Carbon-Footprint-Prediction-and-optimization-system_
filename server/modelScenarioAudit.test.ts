import { execFileSync } from "node:child_process";
import { describe, expect, it } from "vitest";

const isWin = process.platform === "win32";
const pyCmd = isWin ? "py" : "python3";
const pyArgs = isWin ? ["-3.12"] : [];

describe("deterministic XGBoost 100-scenario QA matrix", { timeout: 120_000 }, () => {
  it("runs non-user low, typical, and high-impact profiles through the frozen live runtime", () => {
    const stdout = execFileSync(pyCmd, [...pyArgs, "server/model_runtime/audit_scenarios.py"], {
      cwd: process.cwd(),
      encoding: "utf8",
    });
    const output = JSON.parse(stdout);
    expect(output.scenarioCount).toBe(100);
    expect(output.validation.allPredictionsFinite).toBe(true);
    expect(output.validation.allScenariosReturnedDrivers).toBe(true);
    expect(output.validation.allContributionReconciliationsWithinKg).toBe(0.2);
    expect(output.summary.byProfile.low_impact.count).toBe(34);
    expect(output.summary.byProfile.typical.count).toBe(33);
    expect(output.summary.byProfile.high_impact.count).toBe(33);
    expect(output.summary.maximumKg).toBeGreaterThan(output.summary.minimumKg);
  });
});

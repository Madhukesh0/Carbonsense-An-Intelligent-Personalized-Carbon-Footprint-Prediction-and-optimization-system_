import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const isWin = process.platform === "win32";
const pyCmd = isWin ? "py" : "python3";
const pyArgs = isWin ? ["-3.12"] : [];
const outputPath = "/home/ubuntu/exports/CarbonSense_XGBoost_100_Scenario_QA.xlsx";

describe("deterministic XGBoost QA workbook export", { timeout: 120_000 }, () => {
  it("exports the 100 non-user QA scenarios as a valid Excel workbook", () => {
    const stdout = execFileSync(pyCmd, [...pyArgs, "server/model_runtime/export_audit_xlsx.py"], {
      cwd: process.cwd(),
      encoding: "utf8",
    });
    const output = JSON.parse(stdout);
    expect(output.scenarioCount).toBe(100);
    expect(output.sheets).toEqual(["Read me", "Summary", "Scenarios", "Top drivers"]);
    expect(existsSync(outputPath)).toBe(true);
    expect(readFileSync(outputPath).subarray(0, 2).toString("utf8")).toBe("PK");
  });
});

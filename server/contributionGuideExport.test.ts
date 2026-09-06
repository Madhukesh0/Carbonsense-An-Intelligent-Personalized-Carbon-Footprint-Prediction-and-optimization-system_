import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const isWin = process.platform === "win32";
const pyCmd = isWin ? "py" : "python3";
const pyArgs = isWin ? ["-3.12"] : [];
const outputPath = "/home/ubuntu/exports/CarbonSense_715kgCO2e_Contribution_Guide.docx";

describe("personalized XGBoost contribution guide export", { timeout: 120_000 }, () => {
  it("exports a Word guide that explains the supplied signed contribution values", () => {
    execFileSync(pyCmd, [...pyArgs, "server/model_runtime/export_contribution_guide_docx.py"], {
      cwd: process.cwd(),
      encoding: "utf8",
    });
    expect(existsSync(outputPath)).toBe(true);
    expect(readFileSync(outputPath).subarray(0, 2).toString("utf8")).toBe("PK");
  });
});

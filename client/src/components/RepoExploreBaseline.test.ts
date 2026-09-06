import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

const source = fs.readFileSync(path.resolve(process.cwd(), "client/src/pages/Baseline.tsx"), "utf8");
const lib = fs.readFileSync(path.resolve(process.cwd(), "client/src/lib/v25Baseline.ts"), "utf8");

describe("v2.5-aligned Explore baseline calculator", () => {
  it("retains the calculator structure with live feedback and the aligned factor set", () => {
    expect(source).toContain("AI Prediction");
    expect(source).toContain("Baseline Calculator");
    expect(source).toContain("LIVE ESTIMATE");
    expect(source).toContain("Source-bound factors");
    expect(source).toContain("calculateAlignedBaseline");
    expect(source).toContain("Renewable-heavy supply");
  });

  it("uses the v2.5 aligned factors and no retired DESNZ values", () => {
    expect(lib).toContain("2.31 / 20.0");
    expect(lib + source).not.toContain("0.13096");
    expect(lib + source).not.toContain("0.10151");
    expect(lib + source).not.toContain("SOURCE_BASELINE_FACTORS");
    expect(lib).toContain("Scarborough 2023");
  });
});

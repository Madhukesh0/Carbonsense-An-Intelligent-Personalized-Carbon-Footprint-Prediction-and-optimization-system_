import { calculateAlignedBaseline, alignedBaselineDefaults, gridFactorFor } from "./v25Baseline";
import { describe, expect, it } from "vitest";

// Expected values computed from backend/app/services/baseline.py
// (py: calculate_baseline on the same profile) — the client mirror must
// produce identical numbers to the serving API.
describe("v2.5-aligned client baseline mirror", () => {
  it("matches the FastAPI baseline line-for-line on the default profile", () => {
    const result = calculateAlignedBaseline({ ...alignedBaselineDefaults, tvHours: 4, internetHours: 5 });
    expect(result.breakdown.transport).toBeCloseTo(34.6);
    expect(result.breakdown.home_energy).toBeCloseTo(120.6);
    expect(result.breakdown.food).toBeCloseTo(237.0);
    expect(result.breakdown.waste).toBeCloseTo(79.9);
    expect(result.breakdown.clothing).toBeCloseTo(36.0);
    expect(result.breakdown.cooking).toBeCloseTo(29.1);
    expect(result.breakdown.air_travel).toBe(60);
    expect(result.total).toBe(597.2);
    expect(result.grid).toBe(0.67013);
  });

  it("applies the renewable-heavy grid override and the UK grid factor", () => {
    expect(gridFactorFor("india", true)).toBe(0.147);
    expect(gridFactorFor("uk", false)).toBe(0.21741);
    expect(gridFactorFor("us", true)).toBe(0.085);
  });

  it("scales electric vehicles by the country grid, not a fixed factor", () => {
    const india = calculateAlignedBaseline({ ...alignedBaselineDefaults, vehicleFuel: "electric" });
    const uk = calculateAlignedBaseline({ ...alignedBaselineDefaults, vehicleFuel: "electric", country: "uk" });
    expect(india.breakdown.transport).toBeCloseTo(300 * 0.18 * 0.67013, 1);
    expect(uk.breakdown.transport).toBeLessThan(india.breakdown.transport);
  });

  it("keeps the retired DESNZ values out of every factor", () => {
    const source = JSON.stringify(alignedBaselineDefaults) + JSON.stringify(calculateAlignedBaseline(alignedBaselineDefaults));
    expect(source).not.toContain("0.13096");
    expect(source).not.toContain("0.10151");
  });
});

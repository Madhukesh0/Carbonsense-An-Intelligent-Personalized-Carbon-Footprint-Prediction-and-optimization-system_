import { describe, expect, it } from "vitest";
import { findLatestCompletedScenario } from "./whatIfProfile";

const profile = { diet: "omnivore", vehicle_monthly_distance_km: 300 };

describe("result-led What-if profile pairing", () => {
  it("requires a matching completed prediction and baseline payload", () => {
    const paired = findLatestCompletedScenario([
      { runType: "baseline", inputPayload: { ...profile, diet: "vegan" }, predictedKg: 400, baselineKg: 350, createdAt: new Date("2026-08-20T03:00:00Z") },
      { runType: "prediction", inputPayload: profile, predictedKg: 700, baselineKg: null, createdAt: new Date("2026-08-20T02:00:00Z") },
      { runType: "baseline", inputPayload: profile, predictedKg: 700, baselineKg: 480, createdAt: new Date("2026-08-20T01:00:00Z") },
    ]);
    expect(paired?.baselineKg).toBe(480);
    expect(paired?.inputPayload).toEqual(profile);
  });

  it("does not unlock a scenario from an unmatched baseline or prediction", () => {
    expect(findLatestCompletedScenario([
      { runType: "prediction", inputPayload: profile, predictedKg: 700, baselineKg: null, createdAt: new Date() },
      { runType: "baseline", inputPayload: { ...profile, diet: "vegan" }, predictedKg: 400, baselineKg: 350, createdAt: new Date() },
    ])).toBeNull();
  });
});

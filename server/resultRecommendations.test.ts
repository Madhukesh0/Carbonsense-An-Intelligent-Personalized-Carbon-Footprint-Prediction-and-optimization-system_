import { describe, expect, it } from "vitest";
import { selectResultLedRecommendations } from "./resultRecommendations";

describe("result-led recommendations", () => {
  it("selects only actions grounded in a completed private-vehicle, electricity, omnivore profile", () => {
    const actions = selectResultLedRecommendations({ diet: "omnivore", transport: "private", vehicle_type: "petrol", vehicle_monthly_distance_km: 300, heating_energy_source: "electricity", how_many_new_clothes_monthly: 2 });
    expect(actions.map(action => action.key)).toEqual(expect.arrayContaining(["transit_two_trips", "fuel_efficiency", "cleaner_energy", "lower_impact_meals"]));
    expect(actions.every(action => action.provenance.length > 0 && action.trigger.length > 0)).toBe(true);
  });

  it("does not suggest fossil-vehicle actions to a walk/bicycle profile", () => {
    const actions = selectResultLedRecommendations({ diet: "vegan", transport: "walk/bicycle", vehicle_type: "none", vehicle_monthly_distance_km: 0, heating_energy_source: "wood", how_many_new_clothes_monthly: 0 });
    expect(actions.map(action => action.key)).not.toContain("fuel_efficiency");
    expect(actions.length).toBeGreaterThan(0);
  });
});

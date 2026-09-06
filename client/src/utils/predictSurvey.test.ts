import { describe, expect, it } from "vitest";
import { cardChoiceKeys, fieldGroups, formatSurveyChoice, formatSurveyValue, segmentedChoiceKeys, surveySections } from "./predictSurvey";

describe("Predict survey metadata", () => {
  it("keeps five staged field groups of mechanism-backed questions only", () => {
    expect(surveySections).toHaveLength(4);
    expect(fieldGroups).toHaveLength(4);
    expect(fieldGroups.flat()).toHaveLength(15);
    expect(fieldGroups.flat().find(field => field.key === "recycling")?.role).toBe("compound");
    expect(fieldGroups.flat().find(field => field.key === "cooking_with")?.role).toBe("compound");
    expect(cardChoiceKeys.has("transport")).toBe(true);
    expect(segmentedChoiceKeys.has("region")).toBe(false);
  });

  it("keeps country out of the question flow (context via grid selector)", () => {
    const keys = fieldGroups.flat().map(field => field.key);
    expect(keys).not.toContain("country");
    // household_size lives in the home-energy group
    expect(fieldGroups.flat().find(field => field.key === "household_size")).toBeDefined();
  });

  it("asks no question without a defensible emission mechanism", () => {
    const keys = fieldGroups.flat().map(field => field.key);
    expect(keys).not.toContain("age");
    expect(keys).not.toContain("sex");
    expect(keys).not.toContain("body_type");
    expect(keys).not.toContain("social_activity");
    expect(keys).not.toContain("how_often_shower");
    expect(keys).not.toContain("energy_efficiency");
    // region (grid mix) is retired: country now sets the grid factor
    expect(keys).not.toContain("region");
  });

  it("keeps labels and grocery display formatting independent from model input", () => {
    const grocery = fieldGroups.flat().find(field => field.key === "monthly_grocery_bill");
    expect(grocery).toBeDefined();
    expect(formatSurveyChoice("electric", fieldGroups.flat().find(field => field.key === "vehicle_type")!)).toBe("Electric");
    expect(formatSurveyValue(200, grocery!, "INR")).toContain("₹");
  });
});

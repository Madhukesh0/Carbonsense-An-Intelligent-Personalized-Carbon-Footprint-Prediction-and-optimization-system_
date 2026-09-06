import { describe, expect, it } from "vitest";
import { validateSurvey } from "../lib/surveyValidation";

const completeInteractiveSurvey = {
  country: "india",
  household_size: 2,
  age: 30,
  sex: "female",
  body_type: "normal",
  diet: "omnivore",
  how_often_shower: "daily",
  heating_energy_source: "electricity",
  energy_efficiency: "Sometimes",
  transport: "private",
  vehicle_type: "petrol",
  vehicle_monthly_distance_km: 300,
  frequency_of_traveling_by_air: "rarely",
  region: "mixed",
  monthly_grocery_bill: 200,
  how_many_new_clothes_monthly: 2,
  waste_bag_size: "medium",
  waste_bag_weekly_count: 3,
  how_long_tv_pc_daily_hour: 4,
  how_long_internet_daily_hour: 4,
  social_activity: "sometimes",
  recycling: ["paper", "plastic"],
  cooking_with: ["stove", "oven"],
};

describe("interactive frozen-model questionnaire validation", () => {
  it("accepts a complete 17-question source survey for the frozen model contract", () => {
    expect(validateSurvey(completeInteractiveSurvey)).toBeNull();
  });

  it("blocks unsupported choices and out-of-range values before a model submission", () => {
    expect(validateSurvey({ ...completeInteractiveSurvey, age: 17 })).toContain("Age");
    expect(validateSurvey({ ...completeInteractiveSurvey, monthly_grocery_bill: 5001 })).toContain("Grocery spend / month");
    expect(validateSurvey({ ...completeInteractiveSurvey, recycling: ["paper", "cardboard"] })).toContain("Recycling");
    expect(validateSurvey({ ...completeInteractiveSurvey, household_size: 0 })).toContain("People in your home");
    expect(validateSurvey({ ...completeInteractiveSurvey, country: "mars" })).toContain("Country");
  });
});

import { useState } from "react";

// Reference values the frozen dataset's model contract requires but the
// questionnaire deliberately does not ask: they have no defensible emission
// mechanism (age, sex, body type, social activity) or no concrete meaning
// (the old "energy efficiency" scale). Sending the dataset's reference
// profile keeps the 44-feature model input valid while the form asks only
// mechanism-backed questions.
export const surveyDefaults = {
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
} as const;

export function useSurvey() {
  const [value, setValue] = useState<any>({ ...surveyDefaults, recycling: [...surveyDefaults.recycling], cooking_with: [...surveyDefaults.cooking_with] });
  const set = (key: string, next: any) => setValue((old: any) => ({ ...old, [key]: next }));
  const toggle = (key: "recycling" | "cooking_with", item: string) => setValue((old: any) => {
    const current = old[key] as string[];
    if (item === "none") return { ...old, [key]: ["none"] };
    const withoutNone = current.filter(entry => entry !== "none");
    return { ...old, [key]: withoutNone.includes(item) ? withoutNone.filter(entry => entry !== item) : [...withoutNone, item] };
  });
  return { value, set, toggle };
}

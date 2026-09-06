type NumericRule = {
  key: string;
  label: string;
  min: number;
  max: number;
};

type ChoiceRule = {
  key: string;
  label: string;
  choices: readonly string[];
  multiple?: boolean;
};

const numericRules: readonly NumericRule[] = [
  { key: "age", label: "Age", min: 18, max: 80 },
  { key: "household_size", label: "People in your home", min: 1, max: 10 },
  { key: "vehicle_monthly_distance_km", label: "Vehicle distance / month", min: 0, max: 10000 },
  { key: "monthly_grocery_bill", label: "Grocery spend / month", min: 0, max: 5000 },
  { key: "how_many_new_clothes_monthly", label: "New clothing / month", min: 0, max: 50 },
  { key: "waste_bag_weekly_count", label: "Waste bags / week", min: 0, max: 20 },
  { key: "how_long_tv_pc_daily_hour", label: "TV / PC hours / day", min: 0, max: 24 },
  { key: "how_long_internet_daily_hour", label: "Internet hours / day", min: 0, max: 24 },
];

const choiceRules: readonly ChoiceRule[] = [
  { key: "sex", label: "Sex", choices: ["female", "male"] },
  { key: "body_type", label: "Body type", choices: ["underweight", "normal", "overweight", "obese"] },
  { key: "diet", label: "Diet", choices: ["vegan", "vegetarian", "pescatarian", "omnivore"] },
  { key: "how_often_shower", label: "Shower frequency", choices: ["rarely", "daily", "often", "twice a day"] },
  { key: "heating_energy_source", label: "Heating source", choices: ["electricity", "natural gas", "wood"] },
  { key: "energy_efficiency", label: "Efficiency", choices: ["No", "Sometimes", "Yes"] },
  { key: "transport", label: "Transport", choices: ["private", "public", "walk/bicycle"] },
  { key: "vehicle_type", label: "Vehicle", choices: ["none", "petrol", "diesel", "electric", "hybrid", "lpg"] },
  { key: "frequency_of_traveling_by_air", label: "Air travel", choices: ["never", "rarely", "often", "very frequently"] },
  { key: "country", label: "Country", choices: ["india", "china", "us", "germany", "japan", "uk", "france", "canada", "brazil", "australia", "russia", "south_korea", "saudi_arabia", "indonesia", "uae", "singapore", "netherlands"] },
  { key: "waste_bag_size", label: "Waste bag size", choices: ["small", "medium", "large", "extra large"] },
  { key: "social_activity", label: "Social activity", choices: ["never", "sometimes", "often"] },
  { key: "recycling", label: "Recycling", choices: ["paper", "plastic", "metal", "glass", "none"], multiple: true },
  { key: "cooking_with", label: "Cooking appliances", choices: ["stove", "oven", "microwave", "grill", "airfryer", "none"], multiple: true },
];

export function validateSurvey(value: Record<string, unknown>) {
  for (const rule of numericRules) {
    const rawValue = value[rule.key];
    const numericValue = typeof rawValue === "number" ? rawValue : Number(rawValue);
    if (!Number.isFinite(numericValue) || numericValue < rule.min || numericValue > rule.max) {
      return `${rule.label} must be between ${rule.min} and ${rule.max}.`;
    }
  }

  for (const rule of choiceRules) {
    const selected = value[rule.key];
    if (rule.multiple) {
      if (!Array.isArray(selected) || selected.some(item => !rule.choices.includes(String(item)))) {
        return `Choose supported options for ${rule.label}.`;
      }
    } else if (!rule.choices.includes(String(selected))) {
      return `Choose a supported option for ${rule.label}.`;
    }
  }

  return null;
}

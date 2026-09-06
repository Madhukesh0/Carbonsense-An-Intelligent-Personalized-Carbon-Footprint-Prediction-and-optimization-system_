export type PredictionContribution = { feature: string; label: string; shapValue: number; direction: string };

export function rankContributions(contributions: PredictionContribution[]) {
  return [...contributions].sort((a, b) => Math.abs(b.shapValue) - Math.abs(a.shapValue));
}

export function contributionScale(contributions: PredictionContribution[]) {
  return Math.max(1, ...contributions.map(item => Math.abs(item.shapValue)));
}

export function contributionEffect(direction?: string) {
  return direction === "increases" ? "raises" : "lowers";
}

const currencySymbols: Record<string, string> = { INR: "₹", USD: "$", EUR: "€", GBP: "£" };

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function selectedList(answers: Record<string, unknown>, key: string) {
  const value = answers[key];
  if (!Array.isArray(value)) return [] as string[];
  return (value as string[]).filter(item => item !== "none");
}

// Maps one model contribution group to the plain-language answer the user
// actually submitted, so the results page can say "your petrol car pushed the
// estimate up" instead of naming an abstract feature group.
export function surveyAnswersText(feature: string, answers: Record<string, unknown> | undefined): string {
  const a = answers ?? {};
  switch (feature) {
    case "transport_and_distance": {
      const mode =
        a.transport === "private" ? "Private vehicle"
        : a.transport === "public" ? "Public transport"
        : "Walking / cycling";
      return `${mode}, ${a.vehicle_monthly_distance_km ?? 0} km per month`;
    }
    case "air_travel_frequency":
      return `Flying: ${capitalize(String(a.frequency_of_traveling_by_air ?? "rarely"))}`;
    case "new_clothing":
      return `${a.how_many_new_clothes_monthly ?? 0} new clothing items per month`;
    case "vehicle_type": {
      const vehicle = String(a.vehicle_type ?? "none");
      return vehicle === "none" ? "No private vehicle selected" : `${capitalize(vehicle)}-powered car`;
    }
    case "profile_fields":
      return "Dataset reference profile (gender/body type not asked; no emission mechanism)";
    case "waste_and_recycling": {
      const recycled = selectedList(a, "recycling");
      const recycling = recycled.length ? ` · recycling ${recycled.join(", ")}` : "";
      return `${a.waste_bag_weekly_count ?? 0} ${a.waste_bag_size ?? "medium"} waste bags per week${recycling}`;
    }
    case "diet_and_grocery": {
      const symbol = currencySymbols[String(a.currency ?? "INR")] ?? "₹";
      return `${capitalize(String(a.diet ?? "omnivore"))} diet · ${symbol}${a.monthly_grocery_bill ?? 0} groceries per month`;
    }
    case "digital_use":
      return `${a.how_long_tv_pc_daily_hour ?? 0} h TV/PC · ${a.how_long_internet_daily_hour ?? 0} h internet daily`;
    case "social_activity":
      return "Dataset reference value (social activity not asked; no emission mechanism)";
    case "cooking_equipment": {
      const cooking = selectedList(a, "cooking_with");
      return cooking.length ? `Cooking with ${cooking.join(", ")}` : "No cooking appliances selected";
    }
    case "shower_frequency":
      return "Dataset reference value (shower frequency not asked; near-zero model effect)";
    case "home_energy":
      return `Heating source: ${String(a.heating_energy_source ?? "electricity")}`;
    case "energy_efficiency":
      return "Dataset reference value (efficiency scale not asked; near-zero model effect)";
    default:
      return "";
  }
}

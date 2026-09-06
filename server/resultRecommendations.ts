export type CompletedRecommendationProfile = {
  diet: "vegan" | "vegetarian" | "omnivore" | "pescatarian";
  transport: "private" | "public" | "walk/bicycle";
  vehicle_type: "none" | "petrol" | "diesel" | "electric" | "hybrid" | "lpg";
  vehicle_monthly_distance_km: number;
  heating_energy_source: "electricity" | "natural gas" | "wood";
  how_many_new_clothes_monthly: number;
};

export const approvedRecommendationCatalog = [
  { key: "transit_two_trips", title: "Shift two weekly car trips", description: "Replace two short private-vehicle journeys with public transport, walking, or cycling.", category: "transport", estimatedReductionKg: 32 },
  { key: "cleaner_energy", title: "Use a lower-carbon energy mix", description: "Review renewable electricity or lower-carbon heating options available in your region.", category: "electricity", estimatedReductionKg: 44 },
  { key: "lower_impact_meals", title: "Choose lower-impact meals", description: "Trial two lower-impact meals each week and track the change rather than guessing at outcomes.", category: "diet", estimatedReductionKg: 26 },
  { key: "fuel_efficiency", title: "Reduce avoidable fuel use", description: "Combine trips and monitor fuel consumption before and after the change.", category: "fuel", estimatedReductionKg: 18 },
] as const;

export function selectResultLedRecommendations(profile: CompletedRecommendationProfile) {
  const selected = new Map<string, { provenance: string; trigger: string }>();
  if (profile.transport === "private" && profile.vehicle_monthly_distance_km > 0) {
    selected.set("transit_two_trips", { provenance: "AI profile + transparent transport factor", trigger: `Private travel and ${profile.vehicle_monthly_distance_km} km/month are present in your completed result.` });
  }
  if (profile.transport === "private" && ["petrol", "diesel", "lpg"].includes(profile.vehicle_type)) {
    selected.set("fuel_efficiency", { provenance: "AI profile + transparent transport factor", trigger: `${profile.vehicle_type} vehicle use is present in your completed result.` });
  }
  if (profile.heating_energy_source === "electricity") {
    selected.set("cleaner_energy", { provenance: "AI profile + transparent electricity factor", trigger: "Electricity is the selected heating source in your completed result." });
  }
  if (["omnivore", "pescatarian"].includes(profile.diet)) {
    selected.set("lower_impact_meals", { provenance: "AI profile + baseline screening proxy", trigger: `${profile.diet} diet is present in your completed result.` });
  }
  if (selected.size === 0) {
    selected.set("cleaner_energy", { provenance: "Completed-result planning lens", trigger: "This is a broad next step for reviewing the energy assumptions in your completed result." });
  }
  return approvedRecommendationCatalog.filter(item => selected.has(item.key)).map(item => ({ ...item, ...selected.get(item.key)! }));
}

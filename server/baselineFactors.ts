/**
 * v2.5-aligned cited factor set (TypeScript mirror of
 * backend/app/services/baseline.py FACTOR_SET). Every coefficient is shared
 * with the v2.5 dataset target and the deployed XGBoost model: Ember 2025
 * grid factors, IPCC 2006 fuel chemistry at mid-range fleet economy,
 * Scarborough 2023 diet bands, OWID air bands, EEA clothing, IPCC waste.
 * The retired DESNZ 2026 UK-only reference values (0.13096 grid,
 * 0.10151 bus) are no longer used by any estimation path.
 */
export const TRANSPARENT_BASELINE_FACTOR_SET = {
  id: "carbonsense-v25-aligned-cited-factors",
  label: "v2.5-aligned cited factors: Ember 2025 grid, IPCC 2006 fuel chemistry, Scarborough 2023 diet, OWID air bands, EEA clothing, IPCC waste",
  gridByCountry: { india: 0.67013, us: 0.38440, uk: 0.21741 },
  renewableHeavyGrid: { india: 0.147, us: 0.085, uk: 0.048 },
  groceryByCountry: { india: 0.11, us: 0.36, uk: 0.44 },
  // IPCC 2006 combustion chemistry at the dataset's mid-range economy.
  vehicleKgPerKm: { petrol: 0.1155, diesel: 0.1449, hybrid: 0.0924, lpg: 0.1, none: 0 } as Record<string, number>,
  evKwhPerKm: 0.18,
  transitKgPerPassengerKm: 0.02,
  transitDistanceMultiplier: 1.15,
  monthlyElectricityReferenceKwh: 220,
} as const;

/** Grid factor for a submitted country/region pair (kgCO2e/kWh). */
export function gridFactorFor(country: string | undefined, region: string | undefined): number {
  const c = country && country in TRANSPARENT_BASELINE_FACTOR_SET.gridByCountry ? country : "india";
  return region === "renewable_heavy"
    ? TRANSPARENT_BASELINE_FACTOR_SET.renewableHeavyGrid[c as keyof typeof TRANSPARENT_BASELINE_FACTOR_SET.renewableHeavyGrid]
    : TRANSPARENT_BASELINE_FACTOR_SET.gridByCountry[c as keyof typeof TRANSPARENT_BASELINE_FACTOR_SET.gridByCountry];
}

/** Per-km vehicle factor; electric vehicles scale by the country grid. */
export function vehicleFactorFor(vehicleType: string, grid: number): number {
  if (vehicleType === "electric") return TRANSPARENT_BASELINE_FACTOR_SET.evKwhPerKm * grid;
  return TRANSPARENT_BASELINE_FACTOR_SET.vehicleKgPerKm[vehicleType] ?? 0;
}

/** Effective per-km public-transit factor (CNG/metro band x transit distance). */
export const transitFactor =
  TRANSPARENT_BASELINE_FACTOR_SET.transitKgPerPassengerKm * TRANSPARENT_BASELINE_FACTOR_SET.transitDistanceMultiplier;

export const TRANSPARENT_BASELINE_SOURCES = [
  {
    label: "Ember/OWID carbon-intensity dataset (2025, fetched 2026-09-03)",
    url: "https://ourworldindata.org/grapher/carbon-intensity-electricity.csv",
    coverage: "India, US, and UK grid factors (identical to the v2.5 model factor inputs)",
  },
  {
    label: "IPCC 2006 Guidelines, Vol.2 Energy (fuel chemistry)",
    url: "https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol2.html",
    coverage: "Petrol 2.31 and diesel 2.68 kgCO2e/litre combustion factors; LPG ~3.0 kgCO2e/kg",
  },
  {
    label: "Scarborough 2023 dietary GHG bands",
    url: "https://doi.org/10.1016/j.pecinn.2022.100055",
    coverage: "High-plant / vegetarian / pescatarian / omnivore monthly diet bands",
  },
  {
    label: "OWID air-travel emissions bands",
    url: "https://ourworldindata.org/carbon-footprint-flying",
    coverage: "Monthly kgCO2e bands by self-reported flight frequency",
  },
] as const;

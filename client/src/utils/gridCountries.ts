import { surveyDefaults } from "@/store/survey";

// The country is context, not a question: selected once via the grid
// selector in the form header and switchable at any time. It resolves the
// grid emission factor applied to every electrical line and the grocery
// spend factor for the food line (cited values - citations/country-factors.md).
export const gridCountries = {
  india: { label: "India", flag: "🇮🇳", gridFactor: 0.67013, groceryFactor: 0.11, currency: "INR" },
  us: { label: "United States", flag: "🇺🇸", gridFactor: 0.38440, groceryFactor: 0.36, currency: "USD" },
  uk: { label: "United Kingdom", flag: "🇬🇧", gridFactor: 0.21741, groceryFactor: 0.44, currency: "GBP" },
} as const;

export type GridCountry = keyof typeof gridCountries;

export const gridCountryKeys = Object.keys(gridCountries) as GridCountry[];

// Factors as fetched (Ember/OWID 2025): India 670.13, US 384.40, UK 217.41 gCO2e/kWh.
export const GRID_FACTORS: Record<GridCountry, { mixed: number; renewableHeavy: number }> = {
  india: { mixed: 0.67013, renewableHeavy: 0.147 },
  us: { mixed: 0.38440, renewableHeavy: 0.085 },
  uk: { mixed: 0.21741, renewableHeavy: 0.048 },
};

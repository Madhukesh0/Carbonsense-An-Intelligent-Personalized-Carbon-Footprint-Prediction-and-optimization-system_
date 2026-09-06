/**
 * v2.5-aligned transparent baseline calculator (client mirror of
 * backend/app/services/baseline.py). Every coefficient is the cited value
 * the v2.5 dataset target and the deployed XGBoost model share: Ember 2025
 * grid factors, IPCC 2006 fuel chemistry at mid-range fleet economy,
 * Scarborough 2023 diet bands, OWID air bands, EEA clothing, IPCC waste.
 * The retired DESNZ 2026 UK-only reference values are not used anywhere.
 */
import { GRID_FACTORS, type GridCountry } from "@/utils/gridCountries";

export const V25_FACTORS = {
  // Derived exactly like backend/app/services/baseline.py (fuel chemistry at
  // mid-range economy) so float rounding matches the API bit-for-bit.
  vehicleKgPerKm: { petrol: 2.31 / 20.0, diesel: 2.68 / 18.5, hybrid: 2.31 / 25.0, lpg: 3.0 / 30.0 } as Record<string, number>,
  evKwhPerKm: 0.18,
  transitKgPerPassengerKm: 0.02,
  transitDistanceMultiplier: 1.15,
  tvWatts: 75,
  internetWatts: 40,
  baseLoadKwh: 65,
  electricHeatingKwh: 100,
  heatingFlatKg: { electricity: 0, "natural gas": 20, wood: 8 } as Record<string, number>,
  cookingApplianceKwh: { stove: 12, oven: 9, microwave: 5, grill: 7, airfryer: 8 } as Record<string, number>,
  lpgCookingKg: 15,
  weeksPerMonth: 4.3,
  wasteKgPerKg: 0.65,
  bagMassKg: { small: 5, medium: 10, large: 20, "extra large": 30 } as Record<string, number>,
  recyclingCreditKg: { paper: 4, plastic: 6, metal: 12, glass: 2 } as Record<string, number>,
  dietBand: { vegan: 90, vegetarian: 115, pescatarian: 120, omnivore: 215 } as Record<string, number>,
  airBand: { never: 0, rarely: 60, often: 180, "very frequently": 420 } as Record<string, number>,
  clothingKgPerItem: 18,
  groceryByCountry: { india: 0.11, us: 0.36, uk: 0.44 } as Record<GridCountry, number>,
} as const;

export type AlignedBaselineInput = {
  country: GridCountry;
  renewableHeavy: boolean;
  vehicleMonthlyDistanceKm: number;
  vehicleFuel: string;
  tvHours: number;
  internetHours: number;
  heating: string;
  diet: string;
  groceryBill: number;
  newClothes: number;
  bagSize: string;
  bagsPerWeek: number;
  recycling: string[];
  cooking: string[];
  air: string;
};

export const alignedBaselineDefaults: AlignedBaselineInput = {
  country: "india",
  renewableHeavy: false,
  vehicleMonthlyDistanceKm: 300,
  vehicleFuel: "petrol",
  tvHours: 4,
  internetHours: 4,
  heating: "electricity",
  diet: "omnivore",
  groceryBill: 200,
  newClothes: 2,
  bagSize: "medium",
  bagsPerWeek: 3,
  recycling: ["paper"],
  cooking: ["stove", "oven"],
  air: "rarely",
};



export function gridFactorFor(country: GridCountry, renewableHeavy: boolean): number {
  return renewableHeavy ? GRID_FACTORS[country].renewableHeavy : GRID_FACTORS[country].mixed;
}

export function vehicleKgPerKmFor(fuel: string, grid: number): number {
  if (fuel === "electric") return V25_FACTORS.evKwhPerKm * grid;
  return V25_FACTORS.vehicleKgPerKm[fuel] ?? 0;
}

export function calculateAlignedBaseline(input: AlignedBaselineInput) {
  const grid = gridFactorFor(input.country, input.renewableHeavy);
  const groceryFactor = V25_FACTORS.groceryByCountry[input.country];
  const household = 1; // the standalone calculator models one person

  const vehicleKgPerKm = vehicleKgPerKmFor(input.vehicleFuel, grid);
  const transport = input.vehicleMonthlyDistanceKm * vehicleKgPerKm;
  const electricityKwh =
    (input.tvHours * V25_FACTORS.tvWatts / 1000 + input.internetHours * V25_FACTORS.internetWatts / 1000) * 30
    + V25_FACTORS.baseLoadKwh
    + (input.heating === "electricity" ? V25_FACTORS.electricHeatingKwh : 0);
  const homeEnergy = electricityKwh * grid / household + V25_FACTORS.heatingFlatKg[input.heating];
  const diet = V25_FACTORS.dietBand[input.diet] ?? 0;
  const food = diet + input.groceryBill * groceryFactor;
  const credits = input.recycling.reduce((sum, item) => sum + (V25_FACTORS.recyclingCreditKg[item] ?? 0), 0);
  const waste = Math.max(0, input.bagsPerWeek * V25_FACTORS.weeksPerMonth
    * (V25_FACTORS.bagMassKg[input.bagSize] ?? 0) * V25_FACTORS.wasteKgPerKg / household - credits);
  const clothing = input.newClothes * V25_FACTORS.clothingKgPerItem;
  const cookingKwh = input.cooking.reduce((sum, item) => sum + (V25_FACTORS.cookingApplianceKwh[item] ?? 0), 0);
  const cooking = cookingKwh * grid + (input.cooking.includes("stove") ? V25_FACTORS.lpgCookingKg : 0);
  const air = V25_FACTORS.airBand[input.air] ?? 0;

  return {
    total: round(transport + homeEnergy + food + waste + clothing + cooking + air),
    grid,
    groceryFactor,
    vehicleKgPerKm,
    electricityKwh: round(electricityKwh),
    breakdown: {
      transport: round(transport),
      home_energy: round(homeEnergy),
      food: round(food),
      waste: round(waste),
      clothing: round(clothing),
      cooking: round(cooking),
      air_travel: air,
    },
    arithmetic: {
      transport: `${input.vehicleMonthlyDistanceKm} km × ${round(vehicleKgPerKm, 4)} kg/km (${input.vehicleFuel}, IPCC chemistry)`,
      home_energy: `${round(electricityKwh)} kWh × ${grid} kg/kWh (${input.renewableHeavy ? "renewable" : input.country} grid)${V25_FACTORS.heatingFlatKg[input.heating] ? ` + ${V25_FACTORS.heatingFlatKg[input.heating]} kg ${input.heating} heating` : ""}`,
      food: `${input.diet} band ${diet} kg (Scarborough 2023) + ${input.groceryBill} × ${groceryFactor}`,
      waste: `${input.bagsPerWeek} bags × 4.3 wk × ${V25_FACTORS.bagMassKg[input.bagSize]} kg × 0.65 kg/kg${credits ? ` − ${credits} kg recycling credits` : ""}`,
      clothing: `${input.newClothes} items × 18 kg (EEA)`,
      cooking: `${cookingKwh} appliance-kWh × ${grid} kg/kWh${input.cooking.includes("stove") ? " + 15 kg partial LPG" : ""}`,
      air_travel: `${input.air} band (OWID)`,
    },
  };
}

function round(value: number, decimals = 1) {
  // Mirrors Python round() (half-to-even) so the client matches the API at
  // exact .x5 boundaries, e.g. round(34.65, 1) = 34.6 in both.
  const factor = 10 ** decimals;
  const scaled = value * factor;
  const floor = Math.floor(scaled);
  const diff = scaled - floor;
  const nearest = diff > 0.5 ? floor + 1 : diff < 0.5 ? floor : floor % 2 === 0 ? floor : floor + 1;
  return nearest / factor;
}

"""Transparent baseline factor and proxy calculations for FastAPI.

v2.6: fully aligned with the v2.5 model factor set. The baseline is the
deterministic form of the same cited-factor construction the dataset
target uses (scripts/generate_dataset_v2.py), so the AI estimate vs
baseline gap reflects model behaviour, not factor drift. Country-aware:
the electricity line scales submitted screen-time hours by the country's
Ember 2025 grid factor (India cross-referenced with CEA), the grocery
spend uses the per-currency price-level factor, and shared home-energy
and waste lines are divided per household member. The ``renewable_heavy``
region applies the declared renewable proxy modifier. The v1 UK-only
DESNZ reporting-basis grid factor (0.13096) and local-bus proxy (0.10151)
are retired from this path.
"""

from __future__ import annotations

from typing import Any


FACTOR_SET = {
    "id": "carbonsense-v25-aligned-cited-factors",
    "label": "v2.5-aligned cited factors: Ember 2025 grid, IPCC 2006 fuel chemistry, Scarborough 2023 diet, OWID air bands, EEA clothing, IPCC waste",
    # Same Ember 2025 generation-based grid factors the v2.5 dataset and model
    # use (fetched 2026-09-03, data year 2025); UK 0.21741 replaces the
    # retired DESNZ reporting-basis 0.13096 so both paths share one grid
    # number per country.
    "gridByCountry": {"india": 0.67013, "us": 0.38440, "uk": 0.21741},
    "renewableHeavyGrid": {"india": 0.147, "us": 0.085, "uk": 0.048},
    "groceryByCountry": {"india": 0.11, "us": 0.36, "uk": 0.44},
    # Vehicle factors derived from IPCC 2006 fuel chemistry at the dataset's
    # mid-range fleet economy, matching the model's training construction.
    "fuelKgPerL": {"petrol": 2.31, "diesel": 2.68},
    "midKmPerL": {"petrol": 20.0, "diesel": 18.5, "hybrid": 25.0},
    "lpgKgPerKg": 3.0,
    "midKmPerKgLpg": 30.0,
    "evKwhPerKm": 0.18,
    # Derived per-km factors (fuel chemistry at mid-range economy). The
    # electric entry is computed at runtime as evKwhPerKm x grid because it
    # depends on the selected country's grid factor.
    "vehicleKgPerKm": {"petrol": 0.1155, "diesel": 0.1449, "hybrid": 0.0924, "lpg": 0.1, "none": 0},
    # CNG bus / metro low band with the dataset's 1.15 transit-distance
    # multiplier: 0.02 x 1.15 = 0.023 effective kg per surveyed km.
    "transitKgPerPassengerKm": 0.02,
    "transitDistanceMultiplier": 1.15,
    # Home-energy device conventions (v2.5 dataset construction).
    "tvWatts": 75.0,
    "internetWatts": 40.0,
    "baseLoadKwh": 65.0,
    "electricHeatingKwh": 100.0,
    "heatingFlatKgPerMonth": {"natural gas": 20.0, "wood": 8.0},
    # Cooking (v2.5 dataset construction).
    "cookingApplianceKwh": {"stove": 12.0, "oven": 9.0, "microwave": 5.0, "grill": 7.0, "airfryer": 8.0},
    "lpgCookingKgPerMonth": 15.0,
    # Waste (IPCC Vol.5) and recycling credits.
    "weeksPerMonth": 4.3,
    "wasteKgPerKg": 0.65,
    "bagMassKg": {"small": 5.0, "medium": 10.0, "large": 20.0, "extra large": 30.0},
    "recyclingCreditKg": {"paper": 4.0, "plastic": 6.0, "metal": 12.0, "glass": 2.0},
    # Retained for planning tools: the shared-reference electricity activity.
    "monthlyElectricityReferenceKwh": 220,
}
SOURCES = [
    {"label": "Ember/OWID carbon-intensity dataset (2025, fetched 2026-09-03)", "url": "https://ourworldindata.org/grapher/carbon-intensity-electricity.csv", "coverage": "India, US, and UK grid factors (identical to the v2.5 model factor inputs)"},
    {"label": "CEA CO2 Baseline Database v21.0 (India)", "url": "https://cea.nic.in/cdm-co2-baseline-database/?lang=en", "coverage": "India official fiscal-year grid factor cross-reference"},
    {"label": "IPCC 2006 Guidelines, Vol.2 Energy (fuel chemistry)", "url": "https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol2.html", "coverage": "Petrol 2.31 and diesel 2.68 kgCO2e/litre combustion factors; LPG ~3.0 kgCO2e/kg"},
    {"label": "Scarborough 2023 dietary GHG bands", "url": "https://doi.org/10.1016/j.pecinn.2022.100055", "coverage": "High-plant / vegetarian / pescatarian / omnivore monthly diet bands"},
    {"label": "OWID air-travel emissions bands", "url": "https://ourworldindata.org/carbon-footprint-flying", "coverage": "Monthly kgCO2e bands by self-reported flight frequency"},
    {"label": "EEA clothing footprint estimate", "url": "https://www.eea.europa.eu/", "coverage": "~18 kgCO2e per new garment (textiles lifecycle proxy)"},
]
SCREENING = {
    "diet": {"vegan": 90, "vegetarian": 115, "pescatarian": 120, "omnivore": 215},
    "air": {"never": 0, "rarely": 60, "often": 180, "very frequently": 420},
    "clothing": 18,
}


def _vehicle_factor(country: str, grid: float, vehicle_type: str) -> tuple[float, str]:
    """Return (kg per km, arithmetic note) for the reported vehicle fuel."""
    if vehicle_type == "petrol":
        return FACTOR_SET["fuelKgPerL"]["petrol"] / FACTOR_SET["midKmPerL"]["petrol"], f"{FACTOR_SET['fuelKgPerL']['petrol']} kg/L at {FACTOR_SET['midKmPerL']['petrol']} km/L mid-range"
    if vehicle_type == "diesel":
        return FACTOR_SET["fuelKgPerL"]["diesel"] / FACTOR_SET["midKmPerL"]["diesel"], f"{FACTOR_SET['fuelKgPerL']['diesel']} kg/L at {FACTOR_SET['midKmPerL']['diesel']} km/L mid-range"
    if vehicle_type == "hybrid":
        return FACTOR_SET["fuelKgPerL"]["petrol"] / FACTOR_SET["midKmPerL"]["hybrid"], f"{FACTOR_SET['fuelKgPerL']['petrol']} kg/L at {FACTOR_SET['midKmPerL']['hybrid']} km/L (hybrid economy)"
    if vehicle_type == "lpg":
        return FACTOR_SET["lpgKgPerKg"] / FACTOR_SET["midKmPerKgLpg"], f"{FACTOR_SET['lpgKgPerKg']} kg/kg at {FACTOR_SET['midKmPerKgLpg']} km/kg (IPCC LPG)"
    if vehicle_type == "electric":
        return FACTOR_SET["evKwhPerKm"] * grid, f"{FACTOR_SET['evKwhPerKm']} kWh/km x {grid} kg/kWh grid"
    return 0.0, "no vehicle"


def calculate_baseline(input_payload: dict[str, Any]) -> dict[str, Any]:
    """Deterministic cited-factor baseline over the submitted survey answers.

    Line-for-line mirrors the v2.5 dataset target construction with the
    mid-range value of every sampled quantity (fuel economy, base load,
    electric-heating boost), so a submitted profile has one formula number
    to compare against the model's learned estimate.
    """
    country = input_payload.get("country", "india")
    if country not in FACTOR_SET["gridByCountry"]:
        country = "india"
    household = max(1, int(input_payload.get("household_size", 2)))
    renewable = input_payload.get("region") == "renewable_heavy"
    grid = (FACTOR_SET["renewableHeavyGrid"] if renewable else FACTOR_SET["gridByCountry"])[country]
    grocery_factor = FACTOR_SET["groceryByCountry"][country]

    # --- transport (personal; never divided) ---
    distance = float(input_payload.get("vehicle_monthly_distance_km", 0) or 0)
    if input_payload["transport"] == "private":
        vehicle_factor, vehicle_note = _vehicle_factor(country, grid, input_payload["vehicle_type"])
        transport = distance * vehicle_factor
        transport_note = f"{distance} km x {round(vehicle_factor, 4)} kg/km ({vehicle_note})"
    elif input_payload["transport"] == "public":
        transport = distance * FACTOR_SET["transitKgPerPassengerKm"] * FACTOR_SET["transitDistanceMultiplier"]
        transport_note = f"{distance} km x {FACTOR_SET['transitKgPerPassengerKm']} kg/pkm (CNG/metro band) x {FACTOR_SET['transitDistanceMultiplier']} transit distance"
    else:
        transport = 0.0
        transport_note = "walking / cycling (food emissions already counted)"

    # --- home energy (shared per person) ---
    tv_h = float(input_payload.get("how_long_tv_pc_daily_hour", 0) or 0)
    net_h = float(input_payload.get("how_long_internet_daily_hour", 0) or 0)
    heating = input_payload.get("heating_energy_source", "electricity")
    electricity_kwh = (tv_h * FACTOR_SET["tvWatts"] / 1000
                       + net_h * FACTOR_SET["internetWatts"] / 1000) * 30
    electricity_kwh += FACTOR_SET["baseLoadKwh"]
    if heating == "electricity":
        electricity_kwh += FACTOR_SET["electricHeatingKwh"]
    heating_flat = FACTOR_SET["heatingFlatKgPerMonth"].get(heating, 0.0)
    home_energy = round(electricity_kwh * grid / household + heating_flat, 1)
    home_note = (f"({tv_h} h x 75 W + {net_h} h x 40 W) x 30 d + {FACTOR_SET['baseLoadKwh']} kWh base"
                 + (f" + {FACTOR_SET['electricHeatingKwh']} kWh electric heating" if heating == "electricity" else "")
                 + f" = {round(electricity_kwh, 1)} kWh x {grid} kg/kWh / {household} people"
                 + (f" + {heating_flat} kg {heating} heating" if heating_flat else ""))

    # --- food ---
    diet = SCREENING["diet"][input_payload["diet"]]
    food = round(diet + float(input_payload["monthly_grocery_bill"]) * grocery_factor, 1)
    food_note = f"{input_payload['diet']} band {diet} kg (Scarborough 2023) + {input_payload['monthly_grocery_bill']} x {grocery_factor}"

    # --- waste (shared per person, minus recycling credits) ---
    bag_mass = FACTOR_SET["bagMassKg"][input_payload["waste_bag_size"]]
    credits = sum(FACTOR_SET["recyclingCreditKg"].get(item, 0.0)
                  for item in (input_payload.get("recycling") or []))
    waste = max(0.0, round(float(input_payload["waste_bag_weekly_count"]) * FACTOR_SET["weeksPerMonth"]
                           * bag_mass * FACTOR_SET["wasteKgPerKg"] / household - credits, 1))
    waste_note = (f"{input_payload['waste_bag_weekly_count']} bags x {FACTOR_SET['weeksPerMonth']} weeks x {bag_mass} kg x {FACTOR_SET['wasteKgPerKg']} kg/kg / {household} people"
                  + (f" - {credits} kg recycling credits" if credits else ""))

    # --- consumption & cooking ---
    clothing = round(float(input_payload["how_many_new_clothes_monthly"]) * SCREENING["clothing"], 1)
    clothing_note = f"{input_payload['how_many_new_clothes_monthly']} items x {SCREENING['clothing']} kg (EEA textiles proxy)"
    cooking_with = input_payload.get("cooking_with") or []
    cooking_kwh = sum(FACTOR_SET["cookingApplianceKwh"].get(item, 0.0) for item in cooking_with)
    cooking = cooking_kwh * grid + (FACTOR_SET["lpgCookingKgPerMonth"] if "stove" in cooking_with else 0.0)
    cooking = round(cooking, 1)
    cooking_note = (f"{cooking_kwh} appliance-kWh x {grid} kg/kWh"
                    + (f" + {FACTOR_SET['lpgCookingKgPerMonth']} kg partial LPG" if "stove" in cooking_with else ""))

    # --- air travel ---
    travel = SCREENING["air"][input_payload["frequency_of_traveling_by_air"]]
    travel_note = f"{input_payload['frequency_of_traveling_by_air']} band (OWID flight bands)"

    total = round(transport + home_energy + food + waste + clothing + cooking + travel, 1)
    breakdown = {"transport": round(transport, 1), "home_energy": home_energy, "food": food,
                 "waste": waste, "clothing": clothing, "cooking": cooking, "air_travel": travel}
    arithmetic = {"transport": transport_note, "home_energy": home_note, "food": food_note,
                  "waste": waste_note, "clothing": clothing_note, "cooking": cooking_note,
                  "air_travel": travel_note}
    return {
        "total": total,
        "country": country,
        "gridFactorKgPerKwh": grid,
        "householdSize": household,
        "renewableHeavy": renewable,
        "breakdown": breakdown,
        "arithmetic": arithmetic,
        "factorSet": FACTOR_SET,
        "sourceReferences": SOURCES,
        "sources": [source["label"] for source in SOURCES],
        "assumptions": [
            f"Electricity scales your submitted TV/PC and internet hours ({round(electricity_kwh, 1)} kWh/month incl. base load and electric heating) at the {country.upper()} grid factor ({grid} kgCO2e/kWh), divided by household size ({household}).",
            f"Vehicle distance uses IPCC 2006 combustion chemistry at mid-range fleet economy ({input_payload['vehicle_type']}: {round(FACTOR_SET['vehicleKgPerKm'].get(input_payload['vehicle_type'], 0) if input_payload['vehicle_type'] != 'electric' else FACTOR_SET['evKwhPerKm'] * grid, 4)} kg/km); transit uses a CNG/metro band.",
            f"Diet ({diet} kg), air-travel ({travel} kg), waste-bag, and clothing lines are the same declared screening bands the v2.5 dataset target uses.",
            f"Shared lines (home energy, waste) are divided per household member ({household}); recycling credits ({credits} kg) subtract avoided virgin-material emissions.",
            "Grid factors are national averages (Ember 2025), not state/city-specific measurements.",
        ],
    }

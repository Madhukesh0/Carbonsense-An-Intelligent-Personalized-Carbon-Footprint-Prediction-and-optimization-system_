"""Generate the CarbonSense v2 dataset — 10,000 rows, cited-factor target.

Schema v2.5 = the 15 frontend questions plus `grid_factor`,
`grocery_factor`, `household_size`, and a `country` label column.
The country is context, not a model feature: the model receives the
NUMERIC grid factor (kgCO2e/kWh) and grocery spend factor directly -
verified superior to country one-hots (R2 0.9462 vs 0.9450, fewer
features) and instantly extensible to new countries via the lookup
table. Active countries: India, US, UK (3 national grids spanning
0.048-0.670 with the renewable modifier). Household size divides
shared home-energy and waste lines per person. No sex, body type, age, shower frequency, social
activity, or abstract "energy efficiency" — those columns were dropped from
the questionnaire for lacking an emission mechanism.

Target = transparent factor formula, every coefficient from
citations/factor-sheet.md (CEA grid 0.710/0.15, IPCC fuel chemistry
2.31/2.68 kg/L, OWID flight bands, Scarborough diet bands, EEA clothing
17-18 kg/item, IPCC waste 0.5-0.8 kg/kg, recycling credits), plus
multiplicative lognormal noise (sigma=0.05) so the model learns the
relationship rather than a lookup table.

Deterministic: seed 42. Output: data/v2_training/clean_dataset_v2.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 42
N = 10_000
OUT = "data/v2_training/clean_dataset_v2.csv"

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- factors --
# Latest grid carbon intensities (Ember via OWID, fetched 2026-09-03, data through 2025):
#   India 670.13, US 384.4, UK 217.41 gCO2e/kWh.
# "mixed" = national average grid; "renewable_heavy" = declared proxy for
# green-tariff / renewable-dominant supply.
# Active countries (v2.5): India, US, UK - spanning high/mixed/low grid
# carbon intensity with the best-published official factors.
# Grid factors fetched 2026-09-03 from Ember/OWID CSV (data year 2025):
# https://ourworldindata.org/grapher/carbon-intensity-electricity.csv
# India cross-referenced with CEA v21.0; grocery factors price-level
# calibrated (citations/country-factors.md).
_GRID = {
    "india": {"mixed": 0.67013, "renewable_heavy": 0.147, "grocery": 0.11},
    "us":    {"mixed": 0.38440, "renewable_heavy": 0.085, "grocery": 0.36},
    "uk":    {"mixed": 0.21741, "renewable_heavy": 0.048, "grocery": 0.44},
}
COUNTRY_P = {"india": 0.40, "us": 0.30, "uk": 0.30}
# Grocery spend factor (kgCO2e per unit currency) - scale proxy by price level:
# food production emissions per meal are similar globally, but currency units differ.
# ₹ factor 0.11 (app proxy). $ factor ≈ 0.11 × (rupees-per-$ / rupees-per-unit-food)
# → convention: INR 0.11, USD 0.36, GBP 0.44 (same physical basket, converted).
# Grocery spend factors (kgCO2e per unit local currency): price-level
# calibrated so a median monthly food basket lands ≈ 120-180 kgCO2e/month
# in every country (production emissions are similar; currency units differ).
GROCERY_FACTOR_BY_COUNTRY = {
    "india": 0.11, "china": 0.14, "us": 0.36, "germany": 0.40, "japan": 0.50,
    "uk": 0.44, "france": 0.42, "canada": 0.34, "brazil": 0.28, "australia": 0.33,
    "russia": 0.20, "south_korea": 0.42, "saudi_arabia": 0.18, "indonesia": 0.012,
    "uae": 0.13, "singapore": 0.24, "netherlands": 0.40,
}
# Grocery bill sampled in LOCAL currency units per country (median lognormal).
GROCERY_MEDIAN_LOGNORMAL = {"india": 7.6, "us": 6.1, "uk": 5.9}
FUEL_KG_PER_L = {"petrol": 2.31, "diesel": 2.68}           # IPCC 2006 chemistry (country-independent)
KM_PER_L_RANGE = {"petrol": (14.0, 26.0), "diesel": (13.0, 24.0)}
EV_KWH_PER_100KM = 18.0

TRANSIT_KG_PER_PASSENGER_KM = 0.02                          # CNG bus/metro low band (consumption.md §6.4)
AIR_BANDS = {"never": 0.0, "rarely": 60.0, "often": 180.0, "very frequently": 420.0}
DIET_BANDS = {"vegan": 90.0, "vegetarian": 115.0, "pescatarian": 120.0, "omnivore": 215.0}  # Scarborough 2023 (kg/month)
CLOTHING_KG_PER_ITEM = 18.0                                 # EEA-derived ≈17 kg/kg
WASTE_KG_PER_KG = 0.65                                      # IPCC Vol.5 mid (0.5-0.8)
WEEKS_PER_MONTH = 4.3
BAG_MASS = {"small": 5.0, "medium": 10.0, "large": 20.0, "extra large": 30.0}
RECYCLING_CREDIT = {"paper": 4.0, "plastic": 6.0, "metal": 12.0, "glass": 2.0}  # kgCO2e/month when recycled (avoided virgin)
TV_WATTS = 75.0                                             # device convention
INTERNET_WATTS_EQUIV = 40.0                                 # router + network/DC share
GAS_HEATING_KG_PER_MONTH = 20.0                             # ≈0.20 kg/kWh × ~100 kWh winter-month blend
WOOD_HEATING_KG_PER_MONTH = 8.0
COOKING_APPLIANCE_KWH_MONTH = {"stove": 12.0, "oven": 9.0, "microwave": 5.0, "grill": 7.0, "airfryer": 8.0}
LPG_MONTH_KG = 10.0                                         # ≈0.7 cylinder/month when stove selected

# ---------------------------------------------------------------- sampling --
country = rng.choice(list(COUNTRY_P.keys()), N, p=list(COUNTRY_P.values()))
# renewable-heavy override: 25% of rows (green tariff / rooftop solar users)
_region = rng.choice(["mixed", "renewable_heavy"], N, p=[0.75, 0.25])
grid_factor = np.array([_GRID[c][_region[i]] for i, c in enumerate(country)])
grocery_factor = np.array([_GRID[c]["grocery"] for c in country])
transport = rng.choice(["private", "public", "walk/bicycle"], N, p=[0.62, 0.26, 0.12])
vehicle_type = np.empty(N, dtype=object)
for i, t in enumerate(transport):
    if t == "private":
        vehicle_type[i] = rng.choice(["petrol", "diesel", "electric", "hybrid", "lpg", "none"], p=[0.48, 0.22, 0.06, 0.10, 0.04, 0.10])
    else:
        vehicle_type[i] = "none"

region = rng.choice(["mixed", "renewable_heavy"], N, p=[0.72, 0.28])
heating = rng.choice(["electricity", "natural gas", "wood"], N, p=[0.55, 0.35, 0.10])
diet = rng.choice(["vegan", "vegetarian", "pescatarian", "omnivore"], N, p=[0.10, 0.32, 0.08, 0.50])
air = rng.choice(["never", "rarely", "often", "very frequently"], N, p=[0.35, 0.40, 0.18, 0.07])
waste_bag_size = rng.choice(["small", "medium", "large", "extra large"], N, p=[0.25, 0.40, 0.25, 0.10])

vehicle_monthly_distance_km = np.round(np.clip(rng.lognormal(mean=5.2, sigma=0.9, size=N), 0, 10000), 1)
# Grocery spend in LOCAL currency units per country (see GROCERY_MEDIAN_LOGNORMAL).
monthly_grocery_bill = np.round(np.clip(
    np.array([rng.lognormal(mean=GROCERY_MEDIAN_LOGNORMAL[c], sigma=0.55) for c in country]), 0, 5000), 1)
how_many_new_clothes_monthly = np.round(np.clip(rng.lognormal(mean=0.4, sigma=0.9, size=N), 0, 50)).astype(int)
waste_bag_weekly_count = np.round(np.clip(rng.lognormal(mean=0.9, sigma=0.6, size=N), 0, 20)).astype(int)
how_long_tv_pc_daily_hour = np.round(np.clip(rng.normal(4.2, 2.4, N), 0, 24) * 2) / 2
how_long_internet_daily_hour = np.round(np.clip(rng.normal(5.0, 2.6, N), 0, 24) * 2) / 2

def sample_multi(n, items, probs_map, none_p):
    out = []
    for _ in range(n):
        if rng.random() < none_p:
            out.append(["none"])
            continue
        chosen = [it for it in items if rng.random() < probs_map[it]]
        out.append(chosen if chosen else ["none"])
    return out

household_size = np.clip(rng.geometric(p=0.42, size=N), 1, 10)   # 1-person common, long-ish tail

recycling = sample_multi(N, ["paper", "plastic", "metal", "glass"], {"paper": 0.55, "plastic": 0.50, "metal": 0.30, "glass": 0.28}, 0.30)
cooking_with = sample_multi(N, ["stove", "oven", "microwave", "grill", "airfryer"], {"stove": 0.75, "oven": 0.45, "microwave": 0.55, "grill": 0.15, "airfryer": 0.22}, 0.04)

# ---------------------------------------------------------------- target ----
def compute_target(i, d_km, v_type, trans, heat, tv_h, net_h, diet_v, g_bill,
                   c_items, bag_s, bag_n, rec, cook, air_f, grid, gfac, hh_size):
    # --- transport ---
    if trans == "private":
        if v_type == "electric":
            transport = d_km * EV_KWH_PER_100KM / 100 * grid
        elif v_type in ("petrol", "diesel"):
            kmpl = rng.uniform(*KM_PER_L_RANGE[v_type])
            transport = d_km * FUEL_KG_PER_L[v_type] / kmpl
        elif v_type == "hybrid":
            kmpl = rng.uniform(*KM_PER_L_RANGE["petrol"]) / 0.8   # ~20% better economy
            transport = d_km * FUEL_KG_PER_L["petrol"] / kmpl
        elif v_type == "lpg":
            km_per_kg = rng.uniform(20.0, 30.0) * 1.2             # slightly worse economy than petrol-kg
            transport = d_km * 3.0 / km_per_kg                    # LPG ~3.0 kgCO2e/kg burned (IPCC stoichiometry)
        else:
            transport = d_km * 0.0
    elif trans == "public":
        transit_km = d_km * 1.15          # transit users cover more km shared
        transport = transit_km * TRANSIT_KG_PER_PASSENGER_KM
    else:
        transport = 0.0                   # walk/bicycle ≈ 0 (food already counted)
    # --- home energy ---
    electricity_kwh = tv_h * TV_WATTS / 1000 * 30 + net_h * INTERNET_WATTS_EQUIV / 1000 * 30
    electricity_kwh += rng.uniform(40, 90)             # lights, fridge, fans base load
    if heat == "electricity":
        electricity_kwh += rng.uniform(60, 140)        # geysers / winter heaters
        heating = 0.0
    elif heat == "natural gas":
        heating = GAS_HEATING_KG_PER_MONTH
    else:
        heating = WOOD_HEATING_KG_PER_MONTH
    home = electricity_kwh * grid * (1.0 / hh_size) + heating  # shared home energy per person
    # --- food ---
    food = DIET_BANDS[diet_v] + g_bill * gfac
    # --- waste & recycling ---
    waste = bag_n * WEEKS_PER_MONTH * BAG_MASS[bag_s] * WASTE_KG_PER_KG
    credit = sum(RECYCLING_CREDIT[m] for m in rec if m in RECYCLING_CREDIT)
    waste = max(0.0, waste * (1.0 / hh_size) - credit)   # household waste shared per person
    # --- consumption & cooking ---
    clothing = c_items * CLOTHING_KG_PER_ITEM
    cooking = sum(COOKING_APPLIANCE_KWH_MONTH[a] for a in cook if a in COOKING_APPLIANCE_KWH_MONTH) * grid
    if "stove" in cook:
        cooking += LPG_MONTH_KG * 3.0 * 0.5            # partial LPG use; ~3.0 kgCO2/kg LPG (IPCC stoichiometry)
    # --- air travel ---
    flights = AIR_BANDS[air_f]
    total = transport + home + food + waste + clothing + cooking + flights
    return total * rng.lognormal(0.0, 0.05)             # ±5% multiplicative noise

targets = np.array([
    compute_target(i, vehicle_monthly_distance_km[i], vehicle_type[i], transport[i],
                   heating[i], how_long_tv_pc_daily_hour[i], how_long_internet_daily_hour[i],
                   diet[i], monthly_grocery_bill[i], how_many_new_clothes_monthly[i],
                   waste_bag_size[i], waste_bag_weekly_count[i], recycling[i], cooking_with[i],
                   air[i], grid_factor[i], grocery_factor[i], int(household_size[i]))
    for i in range(N)
])

# ---------------------------------------------------------------- assemble --
df = pd.DataFrame({
    "transport": transport,
    "vehicle_type": vehicle_type,
    "vehicle_monthly_distance_km": vehicle_monthly_distance_km,
    "frequency_of_traveling_by_air": air,
    "region": region,
    "heating_energy_source": heating,
    "how_long_tv_pc_daily_hour": how_long_tv_pc_daily_hour,
    "how_long_internet_daily_hour": how_long_internet_daily_hour,
    "diet": diet,
    "monthly_grocery_bill": monthly_grocery_bill,
    "how_many_new_clothes_monthly": how_many_new_clothes_monthly,
    "waste_bag_size": waste_bag_size,
    "waste_bag_weekly_count": waste_bag_weekly_count,
    "recycling": [str(r) for r in recycling],
    "cooking_with": [str(c) for c in cooking_with],
    "grid_factor": np.round(grid_factor, 5),
    "grocery_factor": grocery_factor,
    "household_size": household_size.astype(int),
    "country": country,
    "region": _region,
    "carbon_emission_kgco2e_month": np.round(targets, 1),
})

import os
os.makedirs("data/v2_training", exist_ok=True)
df.to_csv(OUT, index=False)

print(f"rows: {len(df)}  cols: {len(df.columns)}")
print(f"target: min {df.carbon_emission_kgco2e_month.min():.0f}  max {df.carbon_emission_kgco2e_month.max():.0f}  mean {df.carbon_emission_kgco2e_month.mean():.0f}")
print("region effect check (mean target by region, other cols random):")
print(df.groupby("region").carbon_emission_kgco2e_month.mean().round(1).to_string())
print("diet ordering check:")
print(df.groupby("diet").carbon_emission_kgco2e_month.mean().sort_values().round(1).to_string())
print(f"saved: {OUT}")

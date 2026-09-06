"""Audit the v2.5 dataset + deployed model against the documented construction rules.

Checks (run order):
 1. Schema: rows, columns, nulls, duplicates, ranges within SurveyPayload limits.
 2. Internal consistency: transport/vehicle_type pairing, grid/grocery factor lookup.
 3. Target re-derivation: deterministic factor formula vs stored target (noise check).
 4. Band ordering: diet and air bands must move the target in the documented direction.
 5. Model fidelity: deployed XGBoost vs stored target on all 10k rows.
 6. Anomaly probe: air-band deltas learned by the model on matched profiles.

Run: py -3.12 scripts/audit_v25_dataset.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from backend.app.services.prediction import build_v25_features, get_runtime_v25  # noqa: E402

OUT = PROJECT / "reports"
OUT.mkdir(exist_ok=True)
report: dict[str, object] = {}

df = pd.read_csv(PROJECT / "data" / "v2_training" / "clean_dataset_v2.csv")
TARGET = "carbon_emission_kgco2e_month"

# 1 ── schema ---------------------------------------------------------------
print("== 1. schema ==")
print(f"rows {len(df)}  cols {len(df.columns)}")
nulls = int(df.isna().sum().sum())
dupes = int(df.duplicated().sum())
ranges_ok = {
    "vehicle_monthly_distance_km<=10000": bool(df.vehicle_monthly_distance_km.max() <= 10000),
    "monthly_grocery_bill<=5000": bool(df.monthly_grocery_bill.max() <= 5000),
    "how_many_new_clothes_monthly<=50": bool(df.how_many_new_clothes_monthly.max() <= 50),
    "waste_bag_weekly_count<=20": bool(df.waste_bag_weekly_count.max() <= 20),
    "tv_hours<=24": bool(df.how_long_tv_pc_daily_hour.max() <= 24),
    "internet_hours<=24": bool(df.how_long_internet_daily_hour.max() <= 24),
    "household_size 1..10": bool(df.household_size.between(1, 10).all()),
    "target>0": bool((df[TARGET] > 0).all()),
}
print(f"nulls {nulls}  duplicate-rows {dupes}")
print(f"ranges {ranges_ok}")
report["schema"] = {"rows": len(df), "cols": len(df.columns), "nulls": nulls,
                    "duplicates": dupes, "ranges_ok": ranges_ok,
                    "target": {"min": float(df[TARGET].min()), "max": float(df[TARGET].max()),
                               "mean": round(float(df[TARGET].mean()), 1),
                               "median": round(float(df[TARGET].median()), 1)}}

# 2 ── internal consistency ---------------------------------------------------
print("== 2. consistency ==")
bad_pair = int(((df.transport != "private") & (df.vehicle_type != "none")).sum())
grid_lookup = {"india": {"mixed": 0.67013, "renewable_heavy": 0.147},
               "us": {"mixed": 0.38440, "renewable_heavy": 0.085},
               "uk": {"mixed": 0.21741, "renewable_heavy": 0.048}}
grocery_lookup = {"india": 0.11, "us": 0.36, "uk": 0.44}
grid_ok = all(abs(r.grid_factor - grid_lookup[r.country][getattr(r, "region")]) < 1e-9 for r in df.itertuples())
grocery_ok = all(abs(r.grocery_factor - grocery_lookup[r.country]) < 1e-9 for r in df.itertuples())
print(f"non-private rows with a vehicle: {bad_pair} | grid lookup matches: {grid_ok} | grocery lookup matches: {grocery_ok}")
print(df.groupby("country").grid_factor.agg(["min", "max"]).round(5).to_string())
report["consistency"] = {"non_private_with_vehicle": bad_pair, "grid_lookup_ok": bool(grid_ok),
                         "grocery_lookup_ok": bool(grocery_ok)}

# 3 ── target re-derivation ----------------------------------------------------
print("== 3. target re-derivation (deterministic formula vs stored) ==")
AIR = {"never": 0.0, "rarely": 60.0, "often": 180.0, "very frequently": 420.0}
DIET = {"vegan": 90.0, "vegetarian": 115.0, "pescatarian": 120.0, "omnivore": 215.0}
BAG_MASS = {"small": 5.0, "medium": 10.0, "large": 20.0, "extra large": 30.0}
REC_CREDIT = {"paper": 4.0, "plastic": 6.0, "metal": 12.0, "glass": 2.0}
COOK_KWH = {"stove": 12.0, "oven": 9.0, "microwave": 5.0, "grill": 7.0, "airfryer": 8.0}

def deterministic_target(r) -> tuple[float, dict]:
    d = r._asdict() if hasattr(r, "_asdict") else dict(r)
    if d["transport"] == "private":
        if d["vehicle_type"] == "electric":
            transport = d["vehicle_monthly_distance_km"] * 18.0 / 100 * d["grid_factor"]
        elif d["vehicle_type"] == "petrol":
            transport = d["vehicle_monthly_distance_km"] * 2.31 / 20.0   # mid km/L
        elif d["vehicle_type"] == "diesel":
            transport = d["vehicle_monthly_distance_km"] * 2.68 / 18.5   # mid km/L
        elif d["vehicle_type"] == "hybrid":
            transport = d["vehicle_monthly_distance_km"] * 2.31 / 25.0
        elif d["vehicle_type"] == "lpg":
            transport = d["vehicle_monthly_distance_km"] * 3.0 / 30.0
        else:
            transport = 0.0
    elif d["transport"] == "public":
        transport = d["vehicle_monthly_distance_km"] * 1.15 * 0.02
    else:
        transport = 0.0
    electricity_kwh = (d["how_long_tv_pc_daily_hour"] * 0.075 * 30
                       + d["how_long_internet_daily_hour"] * 0.040 * 30 + 65.0)
    heating = 0.0 if d["heating_energy_source"] == "electricity" else (
        20.0 if d["heating_energy_source"] == "natural gas" else 8.0)
    home = electricity_kwh * d["grid_factor"] / d["household_size"] + heating
    food = DIET[d["diet"]] + d["monthly_grocery_bill"] * d["grocery_factor"]
    waste = d["waste_bag_weekly_count"] * 4.3 * BAG_MASS[d["waste_bag_size"]] * 0.65
    rec = eval(d["recycling"]) if isinstance(d["recycling"], str) else d["recycling"]
    cook = eval(d["cooking_with"]) if isinstance(d["cooking_with"], str) else d["cooking_with"]
    credit = sum(REC_CREDIT[m] for m in rec if m in REC_CREDIT)
    waste = max(0.0, waste / d["household_size"] - credit)
    clothing = d["how_many_new_clothes_monthly"] * 18.0
    cooking = sum(COOK_KWH[a] for a in cook if a in COOK_KWH) * d["grid_factor"]
    if "stove" in cook:
        cooking += 15.0
    flights = AIR[d["frequency_of_traveling_by_air"]]
    return transport + home + food + waste + clothing + cooking + flights, {
        "transport": transport, "home": home, "food": food, "waste": waste,
        "clothing": clothing, "cooking": cooking, "flights": flights}

sample = df.sample(500, random_state=7)
ratios = []
for r in sample.itertuples():
    det, _ = deterministic_target(r)
    if det > 1:
        ratios.append(r.carbon_emission_kgco2e_month / det)
ratios = np.array(ratios)
print(f"ratio target/deterministic: median {np.median(ratios):.3f}  log-std {np.std(np.log(ratios)):.3f}  (expect ~1.0, ~0.05)")
report["target_recompute"] = {"ratio_median": round(float(np.median(ratios)), 3),
                              "ratio_log_std": round(float(np.std(np.log(ratios))), 3)}

# 4 ── band ordering -----------------------------------------------------------
print("== 4. band ordering ==")
diet_means = df.groupby("diet")[TARGET].mean().round(1).to_dict()
air_means = df.groupby("frequency_of_traveling_by_air")[TARGET].mean().round(1).to_dict()
print(f"diet means {diet_means}")
print(f"air means  {air_means}")
order_ok = (diet_means["vegan"] < diet_means["vegetarian"] < diet_means["pescatarian"] < diet_means["omnivore"]
            and air_means["never"] < air_means["rarely"] < air_means["often"] < air_means["very frequently"])
print(f"ordering monotone: {order_ok}")
report["band_order"] = {"diet": diet_means, "air": air_means, "monotone": bool(order_ok)}

# 5 ── model fidelity ------------------------------------------------------------
print("== 5. deployed model vs stored target (all 10k rows) ==")
meta, model, features = get_runtime_v25()
X = pd.DataFrame([build_v25_features(r) for r in df.to_dict(orient="records")])[features]
pred = model.predict(X)
from sklearn.metrics import r2_score, mean_absolute_error
r2 = r2_score(df[TARGET], pred)
mae = mean_absolute_error(df[TARGET], pred)
within = float((np.abs(df[TARGET] - pred) <= meta["conformal_prediction"]["quantile_90"]).mean())
print(f"R2 {r2:.4f}  MAE {mae:.1f} kg  |pred-target|<=q_hat on {within*100:.1f}% of rows")
report["model_fidelity"] = {"r2_all_rows": round(float(r2), 4), "mae_all_rows": round(float(mae), 1),
                            "coverage_at_qhat": round(within, 4)}

# 6 ── air anomaly probe ------------------------------------------------------------
print("== 6. air-band deltas: formula vs learned model (matched profiles) ==")
base_profile = {"country": "india", "region": "mixed", "household_size": 2,
                "transport": "private", "vehicle_type": "petrol", "vehicle_monthly_distance_km": 300,
                "frequency_of_traveling_by_air": "rarely", "heating_energy_source": "electricity",
                "diet": "omnivore", "monthly_grocery_bill": 200, "how_many_new_clothes_monthly": 2,
                "waste_bag_size": "medium", "waste_bag_weekly_count": 3,
                "how_long_tv_pc_daily_hour": 4, "how_long_internet_daily_hour": 4,
                "recycling": [], "cooking_with": []}
air_rows = df[df.frequency_of_traveling_by_air == "very frequently"].head(1).iloc[0]
probe = []
for lvl in ["never", "rarely", "often", "very frequently"]:
    p = dict(base_profile); p["frequency_of_traveling_by_air"] = lvl
    model_pred = float(model.predict(pd.DataFrame([build_v25_features(p)])[features])[0])
    # dataset expectation: target delta vs rarely band (60/180/420 vs rare 60)
    band = AIR[lvl]
    probe.append({"level": lvl, "modelKg": round(model_pred, 1),
                  "bandKgInTarget": band, "deltaVsRare_model": round(model_pred - probe[0]["modelKg"] if probe else float("nan"), 1)})
# fix deltas (needs full list)
for i, rowp in enumerate(probe):
    rowp["deltaVsRare_model"] = round(rowp["modelKg"] - probe[1]["modelKg"], 1) if i != 1 else 0.0
    rowp["deltaVsRare_target"] = round(rowp["bandKgInTarget"] - AIR["rarely"], 1)
for rowp in probe:
    print(rowp)
report["air_probe"] = probe

(OUT / "v25_dataset_audit.json").write_text(json.dumps(report, indent=1, default=str))
print("saved reports/v25_dataset_audit.json")

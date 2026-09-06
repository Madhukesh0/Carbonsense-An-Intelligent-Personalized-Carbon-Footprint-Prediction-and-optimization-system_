"""Generate 10,000 test cases for the v2.5 model (grid-factor design).

Mirrors scripts/generate_prediction_test_cases.py but for the v2.5 schema:
16 dimensions - country (india/us/uk), household_size (1-10), the 14
emitter questions - plus the renewable-heavy modifier. Deterministic
Sobol sequence (seed 42) with forced numeric boundaries and deduplication.

Every case is scored by the deployed v2.5 runtime (XGBoost, R2 0.9514)
with TreeSHAP contributions and the 90% conformal interval (q 71.26).

Outputs:
  data/test_cases/ai_prediction_10000_test_cases_v25.csv
  data/test_cases/ai_prediction_10000_test_cases_v25.json
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from backend.app.services.prediction import (  # noqa: E402
    _v25_group,
    get_runtime_v25,
)
from backend.app.schemas.model import SurveyPayload  # noqa: E402

SEED = 42
N_CASES = 10_000
OUT_DIR = PROJECT / "data" / "test_cases"

CATEGORICALS = {
    "country": ["india", "us", "uk"],
    "transport": ["private", "public", "walk/bicycle"],
    "vehicle_type": ["none", "petrol", "diesel", "electric", "hybrid", "lpg"],
    "frequency_of_traveling_by_air": ["never", "rarely", "often", "very frequently"],
    "heating_energy_source": ["electricity", "natural gas", "wood"],
    "diet": ["vegan", "vegetarian", "pescatarian", "omnivore"],
    "waste_bag_size": ["small", "medium", "large", "extra large"],
}
NUMERICS = {
    "household_size": (1, 10, 0),
    "vehicle_monthly_distance_km": (0, 10000, 1),
    "monthly_grocery_bill": (0, 5000, 1),
    "how_long_tv_pc_daily_hour": (0, 24, 1),
    "how_long_internet_daily_hour": (0, 24, 1),
    "how_many_new_clothes_monthly": (0, 50, 0),
    "waste_bag_weekly_count": (0, 20, 0),
}
RECYCLING_ITEMS = ["paper", "plastic", "metal", "glass"]
COOKING_ITEMS = ["stove", "oven", "microwave", "grill", "airfryer"]


def list_states(items):
    states = [[], ["none"]]
    for size in range(1, len(items) + 1):
        from itertools import combinations
        for combo in combinations(items, size):
            states.append(list(combo))
    return states


RECYCLING_STATES = list_states(RECYCLING_ITEMS)   # 17
COOKING_STATES = list_states(COOKING_ITEMS)       # 33


def payload_from_unit(u):
    keys = (["country"] + list(CATEGORICALS) + ["recycling_state", "cooking_state"]
            + list(NUMERICS))
    d = dict(zip(keys, u))
    p = {"currency": {"india": "INR", "us": "USD", "uk": "GBP"}[
             ["india", "us", "uk"][min(int(d["country"] * 3), 2)]],
         "region": "renewable_heavy" if d.get("renewable_state", 0) >= 0.75 else "mixed"}
    for name, levels in CATEGORICALS.items():
        p[name] = levels[min(int(d[name] * len(levels)), len(levels) - 1)]
    p["recycling"] = RECYCLING_STATES[min(int(d["recycling_state"] * 17), 16)]
    p["cooking_with"] = COOKING_STATES[min(int(d["cooking_state"] * 33), 32)]
    for name, (low, high, dec) in NUMERICS.items():
        value = low + d[name] * (high - low)
        p[name] = int(round(value)) if dec == 0 else round(float(value), dec)
    return p


def payload_key(p):
    return (p["country"], p["transport"], p["vehicle_type"],
            p["frequency_of_traveling_by_air"], p["heating_energy_source"],
            p["diet"], p["waste_bag_size"], tuple(sorted(p["recycling"])),
            tuple(sorted(p["cooking_with"])), p["household_size"],
            p["vehicle_monthly_distance_km"], p["monthly_grocery_bill"],
            p["how_long_tv_pc_daily_hour"], p["how_long_internet_daily_hour"],
            p["how_many_new_clothes_monthly"], p["waste_bag_weekly_count"])


def build_payloads():
    from scipy.stats import qmc

    sobol = qmc.Sobol(d=18, scramble=True, seed=SEED)
    unit = sobol.random(N_CASES + 512)

    payloads, seen = [], set()
    for row in unit:
        p = payload_from_unit(row)
        key = payload_key(p)
        if key in seen:
            continue
        seen.add(key)
        payloads.append(p)
        if len(payloads) == N_CASES:
            break

    # forced boundary + canonical cases replace arbitrary entries
    boundaries = []
    for name, (low, high, dec) in NUMERICS.items():
        for extreme in (low, high):
            b = payloads[len(boundaries)].copy()
            b[name] = int(extreme) if dec == 0 else float(extreme)
            boundaries.append(b)
    base = payloads[-1].copy()
    base.update({"country": "india", "household_size": 2, "transport": "private",
                 "vehicle_type": "petrol", "vehicle_monthly_distance_km": 300,
                 "frequency_of_traveling_by_air": "rarely", "heating_energy_source": "electricity",
                 "monthly_grocery_bill": 1200, "how_many_new_clothes_monthly": 2,
                 "waste_bag_size": "medium", "waste_bag_weekly_count": 2,
                 "how_long_tv_pc_daily_hour": 4, "how_long_internet_daily_hour": 4,
                 "diet": "omnivore", "recycling": ["paper", "plastic"],
                 "cooking_with": ["stove"]})
    boundaries.append(base)
    payloads[:len(boundaries)] = boundaries

    for i, p in enumerate(payloads, 1):
        p["case_id"] = i
        # frozen v1 contract reference fields are sent to the model for
        # schema-compatibility but deliberately EXCLUDED from the saved
        # test cases: they are not user inputs and have no emission mechanism.
        full = dict(p)
        full["age"] = 30; full["sex"] = "female"; full["body_type"] = "normal"
        full["how_often_shower"] = "daily"; full["social_activity"] = "sometimes"
        full["energy_efficiency"] = "Sometimes"
        SurveyPayload.model_validate(full)
    return payloads


def coverage_stats(payloads):
    stats = {"levels_per_feature": {}}
    for name, levels in CATEGORICALS.items():
        counts = {lv: 0 for lv in levels}
        for p in payloads:
            counts[p[name]] += 1
        stats["levels_per_feature"][name] = {
            "missing": [lv for lv, n in counts.items() if n == 0],
            "min_count": min(counts.values())}
    for name, states in (("recycling", RECYCLING_STATES), ("cooking_with", COOKING_STATES)):
        seen = {tuple(sorted(p[name])) for p in payloads}
        stats["levels_per_feature"][name] = {"distinct_states": len(seen),
                                             "total_states": len(states)}
    hh = [p["household_size"] for p in payloads]
    stats["levels_per_feature"]["household_size"] = {"distinct": len(set(hh)),
                                                     "min": min(hh), "max": max(hh)}
    stats["levels_per_feature"]["grid_factor_countries"] = sorted(
        {p["country"] for p in payloads})
    return stats


def main():
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata, model, _features = get_runtime_v25()  # type: ignore[misc]
    metadata, model, _features = get_runtime_v25()
    q_hat = float(metadata["conformal_prediction"]["quantile_90"])

    print(f"[1/4] building {N_CASES} unique schema-valid payloads ...", flush=True)
    payloads = build_payloads()
    print(f"      {len(payloads)} validated ({time.time() - t0:.0f}s)", flush=True)

    print("[2/4] building feature matrix via build_v25_features ...", flush=True)
    from backend.app.services.prediction import build_v25_features
    feats = [build_v25_features(p) for p in payloads]
    feature_names = metadata["feature_names"]
    X = pd.DataFrame(feats)
    X = X.reindex(columns=feature_names, fill_value=0.0).astype(float)

    predictions = model.predict(X)

    print("[3/4] batch TreeSHAP ...", flush=True)
    import shap
    import backend.app.services.prediction as pred_mod
    explainer = pred_mod._v25_explainer()
    shap_values = explainer.shap_values(X)

    print("[4/4] assembling artifacts ...", flush=True)
    group_keys, group_labels = {}, {}
    for f in feature_names:
        k, lbl = _v25_group(f)
        group_keys[f] = k
        group_labels.setdefault(k, lbl)

    rows, grouped_records = [], []
    for i, p in enumerate(payloads):
        pred = max(0.0, float(predictions[i]))
        sv = shap_values[i]
        groups = {}
        for j, f in enumerate(feature_names):
            k = group_keys[f]
            groups[k] = groups.get(k, 0.0) + float(sv[j])
        top = max(groups, key=lambda k: abs(groups[k]))
        EXCLUDE = {"age", "sex", "body_type", "how_often_shower", "social_activity", "energy_efficiency"}
        row = {"case_id": p["case_id"]}
        for k, v in p.items():
            if k in EXCLUDE:
                continue
            row[k] = json.dumps(v) if isinstance(v, list) else v
        row.update({"predictedKg": round(pred, 4),
                    "intervalLow": round(max(0.0, pred - q_hat), 4),
                    "intervalHigh": round(pred + q_hat, 4),
                    "topGroup": top, "topGroupShap": round(groups[top], 4)})
        for j, f in enumerate(feature_names):
            row[f"shap__{f}"] = float(sv[j])
        rows.append(row)
        grouped_records.append({"case_id": p["case_id"], "predictedKg": round(pred, 1),
                                "groups": {k: round(v, 3) for k, v in groups.items()
                                           if abs(round(v, 3)) >= 0.001}})

    out = pd.DataFrame(rows)
    csv_path = OUT_DIR / "ai_prediction_10000_test_cases_v25_clean.csv"
    out.to_csv(csv_path, index=False)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "design": "scrambled Sobol over 18 dimensions (3 countries, household_size, "
                  "14 questions, recycling/cooking states, renewable modifier) + "
                  "forced numeric boundaries + canonical profile; deduplicated",
        "n_cases": len(payloads),
        "model_version": metadata["model_version"],
        "conformal_quantile_90": q_hat,
        "note": "Country is context: each case carries its country's grid factor; "
                "the model input is the numeric factor, not the country name.",
        "coverage": coverage_stats(payloads),
        "prediction_stats": {"min": round(float(predictions.min()), 1),
                             "max": round(float(predictions.max()), 1),
                             "mean": round(float(predictions.mean()), 1)},
        "grouped_shap": grouped_records,
    }
    json_path = OUT_DIR / "ai_prediction_10000_test_cases_v25_clean.json"
    json_path.write_text(json.dumps(summary, indent=1, default=str))

    print(f"cases={len(payloads)} unique={out.drop_duplicates(subset=[c for c in out.columns if c != 'case_id']).shape[0]}")
    print(f"pred range: {predictions.min():.1f} .. {predictions.max():.1f}")
    print(f"saved: {csv_path.name} ({csv_path.stat().st_size/1e6:.1f} MB), {json_path.name} ({json_path.stat().st_size/1e6:.1f} MB)")
    print(f"total time: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

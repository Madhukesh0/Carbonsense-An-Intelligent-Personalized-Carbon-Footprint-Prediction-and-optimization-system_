"""Generate 10,000 unique AI-prediction test cases with SHAP factors stored.

Design: the full categorical contract space is ~1.12 billion combinations
(1,990,656 categorical levels-product x 17 valid recycling states x 33 valid
cooking states), so exhaustive coverage is impossible at 10,000 cases. This
generator uses a scrambled Sobol sequence (seed 42) over all 21 contract
dimensions for deterministic low-discrepancy spread, forces every categorical
level to appear, adds numeric boundary cases, and deduplicates to exactly
10,000 unique payloads. Predictions, the 90% split-conformal interval, and
per-feature SHAP values come from the frozen production runtime (same
preprocessor + model + manifest verification as the FastAPI serving path).

Outputs:
  data/test_cases/ai_prediction_10000_test_cases.csv   one row per case (inputs + prediction + 44 shap columns)
  data/test_cases/ai_prediction_10000_test_cases.json  metadata, coverage stats, grouped SHAP per case
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_RUNTIME = PROJECT_ROOT / "server" / "model_runtime"
if str(MODEL_RUNTIME) not in sys.path:
    sys.path.insert(0, str(MODEL_RUNTIME))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.final_contract import FEATURE_NAMES  # noqa: E402
from backend.app.services.prediction import (  # noqa: E402
    _contribution_group,
    get_runtime,
)
from backend.app.schemas.model import SurveyPayload  # noqa: E402

SEED = 42
N_CASES = 10_000
ALPHA = 0.10
OUT_DIR = PROJECT_ROOT / "data" / "test_cases"

CATEGORICALS = {
    "sex": ["male", "female"],
    "body_type": ["underweight", "normal", "overweight", "obese"],
    "diet": ["vegan", "vegetarian", "omnivore", "pescatarian"],
    "how_often_shower": ["rarely", "daily", "often", "twice a day"],
    "heating_energy_source": ["electricity", "natural gas", "wood"],
    "energy_efficiency": ["No", "Sometimes", "Yes"],
    "transport": ["private", "public", "walk/bicycle"],
    "vehicle_type": ["none", "petrol", "diesel", "electric", "hybrid", "lpg"],
    "frequency_of_traveling_by_air": ["never", "rarely", "often", "very frequently"],
    "region": ["mixed", "renewable_heavy"],
    "waste_bag_size": ["small", "medium", "large", "extra large"],
    "social_activity": ["never", "sometimes", "often"],
}
RECYCLING_ITEMS = ["paper", "plastic", "metal", "glass"]
COOKING_ITEMS = ["stove", "oven", "microwave", "grill", "airfryer"]

# Every valid state: empty list, ["none"], or any non-empty subset of items.
def list_states(items: list[str]) -> list[list[str]]:
    states: list[list[str]] = [[], ["none"]]
    for size in range(1, len(items) + 1):
        for combo in combinations(items, size):
            states.append(list(combo))
    return states

RECYCLING_STATES = list_states(RECYCLING_ITEMS)  # 17 states
COOKING_STATES = list_states(COOKING_ITEMS)      # 33 states

NUMERICS = {
    "age": (18, 80, 0),
    "monthly_grocery_bill": (0.0, 5000.0, 2),
    "vehicle_monthly_distance_km": (0.0, 10000.0, 1),
    "waste_bag_weekly_count": (0, 20, 0),
    "how_long_tv_pc_daily_hour": (0.0, 24.0, 1),
    "how_many_new_clothes_monthly": (0, 50, 0),
    "how_long_internet_daily_hour": (0.0, 24.0, 1),
}


def payload_from_unit(u: np.ndarray) -> dict:
    keys = list(CATEGORICALS) + ["recycling_state", "cooking_state"] + list(NUMERICS)
    d = dict(zip(keys, u))
    payload: dict = {"currency": "USD"}
    for name, levels in CATEGORICALS.items():
        payload[name] = levels[min(int(d[name] * len(levels)), len(levels) - 1)]
    payload["recycling"] = RECYCLING_STATES[min(int(d["recycling_state"] * len(RECYCLING_STATES)), len(RECYCLING_STATES) - 1)]
    payload["cooking_with"] = COOKING_STATES[min(int(d["cooking_state"] * len(COOKING_STATES)), len(COOKING_STATES) - 1)]
    for name, (low, high, decimals) in NUMERICS.items():
        value = low + d[name] * (high - low)
        payload[name] = round(float(value), decimals)
        if decimals == 0:
            payload[name] = int(payload[name])
    return payload


def payload_key(p: dict) -> tuple:
    return (p["sex"], p["body_type"], p["diet"], p["how_often_shower"],
            p["heating_energy_source"], p["energy_efficiency"], p["transport"],
            p["vehicle_type"], p["frequency_of_traveling_by_air"], p["region"],
            p["waste_bag_size"], p["social_activity"], tuple(sorted(p["recycling"])),
            tuple(sorted(p["cooking_with"])), p["age"], p["monthly_grocery_bill"],
            p["vehicle_monthly_distance_km"], p["waste_bag_weekly_count"],
            p["how_long_tv_pc_daily_hour"], p["how_many_new_clothes_monthly"],
            p["how_long_internet_daily_hour"])


def build_payloads() -> list[dict]:
    from scipy.stats import qmc

    sobol = qmc.Sobol(d=21, scramble=True, seed=SEED)
    unit = sobol.random(N_CASES + 512)  # headroom for dedup + boundary swaps

    payloads: list[dict] = []
    seen: set[tuple] = set()
    for row in unit:
        p = payload_from_unit(row)
        key = payload_key(p)
        if key in seen:
            continue
        seen.add(key)
        payloads.append(p)
        if len(payloads) == N_CASES:
            break

    # Boundary / canonical cases replace arbitrary entries (never dropped).
    boundaries: list[dict] = []
    for name, (low, high, _dec) in NUMERICS.items():
        for extreme in (low, high):
            p = payloads[len(boundaries)].copy()
            p[name] = int(extreme) if _dec == 0 else float(extreme)
            boundaries.append(p)
    base = payloads[-1].copy()
    base.update({
        "age": 30, "sex": "female", "body_type": "normal", "diet": "omnivore",
        "how_often_shower": "daily", "heating_energy_source": "electricity",
        "energy_efficiency": "Sometimes", "transport": "private",
        "vehicle_type": "petrol", "vehicle_monthly_distance_km": 300.0,
        "frequency_of_traveling_by_air": "rarely", "region": "mixed",
        "monthly_grocery_bill": 200.0, "how_many_new_clothes_monthly": 2,
        "waste_bag_size": "medium", "waste_bag_weekly_count": 3,
        "how_long_tv_pc_daily_hour": 4.0, "how_long_internet_daily_hour": 4.0,
        "social_activity": "sometimes", "recycling": ["paper", "plastic"],
        "cooking_with": ["stove", "oven"], "currency": "USD",
    })
    boundaries.append(base)
    for index, p in enumerate(boundaries):
        p["case_id"] = 0  # placeholder, fixed below
        payloads[index] = p

    for case_id, p in enumerate(payloads, start=1):
        p["case_id"] = case_id
    return payloads


def coverage_stats(payloads: list[dict]) -> dict:
    stats: dict = {"levels_per_feature": {}}
    for name, levels in CATEGORICALS.items():
        counts = {level: 0 for level in levels}
        for p in payloads:
            counts[p[name]] += 1
        missing = [level for level, n in counts.items() if n == 0]
        stats["levels_per_feature"][name] = {"missing": missing, "min_count": min(counts.values())}
    for name, states in (("recycling", RECYCLING_STATES), ("cooking_with", COOKING_STATES)):
        seen = {tuple(sorted(p[name])) for p in payloads}
        stats["levels_per_feature"][name] = {
            "missing": [s for s in states if tuple(sorted(s)) not in seen][:5],
            "distinct_states": len(seen), "total_states": len(states),
        }
    pair_dims = ["diet", "transport", "vehicle_type", "heating_energy_source",
                 "frequency_of_traveling_by_air", "energy_efficiency"]
    pair_total = pair_seen = 0
    for a, b in combinations(pair_dims, 2):
        la, lb = CATEGORICALS[a], CATEGORICALS[b]
        for x in la:
            for y in lb:
                pair_total += 1
                if any(p[a] == x and p[b] == y for p in payloads):
                    pair_seen += 1
    stats["pairwise_coverage"] = {"covered": pair_seen, "total": pair_total,
                                  "fraction": round(pair_seen / pair_total, 4)}
    return stats


def main() -> None:
    started = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest, metadata, model, preprocessor = get_runtime()
    q_hat = float(metadata["conformal_prediction"]["quantile_90"])

    print(f"[1/4] Building {N_CASES} unique schema-valid payloads ...", flush=True)
    payloads = build_payloads()
    for p in payloads:  # every case must pass the exact serving schema
        SurveyPayload.model_validate(p)
    print(f"      {len(payloads)} payloads validated ({time.time() - started:.1f}s)", flush=True)

    print("[2/4] Transforming + predicting in batch ...", flush=True)
    records = [{k: v for k, v in p.items() if k != "case_id"} for p in payloads]
    transformed = preprocessor.transform(records)
    feature_names = list(preprocessor.get_feature_names_out())
    if transformed.shape != (len(payloads), len(FEATURE_NAMES)) or not np.isfinite(transformed).all():
        raise RuntimeError("Batch transform did not produce the frozen contract matrix")
    predictions = model.predict(transformed)

    print("[3/4] Batch SHAP (TreeExplainer) ...", flush=True)
    import shap

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(transformed)

    print("[4/4] Assembling artifacts ...", flush=True)
    group_names: dict[str, str] = {}
    for f in feature_names:
        key, label = _contribution_group(f)
        group_names[key] = label
    group_keys = list(group_names)

    rows = []
    grouped_records = []
    for i, p in enumerate(payloads):
        pred = max(0.0, float(predictions[i]))
        sv = shap_values[i]
        groups = {k: 0.0 for k in group_keys}
        for j, f in enumerate(feature_names):
            key, _ = _contribution_group(f)
            groups[key] += float(sv[j])
        top_key = max(groups, key=lambda k: abs(groups[k]))
        row = {"case_id": p["case_id"]}
        for k, v in p.items():
            if k == "case_id":
                continue
            row[k] = json.dumps(v) if isinstance(v, list) else v
        row.update({
            "predictedKg": round(pred, 4),
            "intervalLow": round(max(0.0, pred - q_hat), 4),
            "intervalHigh": round(pred + q_hat, 4),
            "topGroup": top_key,
            "topGroupShap": round(groups[top_key], 4),
        })
        for j, f in enumerate(feature_names):
            row[f"shap__{f}"] = float(sv[j])
        rows.append(row)
        grouped_records.append({
            "case_id": p["case_id"],
            "predictedKg": round(pred, 1),
            "groups": {k: round(v, 3) for k, v in groups.items() if abs(round(v, 3)) >= 0.001},
        })

    df = pd.DataFrame(rows)
    csv_path = OUT_DIR / "ai_prediction_10000_test_cases.csv"
    df.to_csv(csv_path, index=False)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "design": "scrambled Sobol sequence over 21 contract dimensions + forced boundary/canonical cases; deduplicated to unique payloads",
        "n_cases": len(payloads),
        "model_version": manifest["model_version"],
        "conformal_alpha": ALPHA,
        "conformal_quantile_90": q_hat,
        "note": "Case space is ~1.12B categorical combinations; 10,000 Sobol cases cover the contract broadly, not exhaustively. Cross combinations (e.g. transport=walk/bicycle with vehicle_type=petrol) are schema-valid and included deliberately.",
        "coverage": coverage_stats(payloads),
        "prediction_stats": {
            "min": round(float(predictions.min()), 1),
            "max": round(float(predictions.max()), 1),
            "mean": round(float(predictions.mean()), 1),
        },
        "grouped_shap": grouped_records,
    }
    json_path = OUT_DIR / "ai_prediction_10000_test_cases.json"
    json_path.write_text(json.dumps(summary, indent=1, default=str))

    print(f"cases={len(payloads)} unique={df.drop_duplicates(subset=[c for c in df.columns if c != 'case_id']).shape[0]}")
    print(f"pred range: {predictions.min():.1f} .. {predictions.max():.1f}")
    print(f"saved: {csv_path.name} ({csv_path.stat().st_size / 1e6:.1f} MB), {json_path.name} ({json_path.stat().st_size / 1e6:.1f} MB)")
    print(f"total time: {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()

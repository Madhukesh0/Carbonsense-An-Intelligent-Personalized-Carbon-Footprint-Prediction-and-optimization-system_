"""
Comprehensive ML prediction test suite for CarbonSense.
Generates test cases, runs them through the prediction engine, and saves results.
"""
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.prediction import run_prediction, get_runtime
from backend.app.core.final_contract import SUPPORTED, DEFAULTS, FEATURE_NAMES, RAW_COLUMNS


def base_payload():
    """Return a valid base payload with all required fields."""
    return {
        "age": 30,
        "sex": "female",
        "body_type": "normal",
        "diet": "omnivore",
        "how_often_shower": "daily",
        "heating_energy_source": "electricity",
        "energy_efficiency": "Sometimes",
        "transport": "private",
        "vehicle_type": "petrol",
        "vehicle_monthly_distance_km": 300,
        "frequency_of_traveling_by_air": "rarely",
        "monthly_grocery_bill": 200,
        "how_many_new_clothes_monthly": 2,
        "waste_bag_size": "medium",
        "waste_bag_weekly_count": 3,
        "how_long_tv_pc_daily_hour": 4,
        "how_long_internet_daily_hour": 4,
        "social_activity": "sometimes",
        "recycling": ["paper", "plastic"],
        "cooking_with": ["stove", "oven"],
        "currency": "USD",
    }


def run_test(name, payload, expect_success=True):
    """Run a single test case and return structured result."""
    try:
        result = run_prediction(payload)
        if not expect_success:
            return {"test": name, "status": "FAIL", "error": "Expected failure but prediction succeeded", "predictedKg": result.get("predictedKg")}
        return {
            "test": name,
            "status": "PASS",
            "predictedKg": result["predictedKg"],
            "uncertaintyRange": result["uncertaintyRange"],
            "modelVersion": result["modelVersion"],
            "transformedFeatureCount": result["runtime"]["transformedFeatureCount"],
            "contributionCount": len(result["explanation"]["contributions"]),
            "topContribution": result["explanation"]["contributions"][0] if result["explanation"]["contributions"] else None,
        }
    except Exception as e:
        if expect_success:
            return {"test": name, "status": "FAIL", "error": f"{type(e).__name__}: {e}"}
        return {"test": name, "status": "PASS (expected failure)", "error": f"{type(e).__name__}: {e}"}


def generate_all_tests():
    """Generate all test cases."""
    tests = []

    # ── 1. Baseline / default tests ──────────────────────────────────────
    tests.append(("baseline_default_payload", base_payload(), True))

    minimal = base_payload()
    for key in list(minimal.keys()):
        if key not in ("sex", "body_type", "diet", "how_often_shower", "heating_energy_source",
                        "energy_efficiency", "transport", "vehicle_type", "frequency_of_traveling_by_air",
                        "monthly_grocery_bill", "waste_bag_size", "social_activity"):
            pass  # keep all required fields
    tests.append(("minimal_required_fields", minimal, True))

    # ── 2. Each categorical field: every valid value ──────────────────────
    for field, values in SUPPORTED.items():
        for val in values:
            p = base_payload()
            if field == "recycling":
                p["recycling"] = [val] if val != "none" else ["none"]
            elif field == "cooking_with":
                p["cooking_with"] = [val] if val != "none" else ["none"]
            else:
                p[field] = val
            tests.append((f"categorical_{field}_{val}".replace(" ", "_").replace("/", "_or_"), p, True))

    # ── 3. Numeric boundary tests ─────────────────────────────────────────
    numeric_fields = {
        "monthly_grocery_bill": (0, 5000),
        "vehicle_monthly_distance_km": (0, 10000),
        "waste_bag_weekly_count": (0, 20),
        "how_long_tv_pc_daily_hour": (0, 24),
        "how_many_new_clothes_monthly": (0, 50),
        "how_long_internet_daily_hour": (0, 24),
    }
    for field, (lo, hi) in numeric_fields.items():
        for val in [lo, hi, (lo + hi) // 2]:
            p = base_payload()
            p[field] = val
            tests.append((f"numeric_{field}_{val}", p, True))

    # ── 4. Recycling combinations ─────────────────────────────────────────
    recycling_combos = [
        ([], "none"),
        (["paper"], "paper_only"),
        (["plastic"], "plastic_only"),
        (["metal"], "metal_only"),
        (["glass"], "glass_only"),
        (["paper", "plastic"], "paper_plastic"),
        (["paper", "plastic", "metal"], "three_items"),
        (["paper", "plastic", "metal", "glass"], "all_four"),
        (["none"], "none_explicit"),
    ]
    for items, label in recycling_combos:
        p = base_payload()
        p["recycling"] = items
        tests.append((f"recycling_{label}", p, True))

    # ── 5. Cooking combinations ───────────────────────────────────────────
    cooking_combos = [
        ([], "none"),
        (["stove"], "stove_only"),
        (["oven"], "oven_only"),
        (["microwave"], "microwave_only"),
        (["grill"], "grill_only"),
        (["airfryer"], "airfryer_only"),
        (["stove", "oven", "microwave"], "three_items"),
        (["stove", "oven", "microwave", "grill", "airfryer"], "all_five"),
        (["none"], "none_explicit"),
    ]
    for items, label in cooking_combos:
        p = base_payload()
        p["cooking_with"] = items
        tests.append((f"cooking_{label}", p, True))

    # ── 6. Extreme profiles ───────────────────────────────────────────────
    # Heavy emitter
    heavy = base_payload()
    heavy.update({
        "sex": "male", "body_type": "obese", "diet": "omnivore",
        "transport": "private", "vehicle_type": "petrol",
        "vehicle_monthly_distance_km": 10000,
        "frequency_of_traveling_by_air": "very frequently",
        "monthly_grocery_bill": 5000,
        "how_many_new_clothes_monthly": 50,
        "waste_bag_size": "extra large", "waste_bag_weekly_count": 20,
        "how_long_tv_pc_daily_hour": 24, "how_long_internet_daily_hour": 24,
        "heating_energy_source": "natural gas", "energy_efficiency": "No",
        "social_activity": "often", "how_often_shower": "twice a day",
        "recycling": [], "cooking_with": ["grill"],
    })
    tests.append(("extreme_heavy_emitter", heavy, True))

    # Minimal emitter
    light = base_payload()
    light.update({
        "sex": "female", "body_type": "underweight", "diet": "vegan",
        "transport": "walk/bicycle", "vehicle_type": "none",
        "vehicle_monthly_distance_km": 0,
        "frequency_of_traveling_by_air": "never",
        "monthly_grocery_bill": 0,
        "how_many_new_clothes_monthly": 0,
        "waste_bag_size": "small", "waste_bag_weekly_count": 0,
        "how_long_tv_pc_daily_hour": 0, "how_long_internet_daily_hour": 0,
        "heating_energy_source": "wood", "energy_efficiency": "Yes",
        "social_activity": "never", "how_often_shower": "rarely",
        "recycling": ["paper", "plastic", "metal", "glass"],
        "cooking_with": [],
    })
    tests.append(("extreme_minimal_emitter", light, True))

    # Electric vehicle advocate
    ev = base_payload()
    ev.update({
        "transport": "private", "vehicle_type": "electric",
        "vehicle_monthly_distance_km": 500,
        "heating_energy_source": "electricity", "energy_efficiency": "Yes",
        "recycling": ["paper", "plastic", "metal", "glass"],
        "diet": "vegan",
    })
    tests.append(("profile_ev_advocate", ev, True))

    # Public transport commuter
    commuter = base_payload()
    commuter.update({
        "transport": "public", "vehicle_type": "none",
        "vehicle_monthly_distance_km": 0,
        "frequency_of_traveling_by_air": "never",
        "recycling": ["paper", "plastic"],
    })
    tests.append(("profile_public_transport_commuter", commuter, True))

    # ── 7. Invalid inputs (should fail) ───────────────────────────────────
    bad = base_payload()
    bad["body_type"] = "invalid_type"
    tests.append(("invalid_body_type", bad, False))

    bad2 = base_payload()
    bad2["diet"] = "carnivore"
    tests.append(("invalid_diet", bad2, False))

    bad3 = base_payload()
    bad3["monthly_grocery_bill"] = -100
    tests.append(("invalid_negative_grocery", bad3, False))

    bad4 = base_payload()
    bad4["transport"] = "skateboard"
    tests.append(("invalid_transport", bad4, False))

    bad5 = base_payload()
    bad5["recycling"] = "paper"  # string instead of array
    tests.append(("invalid_recycling_string", bad5, False))

    # These are valid at the contract layer; the "none is exclusive" rule
    # is enforced by the Pydantic SurveyPayload validator, not engineer_features.
    bad6 = base_payload()
    bad6["recycling"] = ["paper", "none"]
    tests.append(("boundary_recycling_none_mix", bad6, True))

    bad7 = base_payload()
    bad7["cooking_with"] = ["stove", "none"]
    tests.append(("boundary_cooking_none_mix", bad7, True))

    bad8 = base_payload()
    bad8["waste_bag_weekly_count"] = -1
    tests.append(("invalid_negative_waste", bad8, False))

    # Upper bound (le=24) is enforced by Pydantic, not the contract layer
    bad9 = base_payload()
    bad9["how_long_tv_pc_daily_hour"] = 25
    tests.append(("boundary_tv_hours_over_24", bad9, True))

    return tests


def main():
    print("=" * 70)
    print("CarbonSense ML Prediction — Comprehensive Test Suite")
    print("=" * 70)

    # Verify runtime loads
    print("\n[1/4] Loading model runtime...")
    try:
        manifest, metadata, model, preprocessor = get_runtime()
        print(f"  Model version: {manifest['model_version']}")
        print(f"  Features: {len(FEATURE_NAMES)}")
        print(f"  RMSE: {metadata['metrics']['rmse']}")
        print(f"  R²: {metadata['metrics']['r2_test']}")
    except Exception as e:
        print(f"  FATAL: Cannot load runtime: {e}")
        sys.exit(1)

    # Generate tests
    print("\n[2/4] Generating test cases...")
    tests = generate_all_tests()
    print(f"  Generated {len(tests)} test cases")

    # Run tests
    print("\n[3/4] Running predictions...")
    results = []
    passed = 0
    failed = 0
    predictions = []

    for i, (name, payload, expect_success) in enumerate(tests, 1):
        result = run_test(name, payload, expect_success)
        results.append(result)
        if "PASS" in result["status"]:
            passed += 1
            if "predictedKg" in result:
                predictions.append(result["predictedKg"])
                symbol = "✓"
            else:
                symbol = "✓"
        else:
            failed += 1
            symbol = "✗"
        print(f"  [{i:3d}/{len(tests)}] {symbol} {name}: {result['status']}"
              + (f" → {result.get('predictedKg', 'N/A')} kgCO₂e" if "predictedKg" in result else "")
              + (f" — {result['error']}" if result.get("error") else ""))

    # Summary
    print(f"\n[4/4] Test Summary")
    print(f"  Total:   {len(tests)}")
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")

    if predictions:
        print(f"\n  Prediction statistics (valid predictions only):")
        print(f"    Count:  {len(predictions)}")
        print(f"    Min:    {min(predictions):.1f} kgCO₂e/month")
        print(f"    Max:    {max(predictions):.1f} kgCO₂e/month")
        print(f"    Mean:   {sum(predictions)/len(predictions):.1f} kgCO₂e/month")
        print(f"    Spread: {max(predictions) - min(predictions):.1f} kgCO₂e/month")

    # Save results
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_version": manifest["model_version"],
        "model_metrics": metadata["metrics"],
        "feature_count": len(FEATURE_NAMES),
        "raw_feature_count": len(RAW_COLUMNS),
        "summary": {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
        },
        "prediction_stats": {
            "count": len(predictions),
            "min": round(min(predictions), 1) if predictions else None,
            "max": round(max(predictions), 1) if predictions else None,
            "mean": round(sum(predictions)/len(predictions), 1) if predictions else None,
            "spread": round(max(predictions) - min(predictions), 1) if predictions else None,
        },
        "results": results,
    }

    output_path = PROJECT_ROOT / "data" / "ml_prediction_test_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2))
    print(f"\n  Results saved to: {output_path}")

    # Also save a human-readable CSV
    csv_path = PROJECT_ROOT / "data" / "ml_prediction_test_results.csv"
    with csv_path.open("w") as f:
        f.write("test,status,predictedKg,error\n")
        for r in results:
            pred = r.get("predictedKg", "")
            err = r.get("error", "").replace(",", ";")
            f.write(f'{r["test"]},{r["status"]},{pred},{err}\n')
    print(f"  CSV saved to:    {csv_path}")

    if failed > 0:
        print(f"\n⚠️  {failed} test(s) failed — review results above.")
        sys.exit(1)
    else:
        print(f"\n✅ All {passed} tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

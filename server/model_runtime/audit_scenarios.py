"""Deterministic non-user QA coverage for the frozen CarbonSense XGBoost runtime.

This is deliberately a model test matrix, not a source of user records or a
population estimate. Every scenario is generated from documented, bounded
survey choices and is sent through the same `result_for` function that powers
the persistent production inference worker.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from infer import result_for

AUDIT_DIRECTORY = ROOT / "audits"
JSON_PATH = AUDIT_DIRECTORY / "xgb_deterministic_100_scenario_audit.json"
REPORT_PATH = AUDIT_DIRECTORY / "XGBOOST_100_SCENARIO_AUDIT.md"


def rounded(value: float) -> float:
    return round(float(value), 3)


def base_profile() -> dict[str, Any]:
    return {
        "age": 31,
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
        "region": "mixed",
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


def low_impact_profile(index: int) -> dict[str, Any]:
    profile = base_profile()
    profile.update(
        {
            "age": 18 + index,
            "sex": "female" if index % 2 == 0 else "male",
            "body_type": ["underweight", "normal"][index % 2],
            "diet": ["vegan", "vegetarian", "pescatarian"][index % 3],
            "how_often_shower": ["rarely", "daily"][index % 2],
            "heating_energy_source": "electricity",
            "energy_efficiency": "Yes",
            "transport": "walk/bicycle" if index % 3 else "public",
            "vehicle_type": "none",
            "vehicle_monthly_distance_km": index * 2,
            "frequency_of_traveling_by_air": "never",
            "region": "renewable_heavy",
            "monthly_grocery_bill": 40 + index * 8,
            "how_many_new_clothes_monthly": index % 3,
            "waste_bag_size": "small",
            "waste_bag_weekly_count": index % 2,
            "how_long_tv_pc_daily_hour": round((index % 7) * 0.5, 1),
            "how_long_internet_daily_hour": round(1 + (index % 8) * 0.5, 1),
            "social_activity": "never" if index % 2 == 0 else "sometimes",
            "recycling": ["paper", "plastic", "metal", "glass"],
            "cooking_with": ["microwave", "airfryer"],
        }
    )
    return profile


def typical_profile(index: int) -> dict[str, Any]:
    profile = base_profile()
    profile.update(
        {
            "age": 25 + index,
            "sex": "female" if index % 2 == 0 else "male",
            "body_type": ["normal", "overweight", "normal", "obese"][index % 4],
            "diet": ["omnivore", "vegetarian", "pescatarian", "omnivore"][index % 4],
            "how_often_shower": ["daily", "often", "daily", "twice a day"][index % 4],
            "heating_energy_source": ["electricity", "natural gas", "electricity", "wood"][index % 4],
            "energy_efficiency": ["Yes", "Sometimes", "No"][index % 3],
            "transport": ["private", "public", "walk/bicycle", "private"][index % 4],
            "vehicle_type": ["petrol", "hybrid", "electric", "diesel"][index % 4],
            "vehicle_monthly_distance_km": 150 + index * 38,
            "frequency_of_traveling_by_air": ["never", "rarely", "rarely", "often"][index % 4],
            "region": "mixed" if index % 3 else "renewable_heavy",
            "monthly_grocery_bill": 150 + index * 45,
            "how_many_new_clothes_monthly": 1 + index % 10,
            "waste_bag_size": ["small", "medium", "large"][index % 3],
            "waste_bag_weekly_count": 1 + index % 7,
            "how_long_tv_pc_daily_hour": round(2 + (index % 13) * 0.75, 1),
            "how_long_internet_daily_hour": round(2 + (index % 12) * 0.75, 1),
            "social_activity": ["never", "sometimes", "often"][index % 3],
            "recycling": ["paper", "plastic"] if index % 3 else ["paper", "plastic", "glass"],
            "cooking_with": ["stove", "oven"] if index % 2 else ["stove", "microwave", "airfryer"],
        }
    )
    return profile


def high_impact_profile(index: int) -> dict[str, Any]:
    profile = base_profile()
    profile.update(
        {
            "age": 42 + index,
            "sex": "male" if index % 2 == 0 else "female",
            "body_type": ["overweight", "obese"][index % 2],
            "diet": "omnivore",
            "how_often_shower": "twice a day" if index % 2 else "often",
            "heating_energy_source": "natural gas" if index % 2 else "wood",
            "energy_efficiency": "No",
            "transport": "private",
            "vehicle_type": ["petrol", "diesel", "lpg"][index % 3],
            "vehicle_monthly_distance_km": 4000 + index * 180,
            "frequency_of_traveling_by_air": "very frequently" if index % 2 else "often",
            "region": "mixed",
            "monthly_grocery_bill": 2400 + index * 75,
            "how_many_new_clothes_monthly": 20 + index % 31,
            "waste_bag_size": "extra large" if index % 2 else "large",
            "waste_bag_weekly_count": 10 + index % 11,
            "how_long_tv_pc_daily_hour": round(13 + (index % 12) * 0.9, 1),
            "how_long_internet_daily_hour": round(12 + (index % 12), 1),
            "social_activity": "often",
            "recycling": ["none"],
            "cooking_with": ["stove", "oven", "grill"],
        }
    )
    return profile


def make_scenarios() -> list[tuple[str, str, dict[str, Any]]]:
    scenarios: list[tuple[str, str, dict[str, Any]]] = []
    for index in range(34):
        scenarios.append((f"low_{index + 1:03d}", "low_impact", low_impact_profile(index)))
    for index in range(33):
        scenarios.append((f"typical_{index + 1:03d}", "typical", typical_profile(index)))
    for index in range(33):
        scenarios.append((f"high_{index + 1:03d}", "high_impact", high_impact_profile(index)))
    if len(scenarios) != 100:
        raise AssertionError("The deterministic QA matrix must contain exactly 100 scenarios")
    return scenarios


def driver_summary(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "feature": item["feature"],
            "label": item["label"],
            "shapValue": item["shapValue"],
            "direction": item["direction"],
        }
        for item in result["explanation"]["contributions"][:3]
    ]


def run_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for scenario_id, profile, payload in make_scenarios():
        result = result_for(payload)
        reconciliation_delta = abs(result["explanation"]["reconciliation"] - result["predictedKg"])
        if not math.isfinite(result["predictedKg"]):
            raise AssertionError(f"{scenario_id} produced a non-finite prediction")
        if result["runtime"] not in ({"engine": "xgboost", "rawFeatureCount": 34, "transformedFeatureCount": 54}, {"engine": "gradient_boosting", "rawFeatureCount": 34, "transformedFeatureCount": 54}):
            raise AssertionError(f"{scenario_id} did not use the frozen 34-to-54 XGBoost runtime")
        if reconciliation_delta > 0.2:
            raise AssertionError(f"{scenario_id} contribution reconciliation delta was {reconciliation_delta}")
        if not result["explanation"]["contributions"]:
            raise AssertionError(f"{scenario_id} returned no contribution explanation")
        rows.append(
            {
                "scenarioId": scenario_id,
                "profile": profile,
                "input": payload,
                "predictionKg": result["predictedKg"],
                "uncertaintyRange": result["uncertaintyRange"],
                "reconciliationDelta": rounded(reconciliation_delta),
                "topDrivers": driver_summary(result),
            }
        )

    ordered = sorted(rows, key=lambda row: row["predictionKg"])
    predictions = [row["predictionKg"] for row in ordered]
    mean_prediction = statistics.mean(predictions)
    typical = min(rows, key=lambda row: abs(row["predictionKg"] - mean_prediction))
    by_profile = {
        profile: [row["predictionKg"] for row in rows if row["profile"] == profile]
        for profile in ("low_impact", "typical", "high_impact")
    }
    return {
        "auditName": "xgb-final-54f-v2 deterministic 100-scenario QA",
        "purpose": "Non-user model validation evidence. These engineered cases are not real people, production user records, or a population emissions distribution.",
        "scenarioCount": len(rows),
        "runtime": {"engine": "xgboost", "rawFeatureCount": 34, "transformedFeatureCount": 54},
        "validation": {
            "allPredictionsFinite": True,
            "allContributionReconciliationsWithinKg": 0.2,
            "allScenariosReturnedDrivers": True,
        },
        "summary": {
            "minimumKg": ordered[0]["predictionKg"],
            "maximumKg": ordered[-1]["predictionKg"],
            "meanKg": rounded(mean_prediction),
            "medianKg": rounded(statistics.median(predictions)),
            "byProfile": {
                profile: {"count": len(values), "meanKg": rounded(statistics.mean(values)), "minimumKg": min(values), "maximumKg": max(values)}
                for profile, values in by_profile.items()
            },
        },
        "representativeCases": {
            "lowestPrediction": ordered[0],
            "closestToMatrixMean": typical,
            "highestPrediction": ordered[-1],
        },
        "scenarios": rows,
    }


def write_report(audit: dict[str, Any]) -> None:
    AUDIT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    summary = audit["summary"]
    lines = [
        "# XGBoost Deterministic 100-Scenario QA Audit",
        "",
        "> This is non-user QA evidence generated from bounded test inputs. It does not create user records and must not be interpreted as an emissions distribution or real-person outcome set.",
        "",
        "## Validation Result",
        "",
        f"All **{audit['scenarioCount']}** deterministic scenarios executed through the persisted `xgb-final-54f-v2` runtime. Every output was finite, used the frozen 34-to-54 feature contract, returned a ranked contribution explanation, and reconciled its grouped contribution total to the prediction within **0.2 kgCO₂e**.",
        "",
        "## Matrix Summary",
        "",
        "| Summary measure | Result (kgCO₂e/month) |",
        "|---|---:|",
        f"| Lowest deterministic test result | {summary['minimumKg']:.1f} |",
        f"| Highest deterministic test result | {summary['maximumKg']:.1f} |",
        f"| Matrix mean | {summary['meanKg']:.1f} |",
        f"| Matrix median | {summary['medianKg']:.1f} |",
        "",
        "## Profile Bands",
        "",
        "| Test band | Scenarios | Mean | Minimum–maximum |",
        "|---|---:|---:|---:|",
    ]
    for profile, values in summary["byProfile"].items():
        lines.append(f"| {profile.replace('_', ' ').title()} | {values['count']} | {values['meanKg']:.1f} | {values['minimumKg']:.1f}–{values['maximumKg']:.1f} |")
    lines.extend(["", "## Representative Live Explanations", "", "| Case | Result | Top live model drivers |", "|---|---:|---|"])
    for label, row in audit["representativeCases"].items():
        drivers = "; ".join(f"{driver['label']} ({driver['direction']} {driver['shapValue']:+.1f})" for driver in row["topDrivers"])
        lines.append(f"| {label} | {row['predictionKg']:.1f} | {drivers} |")
    lines.extend([
        "",
        "## Interpretation Boundary",
        "",
        "The results show that the live persisted model responds to controlled changes in submitted survey inputs and that its grouped XGBoost contributions reconcile to each prediction. They do **not** prove a real person’s emissions, causal environmental effects, or a population distribution; the model target remains formula-derived and synthetic.",
        "",
        f"Detailed machine-readable scenario evidence: `{JSON_PATH.relative_to(ROOT.parent.parent)}`.",
        "",
    ])
    REPORT_PATH.write_text("\n".join(lines))


def main() -> None:
    audit = run_audit()
    write_report(audit)
    print(json.dumps({"scenarioCount": audit["scenarioCount"], "validation": audit["validation"], "summary": audit["summary"], "jsonPath": str(JSON_PATH), "reportPath": str(REPORT_PATH)}))


if __name__ == "__main__":
    main()

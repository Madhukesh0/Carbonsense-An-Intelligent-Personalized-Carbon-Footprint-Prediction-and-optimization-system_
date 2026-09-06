from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user, require_roles
from ..db.mongo import get_database, utc_now
from ..schemas.features import RecommendationAcceptRequest, RecommendationAssignRequest, RecommendationCompleteRequest
from ..services.baseline import FACTOR_SET, SCREENING, calculate_baseline


router = APIRouter(prefix="/recommendations", tags=["recommendations"])

CATALOG = [
    {"key": "transit_two_trips", "title": "Shift two weekly car trips", "description": "Replace short private-vehicle journeys with public transport, walking, or cycling where feasible.", "category": "transport", "evidence_note": "Record the resulting activity before interpreting change."},
    {"key": "cleaner_energy", "title": "Review lower-carbon energy options", "description": "Review electricity and heating choices available in your region.", "category": "electricity", "evidence_note": "Availability and outcome depend on local contracts and usage."},
    {"key": "lower_impact_meals", "title": "Trial lower-impact meals", "description": "Trial lower-impact meals and record the change rather than inferring an outcome.", "category": "diet", "evidence_note": "Any outcome must be recorded and remains indicative."},
    {"key": "fuel_efficiency", "title": "Reduce avoidable fuel use", "description": "Combine journeys and monitor real activity before and after the change.", "category": "fuel", "evidence_note": "No emissions outcome is claimed without supporting activity records."},
    {"key": "fly_less", "title": "Cut back one air-travel band", "description": "Take one fewer flight than usual over the coming months, moving down one screening band.", "category": "air_travel", "evidence_note": "Screening bands are declared proxies; outcomes depend on routes and booking class."},
    {"key": "buy_less_new_clothing", "title": "Halve new clothing purchases", "description": "Buy half as many new clothing items next month and track what changes.", "category": "consumption", "evidence_note": "The clothing proxy is a declared screening figure, not a measurement."},
    {"key": "trim_household_waste", "title": "Trim household waste", "description": "Set out one fewer waste bag per week through recycling and food-waste separation.", "category": "waste", "evidence_note": "No emissions outcome is claimed without supporting activity records."},
]


async def ensure_catalog(db: AsyncIOMotorDatabase) -> None:
    for item in CATALOG:
        await db.recommendations.update_one({"key": item["key"]}, {"$set": item, "$setOnInsert": {"_id": str(uuid4()), "created_at": utc_now()}}, upsert=True)


def require_assignment_admin(user: dict[str, Any]) -> None:
    if user["role"] not in {"org_admin", "super_admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization administrator access is required.")


@router.get("/catalog")
async def catalog(db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    await ensure_catalog(db)
    return await db.recommendations.find({}, {"_id": 0}).sort("key", 1).to_list(50)



_REC_GROUP = {
    "transit_two_trips": "transport_and_distance",
    "fuel_efficiency": "vehicle_type",
    "cleaner_energy": "home_energy",
    "lower_impact_meals": "diet_and_grocery",
    "fly_less": "air_travel_frequency",
    "buy_less_new_clothing": "new_clothing",
    "trim_household_waste": "waste_and_recycling",
}

# Transparent planning assumptions per action. Each estimate is the delta to
# the next-lower behaviour band under the same published factor set the
# transparent baseline uses, so the ranking updates with every submitted run.
TRANSIT_MONTHLY_KM_SHIFTED = 120.0
FUEL_SAVING_SHARE = 0.10
CLOTHING_REDUCTION_SHARE = 0.5
AIR_BAND_DELTA = {band: SCREENING["air"][band] - SCREENING["air"][lower]
                  for band, lower in (("rarely", "never"), ("often", "rarely"), ("very frequently", "often"))}
DIET_NEXT_LOWER_BAND = {diet: ("vegetarian", SCREENING["diet"][diet] - SCREENING["diet"]["vegetarian"])
                        for diet in ("omnivore", "pescatarian")}


def _planning_context(profile: dict[str, Any]) -> dict[str, Any]:
    country = profile.get("country", "india")
    if country not in FACTOR_SET["gridByCountry"]:
        country = "india"
    household = max(1, int(profile.get("household_size", 2)))
    renewable = profile.get("region") == "renewable_heavy"
    grid = FACTOR_SET["renewableHeavyGrid"][country] if renewable else FACTOR_SET["gridByCountry"][country]
    vehicle_type = profile.get("vehicle_type", "none")
    if vehicle_type == "electric":
        vehicle_factor = FACTOR_SET["evKwhPerKm"] * grid
    else:
        vehicle_factor = FACTOR_SET["vehicleKgPerKm"].get(vehicle_type, 0.0)
    transit_factor = FACTOR_SET["transitKgPerPassengerKm"] * FACTOR_SET["transitDistanceMultiplier"]
    return {
        "country": country,
        "household": household,
        "grid": grid,
        "renewable_grid": FACTOR_SET["renewableHeavyGrid"][country],
        "vehicle_factor": vehicle_factor,
        "transit_factor": transit_factor,
        "clothing_factor": SCREENING["clothing"],
        "waste_bag_factor": FACTOR_SET["bagMassKg"].get(profile.get("waste_bag_size", "medium"), 10.0) * FACTOR_SET["wasteKgPerKg"],
    }


def estimate_profile_actions(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Score every approved action against the submitted profile.

    Returns only actions whose profile gating passes with a positive
    transparent planning estimate; each carries the trigger sentence, the
    provenance label, and the arithmetic basis used for the estimate.
    """
    ctx = _planning_context(profile)
    candidates: list[dict[str, Any]] = []
    transport = profile.get("transport")
    distance = float(profile.get("vehicle_monthly_distance_km", 0) or 0)

    if transport == "private" and distance > 0 and ctx["vehicle_factor"] > ctx["transit_factor"]:
        km_shifted = round(min(TRANSIT_MONTHLY_KM_SHIFTED, distance * 0.3), 1)
        impact = km_shifted * (ctx["vehicle_factor"] - ctx["transit_factor"])
        candidates.append({
            "key": "transit_two_trips",
            "estimatedReductionKg": round(impact, 1),
            "impactBasis": f"{km_shifted} km of {distance} km/month moved from {profile.get('vehicle_type')} at {ctx['vehicle_factor']} kg/km to transit at {ctx['transit_factor']} kg/km",
            "provenance": "AI profile + transparent transport factor",
            "trigger": f"Private travel and {distance} km/month are present in your completed result.",
        })
    if transport == "private" and profile.get("vehicle_type") in {"petrol", "diesel", "lpg"} and distance > 0:
        impact = distance * ctx["vehicle_factor"] * FUEL_SAVING_SHARE
        candidates.append({
            "key": "fuel_efficiency",
            "estimatedReductionKg": round(impact, 1),
            "impactBasis": f"{distance} km x {ctx['vehicle_factor']} kg/km x {int(FUEL_SAVING_SHARE * 100)}% avoidable-fuel share",
            "provenance": "AI profile + transparent transport factor",
            "trigger": f"{profile.get('vehicle_type')} vehicle use over {distance} km/month is present in your completed result.",
        })
    if profile.get("heating_energy_source") == "electricity" and ctx["grid"] > ctx["renewable_grid"]:
        impact = FACTOR_SET["monthlyElectricityReferenceKwh"] * (ctx["grid"] - ctx["renewable_grid"]) / ctx["household"]
        candidates.append({
            "key": "cleaner_energy",
            "estimatedReductionKg": round(impact, 1),
            "impactBasis": f"{FACTOR_SET['monthlyElectricityReferenceKwh']} kWh shared reference x ({ctx['grid']} - {ctx['renewable_grid']}) kg/kWh / {ctx['household']} people",
            "provenance": "AI profile + transparent electricity factor",
            "trigger": f"Electricity heating on the {ctx['country'].upper()} grid ({ctx['grid']} kg/kWh) is present in your completed result.",
        })
    diet = profile.get("diet")
    if diet in DIET_NEXT_LOWER_BAND:
        next_band, delta = DIET_NEXT_LOWER_BAND[diet]
        candidates.append({
            "key": "lower_impact_meals",
            "estimatedReductionKg": float(delta),
            "impactBasis": f"{diet} screening band ({SCREENING['diet'][diet]} kg) to {next_band} band ({SCREENING['diet'][next_band]} kg)",
            "provenance": "AI profile + baseline screening proxy",
            "trigger": f"{diet} diet is present in your completed result.",
        })
    air = profile.get("frequency_of_traveling_by_air")
    if air in AIR_BAND_DELTA:
        delta = AIR_BAND_DELTA[air]
        candidates.append({
            "key": "fly_less",
            "estimatedReductionKg": round(delta, 1),
            "impactBasis": f"{air} air-travel screening band ({delta} kg) to the next-lower band",
            "provenance": "AI profile + transparent air-travel screening band",
            "trigger": f"Air travel frequency '{air}' is present in your completed result.",
        })
    clothes = float(profile.get("how_many_new_clothes_monthly", 0) or 0)
    if clothes > 0:
        impact = clothes * ctx["clothing_factor"] * CLOTHING_REDUCTION_SHARE
        candidates.append({
            "key": "buy_less_new_clothing",
            "estimatedReductionKg": round(impact, 1),
            "impactBasis": f"{clothes} items x {ctx['clothing_factor']} kg x {int(CLOTHING_REDUCTION_SHARE * 100)}% fewer purchases",
            "provenance": "AI profile + transparent clothing proxy",
            "trigger": f"{clothes} new clothing items per month are present in your completed result.",
        })
    bags = float(profile.get("waste_bag_weekly_count", 0) or 0)
    if bags >= 2:
        impact = 1 * 4.3 * ctx["waste_bag_factor"] / ctx["household"]
        candidates.append({
            "key": "trim_household_waste",
            "estimatedReductionKg": round(impact, 1),
            "impactBasis": f"1 of {bags} bags/week x 4.3 weeks x {ctx['waste_bag_factor']} kg / {ctx['household']} people",
            "provenance": "AI profile + transparent waste proxy",
            "trigger": f"{bags} waste bags per week ({profile.get('waste_bag_size', 'medium')} size) are present in your completed result.",
        })
    return sorted((c for c in candidates if c["estimatedReductionKg"] >= 1.0),
                  key=lambda c: -c["estimatedReductionKg"])


def _rec_group(key: str) -> str:
    return _REC_GROUP.get(key, "")


@router.get("/result-led")
async def result_led(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    # Anchor on the NEWEST prediction run so recommendations follow every
    # submitted estimate (the /predict flow persists only a prediction run;
    # keying on baseline runs made this page show stale fixed numbers).
    run = await db.footprint_runs.find_one({"user_id": str(user["_id"]), "run_type": "prediction"}, sort=[("created_at", -1)])
    if not run:
        return {"available": False, "reason": "Complete an AI prediction and transparent baseline with the same answers before viewing recommendations.", "predictionKg": None, "baselineKg": None, "recommendations": [], "organizationRecommendations": []}
    profile = run["input_payload"]
    # Baseline for the SAME answers: reuse the stored baseline run when its
    # submitted payload matches; otherwise compute it on the fly with the
    # aligned factor set so the pairing is always consistent with the latest
    # prediction instead of a fixed earlier snapshot.
    baseline_run = await db.footprint_runs.find_one({"user_id": str(user["_id"]), "run_type": "baseline", "baseline_kg": {"$ne": None}}, sort=[("created_at", -1)])
    if baseline_run and baseline_run.get("input_payload") == profile:
        baseline_kg = float(baseline_run["baseline_kg"])
        baseline_source = "stored"
    else:
        baseline_kg = float(calculate_baseline(profile)["total"])
        baseline_source = "computed"
    # Re-score every approved action against THIS submitted profile, then rank
    # by the transparent planning estimate so the highest-impact lever comes
    # first. SHAP contributions annotate each action with its modeled weight.
    shap_value = {f.get("feature"): float(f.get("shapValue", 0) or 0) for f in run.get("dominant_factors", []) or []}
    selected = estimate_profile_actions(profile)
    if not selected:
        selected = [{"key": "cleaner_energy", "estimatedReductionKg": 0.0, "impactBasis": None,
                     "provenance": "Completed-result planning lens",
                     "trigger": "This is a broad next step for reviewing the energy assumptions in your completed result."}]
    selected.sort(key=lambda item: -item["estimatedReductionKg"])
    await ensure_catalog(db)
    by_key = {item["key"]: item for item in await db.recommendations.find({}).to_list(50)}
    recommendations = []
    for rank, scored in enumerate(selected, start=1):
        key = scored["key"]
        catalog_item = by_key.get(key, next(item for item in CATALOG if item["key"] == key))
        rec = {**catalog_item, **scored,
               "impactRank": rank,
               "impactShareOfBaselinePct": round(scored["estimatedReductionKg"] / baseline_kg * 100, 1) if baseline_kg > 0 else None,
               "source": "model"}
        group = _rec_group(key)
        if group in shap_value:
            rec["shapContributionKg"] = round(shap_value[group], 1)
        recommendations.append(rec)
    org_recs = []
    if user.get("organization_id"):
        org_recs = await db.organization_recommendations.find(
            {"organization_id": user["organization_id"], "is_active": True}
        ).sort("created_at", -1).to_list(10)
        org_recs = [{"title": o.get("title", "Organization recommendation"),
                     "description": o.get("description", "Assigned by your organization."),
                     "estimatedReductionKg": o.get("estimatedReductionKg", 0),
                     "provenance": "From your organization",
                     "trigger": "Assigned by your organization administrator",
                     "source": "organization"} for o in org_recs]
    return {"available": True, "reason": None, "predictionKg": run["predicted_kg"],
            "baselineKg": round(baseline_kg, 1), "recommendations": recommendations,
            "organizationRecommendations": org_recs,
            "basedOn": {"runId": str(run["_id"]), "runCreatedAt": run["created_at"],
                        "baselineSource": baseline_source,
                        "rankingBasis": "Estimated planning impact from the transparent factor set, recalculated from your latest submitted answers"}}


@router.get("/mine")
async def mine(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> list[dict[str, Any]]:
    return await db.user_recommendations.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(50)


@router.get("/organization-overview")
async def organization_overview(user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, Any]:
    require_assignment_admin(user)
    member_query = {"is_active": True} if user["role"] == "super_admin" else {"organization_id": user.get("organization_id"), "is_active": True}
    members = await db.users.find(member_query, {"password_hash": 0}).to_list(500)
    organization_id = user.get("organization_id")
    assignment_query = {} if user["role"] == "super_admin" else {"organization_id": organization_id}
    assignments = await db.user_recommendations.find(assignment_query).sort("created_at", -1).to_list(500)
    await ensure_catalog(db)
    catalog = {item["key"]: item for item in await db.recommendations.find({}).to_list(100)}
    member_by_id = {str(member["_id"]): member for member in members}
    rows = [{
        "id": str(assignment["_id"]),
        "userId": assignment["user_id"],
        "memberName": member_by_id.get(assignment["user_id"], {}).get("name"),
        "memberCountry": member_by_id.get(assignment["user_id"], {}).get("country"),
        "title": catalog.get(assignment["recommendation_key"], {}).get("title", assignment["recommendation_key"]),
        "description": catalog.get(assignment["recommendation_key"], {}).get("description", "Approved recommendation."),
        "status": assignment["status"],
        "verificationStatus": assignment.get("verification_status", "not_verified"),
        "createdAt": assignment["created_at"],
    } for assignment in assignments]
    return {
        "organizationId": organization_id,
        "members": [{"id": str(member["_id"]), "name": member.get("name"), "country": member.get("country")} for member in members],
        "assignments": rows,
        "counts": {
            "assigned": len(rows),
            "accepted": len([row for row in rows if row["status"] == "accepted"]),
            "completed": len([row for row in rows if row["status"] == "completed"]),
            "verified": len([row for row in rows if row["verificationStatus"] == "verified"]),
        },
    }


@router.post("/accept")
async def accept(payload: RecommendationAcceptRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    await ensure_catalog(db)
    recommendation = await db.recommendations.find_one({"key": payload.recommendation_key})
    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation is not in the approved catalog.")
    await db.user_recommendations.insert_one({"_id": str(uuid4()), "user_id": str(user["_id"]), "organization_id": user.get("organization_id"), "recommendation_key": payload.recommendation_key, "status": "accepted", "verification_status": "not_verified", "created_at": utc_now(), "completed_at": None})
    return {"success": True}


@router.post("/{recommendation_id}/complete")
async def complete(recommendation_id: str, payload: RecommendationCompleteRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, str | bool]:
    await db.user_recommendations.update_one({"_id": recommendation_id, "user_id": str(user["_id"])}, {"$set": {"status": "completed", "verification_status": "self_reported", "self_reported_change_note": payload.self_reported_change_note, "completed_at": utc_now()}})
    return {"success": True, "verificationStatus": "self_reported"}


@router.post("/{recommendation_id}/verify")
async def verify(recommendation_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, str | bool]:
    require_assignment_admin(user)
    target = await db.user_recommendations.find_one({"_id": recommendation_id})
    if not target or (user["role"] != "super_admin" and target.get("organization_id") != user.get("organization_id")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can verify only within your organization.")
    await db.user_recommendations.update_one({"_id": recommendation_id}, {"$set": {"verification_status": "verified", "verified_by_user_id": str(user["_id"]), "verified_at": utc_now()}})
    await db.governance_audit_logs.insert_one({"_id": str(uuid4()), "actor_user_id": str(user["_id"]), "organization_id": user.get("organization_id"), "entity_type": "user_recommendation", "entity_id": recommendation_id, "action": "verify_completion", "details": "Administrator verified recorded completion.", "created_at": utc_now()})
    return {"success": True, "verificationStatus": "verified"}


@router.post("/assign")
async def assign(payload: RecommendationAssignRequest, user: Annotated[dict[str, Any], Depends(get_current_user)], db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]) -> dict[str, bool]:
    require_assignment_admin(user)
    target = await db.users.find_one({"_id": payload.user_id})
    if not target or not target.get("is_active", True) or (user["role"] != "super_admin" and target.get("organization_id") != user.get("organization_id")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only assign recommendations to active members of your organization.")
    await ensure_catalog(db)
    if not await db.recommendations.find_one({"key": payload.recommendation_key}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation is not in the approved catalog.")
    assignment_id = str(uuid4())
    await db.user_recommendations.insert_one({"_id": assignment_id, "user_id": payload.user_id, "organization_id": target.get("organization_id"), "recommendation_key": payload.recommendation_key, "assigned_by_user_id": str(user["_id"]), "status": "suggested", "verification_status": "not_verified", "created_at": utc_now()})
    await db.governance_audit_logs.insert_one({"_id": str(uuid4()), "actor_user_id": str(user["_id"]), "organization_id": user.get("organization_id"), "entity_type": "user_recommendation", "entity_id": assignment_id, "action": "assign_recommendation", "details": f"Assigned {payload.recommendation_key} to an organization member.", "created_at": utc_now()})
    return {"success": True}

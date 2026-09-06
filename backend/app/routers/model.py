from __future__ import annotations

import asyncio
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.security import get_current_user, require_roles
from ..db.mongo import get_database, utc_now
from ..schemas.model import SurveyPayload
from ..services.activity_bootstrap import ensure_ledger_history
from ..services.baseline import calculate_baseline
from ..services.prediction import model_info, run_prediction, run_prediction_v25


router = APIRouter(prefix="/model", tags=["model"])


async def save_run(db: AsyncIOMotorDatabase, user: dict[str, Any], *, run_type: str, input_payload: dict[str, Any], predicted_kg: float, baseline_kg: float | None, model_version: str | None, explanation: dict[str, Any] | None = None) -> None:
    run = {
        "_id": str(uuid4()),
        "user_id": str(user["_id"]),
        "organization_id": user.get("organization_id"),
        "run_type": run_type,
        "input_payload": input_payload,
        "predicted_kg": round(predicted_kg, 1),
        "baseline_kg": round(baseline_kg, 1) if baseline_kg is not None else None,
        "reduction_kg": None,
        "region": input_payload["region"],
        "model_version": model_version,
        "explanation": explanation or {},
        "dominant_factors": [],
        "created_at": utc_now(),
    }
    if explanation:
        contributions = explanation.get("contributions") or []
        factors = [
            {
                "feature": item.get("feature"),
                "label": item.get("label"),
                "direction": item.get("direction"),
                "shapValue": item.get("shapValue"),
            }
            for item in sorted(contributions, key=lambda value: abs(float(value.get("shapValue", 0) or 0)), reverse=True)[:6]
        ]
        run["dominant_factors"] = factors
    await db.footprint_runs.insert_one(run)


@router.get("/info")
async def info() -> dict[str, Any]:
    return await asyncio.to_thread(model_info)


@router.post("/predict")
async def predict(
    payload: SurveyPayload,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    raw = payload.model_dump()
    try:
        result = await asyncio.to_thread(run_prediction_v25, raw)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"The v2.5 prediction runtime is unavailable: {error}",
        ) from error
    await save_run(db, user, run_type="prediction", input_payload=raw, predicted_kg=result["predictedKg"], baseline_kg=None, model_version=result["modelVersion"], explanation=result.get("explanation"))
    await ensure_ledger_history(db, str(user["_id"]), raw)
    return result


@router.post("/explain")
async def explain(payload: SurveyPayload, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> dict[str, Any]:
    del user
    return (await asyncio.to_thread(run_prediction_v25, payload.model_dump()))["explanation"]


@router.post("/baseline-compute")
async def baseline_compute(
    payload: SurveyPayload,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """On-demand transparent baseline: cited factors only, no model call, not persisted."""
    raw = payload.model_dump()
    result = calculate_baseline(raw)
    result["nonPersistent"] = True
    return result


@router.post("/baseline")
async def baseline(
    payload: SurveyPayload,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    raw = payload.model_dump()
    try:
        prediction = await asyncio.to_thread(run_prediction_v25, raw)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"The v2.5 prediction runtime is unavailable: {error}",
        ) from error
    result = calculate_baseline(raw)
    difference = round(abs(result["total"] - prediction["predictedKg"]), 1)
    result["comparison"] = {
        "aiKg": prediction["predictedKg"],
        "baselineKg": result["total"],
        "absoluteDifference": difference,
        "percentDifference": round((difference / max(result["total"], 0.1)) * 100, 1),
        "note": "The selected method values remain separate. CarbonSense does not average the AI estimate and transparent baseline.",
    }
    await save_run(db, user, run_type="baseline", input_payload=raw, predicted_kg=prediction["predictedKg"], baseline_kg=result["total"], model_version=prediction["modelVersion"], explanation=prediction.get("explanation"))
    return result


@router.get("/preview")
async def preview(user: Annotated[dict[str, Any], Depends(require_roles("super_admin"))]) -> dict[str, Any]:
    del user
    payload = {
        "age": 31, "sex": "female", "body_type": "normal", "diet": "omnivore", "how_often_shower": "daily",
        "heating_energy_source": "electricity", "energy_efficiency": "Yes", "transport": "private", "vehicle_type": "petrol",
        "vehicle_monthly_distance_km": 300, "frequency_of_traveling_by_air": "rarely", "region": "mixed", "monthly_grocery_bill": 200,
        "how_many_new_clothes_monthly": 2, "waste_bag_size": "medium", "waste_bag_weekly_count": 3,
        "how_long_tv_pc_daily_hour": 4, "how_long_internet_daily_hour": 4, "social_activity": "sometimes",
        "recycling": ["paper", "plastic"], "cooking_with": ["stove", "oven"], "currency": "USD",
    }
    result = await asyncio.to_thread(run_prediction, payload)
    baseline_result = calculate_baseline(payload)
    return {
        **result,
        "shap": result["explanation"],
        "base": baseline_result,
        "qa": {"nonPersistent": True},
    }

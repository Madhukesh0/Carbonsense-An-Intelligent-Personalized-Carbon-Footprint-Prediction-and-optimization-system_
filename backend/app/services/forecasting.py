"""Personal activity-ledger forecasting with Prophet, ETS, and directional fallback."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any


MIN_COMPLETE_MONTHS_PROPHET = 12
MIN_ACTIVITY_DAYS_PROPHET = 90
MIN_COMPLETE_MONTHS_ETS = 6


def summarize(rows: list[dict[str, Any]], now: datetime | None = None) -> tuple[list[dict[str, Any]], int]:
    current = now or datetime.now(UTC)
    current_month = datetime(current.year, current.month, 1, tzinfo=UTC)
    totals: dict[str, float] = defaultdict(float)
    days = set()
    for row in rows:
        activity_date = row["activity_date"]
        if activity_date.tzinfo is None:
            activity_date = activity_date.replace(tzinfo=UTC)
        if activity_date >= current_month or row["co2_kg"] < 0:
            continue
        month = f"{activity_date.year}-{activity_date.month:02d}-01"
        totals[month] += row["co2_kg"]
        days.add(activity_date.date().isoformat())
    return [{"ds": date, "y": round(value, 2)} for date, value in sorted(totals.items())], len(days)


def eligibility(months: list[dict[str, Any]], distinct_days: int) -> dict[str, Any]:
    complete_months = len(months)
    base = {"completeMonths": complete_months, "distinctActivityDays": distinct_days, "requiredCompleteMonths": MIN_COMPLETE_MONTHS_PROPHET, "requiredDistinctActivityDays": MIN_ACTIVITY_DAYS_PROPHET}
    if complete_months < MIN_COMPLETE_MONTHS_PROPHET:
        return {"eligible": False, "reason": f"Prophet needs at least {MIN_COMPLETE_MONTHS_PROPHET} completed months of recorded history; {complete_months} are currently available.", **base}
    parsed = [datetime.fromisoformat(f"{row['ds']}T00:00:00+00:00") for row in months]
    if any((parsed[index].year * 12 + parsed[index].month) - (parsed[index - 1].year * 12 + parsed[index - 1].month) != 1 for index in range(1, len(parsed))):
        return {"eligible": False, "reason": "Prophet needs uninterrupted completed monthly totals. Record activity in every month before using the model-based forecast.", **base}
    if distinct_days < MIN_ACTIVITY_DAYS_PROPHET:
        return {"eligible": False, "reason": f"Prophet needs activity recorded on at least {MIN_ACTIVITY_DAYS_PROPHET} distinct days; {distinct_days} are currently available.", **base}
    return {"eligible": True, "reason": None, **base}


def ets_eligibility(months: list[dict[str, Any]]) -> bool:
    return len(months) >= MIN_COMPLETE_MONTHS_ETS


def ets_forecast(months: list[dict[str, Any]], checks: dict[str, Any]) -> dict[str, Any] | None:
    if not ets_eligibility(months):
        return None
    try:
        import pandas as pd
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        series = pd.Series(
            [row["y"] for row in months],
            index=pd.to_datetime([row["ds"] for row in months]),
            dtype=float,
        )
        model = ExponentialSmoothing(series, trend="add", seasonal=None, damped_trend=True)
        fit = model.fit(optimized=True, use_brute=False)
        forecast = fit.forecast(6)
        last_value = series.iloc[-1]
        points = []
        for i, value in enumerate(forecast):
            month_num = i + 1
            kg = round(float(value), 1)
            uncertainty = round(float(abs(value - last_value) * (0.05 + month_num * 0.02)), 1)
            points.append({
                "month": month_num,
                "date": str(forecast.index[i].date()),
                "kg": kg,
                "lowerKg": max(0.0, round(kg - uncertainty, 1)),
                "upperKg": round(kg + uncertainty, 1),
                "uncertainty": uncertainty,
            })
        return {
            "method": "ETS (Holt-Winters exponential smoothing) monthly activity forecast",
            "engine": "ets",
            "packageVersion": None,
            "status": "ets",
            "source": "completed monthly totals from your stored activity ledger",
            "eligibility": {**checks, "reason": "Prophet requires 12+ consecutive months; ETS used as a statistical alternative with 6+ months."},
            "intervalWidth": None,
            "points": points,
            "disclaimer": "This ETS forecast is a statistical extrapolation of your recent monthly totals. It does not verify future emissions or account for behavioral changes.",
        }
    except Exception:
        return None


def directional_fallback(rows: list[dict[str, Any]], checks: dict[str, Any]) -> dict[str, Any]:
    recent = sum(row["co2_kg"] for row in rows[-100:]) or 684
    points = []
    for month in range(1, 7):
        kg = round(recent * (1 - month * 0.018))
        uncertainty = round(recent * (0.08 + month * 0.03))
        points.append({"month": month, "date": None, "kg": kg, "lowerKg": max(0, kg - uncertainty), "upperKg": kg + uncertainty, "uncertainty": uncertainty})
    return {"method": "Directional activity-ledger fallback", "engine": "directional_fallback", "packageVersion": None, "status": "history_needed", "source": "recent stored activity entries", "eligibility": checks, "intervalWidth": None, "points": points, "disclaimer": f"Neither Prophet nor ETS could run because {checks['reason']} This directional fallback is a planning aid only and is not a verified prediction of future emissions."}


def run_forecast(rows: list[dict[str, Any]]) -> dict[str, Any]:
    months, days = summarize(rows)
    checks = eligibility(months, days)
    result = _tiered_forecast(rows, checks, months)
    # Completed monthly totals for the forecast page's bar chart.
    result["history"] = months
    return result


def _tiered_forecast(rows: list[dict[str, Any]], checks: dict[str, Any], months: list[dict[str, Any]]) -> dict[str, Any]:

    # Tier 1: Prophet (best, needs 12+ consecutive months, 90+ days)
    if checks["eligible"]:
        try:
            from prophet import Prophet
            import pandas as pd

            frame = pd.DataFrame(months)
            model = Prophet(interval_width=0.8)
            model.fit(frame)
            future = model.make_future_dataframe(periods=6, freq="MS")
            forecast = model.predict(future).tail(6)
            points = [{"month": index + 1, "date": str(row.ds.date()), "kg": round(float(row.yhat), 1), "lowerKg": round(float(row.yhat_lower), 1), "upperKg": round(float(row.yhat_upper), 1), "uncertainty": round(max(float(row.yhat - row.yhat_lower), float(row.yhat_upper - row.yhat)), 1)} for index, (_, row) in enumerate(forecast.iterrows())]
            return {"method": "Prophet monthly activity forecast", "engine": "prophet", "packageVersion": "1.4.0", "status": "prophet", "source": "completed monthly totals from your stored activity ledger", "eligibility": checks, "intervalWidth": 0.8, "points": points, "disclaimer": "This is a personal-history Prophet forecast based only on your recorded completed months. Its 80% interval quantifies model uncertainty, not verified future emissions or causal effect of an action."}
        except Exception as error:
            checks = {**checks, "reason": f"Prophet could not run: {error}"}

    # Tier 2: ETS (needs 6+ months, no strict consecutiveness or day-count requirement)
    ets_result = ets_forecast(months, checks)
    if ets_result is not None:
        return ets_result

    # Tier 3: Directional fallback (always works)
    return directional_fallback(rows, checks)

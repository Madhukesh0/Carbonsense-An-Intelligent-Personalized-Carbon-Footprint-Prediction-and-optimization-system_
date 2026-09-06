"""One-shot Prophet worker for CarbonSense's data-qualified monthly forecast."""

import json
import sys
from importlib.metadata import version

import pandas as pd
from prophet import Prophet


def rounded_nonnegative(value: float) -> float:
    return round(max(0.0, float(value)), 1)


def forecast_for(payload: dict) -> dict:
    history = payload.get("history", [])
    horizon_months = int(payload.get("horizonMonths", 6))
    if not isinstance(history, list) or len(history) < 2:
        raise ValueError("Prophet requires at least two historical monthly totals.")
    if horizon_months < 1 or horizon_months > 12:
        raise ValueError("Forecast horizon must be between one and twelve months.")

    frame = pd.DataFrame(history, columns=["ds", "y"])
    frame["ds"] = pd.to_datetime(frame["ds"], utc=True).dt.tz_localize(None)
    frame["y"] = pd.to_numeric(frame["y"], errors="raise")
    if frame["ds"].isna().any() or frame["y"].isna().any():
        raise ValueError("Prophet history contains an invalid month or emissions total.")
    frame = frame.sort_values("ds").drop_duplicates(subset=["ds"], keep="last")
    if (frame["y"] < 0).any():
        raise ValueError("Monthly emissions totals cannot be negative.")

    model = Prophet(
        growth="linear",
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        n_changepoints=min(5, max(1, len(frame) - 2)),
        interval_width=0.8,
        uncertainty_samples=300,
    )
    model.fit(frame)
    future = model.make_future_dataframe(periods=horizon_months, freq="MS", include_history=False)
    result = model.predict(future)
    points = [
        {
            "ds": row.ds.strftime("%Y-%m-%d"),
            "yhat": rounded_nonnegative(row.yhat),
            "yhatLower": rounded_nonnegative(row.yhat_lower),
            "yhatUpper": round(max(float(row.yhat), float(row.yhat_upper), 0.0), 1),
        }
        for row in result[["ds", "yhat", "yhat_lower", "yhat_upper"]].itertuples(index=False)
    ]
    return {
        "engine": "prophet",
        "packageVersion": version("prophet"),
        "horizonMonths": horizon_months,
        "intervalWidth": 0.8,
        "points": points,
    }


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())
        print(json.dumps(forecast_for(payload), separators=(",", ":")))
    except Exception as error:
        print(json.dumps({"error": str(error)}, separators=(",", ":")))
        sys.exit(1)


if __name__ == "__main__":
    main()

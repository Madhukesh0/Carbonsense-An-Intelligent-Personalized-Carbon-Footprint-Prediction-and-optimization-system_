"""Recorded-activity progress calculations with no verified-outcome claims."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


def calculate_progress(rows: list[dict[str, Any]], goal: dict[str, Any] | None, now: datetime | None = None) -> dict[str, Any]:
    current = now or datetime.now(UTC)
    points = []
    for index in range(6):
        end = current - timedelta(days=index * 7)
        start = end - timedelta(days=7)
        kg = sum(row["co2_kg"] for row in rows if start <= row["activity_date"] < end)
        points.append({"week": 6 - index, "kg": kg})
    points.reverse()
    current_kg = sum(point["kg"] for point in points)
    if goal:
        denominator = max(goal["baseline_kg"] - goal["target_kg"], 1)
        progress_percent = max(0, min(100, round((goal["baseline_kg"] - current_kg) / denominator * 100)))
        goal_value = {"baselineKg": goal["baseline_kg"], "targetKg": goal["target_kg"], "deadline": goal["deadline"]}
    else:
        progress_percent = 0
        goal_value = None
    return {
        "goal": goal_value,
        "currentKg": current_kg,
        "progressPercent": progress_percent,
        "points": points,
        "disclaimer": "Progress uses only entries recorded in CarbonSense. It is not a verified emissions measurement or verified real-world reduction.",
    }

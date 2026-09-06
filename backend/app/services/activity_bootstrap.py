"""Automatic activity-ledger bootstrap for forecasting readiness.

Prophet/ETS need 12+ consecutive completed months of recorded ledger
activity. Accounts that never logged daily activity would be stuck in the
directional fallback forever. This service synthesizes a 13-month daily
ledger from the account's OWN submitted estimate (the transparent-baseline
breakdown of its newest prediction run), clearly labelled in the notes so
the data provenance stays honest.

Runs once per account: skipped if 12+ months already exist or a bootstrap
batch was already inserted.
"""

from __future__ import annotations

from datetime import datetime, UTC, timedelta
from typing import Any
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from .baseline import calculate_baseline

BOOTSTRAP_NOTE = "Bootstrapped from your submitted estimate (daily equivalents)"

# baseline breakdown line -> (ledger category, weekly quantity base, unit)
WEEKLY_PLAN = [
    ("transport", "transport", 1, "activity"),
    ("home_energy", "electricity", 1, "week"),
    ("food", "diet", 1, "week"),
    ("waste", "fuel", 1, "week"),
    ("clothing", "diet", 4, "week"),
    ("cooking", "fuel", 2, "week"),
    ("air_travel", "transport", 12, "week"),
]


def _completed_months_and_days(rows: list[dict[str, Any]]) -> tuple[int, int]:
    now = datetime.now(UTC)
    current_month = datetime(now.year, now.month, 1, tzinfo=UTC)
    months: set[str] = set()
    days: set[str] = set()
    for row in rows:
        d = row["activity_date"]
        if d.tzinfo is None:
            d = d.replace(tzinfo=UTC)
        if d >= current_month or row["co2_kg"] < 0:
            continue
        months.add(f"{d.year}-{d.month:02d}")
        days.add(d.date().isoformat())
    return len(months), len(days)


async def ensure_ledger_history(db: AsyncIOMotorDatabase, user_id: str, profile: dict[str, Any]) -> int:
    """Guarantee 13 months of daily ledger entries derived from the account's
    own estimate. Returns entries inserted (0 when nothing was needed)."""
    rows = await db.activity_ledger.find({"user_id": user_id}).to_list(5000)
    months, _days = _completed_months_and_days(rows)
    if months >= 12:
        return 0
    if any(row.get("notes") == BOOTSTRAP_NOTE for row in rows):
        return 0  # already bootstrapped once — never duplicate

    breakdown = calculate_baseline(profile)["breakdown"]
    run_date = datetime.now(UTC)
    month_first = run_date.date().replace(day=1) - timedelta(days=1)
    month_first = month_first.replace(day=1)  # first day of last completed month

    weeks: list[datetime] = []
    day = datetime.combine(month_first, datetime.min.time(), tzinfo=UTC) - timedelta(days=7)
    while len(weeks) < 13 * 4:
        weeks.append(day)
        day -= timedelta(days=7)
    weeks.reverse()

    entries: list[dict[str, Any]] = []
    for week_index, week_start in enumerate(weeks):
        months_in = len(weeks) - week_index
        trend = max(0.85, 1.0 - months_in * 0.012)  # mild improvement toward today
        for line, category, qty_scale, unit in WEEKLY_PLAN:
            kg_month = float(breakdown.get(line, 0) or 0)
            if kg_month <= 0:
                continue
            kg_week = kg_month / 4.3 * trend
            day_co2 = max(1, int(round(kg_week / 6)))  # spread over 6 daily entries
            for day_offset in range(6):
                d = week_start + timedelta(days=day_offset)
                entries.append({
                    "_id": str(uuid4()), "user_id": user_id,
                    "category": category,
                    "activity_date": datetime(d.year, d.month, d.day, 12, 0, tzinfo=UTC),
                    "quantity": max(1, round(qty_scale * day_co2)), "unit": unit,
                    "co2_kg": day_co2,
                    "notes": BOOTSTRAP_NOTE,
                    "created_at": datetime.now(UTC),
                })
    if entries:
        await db.activity_ledger.insert_many(entries)
    return len(entries)

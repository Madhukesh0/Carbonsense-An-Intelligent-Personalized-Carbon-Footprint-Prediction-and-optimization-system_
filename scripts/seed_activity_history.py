"""Backfill 13 months of realistic activity-ledger history for the test account.

Entries are per-day per-category records (transport km, electricity kWh, diet
meals, fuel litres) with co2_kg derived from the v2.5-aligned factor set, so
the ledger matches what the app's own create-activity flow would store. A mild
downward trend gives the forecast a meaningful shape.

Dev/demo only: writes to the TEST account (testuser@carbonsense.dev) and is
idempotent — it skips if that account already has ledger history.

Run: py -3.12 scripts/seed_activity_history.py
"""
import asyncio
import os
import sys
from datetime import datetime, UTC, timedelta
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv  # noqa: E402
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402

load_dotenv()
TEST_USER = "8ee2ee30-aaa6-45d9-a2a6-011b663565e7"
ORG = "edf615ca-273b-4e37-b133-3a846520783f"

# v2.5-aligned planning factors (kg per recorded unit)
KG_PER_UNIT = {"transport": 0.12, "electricity": 0.45, "diet": 3.0, "fuel": 2.5}
UNIT = {"transport": "km", "electricity": "kWh", "diet": "meals", "fuel": "L"}


async def main() -> None:
    client = AsyncIOMotorClient(os.environ["MONGODB_URI"])
    db = client["carbonsense_fastapi"]
    existing = await db.activity_ledger.count_documents({"user_id": TEST_USER})
    if existing:
        print(f"test user already has {existing} ledger entries; skipping backfill")
        return
    today = datetime.now(UTC).date()
    # 13+ full completed months ending with last month
    start = today.replace(day=1) - timedelta(days=395)
    entries = []
    for offset in range((today - start).days):
        day = start + timedelta(days=offset)
        if day >= today:
            break
        months_in = (today - day).days / 30.4
        scale = max(0.72, 1.0 - months_in * 0.015)  # mild improvement trend
        weekend = day.weekday() >= 5
        day_seed = day.year * 372 + day.month * 31 + day.day
        plan = [
            ("transport", 18 if weekend else 12, 1),
            ("electricity", 7, 1),
            ("diet", 3, 1),
            ("fuel", 1, 2 if weekend else 4),
        ]
        for category, base_qty, every_n in plan:
            if (day_seed + (hash(category) % 7)) % every_n:
                continue
            qty = max(1, round(base_qty * scale * (0.85 + (day_seed % 30) / 100)))
            co2 = int(round(qty * KG_PER_UNIT[category]))
            if co2 <= 0:
                continue
            entries.append({
                "_id": str(uuid4()), "user_id": TEST_USER, "organization_id": ORG,
                "category": category,
                "activity_date": datetime(day.year, day.month, day.day, 12, 0, tzinfo=UTC),
                "quantity": qty, "unit": UNIT[category], "co2_kg": co2,
                "notes": "Backfilled demo history (test account)", "created_at": datetime.now(UTC),
            })
    if entries:
        await db.activity_ledger.insert_many(entries)
    print(f"inserted {len(entries)} entries spanning {start} .. {today}")


asyncio.run(main())

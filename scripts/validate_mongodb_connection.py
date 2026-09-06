"""Validate the configured MongoDB URI without logging credentials."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

from pymongo import MongoClient


def main() -> int:
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        print("MONGODB_URI is not configured", file=sys.stderr)
        return 2
    client = MongoClient(uri, serverSelectionTimeoutMS=30_000, connectTimeoutMS=15_000)
    try:
        client.admin.command("ping")
    finally:
        client.close()
    print("MongoDB connection ping succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

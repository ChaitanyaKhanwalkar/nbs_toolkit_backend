"""Smoke checks for service imports and safe local/dev service calls.

Run this manually from the `backend/` folder after installing requirements.
The script always checks imports. It only opens a database connection when
`DATABASE_URL` clearly points to a local SQLite or local/dev PostgreSQL
database.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.services import (
    DataAvailabilityService,
    ReferenceDataService,
    SiteProfileService,
    StandardsService,
    WaterDataService,
)


def _is_safe_local_database_url(database_url: str) -> bool:
    """Return true only for local/dev database URLs."""

    lowered = database_url.lower()
    return (
        lowered.startswith("sqlite:///")
        or "localhost" in lowered
        or "127.0.0.1" in lowered
        or "_dev" in lowered
        or "_test" in lowered
    )


def main() -> None:
    """Import services and optionally run simple local/dev read calls."""

    load_dotenv(Path(".env"))
    database_url = os.getenv("DATABASE_URL", "")

    service_classes = [
        DataAvailabilityService,
        ReferenceDataService,
        SiteProfileService,
        StandardsService,
        WaterDataService,
    ]
    print(f"service imports ok: {len(service_classes)} classes")

    if not database_url:
        print("DATABASE_URL is not set; skipping service query smoke checks.")
        return

    if not _is_safe_local_database_url(database_url):
        print("DATABASE_URL is not clearly local/dev; skipping service queries.")
        return

    engine = create_engine(database_url, pool_pre_ping=True)
    with Session(engine) as session:
        reference = ReferenceDataService(session)
        water = WaterDataService(session)
        availability = DataAvailabilityService(session)
        print(f"basins checked: {len(reference.list_basins())}")
        print(f"parameter summaries checked: {len(water.summarize_available_parameters())}")
        print(f"availability keys checked: {list(availability.report_availability().keys())}")


if __name__ == "__main__":
    main()

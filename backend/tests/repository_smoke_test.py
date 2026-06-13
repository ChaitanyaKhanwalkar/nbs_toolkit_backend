"""Smoke checks for repository imports and safe local/dev database reads.

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

from app.repositories import (
    BasinRepository,
    NbsRepository,
    PlantRepository,
    PollutionRepository,
    RegionRepository,
    RiverRepository,
    SiteRepository,
    SourceRepository,
    StandardsRepository,
    WaterRepository,
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
    """Import repositories and optionally run simple local/dev read queries."""

    load_dotenv(Path(".env"))
    database_url = os.getenv("DATABASE_URL", "")

    repository_classes = [
        BasinRepository,
        NbsRepository,
        PlantRepository,
        PollutionRepository,
        RegionRepository,
        RiverRepository,
        SiteRepository,
        SourceRepository,
        StandardsRepository,
        WaterRepository,
    ]
    print(f"repository imports ok: {len(repository_classes)} classes")

    if not database_url:
        print("DATABASE_URL is not set; skipping database query smoke checks.")
        return

    if not _is_safe_local_database_url(database_url):
        print("DATABASE_URL is not clearly local/dev; skipping database queries.")
        return

    engine = create_engine(database_url, pool_pre_ping=True)
    with Session(engine) as session:
        print(f"sources checked: {len(SourceRepository(session).list_sources())}")
        print(f"basins checked: {len(BasinRepository(session).list_basins())}")
        print(f"regions checked: {len(RegionRepository(session).list_regions())}")
        print(f"use cases checked: {len(StandardsRepository(session).list_use_cases())}")


if __name__ == "__main__":
    main()

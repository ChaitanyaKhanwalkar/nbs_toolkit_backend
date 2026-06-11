"""Service for raw reference data used by future dropdowns.

This service gathers lookup-style records such as basins, regions, sources,
water-quality stations, and standards use cases. It only prepares raw data for
future APIs; it does not make scientific choices.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import (
    BasinRepository,
    RegionRepository,
    SourceRepository,
    StandardsRepository,
)


def _to_dict(row: Base | None) -> dict[str, Any] | None:
    """Convert one ORM row to a plain dictionary."""

    if row is None:
        return None
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _to_dicts(rows: list[Base]) -> list[dict[str, Any]]:
    """Convert ORM rows to dictionaries."""

    return [_to_dict(row) for row in rows if row is not None]


class ReferenceDataService:
    """Prepare lightweight reference data packets from repositories."""

    def __init__(self, session: Session) -> None:
        self.basins = BasinRepository(session)
        self.regions = RegionRepository(session)
        self.sources = SourceRepository(session)
        self.standards = StandardsRepository(session)

    def list_basins(self) -> list[dict[str, Any]]:
        """Return basin lookup rows."""

        return _to_dicts(self.basins.list_basins())

    def list_regions(self) -> list[dict[str, Any]]:
        """Return region lookup rows."""

        return _to_dicts(self.regions.list_regions())

    def list_sources(self) -> list[dict[str, Any]]:
        """Return source/provenance lookup rows."""

        return _to_dicts(self.sources.list_sources())

    def list_available_water_quality_stations(self) -> list[dict[str, Any]]:
        """Return regions marked as water-quality stations."""

        return _to_dicts(self.regions.list_wq_stations())

    def list_standards_use_cases(self) -> list[str]:
        """Return standards use cases exactly as stored in the database."""

        return self.standards.list_use_cases()

    def get_lookup_data(self) -> dict[str, Any]:
        """Return a grouped lookup packet for future dropdowns."""

        return {
            "basins": self.list_basins(),
            "regions": self.list_regions(),
            "sources": self.list_sources(),
            "water_quality_stations": self.list_available_water_quality_stations(),
            "standards_use_cases": self.list_standards_use_cases(),
        }

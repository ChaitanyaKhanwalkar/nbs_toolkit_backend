"""Service for raw site profile packets.

This service combines region, basin, site attribute, and stream attribute data
where available. It does not score suitability or hydrological risk.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import BasinRepository, SiteRepository


def _to_dict(row: Base | None) -> dict[str, Any] | None:
    """Convert one ORM row to a plain dictionary."""

    if row is None:
        return None
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _to_dicts(rows: list[Base]) -> list[dict[str, Any]]:
    """Convert ORM rows to dictionaries."""

    return [_to_dict(row) for row in rows if row is not None]


class SiteProfileService:
    """Prepare raw site profile data from repository results."""

    def __init__(self, session: Session) -> None:
        self.sites = SiteRepository(session)
        self.basins = BasinRepository(session)

    def get_site_profile(self, region_id: int) -> dict[str, Any]:
        """Return raw site profile pieces for a region ID."""

        profile = self.sites.get_full_site_profile(region_id)
        region = profile["region"]
        basin = None
        if region is not None and region.basin_id is not None:
            basin = self.basins.get_by_id(region.basin_id)

        missing_sections = []
        if region is None:
            missing_sections.append("region")
        if profile["site_attributes"] is None:
            missing_sections.append("site_attributes")
        if not profile["stream_attributes"]:
            missing_sections.append("site_stream_attributes")
        if basin is None:
            missing_sections.append("basin")

        return {
            "region": _to_dict(region),
            "basin": _to_dict(basin),
            "site_attributes": _to_dict(profile["site_attributes"]),
            "site_stream_attributes": _to_dicts(profile["stream_attributes"]),
            "missing_sections": missing_sections,
        }

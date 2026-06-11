"""Read-only repository for the `regions` table.

Use this repository to find Narmada station/catchment records. Searches are
simple database lookups, not fuzzy matching or recommendation logic.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Region
from app.repositories.base_repository import BaseRepository


class RegionRepository(BaseRepository):
    """Read helpers for region and station records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_regions(self) -> list[Region]:
        """Return all regions ordered by ID."""

        return self.list_all(Region, order_by=Region.id)

    def get_by_id(self, region_id: int) -> Region | None:
        """Return one region by ID, or `None` when it is missing."""

        return super().get_by_id(Region, region_id)

    def get_by_station(self, station: str) -> Region | None:
        """Return the first region with a matching station name."""

        if not station:
            return None
        statement = select(Region).where(func.lower(Region.station) == station.lower())
        return self.session.scalars(statement).first()

    def search_by_district(self, district: str) -> list[Region]:
        """Return regions whose district contains the supplied text."""

        if not district:
            return []
        statement = (
            select(Region)
            .where(Region.district.ilike(f"%{district}%"))
            .order_by(Region.district, Region.station)
        )
        return list(self.session.scalars(statement).all())

    def list_wq_stations(self) -> list[Region]:
        """Return regions marked as water-quality stations."""

        statement = (
            select(Region)
            .where(Region.is_wq_station == 1)
            .order_by(Region.station)
        )
        return list(self.session.scalars(statement).all())

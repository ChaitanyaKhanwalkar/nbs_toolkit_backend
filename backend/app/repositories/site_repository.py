"""Read-only repository for site profile tables.

This repository combines raw region, site attribute, and stream attribute rows
for callers that need site context. It does not score site suitability.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Region, SiteAttribute, SiteStreamAttribute
from app.repositories.base_repository import BaseRepository


class SiteRepository(BaseRepository):
    """Read helpers for site profile records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_site_attributes(self, region_id: int) -> SiteAttribute | None:
        """Return site attributes for a region, or `None` when missing."""

        statement = select(SiteAttribute).where(SiteAttribute.region_id == region_id)
        return self.session.scalars(statement).first()

    def get_site_stream_attributes(
        self,
        *,
        region_id: int | None = None,
        station: str | None = None,
        gauge_id: int | None = None,
    ) -> list[SiteStreamAttribute]:
        """Return stream attributes using region, station, or gauge ID filters."""

        filters = []
        if region_id is not None:
            filters.append(SiteStreamAttribute.region_id == region_id)
        if station:
            filters.append(SiteStreamAttribute.station == station)
        if gauge_id is not None:
            filters.append(SiteStreamAttribute.gauge_id == gauge_id)
        if not filters:
            return []
        statement = select(SiteStreamAttribute).where(*filters).order_by(SiteStreamAttribute.id)
        return list(self.session.scalars(statement).all())

    def get_full_site_profile(self, region_id: int) -> dict[str, object | None]:
        """Return raw site profile pieces for one region."""

        region = self.get_by_id(Region, region_id)
        site_attributes = self.get_site_attributes(region_id)
        stream_attributes = self.get_site_stream_attributes(region_id=region_id)
        return {
            "region": region,
            "site_attributes": site_attributes,
            "stream_attributes": stream_attributes,
        }

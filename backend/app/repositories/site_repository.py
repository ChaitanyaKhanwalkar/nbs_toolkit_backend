"""Read-only repository for site profile tables.

This repository combines raw region, site attribute, and stream attribute rows
for callers that need site context. It does not score site suitability.
"""

from typing import Any

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

    def list_site_options(self) -> list[dict[str, Any]]:
        """Return compact canonical station options for frontend selectors."""

        return self.fetch_mappings(
            """
            SELECT
                region_id,
                gauge_id,
                station,
                stream_order_strahler,
                nat_discharge_cms,
                drainage_area_km2
            FROM site_attributes
            WHERE station IS NOT NULL
            ORDER BY station
            """
        )

    def get_site_stream_attributes(
        self,
        *,
        region_id: int | None = None,
        station: str | None = None,
        gauge_id: int | None = None,
    ) -> list[SiteStreamAttribute] | list[dict[str, Any]]:
        """Return stream attributes using region, station, or gauge ID filters."""

        if not self.relation_exists("site_stream_attributes"):
            filters = []
            params: dict[str, Any] = {}
            if region_id is not None:
                filters.append("region_id = :region_id")
                params["region_id"] = region_id
            if station:
                filters.append("station = :station")
                params["station"] = station
            if gauge_id is not None:
                filters.append("gauge_id = :gauge_id")
                params["gauge_id"] = gauge_id
            if not filters:
                return []
            where_clause = " AND ".join(filters)
            return self.fetch_mappings(
                f"""
                SELECT
                    id,
                    region_id,
                    gauge_id,
                    station,
                    NULL AS ghi_stn_id,
                    NULL AS cwc_river,
                    stream_order,
                    stream_order_strahler AS ord_clas,
                    NULL AS ord_flow,
                    nat_discharge_cms AS river_discharge_cms,
                    NULL AS upland_skm,
                    drainage_area_km2 AS catch_skm,
                    NULL AS nearest_distance_deg,
                    NULL AS nearest_distance_m,
                    NULL AS station_lon,
                    NULL AS station_lat,
                    NULL AS nearest_lon,
                    NULL AS nearest_lat,
                    nearest_hyriv_id AS hybas_l12,
                    source_id
                FROM site_attributes
                WHERE {where_clause}
                ORDER BY id
                """,
                params,
            )

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

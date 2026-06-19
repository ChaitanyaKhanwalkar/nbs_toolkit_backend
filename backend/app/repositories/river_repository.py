"""Read-only repository for river network and station-stream tables.

Use this repository to fetch raw river segment and station-stream attributes.
It does not calculate hydrological suitability or recommendation scores.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RiverNetwork, SiteStreamAttribute
from app.repositories.base_repository import BaseRepository


class RiverRepository(BaseRepository):
    """Read helpers for river network records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_river_segments(self, limit: int | None = None) -> list[RiverNetwork]:
        """Return river network segments with an optional limit."""

        return self.list_all(RiverNetwork, order_by=RiverNetwork.id, limit=limit)

    def get_segments_by_stream_order(self, stream_order: int) -> list[RiverNetwork]:
        """Return river segments by Strahler stream order."""

        statement = (
            select(RiverNetwork)
            .where(RiverNetwork.ord_stra == stream_order)
            .order_by(RiverNetwork.id)
        )
        return list(self.session.scalars(statement).all())

    def get_segments_near_hybas(self, hybas_l12: int) -> list[RiverNetwork]:
        """Return river segments connected to a HYBAS level-12 value."""

        statement = (
            select(RiverNetwork)
            .where(RiverNetwork.hybas_l12 == hybas_l12)
            .order_by(RiverNetwork.id)
        )
        return list(self.session.scalars(statement).all())

    def get_station_stream_attributes(
        self,
        *,
        station: str | None = None,
        region_id: int | None = None,
    ) -> list[SiteStreamAttribute] | list[dict[str, Any]]:
        """Return station-stream attributes by station or region."""

        if not self.relation_exists("site_stream_attributes"):
            filters = []
            params: dict[str, Any] = {}
            if station:
                filters.append("station = :station")
                params["station"] = station
            if region_id is not None:
                filters.append("region_id = :region_id")
                params["region_id"] = region_id
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
        if station:
            filters.append(SiteStreamAttribute.station == station)
        if region_id is not None:
            filters.append(SiteStreamAttribute.region_id == region_id)
        if not filters:
            return []
        statement = (
            select(SiteStreamAttribute)
            .where(*filters)
            .order_by(SiteStreamAttribute.id)
        )
        return list(self.session.scalars(statement).all())

"""Service for raw river network context data.

This service returns stream attributes and river network segments. It does not
make hydrological risk or suitability scores.
"""

from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import RiverRepository


def _to_dict(row: Base | None) -> dict[str, Any] | None:
    """Convert one ORM row to a plain dictionary."""

    if row is None:
        return None
    if isinstance(row, Mapping):
        return dict(row)
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _to_dicts(rows: list[Base]) -> list[dict[str, Any]]:
    """Convert ORM rows to dictionaries."""

    return [_to_dict(row) for row in rows if row is not None]


class RiverContextService:
    """Prepare raw river context packets from repository results."""

    def __init__(self, session: Session) -> None:
        self.rivers = RiverRepository(session)

    def get_stream_attributes(
        self,
        *,
        station: str | None = None,
        region_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return station-stream attributes where available."""

        return _to_dicts(
            self.rivers.get_station_stream_attributes(
                station=station,
                region_id=region_id,
            )
        )

    def list_river_segments_by_stream_order(self, stream_order: int) -> list[dict[str, Any]]:
        """Return river segments by stored stream order."""

        return _to_dicts(self.rivers.get_segments_by_stream_order(stream_order))

    def get_river_network_context(
        self,
        *,
        stream_order: int | None = None,
        hybas_l12: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Return raw river network rows using simple filters."""

        if stream_order is not None:
            rows = self.rivers.get_segments_by_stream_order(stream_order)
        elif hybas_l12 is not None:
            rows = self.rivers.get_segments_near_hybas(hybas_l12)
        else:
            rows = self.rivers.list_river_segments(limit=limit)
        return {
            "river_segments": _to_dicts(rows),
            "count": len(rows),
        }

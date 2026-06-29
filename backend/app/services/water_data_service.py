"""Service for raw measured water-quality data.

This service fetches and groups observation records. It does not compare values
against standards and does not calculate pollutant exceedance.
"""

from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import WaterRepository


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


class WaterDataService:
    """Prepare raw water observation packets from repository results."""

    def __init__(self, session: Session) -> None:
        self.water = WaterRepository(session)

    def get_observations_by_station(self, station: str) -> list[dict[str, Any]]:
        """Return raw observations for one station."""

        return _to_dicts(self.water.get_observations_by_station(station))

    def get_observations_by_basin(self, basin_id: int) -> list[dict[str, Any]]:
        """Return raw observations for one basin ID."""

        return _to_dicts(self.water.get_observations_by_basin(basin_id))

    def get_observations_for_parameters(
        self,
        station: str,
        parameters: list[str],
    ) -> dict[str, list[dict[str, Any]]]:
        """Return raw station observations grouped by requested parameters."""

        if not parameters:
            return {}
        return {
            parameter: _to_dicts(self.water.get_parameter_values(station, parameter))
            for parameter in parameters
        }

    def get_water_type_profile(self, water_type: str) -> list[dict[str, Any]]:
        """Return active fallback profile rows for one exact water type."""

        return _to_dicts(self.water.get_water_type_profile(water_type))

    def summarize_available_parameters(self) -> list[dict[str, Any]]:
        """Return parameter names and raw row counts only."""

        return self.water.list_parameter_counts()

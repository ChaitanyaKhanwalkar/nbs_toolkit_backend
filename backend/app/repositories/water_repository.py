"""Read-only repository for measured water-quality data.

Use this repository to fetch raw observations and parameter names. It does not
calculate exceedances or compare observations against standards.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import WaterObservation
from app.repositories.base_repository import BaseRepository


class WaterRepository(BaseRepository):
    """Read helpers for water observation records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_observations_by_station(
        self,
        station: str,
    ) -> list[WaterObservation] | list[dict[str, Any]]:
        """Return observations for a station name."""

        if not station:
            return []
        if self.relation_has_columns("water_observations", {"parameter_id", "unit_id"}):
            return self.fetch_mappings(
                """
                SELECT
                    w.id,
                    w.station,
                    w.district,
                    w.state,
                    w.cwc_code,
                    p.name AS parameter,
                    u.name AS unit,
                    w.value_mean,
                    w.value_min,
                    w.value_max,
                    w.n_samples,
                    w.period,
                    w.basin_id,
                    w.source_id
                FROM water_observations AS w
                LEFT JOIN dim_parameter AS p ON p.id = w.parameter_id
                LEFT JOIN dim_unit AS u ON u.id = w.unit_id
                WHERE w.station = :station
                ORDER BY p.name, w.id
                """,
                {"station": station},
            )
        statement = (
            select(WaterObservation)
            .where(WaterObservation.station == station)
            .order_by(WaterObservation.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_observations_by_basin(
        self,
        basin_id: int,
    ) -> list[WaterObservation] | list[dict[str, Any]]:
        """Return observations linked to a basin ID."""

        if self.relation_has_columns("water_observations", {"parameter_id", "unit_id"}):
            return self.fetch_mappings(
                """
                SELECT
                    w.id,
                    w.station,
                    w.district,
                    w.state,
                    w.cwc_code,
                    p.name AS parameter,
                    u.name AS unit,
                    w.value_mean,
                    w.value_min,
                    w.value_max,
                    w.n_samples,
                    w.period,
                    w.basin_id,
                    w.source_id
                FROM water_observations AS w
                LEFT JOIN dim_parameter AS p ON p.id = w.parameter_id
                LEFT JOIN dim_unit AS u ON u.id = w.unit_id
                WHERE w.basin_id = :basin_id
                ORDER BY w.station, p.name, w.id
                """,
                {"basin_id": basin_id},
            )
        statement = (
            select(WaterObservation)
            .where(WaterObservation.basin_id == basin_id)
            .order_by(WaterObservation.station, WaterObservation.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_parameter_values(
        self,
        station: str,
        parameter: str,
    ) -> list[WaterObservation] | list[dict[str, Any]]:
        """Return raw observation rows for a station and parameter."""

        if not station or not parameter:
            return []
        if self.relation_has_columns("water_observations", {"parameter_id", "unit_id"}):
            return self.fetch_mappings(
                """
                SELECT
                    w.id,
                    w.station,
                    w.district,
                    w.state,
                    w.cwc_code,
                    p.name AS parameter,
                    u.name AS unit,
                    w.value_mean,
                    w.value_min,
                    w.value_max,
                    w.n_samples,
                    w.period,
                    w.basin_id,
                    w.source_id
                FROM water_observations AS w
                LEFT JOIN dim_parameter AS p ON p.id = w.parameter_id
                LEFT JOIN dim_unit AS u ON u.id = w.unit_id
                WHERE w.station = :station
                  AND p.name = :parameter
                ORDER BY w.id
                """,
                {"station": station, "parameter": parameter},
            )
        statement = (
            select(WaterObservation)
            .where(
                WaterObservation.station == station,
                WaterObservation.parameter == parameter,
            )
            .order_by(WaterObservation.id)
        )
        return list(self.session.scalars(statement).all())

    def list_available_parameters(self) -> list[str]:
        """Return distinct water-quality parameter names."""

        if self.relation_has_columns("water_observations", {"parameter_id"}):
            rows = self.fetch_mappings(
                """
                SELECT DISTINCT p.name AS parameter
                FROM water_observations AS w
                JOIN dim_parameter AS p ON p.id = w.parameter_id
                WHERE p.name IS NOT NULL
                ORDER BY p.name
                """
            )
            return [str(row["parameter"]) for row in rows if row.get("parameter")]

        statement = (
            select(WaterObservation.parameter)
            .where(WaterObservation.parameter.is_not(None))
            .distinct()
            .order_by(WaterObservation.parameter)
        )
        return list(self.session.scalars(statement).all())

    def list_parameter_counts(self) -> list[dict[str, int | str]]:
        """Return distinct parameter names with raw observation counts."""

        if self.relation_has_columns("water_observations", {"parameter_id"}):
            return self.fetch_mappings(
                """
                SELECT p.name AS parameter, COUNT(w.id) AS count
                FROM water_observations AS w
                JOIN dim_parameter AS p ON p.id = w.parameter_id
                WHERE p.name IS NOT NULL
                GROUP BY p.name
                ORDER BY p.name
                """
            )

        statement = (
            select(WaterObservation.parameter, func.count(WaterObservation.id))
            .where(WaterObservation.parameter.is_not(None))
            .group_by(WaterObservation.parameter)
            .order_by(WaterObservation.parameter)
        )
        return [
            {"parameter": parameter, "count": count}
            for parameter, count in self.session.execute(statement).all()
        ]

"""Read-only repository for measured water-quality data.

Use this repository to fetch raw observations and parameter names. It does not
calculate exceedances or compare observations against standards.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import WaterObservation
from app.repositories.base_repository import BaseRepository


class WaterRepository(BaseRepository):
    """Read helpers for water observation records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_observations_by_station(self, station: str) -> list[WaterObservation]:
        """Return observations for a station name."""

        if not station:
            return []
        statement = (
            select(WaterObservation)
            .where(WaterObservation.station == station)
            .order_by(WaterObservation.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_observations_by_basin(self, basin_id: int) -> list[WaterObservation]:
        """Return observations linked to a basin ID."""

        statement = (
            select(WaterObservation)
            .where(WaterObservation.basin_id == basin_id)
            .order_by(WaterObservation.station, WaterObservation.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_parameter_values(self, station: str, parameter: str) -> list[WaterObservation]:
        """Return raw observation rows for a station and parameter."""

        if not station or not parameter:
            return []
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

        statement = (
            select(WaterObservation.parameter)
            .where(WaterObservation.parameter.is_not(None))
            .distinct()
            .order_by(WaterObservation.parameter)
        )
        return list(self.session.scalars(statement).all())

"""Service for raw plant catalogue data.

This service returns stored plant rows and plant-to-NbS mappings. It does not
assign final plant recommendations.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import PlantRepository


def _to_dict(row: Base | None) -> dict[str, Any] | None:
    """Convert one ORM row to a plain dictionary."""

    if row is None:
        return None
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _to_dicts(rows: list[Base]) -> list[dict[str, Any]]:
    """Convert ORM rows to dictionaries."""

    return [_to_dict(row) for row in rows if row is not None]


class PlantCatalogService:
    """Prepare raw plant catalogue packets from repository results."""

    def __init__(self, session: Session) -> None:
        self.plants = PlantRepository(session)

    def list_plants(self) -> list[dict[str, Any]]:
        """Return all plant records as stored."""

        return _to_dicts(self.plants.list_plants())

    def get_plant_profile(self, plant_id: int) -> dict[str, Any] | None:
        """Return one plant profile by ID."""

        return _to_dict(self.plants.get_plant_by_id(plant_id))

    def get_plants_for_nbs(
        self,
        nbs_id: int,
        *,
        include_invasive: bool = False,
    ) -> list[dict[str, Any]]:
        """Return plants mapped to an NbS option.

        Invasive plants are excluded by default if the repository supports that
        filter.
        """

        return _to_dicts(
            self.plants.get_plants_for_nbs(
                nbs_id,
                include_invasive=include_invasive,
            )
        )

"""Read-only repository for plant tables.

Use this repository to fetch raw plant catalogue rows and plant-to-NbS mappings.
It excludes invasive plants by default for recommendation-support queries, but
does not select or rank plants.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Plant, PlantSolutionMap
from app.repositories.base_repository import BaseRepository


class PlantRepository(BaseRepository):
    """Read helpers for plants and plant-solution mappings."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_plants(self) -> list[Plant]:
        """Return all plant records ordered by species name."""

        return self.list_all(Plant, order_by=Plant.plant_species)

    def get_plant_by_id(self, plant_id: int) -> Plant | None:
        """Return one plant by ID, or `None` when missing."""

        return self.get_by_id(Plant, plant_id)

    def get_plants_for_nbs(
        self,
        nbs_id: int,
        *,
        include_invasive: bool = False,
    ) -> list[Plant]:
        """Return plants mapped to one NbS option.

        Invasive plants are excluded by default because this method will later
        support recommendation workflows. This is a raw filter, not scoring.
        """

        statement = (
            select(Plant)
            .join(PlantSolutionMap, PlantSolutionMap.plant_id == Plant.id)
            .where(PlantSolutionMap.nbs_id == nbs_id)
        )
        if not include_invasive:
            statement = statement.where((Plant.invasive == 0) | (Plant.invasive.is_(None)))
        statement = statement.order_by(Plant.plant_species)
        return list(self.session.scalars(statement).all())

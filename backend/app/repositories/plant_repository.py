"""Read-only repository for plant tables.

Use this repository to fetch raw plant catalogue rows and plant-to-NbS mappings.
It excludes invasive plants by default for recommendation-support queries, but
does not select or rank plants.
"""

from sqlalchemy import func, select
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

    def count_plant_mappings(self, nbs_id: int | None = None) -> int:
        """Return a raw count of plant-solution mapping rows."""

        statement = select(func.count(PlantSolutionMap.id))
        if nbs_id is not None:
            statement = statement.where(PlantSolutionMap.nbs_id == nbs_id)
        return int(self.session.scalar(statement) or 0)

    def list_catalogue_mappings(self) -> list[dict[str, object]]:
        """Return plant records joined to every explicit NbS mapping."""

        return self.fetch_mappings(
            """
            SELECT
                p.id,
                p.plant_species,
                p.locational_availability,
                p.climate_preference,
                p.soil_type,
                p.water_needs,
                p.ecological_role,
                p.plant_type,
                p.native_status,
                p.invasive,
                p.metals_pollutants,
                p.evidence_note,
                p.pollution_tolerance,
                p.optimal_water_type,
                p.source_id AS plant_source_id,
                pm.nbs_id,
                n.solution AS nbs_name,
                pm.basis,
                pm.source_id AS mapping_source_id
            FROM plants AS p
            LEFT JOIN plant_solution_map AS pm ON pm.plant_id = p.id
            LEFT JOIN nbs_options AS n ON n.id = pm.nbs_id
            ORDER BY p.plant_species, pm.nbs_id
            """
        )

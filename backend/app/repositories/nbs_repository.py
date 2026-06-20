"""Read-only repository for nature-based solution tables.

Use this repository to fetch raw NbS options, implementation guidance, removal
efficiency evidence, footprints, and criteria. It does not score or rank them.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    NbsCriteria,
    NbsFootprint,
    NbsImplementation,
    NbsOption,
    RemovalEfficiency,
)
from app.repositories.base_repository import BaseRepository


class NbsRepository(BaseRepository):
    """Read helpers for NbS catalogue and supporting evidence tables."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_options(self) -> list[NbsOption]:
        """Return all NbS options ordered by ID."""

        if self.relation_has_columns("nbs_options", {"family_id", "energy_class"}):
            return self.fetch_mappings(
                """
                SELECT
                    n.id,
                    n.solution,
                    f.name AS family,
                    n.description,
                    n.optimal_water_type,
                    n.location_suitability,
                    n.climate_suitability,
                    n.soil_type,
                    n.resource_requirements,
                    n.notes,
                    n.source_id,
                    n.energy_class
                FROM nbs_options AS n
                LEFT JOIN dim_nbs_family AS f ON f.id = n.family_id
                ORDER BY n.id
                """
            )

        return self.list_all(NbsOption, order_by=NbsOption.id)

    def get_option_by_id(self, nbs_id: int) -> NbsOption | dict[str, Any] | None:
        """Return one NbS option by ID, or `None` when missing."""

        if self.relation_has_columns("nbs_options", {"family_id", "energy_class"}):
            rows = self.fetch_mappings(
                """
                SELECT
                    n.id,
                    n.solution,
                    f.name AS family,
                    n.description,
                    n.optimal_water_type,
                    n.location_suitability,
                    n.climate_suitability,
                    n.soil_type,
                    n.resource_requirements,
                    n.notes,
                    n.source_id,
                    n.energy_class
                FROM nbs_options AS n
                LEFT JOIN dim_nbs_family AS f ON f.id = n.family_id
                WHERE n.id = :nbs_id
                """,
                {"nbs_id": nbs_id},
            )
            return rows[0] if rows else None

        return self.get_by_id(NbsOption, nbs_id)

    def get_removal_efficiencies(
        self,
        nbs_id: int,
    ) -> list[RemovalEfficiency] | list[dict[str, Any]]:
        """Return raw removal efficiency rows for one NbS option."""

        if self.relation_has_columns("removal_efficiency", {"parameter_id", "confidence_id"}):
            return self.fetch_mappings(
                """
                SELECT
                    r.id,
                    n.solution AS nbs,
                    r.nbs_id,
                    p.name AS parameter,
                    r.eff_low,
                    r.eff_high,
                    c.name AS confidence,
                    r.source_id,
                    r.note,
                    s.name AS scale,
                    co.name AS country,
                    r.influent_context,
                    r.hrt_loading,
                    r.temp_climate,
                    r.needs_corroboration
                FROM removal_efficiency AS r
                LEFT JOIN nbs_options AS n ON n.id = r.nbs_id
                LEFT JOIN dim_parameter AS p ON p.id = r.parameter_id
                LEFT JOIN dim_confidence AS c ON c.id = r.confidence_id
                LEFT JOIN dim_scale AS s ON s.id = r.scale_id
                LEFT JOIN dim_country AS co ON co.id = r.country_id
                WHERE r.nbs_id = :nbs_id
                ORDER BY p.name, r.id
                """,
                {"nbs_id": nbs_id},
            )

        statement = (
            select(RemovalEfficiency)
            .where(RemovalEfficiency.nbs_id == nbs_id)
            .order_by(RemovalEfficiency.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_implementation(
        self,
        nbs_id: int,
    ) -> list[NbsImplementation] | list[dict[str, Any]]:
        """Return implementation guidance rows for one NbS option."""

        if not self.relation_has_columns("nbs_implementation", {"solution"}):
            return self.fetch_mappings(
                """
                SELECT
                    i.id,
                    i.nbs_id,
                    n.solution,
                    i.implementation_steps,
                    i.maintenance_requirements,
                    i.source_id
                FROM nbs_implementation AS i
                LEFT JOIN nbs_options AS n ON n.id = i.nbs_id
                WHERE i.nbs_id = :nbs_id
                ORDER BY i.id
                """,
                {"nbs_id": nbs_id},
            )

        statement = (
            select(NbsImplementation)
            .where(NbsImplementation.nbs_id == nbs_id)
            .order_by(NbsImplementation.id)
        )
        return list(self.session.scalars(statement).all())

    def get_footprint(self, nbs_id: int) -> list[NbsFootprint]:
        """Return footprint/loading rows for one NbS option."""

        statement = (
            select(NbsFootprint)
            .where(NbsFootprint.nbs_id == nbs_id)
            .order_by(NbsFootprint.id)
        )
        return list(self.session.scalars(statement).all())

    def get_criteria(self, nbs_id: int) -> list[NbsCriteria] | list[dict[str, Any]]:
        """Return qualitative criteria rows for one NbS option.

        Canonical data dropped the old `nbs_criteria` table. For compatibility
        with the current MCDA matrix builder, practitioner O&M information from
        `nbs_design` is exposed as criteria-like rows.
        """

        if self.relation_exists("nbs_design"):
            return self.fetch_mappings(
                """
                SELECT
                    d.id,
                    d.nbs_id,
                    'om_level' AS criterion,
                    d.skill_om_intensity AS value_qual,
                    NULL AS confidence,
                    NULL AS source_id,
                    d.source_ids,
                    d.pretreatment,
                    d.media_substrate,
                    d.hydraulic_config,
                    d.planting,
                    d.construction_notes,
                    d.startup_establishment,
                    d.om_routine,
                    d.om_periodic,
                    d.monitoring,
                    d.failure_modes,
                    d.climate_dependence
                FROM nbs_design AS d
                WHERE d.nbs_id = :nbs_id
                ORDER BY d.id
                """,
                {"nbs_id": nbs_id},
            )

        statement = (
            select(NbsCriteria)
            .where(NbsCriteria.nbs_id == nbs_id)
            .order_by(NbsCriteria.criterion)
        )
        return list(self.session.scalars(statement).all())

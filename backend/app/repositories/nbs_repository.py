"""Read-only repository for nature-based solution tables.

Use this repository to fetch raw NbS options, implementation guidance, removal
efficiency evidence, footprints, and criteria. It does not score or rank them.
"""

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

        return self.list_all(NbsOption, order_by=NbsOption.id)

    def get_option_by_id(self, nbs_id: int) -> NbsOption | None:
        """Return one NbS option by ID, or `None` when missing."""

        return self.get_by_id(NbsOption, nbs_id)

    def get_removal_efficiencies(self, nbs_id: int) -> list[RemovalEfficiency]:
        """Return raw removal efficiency rows for one NbS option."""

        statement = (
            select(RemovalEfficiency)
            .where(RemovalEfficiency.nbs_id == nbs_id)
            .order_by(RemovalEfficiency.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_implementation(self, nbs_id: int) -> list[NbsImplementation]:
        """Return implementation guidance rows for one NbS option."""

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

    def get_criteria(self, nbs_id: int) -> list[NbsCriteria]:
        """Return qualitative criteria rows for one NbS option."""

        statement = (
            select(NbsCriteria)
            .where(NbsCriteria.nbs_id == nbs_id)
            .order_by(NbsCriteria.criterion)
        )
        return list(self.session.scalars(statement).all())

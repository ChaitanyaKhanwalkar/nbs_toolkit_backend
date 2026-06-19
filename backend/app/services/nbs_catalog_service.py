"""Service for raw nature-based solution catalogue data.

This service combines stored NbS option, removal-efficiency, implementation,
footprint, and criteria rows. It does not rank or filter candidates.
"""

from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import NbsRepository


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


class NbsCatalogService:
    """Prepare raw NbS catalogue packets from repository results."""

    def __init__(self, session: Session) -> None:
        self.nbs = NbsRepository(session)

    def list_options(self) -> list[dict[str, Any]]:
        """Return all NbS options as stored."""

        return _to_dicts(self.nbs.list_options())

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return raw catalogue and evidence rows for one NbS option."""

        option = self.nbs.get_option_by_id(nbs_id)
        removal_efficiencies = self.nbs.get_removal_efficiencies(nbs_id)
        implementation = self.nbs.get_implementation(nbs_id)
        footprint = self.nbs.get_footprint(nbs_id)
        criteria = self.nbs.get_criteria(nbs_id)

        missing_sections = []
        if option is None:
            missing_sections.append("option")
        if not removal_efficiencies:
            missing_sections.append("removal_efficiency")
        if not implementation:
            missing_sections.append("implementation")
        if not footprint:
            missing_sections.append("footprint")
        if not criteria:
            missing_sections.append("criteria")

        return {
            "option": _to_dict(option),
            "removal_efficiencies": _to_dicts(removal_efficiencies),
            "implementation": _to_dicts(implementation),
            "footprint": _to_dicts(footprint),
            "criteria": _to_dicts(criteria),
            "missing_sections": missing_sections,
        }

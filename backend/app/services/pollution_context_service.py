"""Service for raw pollution context data.

This service returns pollution source rows and simple grouped context from the
repository. It does not create pollution pressure scores.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import PollutionRepository


def _to_dict(row: Base | None) -> dict[str, Any] | None:
    """Convert one ORM row to a plain dictionary."""

    if row is None:
        return None
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _to_dicts(rows: list[Base]) -> list[dict[str, Any]]:
    """Convert ORM rows to dictionaries."""

    return [_to_dict(row) for row in rows if row is not None]


class PollutionContextService:
    """Prepare raw pollution context packets from repository results."""

    def __init__(self, session: Session) -> None:
        self.pollution = PollutionRepository(session)

    def get_pollution_sources(self, region_id: int) -> list[dict[str, Any]]:
        """Return raw pollution source records for a region."""

        return _to_dicts(self.pollution.get_pollution_sources(region_id))

    def get_grouped_pollution_context(self, region_id: int) -> list[dict[str, object]]:
        """Return simple grouped context already supported by the repository."""

        return self.pollution.summarize_pollution_pressure(region_id)

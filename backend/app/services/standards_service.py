"""Service for raw standards lookup data.

This service returns stored standards for explicit use cases and parameters. It
does not decide a default use case and does not compare observations to limits.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import StandardsRepository


def _to_dict(row: Base | None) -> dict[str, Any] | None:
    """Convert one ORM row to a plain dictionary."""

    if row is None:
        return None
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _to_dicts(rows: list[Base]) -> list[dict[str, Any]]:
    """Convert ORM rows to dictionaries."""

    return [_to_dict(row) for row in rows if row is not None]


class StandardsService:
    """Prepare raw standards data from repository results."""

    def __init__(self, session: Session) -> None:
        self.standards = StandardsRepository(session)

    def list_use_cases(self) -> list[str]:
        """Return use cases exactly as stored."""

        return self.standards.list_use_cases()

    def get_standards_for_use_case(self, use_case: str) -> list[dict[str, Any]]:
        """Return standards rows for an explicit use case."""

        return _to_dicts(self.standards.get_standards_for_use_case(use_case))

    def get_standard(self, use_case: str, parameter: str) -> dict[str, Any] | None:
        """Return one standard row for an explicit use case and parameter."""

        return _to_dict(self.standards.get_standard(use_case, parameter))

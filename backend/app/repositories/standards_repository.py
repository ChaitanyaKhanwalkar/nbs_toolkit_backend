"""Read-only repository for water-quality standards.

Use this repository to fetch raw standards by use case and parameter. It does
not calculate exceedances or treatment needs.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Standard
from app.repositories.base_repository import BaseRepository


class StandardsRepository(BaseRepository):
    """Read helpers for standard threshold rows."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_use_cases(self) -> list[str]:
        """Return distinct use-case names from the standards table."""

        statement = (
            select(Standard.use_case)
            .where(Standard.use_case.is_not(None))
            .distinct()
            .order_by(Standard.use_case)
        )
        return list(self.session.scalars(statement).all())

    def get_standards_for_use_case(self, use_case: str) -> list[Standard]:
        """Return all standards for one use case."""

        if not use_case:
            return []
        statement = (
            select(Standard)
            .where(Standard.use_case == use_case)
            .order_by(Standard.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_standard(self, use_case: str, parameter: str) -> Standard | None:
        """Return one standard for a use case and parameter."""

        if not use_case or not parameter:
            return None
        statement = select(Standard).where(
            Standard.use_case == use_case,
            Standard.parameter == parameter,
        )
        return self.session.scalars(statement).first()

"""Read-only repository for water-quality standards.

Use this repository to fetch raw standards by use case and parameter. It does
not calculate exceedances or treatment needs.
"""

from typing import Any

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

        if self.relation_has_columns("standards", {"use_case_id", "parameter_id"}):
            rows = self.fetch_mappings(
                """
                SELECT DISTINCT u.name AS use_case
                FROM standards AS s
                JOIN dim_use_case AS u ON u.id = s.use_case_id
                WHERE u.name IS NOT NULL
                ORDER BY u.name
                """
            )
            return [str(row["use_case"]) for row in rows if row.get("use_case")]

        statement = (
            select(Standard.use_case)
            .where(Standard.use_case.is_not(None))
            .distinct()
            .order_by(Standard.use_case)
        )
        return list(self.session.scalars(statement).all())

    def get_standards_for_use_case(
        self,
        use_case: str,
    ) -> list[Standard] | list[dict[str, Any]]:
        """Return all standards for one use case."""

        if not use_case:
            return []
        if self.relation_has_columns("standards", {"use_case_id", "parameter_id"}):
            return self.fetch_mappings(
                """
                SELECT
                    s.id,
                    u.name AS use_case,
                    p.name AS parameter,
                    s.limit_low,
                    s.limit_high,
                    s.direction,
                    un.name AS unit,
                    s.source_id,
                    s.note
                FROM standards AS s
                JOIN dim_use_case AS u ON u.id = s.use_case_id
                JOIN dim_parameter AS p ON p.id = s.parameter_id
                LEFT JOIN dim_unit AS un ON un.id = s.unit_id
                WHERE u.name = :use_case
                ORDER BY p.name
                """,
                {"use_case": use_case},
            )
        statement = (
            select(Standard)
            .where(Standard.use_case == use_case)
            .order_by(Standard.parameter)
        )
        return list(self.session.scalars(statement).all())

    def get_standard(self, use_case: str, parameter: str) -> Standard | dict[str, Any] | None:
        """Return one standard for a use case and parameter."""

        if not use_case or not parameter:
            return None
        if self.relation_has_columns("standards", {"use_case_id", "parameter_id"}):
            rows = self.fetch_mappings(
                """
                SELECT
                    s.id,
                    u.name AS use_case,
                    p.name AS parameter,
                    s.limit_low,
                    s.limit_high,
                    s.direction,
                    un.name AS unit,
                    s.source_id,
                    s.note
                FROM standards AS s
                JOIN dim_use_case AS u ON u.id = s.use_case_id
                JOIN dim_parameter AS p ON p.id = s.parameter_id
                LEFT JOIN dim_unit AS un ON un.id = s.unit_id
                WHERE u.name = :use_case
                  AND p.name = :parameter
                LIMIT 1
                """,
                {"use_case": use_case, "parameter": parameter},
            )
            return rows[0] if rows else None
        statement = select(Standard).where(
            Standard.use_case == use_case,
            Standard.parameter == parameter,
        )
        return self.session.scalars(statement).first()

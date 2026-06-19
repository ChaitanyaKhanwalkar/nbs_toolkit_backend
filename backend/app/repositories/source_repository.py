"""Read-only repository for the `sources` table.

Use this repository whenever code needs citations or provenance records. It
does not create, update, or delete source data.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Source
from app.repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository):
    """Read helpers for source/provenance records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, source_id: int) -> Source | dict[str, Any] | None:
        """Return one source by ID, or `None` when it is missing."""

        if self.relation_has_columns("sources", {"source_type_id"}):
            rows = self.fetch_mappings(
                """
                SELECT
                    s.id,
                    s.short,
                    s.citation,
                    t.name AS type,
                    s.url,
                    s.license
                FROM sources AS s
                LEFT JOIN dim_source_type AS t ON t.id = s.source_type_id
                WHERE s.id = :source_id
                """,
                {"source_id": source_id},
            )
            return rows[0] if rows else None

        return super().get_by_id(Source, source_id)

    def list_sources(self) -> list[Source] | list[dict[str, Any]]:
        """Return all source records ordered by ID."""

        if self.relation_has_columns("sources", {"source_type_id"}):
            return self.fetch_mappings(
                """
                SELECT
                    s.id,
                    s.short,
                    s.citation,
                    t.name AS type,
                    s.url,
                    s.license
                FROM sources AS s
                LEFT JOIN dim_source_type AS t ON t.id = s.source_type_id
                ORDER BY s.id
                """
            )

        return self.list_all(Source, order_by=Source.id)

    def get_many_by_ids(
        self,
        source_ids: list[int] | set[int],
    ) -> list[Source] | list[dict[str, Any]]:
        """Return source records for the requested IDs."""

        if not source_ids:
            return []
        if self.relation_has_columns("sources", {"source_type_id"}):
            clean_ids = set()
            for source_id in source_ids:
                try:
                    clean_ids.add(int(source_id))
                except (TypeError, ValueError):
                    continue
            if not clean_ids:
                return []
            ordered_ids = sorted(clean_ids)
            placeholders = ", ".join(
                f":source_id_{index}"
                for index, _source_id in enumerate(ordered_ids)
            )
            params = {
                f"source_id_{index}": source_id
                for index, source_id in enumerate(ordered_ids)
            }
            return self.fetch_mappings(
                f"""
                SELECT
                    s.id,
                    s.short,
                    s.citation,
                    t.name AS type,
                    s.url,
                    s.license
                FROM sources AS s
                LEFT JOIN dim_source_type AS t ON t.id = s.source_type_id
                WHERE s.id IN ({placeholders})
                ORDER BY s.id
                """,
                params,
            )
        statement = select(Source).where(Source.id.in_(source_ids)).order_by(Source.id)
        return list(self.session.scalars(statement).all())

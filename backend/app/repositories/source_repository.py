"""Read-only repository for the `sources` table.

Use this repository whenever code needs citations or provenance records. It
does not create, update, or delete source data.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Source
from app.repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository):
    """Read helpers for source/provenance records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, source_id: int) -> Source | None:
        """Return one source by ID, or `None` when it is missing."""

        return super().get_by_id(Source, source_id)

    def list_sources(self) -> list[Source]:
        """Return all source records ordered by ID."""

        return self.list_all(Source, order_by=Source.id)

    def get_many_by_ids(self, source_ids: list[int] | set[int]) -> list[Source]:
        """Return source records for the requested IDs."""

        if not source_ids:
            return []
        statement = select(Source).where(Source.id.in_(source_ids)).order_by(Source.id)
        return list(self.session.scalars(statement).all())

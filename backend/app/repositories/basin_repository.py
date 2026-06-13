"""Read-only repository for the `basins` table.

Use this repository to load basin and sub-basin context. It contains no
recommendation or scoring behavior.
"""

from sqlalchemy.orm import Session

from app.models import Basin
from app.repositories.base_repository import BaseRepository


class BasinRepository(BaseRepository):
    """Read helpers for basin records."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_basins(self) -> list[Basin]:
        """Return all basin records ordered by ID."""

        return self.list_all(Basin, order_by=Basin.id)

    def get_by_id(self, basin_id: int) -> Basin | None:
        """Return one basin by ID, or `None` when it is missing."""

        return super().get_by_id(Basin, basin_id)

"""Small base class for read-only repository objects.

Repositories receive a SQLAlchemy `Session` and use it to read approved ORM
models. This base class does not write data and does not contain scientific
recommendation logic.
"""

from typing import TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository:
    """Shared read helpers for repository classes."""

    def __init__(self, session: Session) -> None:
        """Store the database session supplied by API/service code."""

        self.session = session

    def get_by_id(self, model: type[ModelT], record_id: int) -> ModelT | None:
        """Return one ORM object by `id`, or `None` when missing."""

        statement = select(model).where(model.id == record_id)
        return self.session.scalars(statement).first()

    def list_all(
        self,
        model: type[ModelT],
        *,
        order_by: object | None = None,
        limit: int | None = None,
    ) -> list[ModelT]:
        """Return rows for a model with optional ordering and limit."""

        statement: Select[tuple[ModelT]] = select(model)
        if order_by is not None:
            statement = statement.order_by(order_by)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.scalars(statement).all())

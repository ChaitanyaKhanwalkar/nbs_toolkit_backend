"""Small base class for read-only repository objects.

Repositories receive a SQLAlchemy `Session` and use it to read approved ORM
models. This base class does not write data and does not contain scientific
recommendation logic.
"""

from collections.abc import Mapping
from typing import Any, TypeVar

from sqlalchemy import Select, inspect, select, text
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

    def relation_exists(self, name: str) -> bool:
        """Return whether a table or view exists in the connected database."""

        bind = self.session.get_bind()
        inspector = inspect(bind)
        return name in set(inspector.get_table_names()) | set(inspector.get_view_names())

    def relation_has_columns(self, name: str, column_names: set[str]) -> bool:
        """Return whether a table or view exposes every requested column."""

        if not self.relation_exists(name):
            return False
        bind = self.session.get_bind()
        inspector = inspect(bind)
        existing_columns = {
            column["name"]
            for column in inspector.get_columns(name)
        }
        return column_names.issubset(existing_columns)

    def fetch_mappings(
        self,
        sql: str,
        params: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a read-only SQL statement and return plain dictionaries."""

        result = self.session.execute(text(sql), dict(params or {}))
        return [dict(row) for row in result.mappings().all()]

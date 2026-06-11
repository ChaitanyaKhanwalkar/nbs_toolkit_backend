"""SQLAlchemy model for the `sources` table.

This table is the provenance registry. Other tables use `source_id` to show
where a value, citation, or rule came from.
"""

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Source(Base):
    """Citation and provenance source used by scientific data tables."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short: Mapped[str | None] = mapped_column(Text, nullable=True)
    citation: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    license: Mapped[str | None] = mapped_column(Text, nullable=True)

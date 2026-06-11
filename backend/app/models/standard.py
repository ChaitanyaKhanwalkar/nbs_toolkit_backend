"""SQLAlchemy model for the `standards` table.

This table stores threshold limits by use case and parameter.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Standard(Base):
    """Water-quality standard row from the approved schema."""

    __tablename__ = "standards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    use_case: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameter: Mapped[str | None] = mapped_column(Text, nullable=True)
    limit_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    limit_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    direction: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id links each threshold back to its official source.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

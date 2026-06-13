"""SQLAlchemy model for the `pollution_sources` table.

This table stores non-point pollution pressure indicators and future point
source records when approved data is available.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PollutionSource(Base):
    """Pollution pressure record connected to a mapped region."""

    __tablename__ = "pollution_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    gauge_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    station: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(Text, nullable=True)
    indicator: Mapped[str | None] = mapped_column(Text, nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id keeps the provenance visible for pollution-pressure values.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

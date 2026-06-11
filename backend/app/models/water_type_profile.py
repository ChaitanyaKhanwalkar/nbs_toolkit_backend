"""SQLAlchemy model for the `water_type_profiles` table.

This table stores fallback water-type profiles used only when measured data is
not available.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WaterTypeProfile(Base):
    """Fallback water-quality profile row from the approved schema."""

    __tablename__ = "water_type_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    water_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameter: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    deprecated: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # source_id indicates the source for fallback profile values.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

"""SQLAlchemy model for the `water_observations` table.

This table stores measured water-quality observations from approved sources.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WaterObservation(Base):
    """Measured water-quality record from the approved schema."""

    __tablename__ = "water_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station: Mapped[str | None] = mapped_column(Text, nullable=True)
    district: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str | None] = mapped_column(Text, nullable=True)
    cwc_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameter: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    n_samples: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period: Mapped[str | None] = mapped_column(Text, nullable=True)
    basin_id: Mapped[int | None] = mapped_column(ForeignKey("basins.id"), nullable=True)
    # source_id identifies the source for this measured observation.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

"""SQLAlchemy model for the `plants` table.

This table stores plant species and evidence notes for future plant selection.
"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Plant(Base):
    """Plant catalogue row from the approved schema."""

    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_species: Mapped[str | None] = mapped_column(Text, nullable=True)
    locational_availability: Mapped[str | None] = mapped_column(Text, nullable=True)
    climate_preference: Mapped[str | None] = mapped_column(Text, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    water_needs: Mapped[str | None] = mapped_column(Text, nullable=True)
    ecological_role: Mapped[str | None] = mapped_column(Text, nullable=True)
    plant_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    native_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    invasive: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metals_pollutants: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    pollution_tolerance: Mapped[str | None] = mapped_column(Text, nullable=True)
    optimal_water_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id preserves the evidence source for plant data.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

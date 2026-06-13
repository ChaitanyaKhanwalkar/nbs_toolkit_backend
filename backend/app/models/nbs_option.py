"""SQLAlchemy model for the `nbs_options` table.

This table stores the approved catalogue of nature-based solution technologies.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NbsOption(Base):
    """Nature-based solution technology option from the approved schema."""

    __tablename__ = "nbs_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    family: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    optimal_water_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_suitability: Mapped[float | None] = mapped_column(Float, nullable=True)
    climate_suitability: Mapped[str | None] = mapped_column(Text, nullable=True)
    soil_type: Mapped[float | None] = mapped_column(Float, nullable=True)
    resource_requirements: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[float | None] = mapped_column(Float, nullable=True)
    # source_id links the technology description to its source.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

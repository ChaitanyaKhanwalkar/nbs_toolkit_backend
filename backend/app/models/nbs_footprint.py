"""SQLAlchemy model for the `nbs_footprint` table.

This table stores footprint and loading constraints for some NbS technologies.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NbsFootprint(Base):
    """Footprint and loading record for a nature-based solution."""

    __tablename__ = "nbs_footprint"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nbs_id: Mapped[int | None] = mapped_column(ForeignKey("nbs_options.id"), nullable=True)
    area_per_pe_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_per_pe_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    olr_g_m2_d: Mapped[float | None] = mapped_column(Float, nullable=True)
    olr_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    hlr_m3_m2_d: Mapped[float | None] = mapped_column(Float, nullable=True)
    depth_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    # source_id shows the source for footprint and loading assumptions.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

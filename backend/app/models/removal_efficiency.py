"""SQLAlchemy model for the `removal_efficiency` table.

This table stores pollutant-specific removal efficiency ranges for NbS options.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RemovalEfficiency(Base):
    """Removal efficiency evidence row from the approved schema."""

    __tablename__ = "removal_efficiency"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nbs: Mapped[str | None] = mapped_column(Text, nullable=True)
    nbs_id: Mapped[int | None] = mapped_column(ForeignKey("nbs_options.id"), nullable=True)
    parameter: Mapped[str | None] = mapped_column(Text, nullable=True)
    eff_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    eff_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id is critical provenance for efficiency evidence.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

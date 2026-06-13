"""SQLAlchemy model for the `nbs_criteria` table.

This table stores qualitative criteria values for future MCDA inputs.
"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NbsCriteria(Base):
    """Qualitative criterion row for a nature-based solution."""

    __tablename__ = "nbs_criteria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nbs_id: Mapped[int | None] = mapped_column(ForeignKey("nbs_options.id"), nullable=True)
    criterion: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_qual: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id preserves the evidence source for this criterion.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

"""SQLAlchemy model for the `basins` table.

This table stores the Narmada basin and sub-basin context used by site and
water-quality records.
"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Basin(Base):
    """Basin or sub-basin record from the approved schema."""

    __tablename__ = "basins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    basin: Mapped[str | None] = mapped_column(Text, nullable=True)
    sub_basin: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id links this row back to the citation/provenance registry.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

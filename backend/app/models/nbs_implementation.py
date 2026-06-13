"""SQLAlchemy model for the `nbs_implementation` table.

This table stores implementation and maintenance guidance for each NbS option.
"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NbsImplementation(Base):
    """Implementation guidance row for a nature-based solution."""

    __tablename__ = "nbs_implementation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nbs_id: Mapped[int | None] = mapped_column(ForeignKey("nbs_options.id"), nullable=True)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    implementation_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    maintenance_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id identifies the source for implementation guidance.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

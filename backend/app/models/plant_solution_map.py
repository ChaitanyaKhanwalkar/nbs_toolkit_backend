"""SQLAlchemy model for the `plant_solution_map` table.

This table maps plant species to NbS options for future plant selection.
"""

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlantSolutionMap(Base):
    """Mapping between plant species and nature-based solution options."""

    __tablename__ = "plant_solution_map"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_id: Mapped[int | None] = mapped_column(ForeignKey("plants.id"), nullable=True)
    plant_species: Mapped[str | None] = mapped_column(Text, nullable=True)
    nbs_id: Mapped[int | None] = mapped_column(ForeignKey("nbs_options.id"), nullable=True)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id keeps the plant-solution mapping provenance visible.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

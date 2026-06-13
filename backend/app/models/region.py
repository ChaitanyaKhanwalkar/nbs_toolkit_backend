"""SQLAlchemy model for the `regions` table.

This table stores catchment, station, climate, soil, and coordinate context for
Narmada sites.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Region(Base):
    """Site and catchment context record from the approved schema."""

    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    camels_gauge_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    station: Mapped[str | None] = mapped_column(Text, nullable=True)
    river: Mapped[str | None] = mapped_column(Text, nullable=True)
    district: Mapped[str | None] = mapped_column(Text, nullable=True)
    cwc_site_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_wq_station: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rainfall_mm_yr: Mapped[float | None] = mapped_column(Float, nullable=True)
    wet_season: Mapped[str | None] = mapped_column(Text, nullable=True)
    dry_season: Mapped[str | None] = mapped_column(Text, nullable=True)
    tmin_C: Mapped[float | None] = mapped_column(Float, nullable=True)
    tmax_C: Mapped[float | None] = mapped_column(Float, nullable=True)
    aridity_P_PET: Mapped[float | None] = mapped_column(Float, nullable=True)
    pet_mm_yr: Mapped[float | None] = mapped_column(Float, nullable=True)
    sand_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    silt_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    clay_pct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    hydrologic_soil_group: Mapped[str | None] = mapped_column(Text, nullable=True)
    soil_depth_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_avail_water_mm_m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    basin_id: Mapped[int | None] = mapped_column(ForeignKey("basins.id"), nullable=True)
    # These source columns preserve where climate/soil and district data came from.
    source_climate_soil: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_district: Mapped[int | None] = mapped_column(Integer, nullable=True)
    infiltration_class: Mapped[str | None] = mapped_column(Text, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)

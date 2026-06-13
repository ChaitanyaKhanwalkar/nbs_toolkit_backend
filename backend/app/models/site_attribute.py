"""SQLAlchemy model for the `site_attributes` table.

This table stores terrain, land-cover, drainage, and dilution proxy values for
each mapped site.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SiteAttribute(Base):
    """Physical site attributes used later by repositories and services."""

    __tablename__ = "site_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    gauge_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    station: Mapped[str | None] = mapped_column(Text, nullable=True)
    elev_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    elev_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elev_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    slope_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    slope_median: Mapped[float | None] = mapped_column(Float, nullable=True)
    drainage_area_km2: Mapped[float | None] = mapped_column(Float, nullable=True)
    dpsbar: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_frac: Mapped[float | None] = mapped_column(Float, nullable=True)
    trees_frac: Mapped[float | None] = mapped_column(Float, nullable=True)
    agri_frac: Mapped[float | None] = mapped_column(Float, nullable=True)
    builtup_frac: Mapped[float | None] = mapped_column(Float, nullable=True)
    bare_frac: Mapped[float | None] = mapped_column(Float, nullable=True)
    range_frac: Mapped[float | None] = mapped_column(Float, nullable=True)
    dom_land_cover: Mapped[str | None] = mapped_column(Text, nullable=True)
    lai_mean: Mapped[float | None] = mapped_column(Float, nullable=True)
    stream_order: Mapped[float | None] = mapped_column(Float, nullable=True)
    dilution_proxy: Mapped[float | None] = mapped_column(Float, nullable=True)
    # source_id links site attributes back to their data source.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

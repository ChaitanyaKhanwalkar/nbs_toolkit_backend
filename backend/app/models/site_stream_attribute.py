"""SQLAlchemy model for the `site_stream_attributes` table.

This table comes from the river network patch and stores the nearest river
segment attributes for each station/site.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SiteStreamAttribute(Base):
    """Nearest-stream attributes connected to Narmada stations."""

    __tablename__ = "site_stream_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    gauge_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    station: Mapped[str | None] = mapped_column(Text, nullable=True)
    ghi_stn_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    cwc_river: Mapped[str | None] = mapped_column(Text, nullable=True)
    stream_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ord_clas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ord_flow: Mapped[int | None] = mapped_column(Integer, nullable=True)
    river_discharge_cms: Mapped[float | None] = mapped_column(Float, nullable=True)
    upland_skm: Mapped[float | None] = mapped_column(Float, nullable=True)
    catch_skm: Mapped[float | None] = mapped_column(Float, nullable=True)
    nearest_distance_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    nearest_distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    station_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    station_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    nearest_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    nearest_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    hybas_l12: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # source_id links station-stream joins back to HydroRIVERS provenance.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

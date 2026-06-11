"""SQLAlchemy model for the `river_network` table.

This table comes from the river network patch and stores HydroRIVERS line
attributes and geometry text for Narmada river segments.
"""

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiverNetwork(Base):
    """River segment attributes from the approved river network patch."""

    __tablename__ = "river_network"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hyriv_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_down: Mapped[int | None] = mapped_column(Integer, nullable=True)
    main_riv: Mapped[int | None] = mapped_column(Integer, nullable=True)
    length_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    dist_dn_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    dist_up_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    catch_skm: Mapped[float | None] = mapped_column(Float, nullable=True)
    upland_skm: Mapped[float | None] = mapped_column(Float, nullable=True)
    endorheic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dis_av_cms: Mapped[float | None] = mapped_column(Float, nullable=True)
    ord_stra: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ord_clas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ord_flow: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hybas_l12: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geometry_wkt: Mapped[str | None] = mapped_column(Text, nullable=True)
    # source_id links river network values to HydroRIVERS provenance.
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

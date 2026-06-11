"""Pydantic schemas for raw river and stream context responses.

River schemas expose HydroRIVERS and station-stream attributes only. They do
not contain hydrological risk scores.
"""

from pydantic import Field

from app.schemas.common import RawResponseModel
from app.schemas.site import SiteStreamAttributesResponse


class RiverSegmentResponse(RawResponseModel):
    """Raw row from the river_network table."""

    id: int | None = None
    hyriv_id: int | None = None
    next_down: int | None = None
    main_riv: int | None = None
    length_km: float | None = None
    dist_dn_km: float | None = None
    dist_up_km: float | None = None
    catch_skm: float | None = None
    upland_skm: float | None = None
    endorheic: int | None = None
    dis_av_cms: float | None = None
    ord_stra: int | None = None
    ord_clas: int | None = None
    ord_flow: int | None = None
    hybas_l12: int | None = None
    geometry_wkt: str | None = None
    source_id: int | None = None


class SiteStreamContextResponse(RawResponseModel):
    """Stream attributes for a station or region."""

    station: str | None = None
    region_id: int | None = None
    stream_attributes: list[SiteStreamAttributesResponse] = Field(default_factory=list)


class RiverContextResponse(RawResponseModel):
    """Grouped raw river network context packet."""

    river_segments: list[RiverSegmentResponse] = Field(default_factory=list)
    site_stream_attributes: list[SiteStreamAttributesResponse] = Field(default_factory=list)
    count: int = 0
    missing_sections: list[str] = Field(default_factory=list)

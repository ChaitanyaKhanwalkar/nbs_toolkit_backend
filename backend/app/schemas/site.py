"""Pydantic schemas for raw site profile responses.

Site profile responses combine descriptive location, basin, catchment, and
stream attributes. They do not include suitability scores.
"""

from pydantic import Field

from app.schemas.common import RawResponseModel
from app.schemas.reference import BasinResponse, RegionResponse


class SiteAttributesResponse(RawResponseModel):
    """Raw row from the site_attributes table."""

    id: int | None = None
    region_id: int | None = None
    gauge_id: int | None = None
    station: str | None = None
    elev_mean: float | None = None
    elev_min: int | None = None
    elev_max: int | None = None
    slope_mean: float | None = None
    slope_median: float | None = None
    drainage_area_km2: float | None = None
    dpsbar: float | None = None
    water_frac: float | None = None
    trees_frac: float | None = None
    agri_frac: float | None = None
    builtup_frac: float | None = None
    bare_frac: float | None = None
    range_frac: float | None = None
    dom_land_cover: str | None = None
    lai_mean: float | None = None
    stream_order: float | None = None
    dilution_proxy: float | None = None
    source_id: int | None = None


class SiteStreamAttributesResponse(RawResponseModel):
    """Raw row from the site_stream_attributes table."""

    id: int | None = None
    region_id: int | None = None
    gauge_id: int | None = None
    station: str | None = None
    ghi_stn_id: str | None = None
    cwc_river: str | None = None
    stream_order: int | None = None
    ord_clas: int | None = None
    ord_flow: int | None = None
    river_discharge_cms: float | None = None
    upland_skm: float | None = None
    catch_skm: float | None = None
    nearest_distance_deg: float | None = None
    nearest_distance_m: float | None = None
    station_lon: float | None = None
    station_lat: float | None = None
    nearest_lon: float | None = None
    nearest_lat: float | None = None
    hybas_l12: int | None = None
    source_id: int | None = None


class SiteProfileResponse(RawResponseModel):
    """Combined raw site profile packet returned by SiteProfileService."""

    region: RegionResponse | None = None
    basin: BasinResponse | None = None
    site_attributes: SiteAttributesResponse | None = None
    site_stream_attributes: list[SiteStreamAttributesResponse] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)

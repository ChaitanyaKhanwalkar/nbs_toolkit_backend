"""Pydantic schemas for raw reference-data responses.

Reference data means dropdown-friendly records such as basins, regions,
sources, stations, and standards use cases. These schemas do not make any
scientific choices.
"""

from pydantic import Field

from app.schemas.common import RawResponseModel


class BasinResponse(RawResponseModel):
    """Raw basin row as stored in the database."""

    id: int | None = None
    basin: str | None = None
    sub_basin: str | None = None
    description: str | None = None
    source_id: int | None = None


class RegionResponse(RawResponseModel):
    """Raw region/station row with climate, soil, and location context."""

    id: int | None = None
    camels_gauge_id: int | None = None
    station: str | None = None
    river: str | None = None
    district: str | None = None
    cwc_site_type: str | None = None
    is_wq_station: int | None = None
    rainfall_mm_yr: float | None = None
    wet_season: str | None = None
    dry_season: str | None = None
    tmin_C: float | None = None
    tmax_C: float | None = None
    aridity_P_PET: float | None = None
    pet_mm_yr: float | None = None
    sand_pct: int | None = None
    silt_pct: int | None = None
    clay_pct: int | None = None
    soil_type: str | None = None
    hydrologic_soil_group: str | None = None
    soil_depth_m: float | None = None
    soil_avail_water_mm_m: int | None = None
    basin_id: int | None = None
    source_climate_soil: int | None = None
    source_district: int | None = None
    infiltration_class: str | None = None
    lat: float | None = None
    lon: float | None = None


class SourceResponse(RawResponseModel):
    """Raw provenance/source row."""

    id: int | None = None
    short: str | None = None
    citation: str | None = None
    type: str | None = None
    url: str | None = None
    license: str | None = None


class WaterStationResponse(RawResponseModel):
    """Water-quality station summary derived from region rows."""

    id: int | None = None
    station: str | None = None
    river: str | None = None
    district: str | None = None
    camels_gauge_id: int | None = None
    is_wq_station: int | None = None
    basin_id: int | None = None


class UseCaseResponse(RawResponseModel):
    """Stored standards use case label."""

    use_case: str | None = None


class ReferenceDataResponse(RawResponseModel):
    """Grouped raw lookup data for future API dropdowns."""

    basins: list[BasinResponse] = Field(default_factory=list)
    regions: list[RegionResponse] = Field(default_factory=list)
    sources: list[SourceResponse] = Field(default_factory=list)
    water_quality_stations: list[WaterStationResponse] = Field(default_factory=list)
    standards_use_cases: list[str] = Field(default_factory=list)

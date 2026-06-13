"""Pydantic schemas for raw nature-based solution catalogue responses.

These schemas describe stored NbS catalogue, evidence, implementation,
footprint, and criteria rows. They intentionally include no ranking fields.
"""

from pydantic import Field

from app.schemas.common import RawResponseModel


class NbsOptionResponse(RawResponseModel):
    """Raw row from the nbs_options table."""

    id: int | None = None
    solution: str | None = None
    family: str | None = None
    description: str | None = None
    optimal_water_type: str | None = None
    location_suitability: float | None = None
    climate_suitability: str | None = None
    soil_type: float | None = None
    resource_requirements: float | None = None
    notes: float | None = None
    source_id: int | None = None


class RemovalEfficiencyResponse(RawResponseModel):
    """Raw row from the removal_efficiency table."""

    id: int | None = None
    nbs: str | None = None
    nbs_id: int | None = None
    parameter: str | None = None
    eff_low: float | None = None
    eff_high: float | None = None
    confidence: str | None = None
    source_id: int | None = None
    note: str | None = None


class NbsImplementationResponse(RawResponseModel):
    """Raw row from the nbs_implementation table."""

    id: int | None = None
    nbs_id: int | None = None
    solution: str | None = None
    implementation_steps: str | None = None
    maintenance_requirements: str | None = None
    source_id: int | None = None


class NbsFootprintResponse(RawResponseModel):
    """Raw row from the nbs_footprint table."""

    id: int | None = None
    nbs_id: int | None = None
    area_per_pe_low: float | None = None
    area_per_pe_high: float | None = None
    olr_g_m2_d: float | None = None
    olr_basis: str | None = None
    hlr_m3_m2_d: float | None = None
    depth_m: float | None = None
    source_id: int | None = None
    note: str | None = None


class NbsCriteriaResponse(RawResponseModel):
    """Raw row from the nbs_criteria table."""

    id: int | None = None
    nbs_id: int | None = None
    criterion: str | None = None
    value_qual: str | None = None
    confidence: str | None = None
    source_id: int | None = None


class NbsFullProfileResponse(RawResponseModel):
    """Combined raw NbS catalogue packet returned by NbsCatalogService."""

    option: NbsOptionResponse | None = None
    removal_efficiencies: list[RemovalEfficiencyResponse] = Field(default_factory=list)
    implementation: list[NbsImplementationResponse] = Field(default_factory=list)
    footprint: list[NbsFootprintResponse] = Field(default_factory=list)
    criteria: list[NbsCriteriaResponse] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)

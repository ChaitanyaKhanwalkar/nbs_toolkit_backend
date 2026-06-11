"""Pydantic schemas for raw plant catalogue responses.

Plant schemas expose stored plant and plant-to-NbS mapping data only. They do
not label final plant recommendations.
"""

from pydantic import Field

from app.schemas.common import RawResponseModel


class PlantResponse(RawResponseModel):
    """Raw row from the plants table."""

    id: int | None = None
    plant_species: str | None = None
    locational_availability: str | None = None
    climate_preference: str | None = None
    soil_type: str | None = None
    water_needs: str | None = None
    ecological_role: str | None = None
    plant_type: str | None = None
    native_status: str | None = None
    invasive: int | None = None
    metals_pollutants: str | None = None
    evidence_note: str | None = None
    pollution_tolerance: str | None = None
    optimal_water_type: str | None = None
    source_id: int | None = None


class PlantMappingResponse(RawResponseModel):
    """Raw row from the plant_solution_map table."""

    id: int | None = None
    plant_id: int | None = None
    plant_species: str | None = None
    nbs_id: int | None = None
    solution: str | None = None
    basis: str | None = None
    source_id: int | None = None


class PlantCatalogResponse(RawResponseModel):
    """Raw plant catalogue packet for future routes."""

    plants: list[PlantResponse] = Field(default_factory=list)
    mappings: list[PlantMappingResponse] = Field(default_factory=list)
    nbs_id: int | None = None
    include_invasive: bool = False
    missing_sections: list[str] = Field(default_factory=list)

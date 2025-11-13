"""
Pydantic schemas for FastAPI I/O.

IMPORTANT:
Whenever you change fields in `/app/db/models.py`, update these Pydantic models
to keep your API responses/requests in sync.
"""

from typing import Optional
from pydantic import BaseModel


# ----------- Base helpers -----------

class ORMModel(BaseModel):
    class Config:
        orm_mode = True


# ----------- MergedDistrictData -----------

class MergedDistrictDataBase(ORMModel):
    state_name: str
    district_name: Optional[str] = None
    soil_type: Optional[str] = None

class MergedDistrictDataOut(MergedDistrictDataBase):
    id: int


# ----------- PlantData -----------

class PlantDataBase(ORMModel):
    plant_species: str
    climate_preference: Optional[str] = None
    water_needs: Optional[str] = None
    ecological_role: Optional[str] = None
    soil_type: Optional[str] = None
    locational_availability: Optional[str] = None
    pollution_tolerance: Optional[str] = None
    state_name: str
    optimal_water_type: str

class PlantDataOut(PlantDataBase):
    id: int
    match_level: Optional[str] = None  # used by recommendation engine


# ----------- NbsOption -----------

class NbsOptionBase(ORMModel):
    solution: str
    optimal_water_type: str
    location_suitability: Optional[str] = None
    climate_suitability: Optional[str] = None
    soil_type: Optional[str] = None
    resource_requirements: Optional[str] = None
    notes: Optional[str] = None
    state_name: str

class NbsOptionOut(NbsOptionBase):
    id: int
    match_level: Optional[str] = None  # used by recommendation engine


# ----------- NbsImplementation -----------

class NbsImplementationBase(ORMModel):
    solution: str
    implementation_steps: Optional[str] = None
    maintenance_requirements: Optional[str] = None

class NbsImplementationOut(NbsImplementationBase):
    id: int


# ----------- WaterData (optional persistence) -----------

class WaterDataBase(ORMModel):
    water_type: Optional[str] = None
    colour: Optional[str] = None
    odour: Optional[str] = None
    turbidity: Optional[float] = None
    temperature: Optional[float] = None
    tss: Optional[float] = None
    ph: Optional[float] = None
    bod: Optional[float] = None
    cod: Optional[float] = None
    nitrate: Optional[float] = None
    phosphate: Optional[float] = None
    ammonia: Optional[float] = None
    chloride: Optional[float] = None

class WaterDataOut(WaterDataBase):
    id: int


# ----------- Recommendation envelope -----------

class RecommendationsOut(ORMModel):
    soil_type: Optional[str] = None
    plant_match_level: Optional[str] = None
    nbs_match_level: Optional[str] = None
    plants: list[PlantDataOut] = []
    nbs_options: list[NbsOptionOut] = []
    meta: dict = {}

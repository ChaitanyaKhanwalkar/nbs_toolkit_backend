from pydantic import BaseModel
from typing import Optional

class WaterDataSchema(BaseModel):
    water_type: Optional[str]
    colour: Optional[str]
    turbidity: Optional[str]
    temperature: Optional[str]
    odour: Optional[str]
    tss: Optional[str]
    ph: Optional[str]
    bod: Optional[str]
    cod: Optional[str]
    nitrate: Optional[str]
    phosphate: Optional[str]
    ammonia: Optional[str]
    chloride: Optional[str]

class UserLocationSchema(BaseModel):
    state_name: str
    state_raw_input: Optional[str] = None
    location_source: Optional[str] = "user_selected"
    notes: Optional[str] = None
    # Pydantic request/response schemas
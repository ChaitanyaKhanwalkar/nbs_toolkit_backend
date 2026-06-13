"""Pydantic schemas for raw water-quality responses.

Water responses describe measured observations and simple parameter counts
only. They do not compare observations with standards or calculate exceedance.
"""

from pydantic import Field

from app.schemas.common import RawResponseModel


class WaterObservationResponse(RawResponseModel):
    """Raw row from the water_observations table."""

    id: int | None = None
    station: str | None = None
    district: str | None = None
    state: str | None = None
    cwc_code: str | None = None
    parameter: str | None = None
    unit: str | None = None
    value_mean: float | None = None
    value_min: float | None = None
    value_max: float | None = None
    n_samples: int | None = None
    period: str | None = None
    basin_id: int | None = None
    source_id: int | None = None


class WaterParameterSummaryResponse(RawResponseModel):
    """Stored parameter name and raw observation count."""

    parameter: str | None = None
    count: int = 0


class WaterDataResponse(RawResponseModel):
    """Grouped raw water observation packet for future routes."""

    station: str | None = None
    basin_id: int | None = None
    observations: list[WaterObservationResponse] = Field(default_factory=list)
    parameter_summaries: list[WaterParameterSummaryResponse] = Field(default_factory=list)
    parameters: dict[str, list[WaterObservationResponse]] = Field(default_factory=dict)

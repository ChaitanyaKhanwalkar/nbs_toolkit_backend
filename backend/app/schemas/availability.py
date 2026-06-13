"""Pydantic schemas for raw data availability responses.

Availability responses report booleans, counts, inputs, and missing sections
only. They do not decide whether a recommendation should be produced.
"""

from typing import Any

from pydantic import Field

from app.schemas.common import RawResponseModel


class DataSectionAvailabilityResponse(RawResponseModel):
    """Availability summary for one raw data section."""

    available: bool = False
    count: int = 0
    requires_nbs_id: bool | None = None


class DataAvailabilityResponse(RawResponseModel):
    """Grouped availability packet returned by DataAvailabilityService."""

    inputs: dict[str, Any] = Field(default_factory=dict)
    sections: dict[str, DataSectionAvailabilityResponse] = Field(default_factory=dict)
    missing_sections: list[str] = Field(default_factory=list)

"""Pydantic schemas for raw pollution context responses.

Pollution schemas describe stored source records and simple grouped context.
They do not create pollution pressure scores.
"""

from typing import Any

from pydantic import Field

from app.schemas.common import RawResponseModel


class PollutionSourceResponse(RawResponseModel):
    """Raw row from the pollution_sources table."""

    id: int | None = None
    region_id: int | None = None
    gauge_id: int | None = None
    station: str | None = None
    source_type: str | None = None
    category: str | None = None
    indicator: str | None = None
    value: float | None = None
    unit: str | None = None
    note: str | None = None
    source_id: int | None = None


class PollutionContextResponse(RawResponseModel):
    """Raw pollution context packet returned by PollutionContextService."""

    region_id: int | None = None
    pollution_sources: list[PollutionSourceResponse] = Field(default_factory=list)
    grouped_context: list[dict[str, Any]] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)

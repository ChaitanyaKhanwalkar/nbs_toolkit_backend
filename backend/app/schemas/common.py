"""Shared Pydantic schemas used by future read-only API responses.

These small response shapes keep common fields in one place so beginners do
not have to copy the same source/provenance or message structures across many
files.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RawResponseModel(BaseModel):
    """Base model that can read either dictionaries or SQLAlchemy objects."""

    model_config = ConfigDict(from_attributes=True)


class SourceRef(RawResponseModel):
    """Reference to stored source/provenance rows."""

    source_id: int | None = None
    source_ids: list[int] = Field(default_factory=list)


class MessageResponse(RawResponseModel):
    """Simple response for future status or informational endpoints."""

    message: str
    detail: str | None = None


class MissingSectionResponse(RawResponseModel):
    """Names of raw data sections that were not available."""

    missing_sections: list[str] = Field(default_factory=list)


class PaginationParams(RawResponseModel):
    """Future pagination input shape only; no pagination logic lives here."""

    limit: int | None = None
    offset: int | None = None


class RawDictResponse(RawResponseModel):
    """Fallback container for raw grouped dictionaries from services."""

    data: dict[str, Any] = Field(default_factory=dict)

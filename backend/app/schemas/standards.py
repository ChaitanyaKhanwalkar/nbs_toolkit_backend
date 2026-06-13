"""Pydantic schemas for raw standards responses.

These schemas expose stored standard limits for explicit use cases. They do
not decide a default target use case and do not evaluate compliance.
"""

from pydantic import Field

from app.schemas.common import RawResponseModel


class StandardResponse(RawResponseModel):
    """Raw row from the standards table."""

    id: int | None = None
    use_case: str | None = None
    parameter: str | None = None
    limit_low: float | None = None
    limit_high: float | None = None
    direction: str | None = None
    unit: str | None = None
    source_id: int | None = None
    note: str | None = None


class StandardsUseCaseResponse(RawResponseModel):
    """Stored standards use case and its raw standards rows."""

    use_case: str | None = None
    standards: list[StandardResponse] = Field(default_factory=list)


class StandardsListResponse(RawResponseModel):
    """Raw standards list response for one or more explicit use cases."""

    use_cases: list[str] = Field(default_factory=list)
    selected_use_case: str | None = None
    standards: list[StandardResponse] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)

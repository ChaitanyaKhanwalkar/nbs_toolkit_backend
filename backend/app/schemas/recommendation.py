"""Local API schemas for the recommendation readiness endpoint.

These schemas are for the local FastAPI wrapper around the staged scientific
workflow. They do not add scientific logic, database writes, Azure settings, or
deployment behavior.
"""

from typing import Any

from pydantic import Field

from app.schemas.common import RawResponseModel
from app.schemas.engine import RecommendationAssemblyBundleResponse


class RecommendationRequest(RawResponseModel):
    """Input payload for the local recommendation workflow endpoint."""

    use_case: str
    measured_observations: list[dict[str, Any]] = Field(default_factory=list)
    selected_parameters: list[str] = Field(default_factory=list)
    station: str | None = None
    basin_id: int | None = None
    region_id: int | None = None
    temporary_weights: dict[str, float] | None = None
    notes: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)

    def workflow_input(self) -> dict[str, Any]:
        """Return fields accepted by the internal ScientificWorkflowService."""

        payload: dict[str, Any] = {
            "use_case": self.use_case,
            "measured_observations": list(self.measured_observations),
            "selected_parameters": list(self.selected_parameters),
        }
        if self.station is not None:
            payload["station"] = self.station
        if self.basin_id is not None:
            payload["basin_id"] = self.basin_id
        if self.region_id is not None:
            payload["region_id"] = self.region_id
        if self.notes is not None:
            payload["notes"] = self.notes
        if self.context:
            payload["context"] = dict(self.context)
        return payload


class RecommendationResponse(RawResponseModel):
    """Safe response returned by the local recommendation workflow endpoint."""

    workflow_status: str
    step_completed: str | None = None
    use_case: str | None = None
    recommendation_assembly_bundle: RecommendationAssemblyBundleResponse | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    missing_data_messages: list[str] = Field(default_factory=list)
    weights_status: str | None = None
    expert_validated: bool = False
    provisional_note: str | None = None

"""Pydantic schemas for internal scientific engine bundle outputs.

These response shapes mirror the current Step A-E engine dataclasses so future
code can serialize them safely. They do not add scientific behavior, routes,
final recommendations, rankings, TOPSIS/AHP fields, confidence scores, or plant
recommendations.
"""

from typing import Any

from pydantic import Field

from app.schemas.common import RawResponseModel


class InputContextResponse(RawResponseModel):
    """Serialized output from Step A input normalization."""

    original_input: dict[str, Any] = Field(default_factory=dict)
    normalized_input: dict[str, Any] = Field(default_factory=dict)
    validation_status: str
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    missing_inputs: list[str] = Field(default_factory=list)
    available_use_cases: list[str] = Field(default_factory=list)
    data_priority_note: str | None = None


class WaterInputBundleResponse(RawResponseModel):
    """Serialized output from Step B water input assembly."""

    selected_source_type: str
    observations: list[dict[str, Any]] = Field(default_factory=list)
    observation_count: int = 0
    selected_parameters: list[str] = Field(default_factory=list)
    missing_inputs: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    source_priority_applied: list[str] = Field(default_factory=list)
    data_quality_notes: list[str] = Field(default_factory=list)
    provenance_notes: list[str] = Field(default_factory=list)
    source_id: int | None = None
    source_ids: list[int] = Field(default_factory=list)
    station: str | None = None
    basin_id: int | None = None
    use_case: str | None = None


class ParameterGapResultResponse(RawResponseModel):
    """Serialized output for one Step C pollutant gap result."""

    parameter: str | None = None
    observed_value: float | None = None
    observed_unit: str | None = None
    standard_unit: str | None = None
    limit_low: float | None = None
    limit_high: float | None = None
    comparison_type: str
    status: str
    gap_value: float | None = None
    gap_ratio: float | None = None
    required_removal_fraction: float | None = None
    required_removal_percent: float | None = None
    direction: str
    source_type: str
    source_id: int | None = None
    source_ids: list[int] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class PollutantGapBundleResponse(RawResponseModel):
    """Serialized output from Step C pollutant gap calculation."""

    use_case: str
    selected_source_type: str
    total_observations_checked: int = 0
    comparable_count: int = 0
    exceedance_count: int = 0
    missing_standard_count: int = 0
    unit_mismatch_count: int = 0
    results: list[ParameterGapResultResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class TreatmentNeedResultResponse(RawResponseModel):
    """Serialized output for one Step D treatment need group."""

    need_group: str
    triggering_parameters: list[str] = Field(default_factory=list)
    triggering_statuses: list[str] = Field(default_factory=list)
    max_gap_ratio: float | None = None
    required_removal_percent_max: float | None = None
    direction: str = "unknown"
    notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class TreatmentNeedBundleResponse(RawResponseModel):
    """Serialized output from Step D treatment need classification."""

    use_case: str
    selected_source_type: str
    treatment_needs: list[TreatmentNeedResultResponse] = Field(default_factory=list)
    unclassified_parameters: list[str] = Field(default_factory=list)
    warning_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)


class CandidateFilterResultResponse(RawResponseModel):
    """Serialized output for one Step E candidate eligibility result."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    eligibility_status: str
    supported_treatment_needs: list[str] = Field(default_factory=list)
    unsupported_treatment_needs: list[str] = Field(default_factory=list)
    data_pending_reasons: list[str] = Field(default_factory=list)
    exclusion_reasons: list[str] = Field(default_factory=list)
    caution_flags: list[str] = Field(default_factory=list)
    evidence_source_ids: list[int] = Field(default_factory=list)
    implementation_source_ids: list[int] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class CandidateFilterBundleResponse(RawResponseModel):
    """Serialized output from Step E candidate eligibility filtering."""

    use_case: str
    selected_source_type: str
    treatment_need_groups: list[str] = Field(default_factory=list)
    candidate_count: int = 0
    eligible_count: int = 0
    ineligible_count: int = 0
    data_pending_count: int = 0
    results: list[CandidateFilterResultResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ScientificWorkflowResultResponse(RawResponseModel):
    """Serialized output from the internal Scientific Workflow service.

    Bundle fields are optional because the workflow can stop safely after Step A
    validation or Step B water-input assembly. This schema only mirrors staged
    outputs and does not add final recommendation, ranking, TOPSIS, AHP,
    confidence-score, or plant-selection fields.
    """

    workflow_status: str
    step_completed: str | None = None
    input_context: InputContextResponse | None = None
    water_input_bundle: WaterInputBundleResponse | None = None
    pollutant_gap_bundle: PollutantGapBundleResponse | None = None
    treatment_need_bundle: TreatmentNeedBundleResponse | None = None
    candidate_filter_bundle: CandidateFilterBundleResponse | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

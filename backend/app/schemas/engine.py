"""Pydantic schemas for internal scientific engine bundle outputs.

These response shapes mirror the current Step A-L engine dataclasses so future
code can serialize them safely. They do not add scientific behavior, routes,
API endpoints, AHP pairwise weights, or plant recommendations. Step I
schemas keep TOPSIS closeness separate from match-score fields. Step J schemas
serialize confidence scores separately from TOPSIS closeness and rank. Step K
schemas serialize explicit plant mappings without changing ranks or confidence.
Step L-A schemas serialize internal recommendation assembly objects only, and
the workflow wrapper can carry that bundle when max_step="L" is explicitly
requested.
"""

from typing import Any, Literal

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
    nbs_family: str | None = None
    nbs_family_id: int | None = None
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


class ApplicabilityRuleHitResponse(RawResponseModel):
    """Serialized output for one A0 applicability rule match."""

    rule_id: str
    rule_type: str
    severity: str
    action: str
    factor_name: str
    user_message: str
    technical_reason: str
    score_modifier: float | None = None
    confidence_modifier: float | None = None
    target_level: str | None = None


class CandidateApplicabilityResultResponse(RawResponseModel):
    """Serialized A0 applicability result for one candidate."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    applicability_status: str
    triggered_rules: list[ApplicabilityRuleHitResponse] = Field(default_factory=list)
    user_messages: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    technical_reasons: list[str] = Field(default_factory=list)
    score_modifier_total: float = 0.0
    confidence_modifier_total: float = 0.0


class ApplicabilityFilterBundleResponse(RawResponseModel):
    """Serialized output from A0 applicability filtering."""

    use_case: str
    result_count: int = 0
    allowed_count: int = 0
    rejected_count: int = 0
    conditional_count: int = 0
    results: list[CandidateApplicabilityResultResponse] = Field(default_factory=list)
    rejected_options: list[CandidateApplicabilityResultResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class McdaMatrixRowResponse(RawResponseModel):
    """Serialized output for one Step F raw MCDA matrix row."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    eligibility_status: str
    supported_treatment_needs: list[str] = Field(default_factory=list)
    criteria_values: dict[str, Any] = Field(default_factory=dict)
    missing_criteria: list[str] = Field(default_factory=list)
    caution_flags: list[str] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class McdaMatrixBundleResponse(RawResponseModel):
    """Serialized output from Step F raw MCDA matrix preparation."""

    use_case: str
    treatment_need_groups: list[str] = Field(default_factory=list)
    row_count: int = 0
    excluded_ineligible_count: int = 0
    criteria_names: list[str] = Field(default_factory=list)
    rows: list[McdaMatrixRowResponse] = Field(default_factory=list)
    missing_criteria_summary: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    weights_status: str = "not_applied"


class NormalizedMcdaCriterionResponse(RawResponseModel):
    """Serialized output for one Step G normalized MCDA criterion."""

    criterion_name: str
    raw_value: Any = None
    normalized_value: float | None = None
    direction: str
    normalization_status: str
    notes: list[str] = Field(default_factory=list)


class NormalizedMcdaMatrixRowResponse(RawResponseModel):
    """Serialized output for one Step G normalized MCDA matrix row."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    eligibility_status: str
    supported_treatment_needs: list[str] = Field(default_factory=list)
    normalized_criteria: list[NormalizedMcdaCriterionResponse] = Field(
        default_factory=list
    )
    missing_criteria: list[str] = Field(default_factory=list)
    caution_flags: list[str] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class NormalizedMcdaMatrixBundleResponse(RawResponseModel):
    """Serialized output from Step G unweighted MCDA normalization."""

    use_case: str
    treatment_need_groups: list[str] = Field(default_factory=list)
    row_count: int = 0
    criteria_names: list[str] = Field(default_factory=list)
    rows: list[NormalizedMcdaMatrixRowResponse] = Field(default_factory=list)
    normalization_method: str = "min_max_unweighted"
    weights_status: str = "not_applied"
    normalized_criteria_count: int = 0
    skipped_criteria_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class McdaWeightsBundleResponse(RawResponseModel):
    """Serialized output from Step H MCDA criteria weight handling."""

    criteria_names: list[str] = Field(default_factory=list)
    weights: dict[str, float] = Field(default_factory=dict)
    weights_status: Literal[
        "weights_missing",
        "temporary_not_expert_validated",
        "expert_validated",
        "invalid_weights",
    ] = "weights_missing"
    weights_source: str | None = None
    expert_validated: bool = False
    missing_weight_criteria: list[str] = Field(default_factory=list)
    extra_weight_criteria: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class TopsisCriterionContributionResponse(RawResponseModel):
    """Serialized output for one Step I weighted TOPSIS criterion."""

    criterion_name: str
    normalized_value: float
    weight: float
    weighted_value: float


class TopsisRankedCandidateResponse(RawResponseModel):
    """Serialized output for one Step I TOPSIS-ranked candidate."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    eligibility_status: str
    rank: int
    topsis_closeness: float | None = None
    distance_to_ideal_best: float | None = None
    distance_to_ideal_worst: float | None = None
    criterion_contributions: list[TopsisCriterionContributionResponse] = Field(
        default_factory=list
    )
    caution_flags: list[str] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class TopsisRankingBundleResponse(RawResponseModel):
    """Serialized output from Step I TOPSIS ranking.

    This schema mirrors TOPSIS ranking internals only. It does not rename
    `topsis_closeness` to a match score and does not include final
    recommendation, confidence-score, plant, health-risk, or API route fields.
    """

    use_case: str
    treatment_need_groups: list[str] = Field(default_factory=list)
    row_count: int = 0
    ranked_count: int = 0
    criteria_used: list[str] = Field(default_factory=list)
    criteria_skipped: list[str] = Field(default_factory=list)
    weights_status: Literal[
        "weights_missing",
        "temporary_not_expert_validated",
        "expert_validated",
        "invalid_weights",
    ] = "weights_missing"
    weights_source: str | None = None
    expert_validated: bool = False
    ranking_method: Literal["topsis"] = "topsis"
    ranked_candidates: list[TopsisRankedCandidateResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ConfidenceFactorResponse(RawResponseModel):
    """Serialized output for one Step J confidence factor."""

    factor_name: str
    factor_score: float
    factor_weight: float
    weighted_score: float
    notes: list[str] = Field(default_factory=list)


class CandidateConfidenceResultResponse(RawResponseModel):
    """Serialized output for one Step J candidate confidence result."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    rank: int
    topsis_closeness: float | None = None
    confidence_score: float
    confidence_label: Literal["high", "medium", "low"]
    factors: list[ConfidenceFactorResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ConfidenceScoringBundleResponse(RawResponseModel):
    """Serialized output from Step J confidence scoring.

    This schema keeps `confidence_score` separate from TOPSIS closeness and
    preserves the Step I rank value. It does not include final recommendation,
    match-score, plant, health-risk, or API route fields.
    """

    use_case: str
    ranking_method: Literal["topsis"] = "topsis"
    weights_status: Literal[
        "weights_missing",
        "temporary_not_expert_validated",
        "expert_validated",
        "invalid_weights",
    ] = "weights_missing"
    expert_validated: bool = False
    confidence_method: Literal["rule_based_v1"] = "rule_based_v1"
    results: list[CandidateConfidenceResultResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class PlantMatchResponse(RawResponseModel):
    """Serialized output for one Step K explicit plant match."""

    plant_id: int | None = None
    scientific_name: str | None = None
    common_name: str | None = None
    local_name: str | None = None
    nbs_id: int | None = None
    nbs_name: str | None = None
    suitability_notes: list[str] = Field(default_factory=list)
    source_ids: list[int] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class CandidatePlantMatchesResponse(RawResponseModel):
    """Serialized Step K plant matches for one already-ranked candidate."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    rank: int
    topsis_closeness: float | None = None
    confidence_score: float | None = None
    confidence_label: Literal["high", "medium", "low"] | None = None
    plant_matches: list[PlantMatchResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class PlantMatchingBundleResponse(RawResponseModel):
    """Serialized output from Step K explicit plant matching.

    This schema keeps plant matching downstream from ranking and confidence. It
    does not include final recommendation, match-score, health-risk, or API
    route fields.
    """

    use_case: str
    ranking_method: Literal["topsis"] = "topsis"
    confidence_method: Literal["rule_based_v1"] | None = None
    plant_matching_method: Literal["explicit_mapping_v1"] = "explicit_mapping_v1"
    candidate_matches: list[CandidatePlantMatchesResponse] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class RecommendationEvidenceSummaryResponse(RawResponseModel):
    """Serialized evidence summary for one Step L-A recommendation."""

    source_ids: list[int] = Field(default_factory=list)
    caution_flags: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class AssembledRecommendationResponse(RawResponseModel):
    """Serialized internal assembled recommendation from Step L-A."""

    nbs_id: int | None = None
    nbs_name: str | None = None
    rank: int
    match_score: float | None = None
    topsis_closeness: float | None = None
    confidence_score: float | None = None
    confidence_label: Literal["high", "medium", "low"] | None = None
    weights_status: Literal[
        "weights_missing",
        "temporary_not_expert_validated",
        "expert_validated",
        "invalid_weights",
    ] = "weights_missing"
    expert_validated: bool = False
    ranking_method: Literal["topsis"] = "topsis"
    confidence_method: Literal["rule_based_v1"] | None = None
    plant_matches: list[PlantMatchResponse] = Field(default_factory=list)
    evidence_summary: RecommendationEvidenceSummaryResponse = Field(
        default_factory=RecommendationEvidenceSummaryResponse
    )
    criteria_breakdown: list[TopsisCriterionContributionResponse] = Field(
        default_factory=list
    )
    explanation: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class RecommendationAssemblyBundleResponse(RawResponseModel):
    """Serialized output from Step L-A internal recommendation assembly.

    This schema may expose `match_score`, but only as the internal copy of
    `topsis_closeness`. It does not create API route fields, health-risk fields,
    or AHP fields.
    """

    use_case: str
    assembly_method: Literal["rank_confidence_plants_v1"] = (
        "rank_confidence_plants_v1"
    )
    recommendation_count: int = 0
    recommendations: list[AssembledRecommendationResponse] = Field(
        default_factory=list
    )
    weights_status: Literal[
        "weights_missing",
        "temporary_not_expert_validated",
        "expert_validated",
        "invalid_weights",
    ] = "weights_missing"
    expert_validated: bool = False
    ranking_method: Literal["topsis"] = "topsis"
    confidence_method: Literal["rule_based_v1"] | None = None
    plant_matching_method: Literal["explicit_mapping_v1"] | None = None
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ScientificWorkflowResultResponse(RawResponseModel):
    """Serialized output from the internal Scientific Workflow service.

    Bundle fields are optional because the workflow can stop safely at early
    stages or can be requested to stop at Step E for backward-compatible raw
    orchestration. This schema mirrors staged outputs through explicit Step L
    and does not add API routes, AHP pairwise, plant-driven ranking, or
    health-risk fields.
    """

    workflow_status: str
    step_completed: str | None = None
    input_context: InputContextResponse | None = None
    water_input_bundle: WaterInputBundleResponse | None = None
    pollutant_gap_bundle: PollutantGapBundleResponse | None = None
    treatment_need_bundle: TreatmentNeedBundleResponse | None = None
    candidate_filter_bundle: CandidateFilterBundleResponse | None = None
    applicability_filter_bundle: ApplicabilityFilterBundleResponse | None = None
    mcda_matrix_bundle: McdaMatrixBundleResponse | None = None
    normalized_mcda_matrix_bundle: NormalizedMcdaMatrixBundleResponse | None = None
    mcda_weights_bundle: McdaWeightsBundleResponse | None = None
    topsis_ranking_bundle: TopsisRankingBundleResponse | None = None
    confidence_scoring_bundle: ConfidenceScoringBundleResponse | None = None
    plant_matching_bundle: PlantMatchingBundleResponse | None = None
    recommendation_assembly_bundle: RecommendationAssemblyBundleResponse | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

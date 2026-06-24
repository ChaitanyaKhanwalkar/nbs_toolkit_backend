"""Local recommendation workflow route.

This route is a thin FastAPI wrapper around the internal staged workflow
service. It calls `max_step="L"` and returns the internal recommendation
assembly output. It does not mutate data, deploy anything, or change Azure
settings.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.engines.applicability_filter import ApplicabilityFilterEngine
from app.engines.candidate_filtering import CandidateFilteringEngine
from app.engines.component_recommendation import IndividualNbsRecommendationEngine
from app.engines.design_readiness import DesignReadinessEngine
from app.engines.scenario_comparison import ScenarioComparisonEngine
from app.engines.sizing_estimator import SizingEstimator
from app.engines.input_normalization import InputContext, InputNormalizationEngine
from app.engines.target_validation import TargetUseCaseValidator
from app.engines.train_recommendation import TrainRecommendationEngine
from app.engines.treatment_need import TreatmentNeedBundle
from app.repositories import EngineDataRepository
from app.schemas import RecommendationRequest, RecommendationResponse
from app.services import (
    LocationContextService,
    NbsCatalogService,
    PlantCatalogService,
    ScientificWorkflowService,
)
from app.services.reference_data_service import ReferenceDataService

router = APIRouter(prefix="/recommend", tags=["recommendation"])


def get_scientific_workflow_service(
    db: Annotated[Session, Depends(get_db)],
) -> ScientificWorkflowService:
    """Build the read-only scientific workflow service for one request."""

    return ScientificWorkflowService.from_session(db)


def get_reference_data_service(
    db: Annotated[Session, Depends(get_db)],
) -> ReferenceDataService:
    """Build the read-only reference-data service for citation resolution."""

    return ReferenceDataService(db)


def get_engine_data_repository(
    db: Annotated[Session, Depends(get_db)],
) -> EngineDataRepository:
    """Build the read-only engine-data repository for canonical train views."""

    return EngineDataRepository(db)


def get_nbs_catalog_service(
    db: Annotated[Session, Depends(get_db)],
) -> NbsCatalogService:
    """Build the read-only canonical NbS catalogue service."""

    return NbsCatalogService(db)


def get_plant_catalog_service(
    db: Annotated[Session, Depends(get_db)],
) -> PlantCatalogService:
    """Build the read-only non-invasive plant catalogue service."""

    return PlantCatalogService(db)


def get_location_context_service(
    db: Annotated[Session, Depends(get_db)],
) -> LocationContextService:
    """Build the read-only location-intelligence service for one request."""

    return LocationContextService(db)


def get_target_use_case_validator(
    db: Annotated[Session, Depends(get_db)],
) -> TargetUseCaseValidator:
    """Build the canonical target-use-case validator for one request."""

    return TargetUseCaseValidator.from_session(db)


@router.post("", response_model=RecommendationResponse)
def run_local_recommendation_workflow(
    request: RecommendationRequest,
    workflow_service: Annotated[
        ScientificWorkflowService,
        Depends(get_scientific_workflow_service),
    ],
    reference_service: Annotated[
        ReferenceDataService,
        Depends(get_reference_data_service),
    ],
    engine_data: Annotated[
        EngineDataRepository,
        Depends(get_engine_data_repository),
    ],
    nbs_catalog: Annotated[
        NbsCatalogService,
        Depends(get_nbs_catalog_service),
    ],
    plant_catalog: Annotated[
        PlantCatalogService,
        Depends(get_plant_catalog_service),
    ],
    location_service: Annotated[
        LocationContextService,
        Depends(get_location_context_service),
    ],
    target_validator: Annotated[
        TargetUseCaseValidator,
        Depends(get_target_use_case_validator),
    ],
) -> dict[str, Any]:
    """Run the staged A-L workflow and return safe recommendation assembly output."""

    normalized_request_input = request.workflow_input()
    target_context = InputNormalizationEngine().normalize(**normalized_request_input)
    target_validation = target_validator.validate(target_context)
    if target_validation.validation_status != "valid":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": (
                    "Select a valid target use case before running the "
                    "recommendation."
                ),
                "errors": target_validation.errors,
                "available_use_cases": target_validation.available_use_cases,
            },
        )
    normalized_request_input["use_case"] = target_validation.normalized_input[
        "use_case"
    ]

    try:
        result = workflow_service.run(
            normalized_request_input,
            max_step="L",
            supplied_weights=request.temporary_weights,
            weights_source=(
                "temporary_api_request"
                if request.temporary_weights
                else None
            ),
            expert_validated=False,
            use_default_weights=request.use_default_weights,
        )
    except Exception as exc:  # pragma: no cover - defensive API boundary
        return {
            "workflow_status": "failed",
            "step_completed": None,
            "use_case": request.use_case,
            "location_profile": None,
            "location_context": {},
            "design_readiness": {},
            "sizing_estimates": [],
            "scenario_comparison": {},
            "input_summary": {},
            "contaminant_gaps": [],
            "ranked_trains": [],
            "component_recommendations": [],
            "filtered_components": [],
            "component_recommendation_method": None,
            "rejected_options": [],
            "train_usecase_matrix": [],
            "recommendation_assembly_bundle": None,
            "warnings": ["The recommendation workflow failed safely."],
            "errors": [f"Recommendation workflow failed: {exc}"],
            "missing_data_messages": [],
            "weights_status": None,
            "expert_validated": False,
            "provisional_note": None,
            "citations": [],
        }

    payload = result.to_dict()
    assembly_bundle = payload.get("recommendation_assembly_bundle")
    weights_status = _weights_status(payload, assembly_bundle)
    expert_validated = _expert_validated(payload, assembly_bundle)
    train_usecase_matrix = engine_data.list_engine_usecase_matrix()
    train_result = TrainRecommendationEngine(engine_data).rank(
        use_case=_use_case(payload, request.use_case) or request.use_case,
        contaminant_gaps=_contaminant_gaps(payload),
        context=request.context,
        region_id=request.region_id,
        input_source_type=(payload.get("water_input_bundle") or {}).get(
            "selected_source_type"
        ),
    )
    candidate_bundle, applicability_bundle = _component_screen_bundles(
        payload,
        request,
        nbs_catalog,
        engine_data,
    )
    component_result = IndividualNbsRecommendationEngine(
        nbs_catalog,
        plant_catalog,
    ).assemble(
        assembly_bundle=assembly_bundle,
        candidate_bundle=candidate_bundle,
        applicability_bundle=applicability_bundle,
        context=request.context,
        contaminant_gaps=_contaminant_gaps(payload),
    )
    input_summary = _input_summary(payload)
    location_context = location_service.build(
        region_id=request.region_id,
        station=request.station,
        context=request.context,
    )
    design_readiness = DesignReadinessEngine().assess(
        measured_observations=input_summary["data_used"],
        context=request.context,
        location_context=location_context,
        ranked_trains=train_result["ranked_trains"],
    )
    sizing_estimates = SizingEstimator(engine_data).estimate(
        ranked_trains=train_result["ranked_trains"],
        context=request.context,
    )
    sizing_by_train = {
        int(row["train_id"]): row for row in sizing_estimates
    }
    for train in train_result["ranked_trains"]:
        train["sizing_estimate"] = sizing_by_train.get(int(train["train_id"]), {})
    scenario_comparison = ScenarioComparisonEngine().compare(
        ranked_trains=train_result["ranked_trains"],
        component_recommendations=component_result["recommendations"],
        sizing_estimates=sizing_estimates,
        design_readiness=design_readiness,
        context=request.context,
    )
    citations = _resolve_citations(
        assembly_bundle,
        reference_service,
        train_result["ranked_trains"],
    )

    return {
        "workflow_status": _workflow_status(
            payload,
            request.context,
            train_result["ranked_trains"],
        ),
        "step_completed": payload.get("step_completed"),
        "use_case": _use_case(payload, request.use_case),
        "location_profile": _location_profile(payload),
        "location_context": location_context,
        "design_readiness": design_readiness,
        "sizing_estimates": sizing_estimates,
        "scenario_comparison": scenario_comparison,
        "input_summary": input_summary,
        "parameter_coverage": _parameter_coverage(
            input_summary,
            train_result["ranked_trains"],
        ),
        "contaminant_gaps": _contaminant_gaps(payload),
        "ranked_trains": train_result["ranked_trains"],
        "component_recommendations": component_result["recommendations"],
        "filtered_components": component_result["filtered_components"],
        "component_recommendation_method": component_result["method"],
        "rejected_options": [
            *_rejected_options(payload),
            *train_result["rejected_options"],
        ],
        "train_usecase_matrix": train_usecase_matrix,
        "recommendation_assembly_bundle": assembly_bundle,
        "citations": citations,
        "warnings": _unique(
            [
                *_warnings(payload, weights_status),
                *train_result["warnings"],
                *_context_guidance_warnings(payload, request.context),
            ]
        ),
        "errors": list(payload.get("errors") or []),
        "missing_data_messages": _missing_data_messages(payload),
        "weights_status": weights_status,
        "expert_validated": expert_validated,
        "provisional_note": _provisional_note(weights_status),
    }


def _resolve_citations(
    assembly_bundle: dict[str, Any] | None,
    reference_service: ReferenceDataService,
    ranked_trains: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Resolve every source ID referenced by the recommendations into citations."""

    source_ids: list[int] = []
    for recommendation in (assembly_bundle or {}).get("recommendations") or []:
        evidence_summary = recommendation.get("evidence_summary") or {}
        for source_id in evidence_summary.get("source_ids") or []:
            if source_id not in source_ids:
                source_ids.append(source_id)
    for train in ranked_trains or []:
        for source_id in train.get("evidence_source_ids") or []:
            if source_id not in source_ids:
                source_ids.append(source_id)
    if not source_ids:
        return []
    try:
        return reference_service.get_citations_for_ids(source_ids)
    except Exception:  # pragma: no cover - citations are best-effort provenance
        return []


def _location_profile(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Return currently known location identifiers without inventing site data."""

    input_context = payload.get("input_context") or {}
    normalized_input = input_context.get("normalized_input") or {}
    profile = {
        "region_id": normalized_input.get("region_id"),
        "basin_id": normalized_input.get("basin_id"),
        "station": normalized_input.get("station"),
    }
    return profile if any(value is not None for value in profile.values()) else None


def _component_screen_bundles(
    payload: dict[str, Any],
    request: RecommendationRequest,
    nbs_catalog: NbsCatalogService,
    engine_data: EngineDataRepository,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return existing A0 outputs or build an unscored context-only screen."""

    candidate_bundle = payload.get("candidate_filter_bundle")
    applicability_bundle = payload.get("applicability_filter_bundle")
    if candidate_bundle and applicability_bundle:
        return candidate_bundle, applicability_bundle

    candidates = CandidateFilteringEngine(nbs_catalog).filter_candidates(
        TreatmentNeedBundle(
            use_case=request.use_case,
            selected_source_type="missing",
        )
    )
    input_context = InputContext(
        original_input=request.workflow_input(),
        normalized_input={
            "use_case": request.use_case,
            "measured_observations": request.measured_observations,
            "context": request.context,
        },
        validation_status="context_guidance",
    )
    applicability, filtered_candidates = ApplicabilityFilterEngine(
        engine_data
    ).apply(
        candidates,
        input_context=input_context,
        rules=engine_data.list_applicability_rules(active_only=True),
    )
    return filtered_candidates.to_dict(), applicability.to_dict()


def _workflow_status(
    payload: dict[str, Any],
    context: dict[str, Any],
    ranked_trains: list[dict[str, Any]],
) -> str:
    """Label location/source-only output as guidance rather than failure."""

    mode = context.get("workflow_mode")
    if (
        payload.get("workflow_status") == "data_missing"
        and mode in {"site_context_only", "pollution_source_screening"}
        and ranked_trains
    ):
        return "context_guidance"
    return payload.get("workflow_status", "failed")


def _context_guidance_warnings(
    payload: dict[str, Any],
    context: dict[str, Any],
) -> list[str]:
    """Explain the scientific boundary of context-only workflows."""

    if (
        payload.get("workflow_status") == "data_missing"
        and context.get("workflow_mode")
        in {"site_context_only", "pollution_source_screening"}
    ):
        return [
            "Context guidance only: measured water-quality data are required "
            "for treatment pass/fail conclusions."
        ]
    return []


def _input_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Summarize user input and selected water source for the frontend."""

    input_context = payload.get("input_context") or {}
    normalized_input = input_context.get("normalized_input") or {}
    water_bundle = payload.get("water_input_bundle") or {}
    observations = normalized_input.get("measured_observations") or []
    return {
        "use_case": normalized_input.get("use_case"),
        "selected_source_type": water_bundle.get("selected_source_type"),
        "observation_count": water_bundle.get("observation_count", 0),
        "selected_parameters": normalized_input.get("selected_parameters") or [],
        "data_used": [
            {
                "parameter": row.get("parameter"),
                "display_name": (
                    (row.get("original") or {}).get("display_name")
                    or row.get("parameter")
                ),
                "value": row.get("value"),
                "unit": row.get("unit"),
                "source": row.get("source") or "unknown",
            }
            for row in observations
            if row.get("parameter") and row.get("value") is not None
        ],
        "context": normalized_input.get("context") or {},
    }


def _parameter_coverage(
    input_summary: dict[str, Any],
    ranked_trains: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Summarize recognized and skipped input rows without hiding any value."""

    top_breakdown = (
        ranked_trains[0].get("pollutant_gap_breakdown") or []
        if ranked_trains
        else []
    )
    breakdown_by_parameter = {
        str(row.get("parameter") or "").lower(): row for row in top_breakdown
    }
    rows = []
    selected_use_case = input_summary.get("use_case")
    for observation in input_summary.get("data_used") or []:
        parameter = str(observation.get("parameter") or "").lower()
        gap = breakdown_by_parameter.get(parameter) or {}
        category = gap.get("coverage_category") or "read_not_assessed"
        target_threshold = gap.get("target_threshold") or {}
        target_available = _target_available(target_threshold)
        rows.append(
            {
                **observation,
                "selected_use_case": selected_use_case,
                "target_limit": target_threshold if target_available else None,
                "target_available": target_available,
                "target_status": _target_status(gap.get("gap_status")),
                "coverage_category": category,
                "coverage_label": gap.get("coverage_label")
                or "Read, but not scored yet.",
                "treatment_evidence_status": (
                    "available"
                    if gap.get("train_addresses_parameter") is True
                    else "insufficient"
                ),
            }
        )
    csv_summary = (input_summary.get("context") or {}).get(
        "csv_validation_summary"
    )
    if isinstance(csv_summary, dict):
        for field in ("unknown_parameters", "non_numeric_values"):
            for warning in csv_summary.get(field) or []:
                rows.append(
                    {
                        "parameter": None,
                        "display_name": str(warning),
                        "value": None,
                        "unit": None,
                        "source": "user_csv",
                        "selected_use_case": selected_use_case,
                        "target_limit": None,
                        "target_available": False,
                        "target_status": "not_applicable",
                        "coverage_category": "skipped",
                        "coverage_label": "Not recognized or skipped.",
                        "treatment_evidence_status": "not_applicable",
                    }
                )
    return rows


def _target_available(target_threshold: dict[str, Any]) -> bool:
    """Return whether a stored target limit is present for one row."""

    return any(
        target_threshold.get(key) is not None for key in ("limit_low", "limit_high")
    )


def _target_status(gap_status: Any) -> str:
    """Translate engine gap status into export-stable target status wording."""

    if gap_status == "below_target":
        return "within_selected_target"
    if gap_status == "exceeds_target":
        return "exceeds_selected_target"
    return "read_not_scored_against_stored_target"


def _contaminant_gaps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Expose Step C pollutant gap rows as contaminant gaps."""

    gap_bundle = payload.get("pollutant_gap_bundle") or {}
    return list(gap_bundle.get("results") or [])


def _rejected_options(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Expose A0 rejected options with rule reasons."""

    applicability_bundle = payload.get("applicability_filter_bundle") or {}
    return list(applicability_bundle.get("rejected_options") or [])


def _use_case(payload: dict[str, Any], fallback: str) -> str | None:
    """Read the normalized use case when Step A ran, otherwise use request text."""

    assembly_bundle = payload.get("recommendation_assembly_bundle") or {}
    if assembly_bundle.get("use_case"):
        return assembly_bundle["use_case"]
    input_context = payload.get("input_context") or {}
    normalized_input = input_context.get("normalized_input") or {}
    return normalized_input.get("use_case") or fallback


def _weights_status(
    payload: dict[str, Any],
    assembly_bundle: dict[str, Any] | None,
) -> str | None:
    """Return the most specific visible Step H/I/L weight status."""

    if assembly_bundle and assembly_bundle.get("weights_status"):
        return assembly_bundle["weights_status"]
    ranking_bundle = payload.get("topsis_ranking_bundle") or {}
    if ranking_bundle.get("weights_status"):
        return ranking_bundle["weights_status"]
    weights_bundle = payload.get("mcda_weights_bundle") or {}
    return weights_bundle.get("weights_status")


def _expert_validated(
    payload: dict[str, Any],
    assembly_bundle: dict[str, Any] | None,
) -> bool:
    """Return whether weights were explicitly expert validated."""

    if assembly_bundle is not None:
        return bool(assembly_bundle.get("expert_validated", False))
    ranking_bundle = payload.get("topsis_ranking_bundle") or {}
    if "expert_validated" in ranking_bundle:
        return bool(ranking_bundle.get("expert_validated"))
    weights_bundle = payload.get("mcda_weights_bundle") or {}
    return bool(weights_bundle.get("expert_validated", False))


def _warnings(payload: dict[str, Any], weights_status: str | None) -> list[str]:
    """Combine workflow warnings with a final-v1 method note when needed."""

    warnings = list(payload.get("warnings") or [])
    if weights_status == "temporary_not_expert_validated":
        warning = (
            "Treatment-train ranking uses final v1 AHP-Fuzzy AHP ensemble "
            "weights with TOPSIS; C5 health-risk remains reserved for future "
            "integration."
        )
        if warning not in warnings:
            warnings.append(warning)
    return warnings


def _missing_data_messages(payload: dict[str, Any]) -> list[str]:
    """Collect safe missing-data messages from early workflow outputs."""

    messages: list[str] = []
    input_context = payload.get("input_context") or {}
    for missing_input in input_context.get("missing_inputs") or []:
        messages.append(f"Missing input: {missing_input}")

    water_bundle = payload.get("water_input_bundle") or {}
    for missing_input in water_bundle.get("missing_inputs") or []:
        messages.append(f"Missing water input: {missing_input}")

    if payload.get("workflow_status") == "data_missing":
        messages.append("Water input data was missing, so ranking was not produced.")
    return _unique(messages)


def _provisional_note(weights_status: str | None) -> str | None:
    """Return a visible note when non-final weights drove the staged workflow."""

    if weights_status == "temporary_not_expert_validated":
        return (
            "Treatment-train ranking uses final v1 AHP-Fuzzy AHP ensemble "
            "weights with TOPSIS. C5 health-risk and field validation remain "
            "future work."
        )
    if weights_status == "weights_missing":
        return (
            "No criteria weights were supplied, so TOPSIS ranking and assembled "
            "recommendations may be unavailable."
        )
    return None


def _unique(values: list[str]) -> list[str]:
    """Return unique non-empty strings while preserving order."""

    unique_values: list[str] = []
    for value in values:
        if value and value not in unique_values:
            unique_values.append(value)
    return unique_values

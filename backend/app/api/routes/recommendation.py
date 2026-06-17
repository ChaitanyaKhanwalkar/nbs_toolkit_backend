"""Local recommendation workflow route.

This route is a thin FastAPI wrapper around the internal staged workflow
service. It calls `max_step="L"` and returns the internal recommendation
assembly output. It does not mutate data, deploy anything, or change Azure
settings.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RecommendationRequest, RecommendationResponse
from app.services import ScientificWorkflowService
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
) -> dict[str, Any]:
    """Run the staged A-L workflow and return safe recommendation assembly output."""

    try:
        result = workflow_service.run(
            request.workflow_input(),
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
    citations = _resolve_citations(assembly_bundle, reference_service)

    return {
        "workflow_status": payload.get("workflow_status", "failed"),
        "step_completed": payload.get("step_completed"),
        "use_case": _use_case(payload, request.use_case),
        "recommendation_assembly_bundle": assembly_bundle,
        "citations": citations,
        "warnings": _warnings(payload, weights_status),
        "errors": list(payload.get("errors") or []),
        "missing_data_messages": _missing_data_messages(payload),
        "weights_status": weights_status,
        "expert_validated": expert_validated,
        "provisional_note": _provisional_note(weights_status),
    }


def _resolve_citations(
    assembly_bundle: dict[str, Any] | None,
    reference_service: ReferenceDataService,
) -> list[dict[str, Any]]:
    """Resolve every source ID referenced by the recommendations into citations."""

    if not assembly_bundle:
        return []
    source_ids: list[int] = []
    for recommendation in assembly_bundle.get("recommendations") or []:
        evidence_summary = recommendation.get("evidence_summary") or {}
        for source_id in evidence_summary.get("source_ids") or []:
            if source_id not in source_ids:
                source_ids.append(source_id)
    if not source_ids:
        return []
    try:
        return reference_service.get_citations_for_ids(source_ids)
    except Exception:  # pragma: no cover - citations are best-effort provenance
        return []


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
    """Combine workflow warnings with the provisional-weight note when needed."""

    warnings = list(payload.get("warnings") or [])
    if weights_status == "temporary_not_expert_validated":
        warning = (
            "Temporary weights are provisional and remain "
            "temporary_not_expert_validated."
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
    """Return a visible note when temporary weights drove the ranking."""

    if weights_status == "temporary_not_expert_validated":
        return (
            "This response used temporary criteria weights. Treat ranking and "
            "match_score as provisional until expert-validated weights are available."
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

r"""Smoke tests for Step L-A recommendation assembly response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\recommendation_assembly_schema_test.py

These tests validate read-only Pydantic shapes only. They do not connect to
Azure, mutate data, call API routes, classify health risk, calculate AHP
pairwise weights, or create `/recommend`.
"""

from __future__ import annotations

from typing import Any

from app.schemas import (
    AssembledRecommendationResponse,
    PlantMatchResponse,
    RecommendationAssemblyBundleResponse,
    RecommendationEvidenceSummaryResponse,
)
from plant_matching_schema_test import minimal_plant_match


FORBIDDEN_FIELDS = {
    "health_risk",
    "api_route",
    "recommend_endpoint",
    "endpoint",
    "route",
    "ahp",
    "ahp_weight",
}


def model_to_dict(model: Any) -> dict[str, Any]:
    """Support both Pydantic v1 and v2 style dumping."""

    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def schema_fields(model_class: Any) -> set[str]:
    """Return field names for Pydantic v1 or v2 models."""

    fields = getattr(model_class, "model_fields", None)
    if fields is None:
        fields = getattr(model_class, "__fields__", {})
    return set(fields)


def minimal_evidence_summary() -> RecommendationEvidenceSummaryResponse:
    """Create a minimal Step L-A evidence summary schema."""

    return RecommendationEvidenceSummaryResponse(
        source_ids=[31, 701],
        caution_flags=["Pathogen contact caution."],
        warnings=[],
        notes=["Source IDs were copied from upstream staged outputs."],
    )


def minimal_recommendation() -> AssembledRecommendationResponse:
    """Create a minimal Step L-A assembled recommendation schema."""

    return AssembledRecommendationResponse(
        nbs_id=1,
        nbs_name="Horizontal wetland",
        rank=1,
        match_score=0.82,
        topsis_closeness=0.82,
        confidence_score=0.70,
        confidence_label="medium",
        weights_status="temporary_not_expert_validated",
        expert_validated=False,
        ranking_method="topsis",
        confidence_method="rule_based_v1",
        plant_matches=[minimal_plant_match()],
        evidence_summary=minimal_evidence_summary(),
        explanation=["match_score is copied directly from topsis_closeness."],
        warnings=["Temporary weights are provisional."],
        notes=["Internal assembly only."],
    )


def minimal_bundle() -> RecommendationAssemblyBundleResponse:
    """Create a minimal Step L-A assembly bundle schema."""

    return RecommendationAssemblyBundleResponse(
        use_case="surface_discharge",
        assembly_method="rank_confidence_plants_v1",
        recommendation_count=1,
        recommendations=[minimal_recommendation()],
        weights_status="temporary_not_expert_validated",
        expert_validated=False,
        ranking_method="topsis",
        confidence_method="rule_based_v1",
        plant_matching_method="explicit_mapping_v1",
        warnings=["Temporary weights are provisional."],
        notes=["Step L-A serializes internal assembly only."],
    )


def assert_minimal_schemas_validate() -> None:
    """The Step L-A response schemas should accept minimal valid objects."""

    evidence_summary = minimal_evidence_summary()
    recommendation = minimal_recommendation()
    bundle = minimal_bundle()

    assert evidence_summary.source_ids == [31, 701]
    assert recommendation.match_score == recommendation.topsis_closeness
    assert recommendation.confidence_score != recommendation.match_score
    assert recommendation.rank == 1
    assert bundle.assembly_method == "rank_confidence_plants_v1"
    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False


def assert_missing_optional_fields_validate() -> None:
    """Confidence and plant fields may be empty when upstream data is missing."""

    recommendation = AssembledRecommendationResponse(
        nbs_id=2,
        nbs_name="Data pending polishing system",
        rank=2,
        match_score=0.61,
        topsis_closeness=0.61,
        confidence_score=None,
        confidence_label=None,
        weights_status="temporary_not_expert_validated",
        expert_validated=False,
        ranking_method="topsis",
        confidence_method=None,
        plant_matches=[],
        evidence_summary=RecommendationEvidenceSummaryResponse(),
    )

    assert recommendation.confidence_score is None
    assert recommendation.plant_matches == []


def assert_forbidden_fields_absent() -> None:
    """Step L-A schemas must not expose API, AHP, or health-risk fields."""

    schema_classes = [
        RecommendationEvidenceSummaryResponse,
        AssembledRecommendationResponse,
        RecommendationAssemblyBundleResponse,
        PlantMatchResponse,
    ]
    for schema_class in schema_classes:
        forbidden_present = FORBIDDEN_FIELDS.intersection(schema_fields(schema_class))
        assert not forbidden_present, (
            f"Forbidden schema fields found on {schema_class.__name__}: "
            f"{forbidden_present}"
        )

    payload = model_to_dict(minimal_bundle())
    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step L-A schema payload leaked forbidden fields: {sorted(found)}"


def _find_forbidden_keys(value: Any, forbidden_fields: set[str]) -> set[str]:
    """Recursively find forbidden keys in dictionaries/lists."""

    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in forbidden_fields:
                found.add(key_text)
            found.update(_find_forbidden_keys(child, forbidden_fields))
    elif isinstance(value, list):
        for child in value:
            found.update(_find_forbidden_keys(child, forbidden_fields))
    return found


def main() -> None:
    """Run all Step L-A schema checks."""

    assert_minimal_schemas_validate()
    assert_missing_optional_fields_validate()
    assert_forbidden_fields_absent()
    print("recommendation assembly schema checks ok: Step L-A response schemas only")


if __name__ == "__main__":
    main()

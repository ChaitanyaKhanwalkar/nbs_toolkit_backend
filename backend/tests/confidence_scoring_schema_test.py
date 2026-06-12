r"""Smoke tests for Step J confidence scoring response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\confidence_scoring_schema_test.py

These tests validate read-only Pydantic shapes only. They do not connect to
Azure, mutate data, call API routes, change TOPSIS rank, recommend plants,
classify health risk, calculate AHP pairwise weights, or create final
recommendations.
"""

from __future__ import annotations

from typing import Any

from app.schemas import (
    CandidateConfidenceResultResponse,
    ConfidenceFactorResponse,
    ConfidenceScoringBundleResponse,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "plant_recommendation",
    "plant_recommendations",
    "plants",
    "health_risk",
    "api_route",
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


def minimal_factor() -> ConfidenceFactorResponse:
    """Create a minimal Step J confidence factor schema."""

    return ConfidenceFactorResponse(
        factor_name="water_data_quality",
        factor_score=1.0,
        factor_weight=0.25,
        weighted_score=0.25,
        notes=["User measured water data was used."],
    )


def minimal_candidate(label: str = "high") -> CandidateConfidenceResultResponse:
    """Create a minimal Step J candidate confidence schema."""

    return CandidateConfidenceResultResponse(
        nbs_id=1,
        nbs_name="Horizontal wetland",
        rank=1,
        topsis_closeness=0.82,
        confidence_score=0.90 if label == "high" else 0.62 if label == "medium" else 0.35,
        confidence_label=label,
        factors=[minimal_factor()],
        warnings=[],
        notes=["Confidence is separate from TOPSIS closeness."],
    )


def minimal_bundle() -> ConfidenceScoringBundleResponse:
    """Create a minimal Step J confidence bundle schema."""

    return ConfidenceScoringBundleResponse(
        use_case="surface_discharge",
        ranking_method="topsis",
        weights_status="temporary_not_expert_validated",
        expert_validated=False,
        confidence_method="rule_based_v1",
        results=[
            minimal_candidate("high"),
            minimal_candidate("medium"),
            minimal_candidate("low"),
        ],
        warnings=["Temporary weights make ranking provisional."],
        notes=["Step J serializes confidence only."],
    )


def assert_minimal_schemas_validate() -> None:
    """The Step J response schemas should accept minimal valid objects."""

    factor = minimal_factor()
    candidate = minimal_candidate()
    bundle = minimal_bundle()

    assert factor.factor_name == "water_data_quality"
    assert candidate.confidence_label == "high"
    assert candidate.confidence_score != candidate.topsis_closeness
    assert candidate.rank == 1
    assert bundle.confidence_method == "rule_based_v1"
    assert bundle.ranking_method == "topsis"
    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False
    assert [result.confidence_label for result in bundle.results] == [
        "high",
        "medium",
        "low",
    ]


def assert_forbidden_fields_absent() -> None:
    """Step J schemas must not expose final recommendation/API fields."""

    schema_classes = [
        ConfidenceFactorResponse,
        CandidateConfidenceResultResponse,
        ConfidenceScoringBundleResponse,
    ]
    for schema_class in schema_classes:
        forbidden_present = FORBIDDEN_FIELDS.intersection(schema_fields(schema_class))
        assert not forbidden_present, (
            f"Forbidden schema fields found on {schema_class.__name__}: "
            f"{forbidden_present}"
        )

    payload = model_to_dict(minimal_bundle())
    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step J schema payload leaked forbidden fields: {sorted(found)}"


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
    """Run all Step J schema checks."""

    assert_minimal_schemas_validate()
    assert_forbidden_fields_absent()
    print("confidence scoring schema checks ok: Step J response schemas only")


if __name__ == "__main__":
    main()

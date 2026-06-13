r"""Smoke tests for Step I TOPSIS ranking response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\topsis_ranking_schema_test.py

These tests validate read-only Pydantic shapes only. They do not connect to
Azure, mutate data, call API routes, create final recommendations, calculate
confidence scores, recommend plants, classify health risk, or calculate AHP
pairwise weights.
"""

from __future__ import annotations

from typing import Any

from app.schemas import (
    TopsisCriterionContributionResponse,
    TopsisRankedCandidateResponse,
    TopsisRankingBundleResponse,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "confidence_score",
    "plant_recommendation",
    "plant_recommendations",
    "health_risk",
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


def minimal_contribution() -> TopsisCriterionContributionResponse:
    """Create a minimal Step I criterion contribution schema."""

    return TopsisCriterionContributionResponse(
        criterion_name="removal_evidence_coverage",
        normalized_value=0.75,
        weight=0.5,
        weighted_value=0.375,
    )


def minimal_candidate() -> TopsisRankedCandidateResponse:
    """Create a minimal Step I ranked candidate schema."""

    return TopsisRankedCandidateResponse(
        nbs_id=1,
        nbs_name="Horizontal wetland",
        eligibility_status="eligible",
        rank=1,
        topsis_closeness=0.82,
        distance_to_ideal_best=0.12,
        distance_to_ideal_worst=0.55,
        criterion_contributions=[minimal_contribution()],
        caution_flags=["Temporary weights require review."],
        source_ids=[10, 31],
        notes=["TOPSIS closeness is not a final recommendation."],
        warnings=[],
    )


def minimal_bundle() -> TopsisRankingBundleResponse:
    """Create a minimal Step I ranking bundle schema."""

    return TopsisRankingBundleResponse(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load"],
        row_count=1,
        ranked_count=1,
        criteria_used=["removal_evidence_coverage"],
        criteria_skipped=["maintenance_indicator"],
        weights_status="temporary_not_expert_validated",
        weights_source="temporary_schema_test_weights",
        expert_validated=False,
        ranking_method="topsis",
        ranked_candidates=[minimal_candidate()],
        warnings=["Temporary weights are provisional."],
        notes=["Step I serializes TOPSIS ranking only."],
    )


def assert_minimal_schemas_validate() -> None:
    """The Step I response schemas should accept minimal valid objects."""

    contribution = minimal_contribution()
    candidate = minimal_candidate()
    bundle = minimal_bundle()

    assert contribution.weighted_value == 0.375
    assert candidate.topsis_closeness == 0.82
    assert candidate.criterion_contributions[0].criterion_name == (
        "removal_evidence_coverage"
    )
    assert bundle.ranking_method == "topsis"
    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False
    assert bundle.ranked_candidates[0].rank == 1


def assert_forbidden_fields_absent() -> None:
    """Step I schemas must not expose future recommendation/confidence fields."""

    schema_classes = [
        TopsisCriterionContributionResponse,
        TopsisRankedCandidateResponse,
        TopsisRankingBundleResponse,
    ]
    for schema_class in schema_classes:
        forbidden_present = FORBIDDEN_FIELDS.intersection(schema_fields(schema_class))
        assert not forbidden_present, (
            f"Forbidden schema fields found on {schema_class.__name__}: "
            f"{forbidden_present}"
        )

    payload = model_to_dict(minimal_bundle())
    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step I schema payload leaked future fields: {sorted(found)}"


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
    """Run all Step I schema checks."""

    assert_minimal_schemas_validate()
    assert_forbidden_fields_absent()
    print("topsis ranking schema checks ok: Step I response schemas only")


if __name__ == "__main__":
    main()

r"""Smoke tests for Step K plant matching response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\plant_matching_schema_test.py

These tests validate read-only Pydantic shapes only. They do not connect to
Azure, mutate data, call API routes, change TOPSIS rank, change confidence,
calculate match_score, classify health risk, or create final recommendations.
"""

from __future__ import annotations

from typing import Any

from app.schemas import (
    CandidatePlantMatchesResponse,
    PlantMatchResponse,
    PlantMatchingBundleResponse,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "plant_recommendation",
    "plant_recommendations",
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


def minimal_plant_match() -> PlantMatchResponse:
    """Create a minimal explicit plant match response."""

    return PlantMatchResponse(
        plant_id=501,
        scientific_name="Typha latifolia",
        common_name="Broadleaf cattail",
        local_name=None,
        nbs_id=1,
        nbs_name="High confidence wetland",
        suitability_notes=["Explicit plant-solution mapping row."],
        source_ids=[701],
        warnings=[],
        notes=["Serialized Step K plant match."],
    )


def minimal_candidate_match() -> CandidatePlantMatchesResponse:
    """Create a minimal candidate plant match response."""

    return CandidatePlantMatchesResponse(
        nbs_id=1,
        nbs_name="High confidence wetland",
        rank=1,
        topsis_closeness=0.82,
        confidence_score=0.90,
        confidence_label="high",
        plant_matches=[minimal_plant_match()],
        warnings=[],
        notes=["Rank and confidence are preserved."],
    )


def minimal_bundle() -> PlantMatchingBundleResponse:
    """Create a minimal Step K plant matching bundle response."""

    return PlantMatchingBundleResponse(
        use_case="surface_discharge",
        ranking_method="topsis",
        confidence_method="rule_based_v1",
        plant_matching_method="explicit_mapping_v1",
        candidate_matches=[minimal_candidate_match()],
        warnings=[],
        notes=["Step K serializes explicit mappings only."],
    )


def assert_minimal_schemas_validate() -> None:
    """The Step K response schemas should accept minimal valid objects."""

    plant_match = minimal_plant_match()
    candidate_match = minimal_candidate_match()
    bundle = minimal_bundle()

    assert plant_match.plant_id == 501
    assert candidate_match.rank == 1
    assert candidate_match.confidence_score == 0.90
    assert bundle.plant_matching_method == "explicit_mapping_v1"
    assert bundle.ranking_method == "topsis"
    assert bundle.confidence_method == "rule_based_v1"


def assert_schema_allows_missing_confidence_fields() -> None:
    """Confidence fields may be absent when Step J output was not supplied."""

    candidate_match = CandidatePlantMatchesResponse(
        nbs_id=2,
        nbs_name="Data pending polishing system",
        rank=2,
        topsis_closeness=0.61,
        confidence_score=None,
        confidence_label=None,
        plant_matches=[],
        warnings=["No explicit plant mappings were found for nbs_id 2."],
    )

    assert candidate_match.confidence_score is None
    assert candidate_match.confidence_label is None
    assert candidate_match.plant_matches == []


def assert_forbidden_fields_absent() -> None:
    """Step K schemas must not expose final recommendation/API fields."""

    schema_classes = [
        PlantMatchResponse,
        CandidatePlantMatchesResponse,
        PlantMatchingBundleResponse,
    ]
    for schema_class in schema_classes:
        forbidden_present = FORBIDDEN_FIELDS.intersection(schema_fields(schema_class))
        assert not forbidden_present, (
            f"Forbidden schema fields found on {schema_class.__name__}: "
            f"{forbidden_present}"
        )

    payload = model_to_dict(minimal_bundle())
    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step K schema payload leaked forbidden fields: {sorted(found)}"


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
    """Run all Step K schema checks."""

    assert_minimal_schemas_validate()
    assert_schema_allows_missing_confidence_fields()
    assert_forbidden_fields_absent()
    print("plant matching schema checks ok: Step K response schemas only")


if __name__ == "__main__":
    main()

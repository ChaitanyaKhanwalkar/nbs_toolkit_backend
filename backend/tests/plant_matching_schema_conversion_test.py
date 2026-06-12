r"""Conversion checks for real Step K plant matching output.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\plant_matching_schema_conversion_test.py

These tests validate that actual PlantMatchingBundle.to_dict() output can be
serialized by the Step K Pydantic response schema. They do not create routes,
final recommendations, match_score fields, health-risk classifications, or AHP
pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import PlantMatchingEngine
from app.schemas import PlantMatchingBundleResponse
from confidence_scoring_test import ranking_bundle, score_complete_expert_case
from plant_matching_test import FORBIDDEN_FIELDS, fake_provider


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


def actual_plant_matching_payload() -> dict[str, Any]:
    """Run Step K and return the actual dataclass dictionary output."""

    plant_bundle = PlantMatchingEngine(fake_provider()).match_plants(
        ranking_bundle(),
        score_complete_expert_case(),
    )
    return plant_bundle.to_dict()


def assert_actual_output_converts_to_schema() -> None:
    """Actual Step K output should validate as the response schema."""

    payload = actual_plant_matching_payload()
    response = PlantMatchingBundleResponse(**payload)
    serialized = model_to_dict(response)

    assert response.plant_matching_method == "explicit_mapping_v1"
    assert response.ranking_method == "topsis"
    assert response.confidence_method == "rule_based_v1"
    assert response.candidate_matches
    assert response.candidate_matches[0].plant_matches
    assert response.candidate_matches[1].plant_matches == []
    assert any("No explicit plant mappings" in warning for warning in response.warnings)

    assert_forbidden_fields_absent(payload)
    assert_forbidden_fields_absent(serialized)
    assert_schema_has_no_forbidden_fields()


def assert_rank_closeness_and_confidence_survive_conversion() -> None:
    """Schema conversion should preserve upstream ranking and confidence fields."""

    payload = actual_plant_matching_payload()
    response = PlantMatchingBundleResponse(**payload)

    assert [candidate["rank"] for candidate in payload["candidate_matches"]] == [
        candidate.rank for candidate in response.candidate_matches
    ]
    assert [
        candidate["topsis_closeness"]
        for candidate in payload["candidate_matches"]
    ] == [
        candidate.topsis_closeness
        for candidate in response.candidate_matches
    ]
    assert [
        candidate["confidence_score"]
        for candidate in payload["candidate_matches"]
    ] == [
        candidate.confidence_score
        for candidate in response.candidate_matches
    ]


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay in engines/schemas only."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def assert_forbidden_fields_absent(payload: Any) -> None:
    """Recursively confirm forbidden output fields are absent."""

    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step K conversion leaked forbidden fields: {sorted(found)}"


def assert_schema_has_no_forbidden_fields() -> None:
    """Check schema declarations, not just serialized sample payloads."""

    forbidden_present = FORBIDDEN_FIELDS.intersection(
        schema_fields(PlantMatchingBundleResponse)
    )
    assert not forbidden_present, f"Forbidden schema fields found: {forbidden_present}"


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
    """Run all Step K schema conversion checks."""

    assert_actual_output_converts_to_schema()
    assert_rank_closeness_and_confidence_survive_conversion()
    assert_no_api_or_recommend_route_involved()
    print("plant matching schema conversion checks ok: real Step K output validates")


if __name__ == "__main__":
    main()

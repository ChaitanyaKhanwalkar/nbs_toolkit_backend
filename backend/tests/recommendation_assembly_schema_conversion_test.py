r"""Conversion checks for real Step L-A recommendation assembly output.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\recommendation_assembly_schema_conversion_test.py

These tests validate that actual RecommendationAssemblyBundle.to_dict() output
can be serialized by the Step L-A Pydantic response schema. They do not create
routes, call `/recommend`, classify health risk, or calculate AHP pairwise
weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import RecommendationAssemblyEngine
from app.schemas import RecommendationAssemblyBundleResponse
from recommendation_assembly_test import (
    FORBIDDEN_FIELDS,
    plant_bundle,
)
from confidence_scoring_test import ranking_bundle, score_complete_expert_case


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


def actual_assembly_payload() -> dict[str, Any]:
    """Run Step L-A and return the actual dataclass dictionary output."""

    bundle = RecommendationAssemblyEngine().assemble(
        ranking_bundle(),
        score_complete_expert_case(),
        plant_bundle(),
    )
    return bundle.to_dict()


def assert_actual_output_converts_to_schema() -> None:
    """Actual Step L-A output should validate as the response schema."""

    payload = actual_assembly_payload()
    response = RecommendationAssemblyBundleResponse(**payload)
    serialized = model_to_dict(response)

    assert response.assembly_method == "rank_confidence_plants_v1"
    assert response.recommendation_count == len(response.recommendations)
    assert response.ranking_method == "topsis"
    assert response.confidence_method == "rule_based_v1"
    assert response.plant_matching_method == "explicit_mapping_v1"
    assert response.recommendations[0].match_score == (
        response.recommendations[0].topsis_closeness
    )
    assert response.recommendations[0].confidence_score != (
        response.recommendations[0].match_score
    )

    assert_forbidden_fields_absent(payload)
    assert_forbidden_fields_absent(serialized)
    assert_schema_has_no_forbidden_fields()


def assert_rank_and_plants_survive_conversion() -> None:
    """Schema conversion should preserve rank and plant support fields."""

    payload = actual_assembly_payload()
    response = RecommendationAssemblyBundleResponse(**payload)

    assert [item["rank"] for item in payload["recommendations"]] == [
        recommendation.rank for recommendation in response.recommendations
    ]
    assert response.recommendations[0].plant_matches
    assert response.recommendations[1].plant_matches == []


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay in engines/schemas only."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def assert_forbidden_fields_absent(payload: Any) -> None:
    """Recursively confirm forbidden output fields are absent."""

    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step L-A conversion leaked forbidden fields: {sorted(found)}"


def assert_schema_has_no_forbidden_fields() -> None:
    """Check schema declarations, not just serialized sample payloads."""

    forbidden_present = FORBIDDEN_FIELDS.intersection(
        schema_fields(RecommendationAssemblyBundleResponse)
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
    """Run all Step L-A schema conversion checks."""

    assert_actual_output_converts_to_schema()
    assert_rank_and_plants_survive_conversion()
    assert_no_api_or_recommend_route_involved()
    print("recommendation assembly schema conversion checks ok: real Step L-A output validates")


if __name__ == "__main__":
    main()

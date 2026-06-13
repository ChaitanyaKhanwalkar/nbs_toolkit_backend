r"""Conversion checks for real Step J confidence scoring output.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\confidence_scoring_schema_conversion_test.py

These tests validate that actual ConfidenceScoringBundle.to_dict() output can
be serialized by the Step J Pydantic response schema. They do not create routes,
final recommendations, match_score fields, plant recommendations, health-risk
classifications, or AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.schemas import ConfidenceScoringBundleResponse
from confidence_scoring_test import (
    candidate_bundle,
    normalized_bundle,
    ranking_bundle,
    temporary_weights,
    water_bundle,
)
from app.engines import ConfidenceScoringEngine


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


def actual_confidence_payload() -> dict[str, Any]:
    """Run Step J and return the actual dataclass dictionary output."""

    confidence_bundle = ConfidenceScoringEngine().score(
        ranking_bundle(
            weights_status="temporary_not_expert_validated",
            expert_validated=False,
        ),
        water_bundle=water_bundle(),
        candidate_bundle=candidate_bundle(),
        normalized_bundle=normalized_bundle(),
        weights_bundle=temporary_weights(),
    )
    return confidence_bundle.to_dict()


def assert_actual_output_converts_to_schema() -> None:
    """Actual Step J output should validate as the response schema."""

    payload = actual_confidence_payload()
    response = ConfidenceScoringBundleResponse(**payload)
    serialized = model_to_dict(response)

    assert response.confidence_method == "rule_based_v1"
    assert response.ranking_method == "topsis"
    assert response.weights_status == "temporary_not_expert_validated"
    assert response.expert_validated is False
    assert response.results
    assert [result.rank for result in response.results] == [1, 2]
    assert all(result.factors for result in response.results)
    assert all(0.0 <= result.confidence_score <= 1.0 for result in response.results)
    assert all(
        result.confidence_score != result.topsis_closeness
        for result in response.results
    )
    assert {result.confidence_label for result in response.results}.issubset(
        {"high", "medium", "low"}
    )

    assert_forbidden_fields_absent(payload)
    assert_forbidden_fields_absent(serialized)
    assert_schema_has_no_forbidden_fields()


def assert_rank_is_preserved() -> None:
    """Schema conversion should not change Step I rank values."""

    payload = actual_confidence_payload()
    response = ConfidenceScoringBundleResponse(**payload)

    assert [result["rank"] for result in payload["results"]] == [
        result.rank for result in response.results
    ]


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay in engines/schemas only."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def assert_forbidden_fields_absent(payload: Any) -> None:
    """Recursively confirm forbidden output fields are absent."""

    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step J conversion leaked forbidden fields: {sorted(found)}"


def assert_schema_has_no_forbidden_fields() -> None:
    """Check schema declarations, not just serialized sample payloads."""

    forbidden_present = FORBIDDEN_FIELDS.intersection(
        schema_fields(ConfidenceScoringBundleResponse)
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
    """Run all Step J schema conversion checks."""

    assert_actual_output_converts_to_schema()
    assert_rank_is_preserved()
    assert_no_api_or_recommend_route_involved()
    print("confidence scoring schema conversion checks ok: real Step J output validates")


if __name__ == "__main__":
    main()

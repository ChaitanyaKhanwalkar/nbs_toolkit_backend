r"""Conversion checks for real Step H MCDA weights output.

Run from backend/ with:
    set PYTHONPATH=%CD%
    python tests\mcda_weights_schema_conversion_test.py

These tests use fake criteria names only. They validate that actual
McdaWeightsBundle.to_dict() output can be serialized by the Step H Pydantic
response schema. They do not create recommendations, routes, rankings, TOPSIS,
AHP weights, or plant recommendations.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import McdaWeightsHandler
from app.schemas import McdaWeightsBundleResponse


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "ranking",
    "rank",
    "match_score",
    "confidence_score",
    "topsis",
    "topsis_score",
    "ahp",
    "ahp_weight",
}

CRITERIA_NAMES = [
    "removal_evidence_coverage",
    "site_suitability",
    "cost_indicator",
]


def model_to_dict(model: Any) -> dict[str, Any]:
    """Support both Pydantic v1 and v2 style dumping."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def assert_forbidden_fields_absent(payload: Any) -> None:
    """Recursively confirm that no recommendation/ranking fields are present."""
    if isinstance(payload, dict):
        forbidden_present = FORBIDDEN_FIELDS.intersection(payload)
        assert not forbidden_present, f"Forbidden fields found: {forbidden_present}"
        for value in payload.values():
            assert_forbidden_fields_absent(value)
    elif isinstance(payload, list):
        for item in payload:
            assert_forbidden_fields_absent(item)


def assert_schema_has_no_forbidden_model_fields() -> None:
    """Check schema field declarations, not just serialized test payloads."""
    schema_fields = getattr(McdaWeightsBundleResponse, "model_fields", None)
    if schema_fields is None:
        schema_fields = getattr(McdaWeightsBundleResponse, "__fields__", {})
    forbidden_present = FORBIDDEN_FIELDS.intersection(schema_fields)
    assert not forbidden_present, f"Forbidden schema fields found: {forbidden_present}"


def test_missing_weights_output_converts_to_schema() -> None:
    handler = McdaWeightsHandler()

    payload = handler.prepare_weights(CRITERIA_NAMES).to_dict()
    response = McdaWeightsBundleResponse(**payload)
    serialized = model_to_dict(response)

    assert response.weights_status == "weights_missing"
    assert response.weights == {}
    assert response.expert_validated is False
    assert response.missing_weight_criteria == CRITERIA_NAMES
    assert response.extra_weight_criteria == []
    assert response.weights_status == payload["weights_status"]
    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules

    assert_forbidden_fields_absent(payload)
    assert_forbidden_fields_absent(serialized)
    assert_schema_has_no_forbidden_model_fields()


def test_temporary_weights_output_converts_to_schema() -> None:
    handler = McdaWeightsHandler()
    supplied_weights = {
        "removal_evidence_coverage": 2,
        "site_suitability": 1,
        "unknown_future_criterion": 5,
    }

    payload = handler.prepare_weights(
        CRITERIA_NAMES,
        supplied_weights=supplied_weights,
        weights_source="temporary_user_supplied",
        expert_validated=False,
    ).to_dict()
    response = McdaWeightsBundleResponse(**payload)
    serialized = model_to_dict(response)

    assert response.weights_status == "temporary_not_expert_validated"
    assert response.weights_status == payload["weights_status"]
    assert response.expert_validated is False
    assert abs(sum(response.weights.values()) - 1.0) < 0.000001
    assert response.weights["removal_evidence_coverage"] == 2 / 3
    assert response.weights["site_suitability"] == 1 / 3
    assert "unknown_future_criterion" not in response.weights
    assert response.missing_weight_criteria == ["cost_indicator"]
    assert response.extra_weight_criteria == ["unknown_future_criterion"]
    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules

    assert_forbidden_fields_absent(payload)
    assert_forbidden_fields_absent(serialized)
    assert_schema_has_no_forbidden_model_fields()


def main() -> None:
    test_missing_weights_output_converts_to_schema()
    test_temporary_weights_output_converts_to_schema()
    print("mcda weights schema conversion checks ok: real Step H output validates")


if __name__ == "__main__":
    main()

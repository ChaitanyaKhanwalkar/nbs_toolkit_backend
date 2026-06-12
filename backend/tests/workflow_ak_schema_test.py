r"""Smoke tests for A-K ScientificWorkflowResultResponse schema output.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\workflow_ak_schema_test.py

These tests only validate Pydantic response shapes. They do not connect to
Azure, mutate data, call API routes, create final recommendations, create
match_score fields, classify health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.schemas import ScientificWorkflowResultResponse
from plant_matching_schema_test import minimal_bundle as plant_matching_bundle_model
from workflow_aj_schema_test import completed_aj_payload, model_to_dict
from workflow_schema_test import (
    candidate_filter_payload,
    input_context_payload,
    pollutant_gap_payload,
    treatment_need_payload,
    water_bundle_payload,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "health_risk",
    "recommend_endpoint",
    "api_route",
    "ahp",
    "ahp_weight",
}


def completed_ak_payload() -> dict[str, Any]:
    """Return a complete A-K workflow response payload."""

    payload = completed_aj_payload()
    payload["step_completed"] = "K"
    payload["plant_matching_bundle"] = model_to_dict(plant_matching_bundle_model())
    return payload


def assert_completed_ak_workflow_schema_validates() -> None:
    """A completed A-K workflow should validate with Step K output."""

    response = ScientificWorkflowResultResponse(**completed_ak_payload())
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "K"
    assert dump["topsis_ranking_bundle"]["ranking_method"] == "topsis"
    assert dump["confidence_scoring_bundle"]["confidence_method"] == "rule_based_v1"
    assert dump["plant_matching_bundle"]["plant_matching_method"] == "explicit_mapping_v1"
    assert dump["plant_matching_bundle"]["candidate_matches"][0]["rank"] == 1
    assert dump["plant_matching_bundle"]["candidate_matches"][0]["confidence_score"] == 0.90


def assert_optional_plant_matching_bundle_can_be_absent() -> None:
    """A-E and A-J workflow outputs should remain schema-compatible."""

    ae_response = ScientificWorkflowResultResponse(
        workflow_status="completed",
        step_completed="E",
        input_context=input_context_payload(),
        water_input_bundle=water_bundle_payload(),
        pollutant_gap_bundle=pollutant_gap_payload(),
        treatment_need_bundle=treatment_need_payload(),
        candidate_filter_bundle=candidate_filter_payload(),
        errors=[],
        warnings=[],
    )
    aj_response = ScientificWorkflowResultResponse(**completed_aj_payload())

    assert ae_response.model_dump()["plant_matching_bundle"] is None
    assert aj_response.model_dump()["plant_matching_bundle"] is None


def assert_forbidden_fields_are_absent() -> None:
    """A-K workflow schema dumps must not include final recommendation fields."""

    payloads = [
        ScientificWorkflowResultResponse(**completed_ak_payload()).model_dump(),
        ScientificWorkflowResultResponse(**completed_aj_payload()).model_dump(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))
    found.update(
        key.lower()
        for key in ScientificWorkflowResultResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"A-K workflow schema leaked fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The workflow schema test should stay in schemas and avoid API behavior."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


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
    """Run all A-K workflow schema checks."""

    assert_completed_ak_workflow_schema_validates()
    assert_optional_plant_matching_bundle_can_be_absent()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow A-K schema checks ok: optional Step K response shape only")


if __name__ == "__main__":
    main()

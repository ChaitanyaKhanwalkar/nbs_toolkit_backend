r"""Smoke tests for A-L ScientificWorkflowResultResponse schema output.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\workflow_al_schema_test.py

These tests only validate Pydantic response shapes. They do not connect to
Azure, mutate data, call API routes, create `/recommend`, classify health risk,
or calculate AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.schemas import ScientificWorkflowResultResponse
from recommendation_assembly_schema_test import minimal_bundle as assembly_bundle_model
from workflow_ak_schema_test import completed_ak_payload
from workflow_aj_schema_test import completed_aj_payload, model_to_dict
from workflow_schema_test import (
    candidate_filter_payload,
    input_context_payload,
    pollutant_gap_payload,
    treatment_need_payload,
    water_bundle_payload,
)


FORBIDDEN_FIELDS = {
    "health_risk",
    "recommend_endpoint",
    "api_route",
    "endpoint",
    "route",
    "ahp",
    "ahp_weight",
}


def completed_al_payload() -> dict[str, Any]:
    """Return a complete A-L workflow response payload."""

    payload = completed_ak_payload()
    payload["step_completed"] = "L"
    payload["recommendation_assembly_bundle"] = model_to_dict(
        assembly_bundle_model()
    )
    return payload


def assert_completed_al_workflow_schema_validates() -> None:
    """A completed A-L workflow should validate with Step L assembly output."""

    response = ScientificWorkflowResultResponse(**completed_al_payload())
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "L"
    assert dump["plant_matching_bundle"]["plant_matching_method"] == (
        "explicit_mapping_v1"
    )
    assert dump["recommendation_assembly_bundle"]["assembly_method"] == (
        "rank_confidence_plants_v1"
    )
    recommendation = dump["recommendation_assembly_bundle"]["recommendations"][0]
    assert recommendation["rank"] == 1
    assert recommendation["match_score"] == recommendation["topsis_closeness"]
    assert recommendation["confidence_score"] != recommendation["match_score"]
    assert dump["recommendation_assembly_bundle"]["weights_status"] == (
        "temporary_not_expert_validated"
    )


def assert_optional_recommendation_assembly_can_be_absent() -> None:
    """A-E, A-J, and A-K workflow outputs should remain schema-compatible."""

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
    ak_response = ScientificWorkflowResultResponse(**completed_ak_payload())

    assert ae_response.model_dump()["recommendation_assembly_bundle"] is None
    assert aj_response.model_dump()["recommendation_assembly_bundle"] is None
    assert ak_response.model_dump()["recommendation_assembly_bundle"] is None


def assert_forbidden_fields_are_absent() -> None:
    """A-L workflow schema dumps must not include API, AHP, or health-risk fields."""

    payloads = [
        ScientificWorkflowResultResponse(**completed_al_payload()).model_dump(),
        ScientificWorkflowResultResponse(**completed_ak_payload()).model_dump(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))
    found.update(
        key.lower()
        for key in ScientificWorkflowResultResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"A-L workflow schema leaked fields: {sorted(found)}"


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
    """Run all A-L workflow schema checks."""

    assert_completed_al_workflow_schema_validates()
    assert_optional_recommendation_assembly_can_be_absent()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow A-L schema checks ok: optional Step L response shape only")


if __name__ == "__main__":
    main()

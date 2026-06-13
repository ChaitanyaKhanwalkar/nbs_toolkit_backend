r"""Conversion test from A-L ScientificWorkflowService output to workflow schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\workflow_al_schema_conversion_test.py

This test uses fake/local standards, fake NbS catalogue providers, fake numeric
MCDA criteria, fake temporary weights, and fake explicit plant mappings. It does
not connect to Azure, mutate data, call API routes, create `/recommend`,
classify health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.schemas import ScientificWorkflowResultResponse
from scientific_workflow_service_al_test import run_al_workflow
from scientific_workflow_service_ak_test import (
    build_raw_input,
    run_aj_workflow,
    run_ak_workflow,
    workflow_service,
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
    """Run the real A-L workflow service and return dictionary output."""

    return run_al_workflow().to_dict()


def completed_ak_payload() -> dict[str, Any]:
    """Run the real A-K workflow service and return dictionary output."""

    return run_ak_workflow().to_dict()


def completed_aj_payload() -> dict[str, Any]:
    """Run the real A-J workflow service and return dictionary output."""

    return run_aj_workflow().to_dict()


def completed_ae_payload() -> dict[str, Any]:
    """Run the default A-E workflow service and return dictionary output."""

    return workflow_service().run(build_raw_input()).to_dict()


def assert_completed_al_output_validates() -> None:
    """A real completed A-L output should validate against the schema."""

    payload = completed_al_payload()
    response = ScientificWorkflowResultResponse(**payload)
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "L"
    assert dump["plant_matching_bundle"]["plant_matching_method"] == (
        "explicit_mapping_v1"
    )
    assert dump["recommendation_assembly_bundle"]["assembly_method"] == (
        "rank_confidence_plants_v1"
    )
    assert dump["recommendation_assembly_bundle"]["recommendations"]
    assert dump["recommendation_assembly_bundle"]["weights_status"] == (
        "temporary_not_expert_validated"
    )
    assert dump["recommendation_assembly_bundle"]["expert_validated"] is False


def assert_rank_match_score_and_confidence_survive_conversion() -> None:
    """Schema conversion should preserve Step I/J/L values."""

    dump = ScientificWorkflowResultResponse(**completed_al_payload()).model_dump()

    ranked_candidates = dump["topsis_ranking_bundle"]["ranked_candidates"]
    confidence_results = dump["confidence_scoring_bundle"]["results"]
    recommendations = dump["recommendation_assembly_bundle"]["recommendations"]

    assert [recommendation["rank"] for recommendation in recommendations] == [
        candidate["rank"] for candidate in ranked_candidates
    ]
    assert [recommendation["match_score"] for recommendation in recommendations] == [
        candidate["topsis_closeness"] for candidate in ranked_candidates
    ]
    assert [
        recommendation["topsis_closeness"] for recommendation in recommendations
    ] == [
        candidate["topsis_closeness"] for candidate in ranked_candidates
    ]
    assert [
        recommendation["confidence_score"] for recommendation in recommendations
    ] == [
        confidence["confidence_score"] for confidence in confidence_results
    ]
    assert all(
        recommendation["confidence_score"] != recommendation["match_score"]
        for recommendation in recommendations
    )


def assert_earlier_workflow_outputs_still_validate_without_step_l() -> None:
    """A-E, A-J, and A-K outputs should keep assembly optional."""

    ae_dump = ScientificWorkflowResultResponse(**completed_ae_payload()).model_dump()
    aj_dump = ScientificWorkflowResultResponse(**completed_aj_payload()).model_dump()
    ak_dump = ScientificWorkflowResultResponse(**completed_ak_payload()).model_dump()

    assert ae_dump["step_completed"] == "E"
    assert ae_dump["recommendation_assembly_bundle"] is None
    assert aj_dump["step_completed"] == "J"
    assert aj_dump["recommendation_assembly_bundle"] is None
    assert ak_dump["step_completed"] == "K"
    assert ak_dump["recommendation_assembly_bundle"] is None


def assert_forbidden_fields_are_absent() -> None:
    """Converted workflow schema dumps must not include API, AHP, or health fields."""

    payloads = [
        ScientificWorkflowResultResponse(**completed_al_payload()).model_dump(),
        ScientificWorkflowResultResponse(**completed_ak_payload()).model_dump(),
        ScientificWorkflowResultResponse(**completed_aj_payload()).model_dump(),
        ScientificWorkflowResultResponse(**completed_ae_payload()).model_dump(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))
    found.update(
        key.lower()
        for key in ScientificWorkflowResultResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"A-L workflow schema conversion leaked fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay out of API route modules."""

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
    """Run all A-L workflow schema conversion checks."""

    assert_completed_al_output_validates()
    assert_rank_match_score_and_confidence_survive_conversion()
    assert_earlier_workflow_outputs_still_validate_without_step_l()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow A-L schema conversion checks ok: real service output validates")


if __name__ == "__main__":
    main()

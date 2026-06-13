r"""Conversion test from A-K ScientificWorkflowService output to workflow schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\workflow_ak_schema_conversion_test.py

This test uses fake/local standards, fake NbS catalogue providers, fake numeric
MCDA criteria, fake temporary weights, and fake explicit plant mappings. It does
not connect to Azure, mutate data, call API routes, create final
recommendations, create match_score fields, classify health risk, or calculate
AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.schemas import ScientificWorkflowResultResponse
from scientific_workflow_service_ak_test import (
    build_raw_input,
    run_aj_workflow,
    run_ak_workflow,
    workflow_service,
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
    """Run the real A-K workflow service and return dictionary output."""

    return run_ak_workflow().to_dict()


def completed_aj_payload() -> dict[str, Any]:
    """Run the real A-J workflow service and return dictionary output."""

    return run_aj_workflow().to_dict()


def completed_ae_payload() -> dict[str, Any]:
    """Run the default A-E workflow service and return dictionary output."""

    return workflow_service().run(build_raw_input()).to_dict()


def assert_completed_ak_output_validates() -> None:
    """A real completed A-K output should validate against the schema."""

    payload = completed_ak_payload()
    response = ScientificWorkflowResultResponse(**payload)
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "K"
    assert dump["topsis_ranking_bundle"]["ranking_method"] == "topsis"
    assert dump["confidence_scoring_bundle"]["confidence_method"] == "rule_based_v1"
    assert dump["plant_matching_bundle"]["plant_matching_method"] == "explicit_mapping_v1"
    assert dump["plant_matching_bundle"]["candidate_matches"]
    assert any(
        "No explicit plant mappings" in warning
        for warning in dump["plant_matching_bundle"]["warnings"]
    )


def assert_rank_closeness_and_confidence_are_preserved() -> None:
    """Schema conversion should preserve Step I/J values inside Step K."""

    dump = ScientificWorkflowResultResponse(**completed_ak_payload()).model_dump()

    ranking_candidates = dump["topsis_ranking_bundle"]["ranked_candidates"]
    confidence_results = dump["confidence_scoring_bundle"]["results"]
    plant_matches = dump["plant_matching_bundle"]["candidate_matches"]

    assert [candidate["rank"] for candidate in plant_matches] == [
        candidate["rank"] for candidate in ranking_candidates
    ]
    assert [candidate["topsis_closeness"] for candidate in plant_matches] == [
        candidate["topsis_closeness"] for candidate in ranking_candidates
    ]
    assert [candidate["confidence_score"] for candidate in plant_matches] == [
        candidate["confidence_score"] for candidate in confidence_results
    ]
    assert [candidate["confidence_label"] for candidate in plant_matches] == [
        candidate["confidence_label"] for candidate in confidence_results
    ]


def assert_earlier_workflow_outputs_still_validate_without_step_k() -> None:
    """A-E and A-J outputs should keep plant_matching_bundle optional."""

    ae_dump = ScientificWorkflowResultResponse(**completed_ae_payload()).model_dump()
    aj_dump = ScientificWorkflowResultResponse(**completed_aj_payload()).model_dump()

    assert ae_dump["step_completed"] == "E"
    assert ae_dump["plant_matching_bundle"] is None
    assert aj_dump["step_completed"] == "J"
    assert aj_dump["plant_matching_bundle"] is None


def assert_forbidden_fields_are_absent() -> None:
    """Converted workflow schema dumps must not include final recommendation fields."""

    payloads = [
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

    assert not found, f"A-K workflow schema conversion leaked fields: {sorted(found)}"


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
    """Run all A-K workflow schema conversion checks."""

    assert_completed_ak_output_validates()
    assert_rank_closeness_and_confidence_are_preserved()
    assert_earlier_workflow_outputs_still_validate_without_step_k()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow A-K schema conversion checks ok: real service output validates")


if __name__ == "__main__":
    main()

r"""Conversion test from A-J ScientificWorkflowService output to workflow schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\workflow_aj_schema_conversion_test.py

This test uses fake/local standards, fake NbS catalogue providers, fake numeric
MCDA criteria, and fake temporary weights. It does not connect to Azure, mutate
data, call API routes, create final recommendations, recommend plants, classify
health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.schemas import ScientificWorkflowResultResponse
from scientific_workflow_service_aj_test import (
    build_raw_input,
    run_aj_workflow,
    workflow_service,
)


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


def completed_aj_payload() -> dict[str, Any]:
    """Run the real A-J workflow service and return dictionary output."""

    return run_aj_workflow().to_dict()


def completed_ae_payload() -> dict[str, Any]:
    """Run the default A-E workflow service and return dictionary output."""

    return workflow_service().run(build_raw_input()).to_dict()


def validation_failed_payload() -> dict[str, Any]:
    """Run the workflow service with missing use_case and return output."""

    return workflow_service().run({"measured_observations": []}, max_step="J").to_dict()


def assert_completed_aj_output_validates() -> None:
    """A real completed A-J output should validate against the schema."""

    payload = completed_aj_payload()
    response = ScientificWorkflowResultResponse(**payload)
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "J"
    assert dump["mcda_matrix_bundle"] is not None
    assert dump["normalized_mcda_matrix_bundle"] is not None
    assert dump["mcda_weights_bundle"]["weights_status"] == (
        "temporary_not_expert_validated"
    )
    assert dump["mcda_weights_bundle"]["expert_validated"] is False
    assert dump["topsis_ranking_bundle"]["ranking_method"] == "topsis"
    assert dump["topsis_ranking_bundle"]["weights_status"] == (
        "temporary_not_expert_validated"
    )
    assert dump["confidence_scoring_bundle"]["confidence_method"] == "rule_based_v1"
    assert dump["confidence_scoring_bundle"]["weights_status"] == (
        "temporary_not_expert_validated"
    )
    assert dump["confidence_scoring_bundle"]["expert_validated"] is False
    assert dump["confidence_scoring_bundle"]["results"]

    ranking_ranks = [
        candidate["rank"]
        for candidate in dump["topsis_ranking_bundle"]["ranked_candidates"]
    ]
    confidence_ranks = [
        candidate["rank"]
        for candidate in dump["confidence_scoring_bundle"]["results"]
    ]
    assert confidence_ranks == ranking_ranks


def assert_default_ae_output_still_validates() -> None:
    """Default A-E output should remain schema-compatible."""

    payload = completed_ae_payload()
    response = ScientificWorkflowResultResponse(**payload)
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "E"
    assert dump["candidate_filter_bundle"] is not None
    assert dump["mcda_matrix_bundle"] is None
    assert dump["confidence_scoring_bundle"] is None


def assert_validation_failed_output_validates() -> None:
    """Early-stop validation output should remain schema-compatible."""

    payload = validation_failed_payload()
    response = ScientificWorkflowResultResponse(**payload)
    dump = response.model_dump()

    assert dump["workflow_status"] == "validation_failed"
    assert dump["step_completed"] == "A"
    assert dump["input_context"]["validation_status"] == "invalid"
    assert dump["water_input_bundle"] is None
    assert dump["confidence_scoring_bundle"] is None
    assert dump["errors"] == ["use_case is required."]


def assert_forbidden_fields_are_absent() -> None:
    """Converted workflow schema dumps must not include final recommendation fields."""

    payloads = [
        ScientificWorkflowResultResponse(**completed_aj_payload()).model_dump(),
        ScientificWorkflowResultResponse(**completed_ae_payload()).model_dump(),
        ScientificWorkflowResultResponse(**validation_failed_payload()).model_dump(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))
    found.update(
        key.lower()
        for key in ScientificWorkflowResultResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"A-J workflow schema conversion leaked fields: {sorted(found)}"


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
    """Run all A-J workflow schema conversion checks."""

    assert_completed_aj_output_validates()
    assert_default_ae_output_still_validates()
    assert_validation_failed_output_validates()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow A-J schema conversion checks ok: real service output validates")


if __name__ == "__main__":
    main()

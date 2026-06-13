r"""Smoke tests for A-J ScientificWorkflowResultResponse schema output.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\workflow_aj_schema_test.py

These tests only validate Pydantic response shapes. They do not connect to
Azure, mutate data, call API routes, create final recommendations, recommend
plants, classify health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.schemas import ScientificWorkflowResultResponse
from confidence_scoring_schema_test import minimal_bundle as confidence_bundle_model
from topsis_ranking_schema_test import minimal_bundle as topsis_bundle_model
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


def mcda_matrix_payload() -> dict[str, Any]:
    """Return a minimal Step F response payload."""

    return {
        "use_case": "surface_discharge",
        "treatment_need_groups": ["organic_load"],
        "row_count": 1,
        "excluded_ineligible_count": 0,
        "criteria_names": ["removal_evidence_coverage", "site_suitability"],
        "rows": [
            {
                "nbs_id": 1,
                "nbs_name": "Horizontal wetland",
                "eligibility_status": "eligible",
                "supported_treatment_needs": ["organic_load"],
                "criteria_values": {
                    "removal_evidence_coverage": 0.9,
                    "site_suitability": 0.8,
                },
                "missing_criteria": [],
                "caution_flags": [],
                "source_ids": [31],
                "notes": ["Step F raw matrix row only."],
            }
        ],
        "missing_criteria_summary": {},
        "warnings": [],
        "weights_status": "not_applied",
    }


def normalized_matrix_payload() -> dict[str, Any]:
    """Return a minimal Step G response payload."""

    return {
        "use_case": "surface_discharge",
        "treatment_need_groups": ["organic_load"],
        "row_count": 1,
        "criteria_names": ["removal_evidence_coverage", "site_suitability"],
        "rows": [
            {
                "nbs_id": 1,
                "nbs_name": "Horizontal wetland",
                "eligibility_status": "eligible",
                "supported_treatment_needs": ["organic_load"],
                "normalized_criteria": [
                    {
                        "criterion_name": "removal_evidence_coverage",
                        "raw_value": 0.9,
                        "normalized_value": 1.0,
                        "direction": "benefit",
                        "normalization_status": "normalized",
                        "notes": [],
                    }
                ],
                "missing_criteria": [],
                "caution_flags": [],
                "source_ids": [31],
                "notes": ["Step G normalized matrix row only."],
            }
        ],
        "normalization_method": "min_max_unweighted",
        "weights_status": "not_applied",
        "normalized_criteria_count": 1,
        "skipped_criteria_count": 0,
        "warnings": [],
    }


def weights_payload() -> dict[str, Any]:
    """Return a minimal Step H response payload."""

    return {
        "criteria_names": ["removal_evidence_coverage", "site_suitability"],
        "weights": {
            "removal_evidence_coverage": 0.6,
            "site_suitability": 0.4,
        },
        "weights_status": "temporary_not_expert_validated",
        "weights_source": "temporary_workflow_schema_test_weights",
        "expert_validated": False,
        "missing_weight_criteria": [],
        "extra_weight_criteria": [],
        "warnings": ["Temporary weights are provisional."],
        "notes": ["Step H weights only."],
    }


def completed_aj_payload() -> dict[str, Any]:
    """Return a complete A-J workflow response payload."""

    return {
        "workflow_status": "completed",
        "step_completed": "J",
        "input_context": input_context_payload(),
        "water_input_bundle": water_bundle_payload(),
        "pollutant_gap_bundle": pollutant_gap_payload(),
        "treatment_need_bundle": treatment_need_payload(),
        "candidate_filter_bundle": candidate_filter_payload(),
        "mcda_matrix_bundle": mcda_matrix_payload(),
        "normalized_mcda_matrix_bundle": normalized_matrix_payload(),
        "mcda_weights_bundle": weights_payload(),
        "topsis_ranking_bundle": model_to_dict(topsis_bundle_model()),
        "confidence_scoring_bundle": model_to_dict(confidence_bundle_model()),
        "errors": [],
        "warnings": ["Temporary weights are provisional."],
    }


def assert_completed_aj_workflow_schema_validates() -> None:
    """A completed A-J workflow should validate with all staged bundles."""

    response = ScientificWorkflowResultResponse(**completed_aj_payload())
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "J"
    assert dump["mcda_weights_bundle"]["weights_status"] == (
        "temporary_not_expert_validated"
    )
    assert dump["topsis_ranking_bundle"]["ranking_method"] == "topsis"
    assert dump["confidence_scoring_bundle"]["confidence_method"] == "rule_based_v1"
    assert dump["confidence_scoring_bundle"]["results"][0]["rank"] == 1


def assert_backward_compatible_ae_schema_still_validates() -> None:
    """The workflow schema should still accept older A-E staged output."""

    response = ScientificWorkflowResultResponse(
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
    dump = response.model_dump()

    assert dump["step_completed"] == "E"
    assert dump["mcda_matrix_bundle"] is None
    assert dump["confidence_scoring_bundle"] is None


def assert_forbidden_fields_are_absent() -> None:
    """A-J workflow schema dumps must not include final recommendation fields."""

    payloads = [
        ScientificWorkflowResultResponse(**completed_aj_payload()).model_dump(),
        ScientificWorkflowResultResponse(
            workflow_status="completed",
            step_completed="E",
            input_context=input_context_payload(),
            water_input_bundle=water_bundle_payload(),
            pollutant_gap_bundle=pollutant_gap_payload(),
            treatment_need_bundle=treatment_need_payload(),
            candidate_filter_bundle=candidate_filter_payload(),
        ).model_dump(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))
    found.update(
        key.lower()
        for key in ScientificWorkflowResultResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"A-J workflow schema leaked fields: {sorted(found)}"


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
    """Run all A-J workflow schema checks."""

    assert_completed_aj_workflow_schema_validates()
    assert_backward_compatible_ae_schema_still_validates()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow A-J schema checks ok: staged response shape only")


if __name__ == "__main__":
    main()

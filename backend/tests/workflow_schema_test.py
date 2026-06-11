"""Smoke tests for the ScientificWorkflowResultResponse schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\workflow_schema_test.py

These tests only validate Pydantic response shapes. They do not connect to
Azure, mutate data, call API routes, or create final recommendations.
"""

import sys
from typing import Any

from app.schemas import ScientificWorkflowResultResponse


FORBIDDEN_FIELDS = {
    "recommendation",
    "ranking",
    "match_score",
    "confidence_score",
    "topsis",
    "ahp",
}


def input_context_payload(validation_status: str = "valid") -> dict[str, Any]:
    """Return a minimal Step A response payload."""

    missing_inputs = [] if validation_status == "valid" else ["use_case"]
    errors = [] if validation_status == "valid" else ["use_case is required."]
    return {
        "original_input": {"use_case": " surface discharge "},
        "normalized_input": {"use_case": "surface_discharge"},
        "validation_status": validation_status,
        "errors": errors,
        "warnings": [],
        "missing_inputs": missing_inputs,
        "available_use_cases": ["surface_discharge"],
        "data_priority_note": "user measured data > station observations > regional/catchment fallback > water_type profile fallback",
    }


def water_bundle_payload(selected_source_type: str = "user_measured") -> dict[str, Any]:
    """Return a minimal Step B response payload."""

    if selected_source_type == "missing":
        return {
            "selected_source_type": "missing",
            "observations": [],
            "observation_count": 0,
            "missing_inputs": ["water_observations"],
            "warnings": [],
            "source_ids": [],
            "use_case": "surface_discharge",
        }
    return {
        "selected_source_type": "user_measured",
        "observations": [
            {"parameter": "BOD", "value": 12.0, "unit": "mg/L", "source_id": 101}
        ],
        "observation_count": 1,
        "selected_parameters": ["BOD"],
        "missing_inputs": [],
        "warnings": [],
        "source_priority_applied": [
            "user_measured",
            "station_observations",
            "basin_observations",
            "missing",
        ],
        "data_quality_notes": ["User measured observations were selected first."],
        "provenance_notes": ["source_id values are preserved where available."],
        "source_id": 101,
        "source_ids": [101],
        "station": None,
        "basin_id": None,
        "use_case": "surface_discharge",
    }


def pollutant_gap_payload() -> dict[str, Any]:
    """Return a minimal Step C response payload."""

    return {
        "use_case": "surface_discharge",
        "selected_source_type": "user_measured",
        "total_observations_checked": 1,
        "comparable_count": 1,
        "exceedance_count": 1,
        "missing_standard_count": 0,
        "unit_mismatch_count": 0,
        "results": [
            {
                "parameter": "BOD",
                "observed_value": 12.0,
                "observed_unit": "mg/L",
                "standard_unit": "mg/L",
                "limit_low": None,
                "limit_high": 3.0,
                "comparison_type": "max_limit",
                "status": "exceeds_standard",
                "gap_value": 9.0,
                "gap_ratio": 3.0,
                "required_removal_fraction": 0.75,
                "required_removal_percent": 75.0,
                "direction": "reduce",
                "source_type": "user_measured",
                "source_id": 101,
                "source_ids": [101],
                "warnings": [],
                "notes": [],
            }
        ],
        "warnings": [],
    }


def treatment_need_payload() -> dict[str, Any]:
    """Return a minimal Step D response payload."""

    return {
        "use_case": "surface_discharge",
        "selected_source_type": "user_measured",
        "treatment_needs": [
            {
                "need_group": "organic_load",
                "triggering_parameters": ["BOD"],
                "triggering_statuses": ["exceeds_standard"],
                "max_gap_ratio": 3.0,
                "required_removal_percent_max": 75.0,
                "direction": "reduce",
                "notes": [],
                "warnings": [],
            }
        ],
        "unclassified_parameters": [],
        "warning_count": 0,
        "warnings": [],
        "source_ids": [101],
    }


def candidate_filter_payload() -> dict[str, Any]:
    """Return a minimal Step E response payload."""

    return {
        "use_case": "surface_discharge",
        "selected_source_type": "user_measured",
        "treatment_need_groups": ["organic_load"],
        "candidate_count": 1,
        "eligible_count": 1,
        "ineligible_count": 0,
        "data_pending_count": 0,
        "results": [
            {
                "nbs_id": 1,
                "nbs_name": "Horizontal wetland",
                "eligibility_status": "eligible",
                "supported_treatment_needs": ["organic_load"],
                "unsupported_treatment_needs": [],
                "data_pending_reasons": [],
                "exclusion_reasons": [],
                "caution_flags": [],
                "evidence_source_ids": [31],
                "implementation_source_ids": [20],
                "notes": [],
            }
        ],
        "warnings": [],
    }


def assert_completed_workflow_schema_validates() -> None:
    """A completed A-E workflow should validate with all staged bundles."""

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
    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "E"
    assert dump["candidate_filter_bundle"]["candidate_count"] == 1


def assert_validation_failed_workflow_schema_validates() -> None:
    """A Step A failure should validate without later workflow bundles."""

    response = ScientificWorkflowResultResponse(
        workflow_status="validation_failed",
        step_completed="A",
        input_context=input_context_payload(validation_status="invalid"),
        errors=["use_case is required."],
        warnings=[],
    )

    dump = response.model_dump()
    assert dump["workflow_status"] == "validation_failed"
    assert dump["water_input_bundle"] is None
    assert dump["candidate_filter_bundle"] is None
    assert "use_case is required." in dump["errors"]


def assert_data_missing_workflow_schema_validates() -> None:
    """A Step B data-missing result should validate with early-stop fields."""

    response = ScientificWorkflowResultResponse(
        workflow_status="data_missing",
        step_completed="B",
        input_context=input_context_payload(),
        water_input_bundle=water_bundle_payload(selected_source_type="missing"),
        errors=[],
        warnings=[],
    )

    dump = response.model_dump()
    assert dump["workflow_status"] == "data_missing"
    assert dump["water_input_bundle"]["selected_source_type"] == "missing"
    assert dump["pollutant_gap_bundle"] is None
    assert dump["treatment_need_bundle"] is None
    assert dump["candidate_filter_bundle"] is None


def assert_forbidden_fields_are_absent() -> None:
    """Workflow schema dumps must not include future recommendation/scoring fields."""

    payloads = [
        ScientificWorkflowResultResponse(
            workflow_status="completed",
            step_completed="E",
            input_context=input_context_payload(),
            water_input_bundle=water_bundle_payload(),
            pollutant_gap_bundle=pollutant_gap_payload(),
            treatment_need_bundle=treatment_need_payload(),
            candidate_filter_bundle=candidate_filter_payload(),
        ).model_dump(),
        ScientificWorkflowResultResponse(
            workflow_status="validation_failed",
            step_completed="A",
            input_context=input_context_payload(validation_status="invalid"),
            errors=["use_case is required."],
        ).model_dump(),
        ScientificWorkflowResultResponse(
            workflow_status="data_missing",
            step_completed="B",
            input_context=input_context_payload(),
            water_input_bundle=water_bundle_payload(selected_source_type="missing"),
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

    assert not found, f"Workflow schema leaked future fields: {sorted(found)}"


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
    """Run all workflow schema smoke checks."""

    assert_completed_workflow_schema_validates()
    assert_validation_failed_workflow_schema_validates()
    assert_data_missing_workflow_schema_validates()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow schema checks ok: ScientificWorkflowResultResponse only")


if __name__ == "__main__":
    main()

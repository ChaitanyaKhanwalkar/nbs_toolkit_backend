"""Conversion test from ScientificWorkflowService output to workflow schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\workflow_schema_conversion_test.py

This test uses fake/local standards and fake NbS catalogue providers. It does
not connect to Azure, mutate data, call API routes, or create final
recommendations.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any

from app.schemas import ScientificWorkflowResultResponse


SERVICE_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "services"
    / "scientific_workflow_service.py"
)
SERVICE_SPEC = importlib.util.spec_from_file_location(
    "scientific_workflow_service_conversion_under_test",
    SERVICE_MODULE_PATH,
)
assert SERVICE_SPEC is not None
scientific_workflow_service = importlib.util.module_from_spec(SERVICE_SPEC)
assert SERVICE_SPEC.loader is not None
sys.modules[SERVICE_SPEC.name] = scientific_workflow_service
SERVICE_SPEC.loader.exec_module(scientific_workflow_service)

ScientificWorkflowService = scientific_workflow_service.ScientificWorkflowService


FORBIDDEN_FIELDS = {
    "recommendation",
    "ranking",
    "match_score",
    "confidence_score",
    "topsis",
    "ahp",
}


class FakeStandardsService:
    """Small provider-shaped test double for Step C standards."""

    def __init__(self, standards: list[dict[str, Any]]) -> None:
        self._standards = standards

    def get_standards_for_use_case(self, use_case: str) -> list[dict[str, Any]]:
        """Return fake standard rows for the requested use case only."""

        return [
            standard
            for standard in self._standards
            if standard.get("use_case") == use_case
        ]


class FakeNbsCatalogService:
    """Small provider-shaped test double for Step E candidate profiles."""

    def __init__(self, profiles: dict[int, dict[str, Any]]) -> None:
        self.profiles = profiles

    def list_options(self) -> list[dict[str, Any]]:
        """Return fake NbS options without querying a database."""

        return [
            profile["option"]
            for profile in self.profiles.values()
            if profile.get("option")
        ]

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return one fake NbS profile."""

        return self.profiles.get(nbs_id, {})


def fake_standards_service() -> FakeStandardsService:
    """Build explicit fake standards for the workflow conversion test."""

    return FakeStandardsService(
        [
            {
                "use_case": "surface_discharge",
                "parameter": "BOD",
                "limit_high": 3.0,
                "unit": "mg/L",
            },
            {
                "use_case": "surface_discharge",
                "parameter": "TSS",
                "limit_high": 30.0,
                "unit": "mg/L",
            },
            {
                "use_case": "surface_discharge",
                "parameter": "nitrate",
                "limit_high": 10.0,
                "unit": "mg/L",
            },
        ]
    )


def nbs_profile(
    *,
    nbs_id: int,
    solution: str,
    removal_rows: list[dict[str, Any]] | None = None,
    option_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a raw Step E profile shaped like NbsCatalogService output."""

    option = {
        "id": nbs_id,
        "solution": solution,
        "family": "Test family",
        "description": "Fake workflow schema conversion catalogue row",
        "source_id": 10,
    }
    option.update(option_extra or {})
    return {
        "option": option,
        "removal_efficiencies": removal_rows or [],
        "implementation": [
            {
                "nbs_id": nbs_id,
                "implementation_steps": "Build and maintain as documented.",
                "source_id": 20,
            }
        ],
        "footprint": [],
        "criteria": [],
        "missing_sections": [],
    }


def fake_nbs_provider() -> FakeNbsCatalogService:
    """Build fake NbS profiles for Step E output conversion."""

    return FakeNbsCatalogService(
        {
            1: nbs_profile(
                nbs_id=1,
                solution="Horizontal wetland",
                removal_rows=[
                    {"parameter": "BOD", "eff_low": 60.0, "source_id": 31},
                    {"parameter": "TSS", "eff_high": 80.0, "source_id": 32},
                ],
            ),
            2: nbs_profile(
                nbs_id=2,
                solution="Catalogue-only nutrient system",
                option_extra={"supported_treatment_needs": ["nutrients"]},
            ),
        }
    )


def workflow_service() -> ScientificWorkflowService:
    """Return the internal workflow service with fake read-only providers."""

    return ScientificWorkflowService(
        standards_service=fake_standards_service(),
        nbs_provider=fake_nbs_provider(),
    )


def build_raw_input() -> dict[str, Any]:
    """Return request-like raw input for a completed A-E workflow."""

    return {
        "use_case": " surface discharge ",
        "selected_parameters": [" BOD ", " TSS ", " nitrate "],
        "measured_observations": [
            {"parameter": "BOD", "value": "12.0", "unit": "mg/L", "source_id": 101},
            {"parameter": "TSS", "value": 75.0, "unit": "mg/L", "source_id": 101},
            {"parameter": "nitrate", "value": 18.0, "unit": "mg/L", "source_id": 102},
        ],
    }


def completed_workflow_payload() -> dict[str, Any]:
    """Run the real workflow service and return its dictionary output."""

    return workflow_service().run(build_raw_input()).to_dict()


def validation_failed_payload() -> dict[str, Any]:
    """Run the real workflow service with missing use_case and return output."""

    return workflow_service().run({"measured_observations": []}).to_dict()


def assert_completed_workflow_output_validates() -> None:
    """A real completed workflow output should validate against the schema."""

    payload = completed_workflow_payload()
    response = ScientificWorkflowResultResponse(**payload)
    dump = response.model_dump()

    assert dump["workflow_status"] == "completed"
    assert dump["step_completed"] == "E"
    assert dump["input_context"]["normalized_input"]["use_case"] == "surface_discharge"
    assert dump["water_input_bundle"]["selected_source_type"] == "user_measured"
    assert dump["candidate_filter_bundle"] is not None
    assert dump["candidate_filter_bundle"]["candidate_count"] == 2


def assert_validation_failed_output_validates() -> None:
    """A real early-stop Step A output should also validate against the schema."""

    payload = validation_failed_payload()
    response = ScientificWorkflowResultResponse(**payload)
    dump = response.model_dump()

    assert dump["workflow_status"] == "validation_failed"
    assert dump["step_completed"] == "A"
    assert dump["input_context"]["validation_status"] == "invalid"
    assert dump["water_input_bundle"] is None
    assert dump["candidate_filter_bundle"] is None
    assert dump["errors"] == ["use_case is required."]


def assert_forbidden_fields_are_absent() -> None:
    """Converted workflow schema dumps must not include future scoring fields."""

    payloads = [
        ScientificWorkflowResultResponse(**completed_workflow_payload()).model_dump(),
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

    assert not found, f"Workflow schema conversion leaked fields: {sorted(found)}"


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
    """Run all workflow schema conversion checks."""

    assert_completed_workflow_output_validates()
    assert_validation_failed_output_validates()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("workflow schema conversion checks ok: real service output validates")


if __name__ == "__main__":
    main()

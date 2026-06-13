"""Smoke tests for the internal Scientific Workflow service.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\scientific_workflow_service_test.py

These tests use fake standards and fake NbS catalogue providers. They do not
connect to Azure, mutate data, call API routes, or create final recommendations.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Any

SERVICE_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "services"
    / "scientific_workflow_service.py"
)
SERVICE_SPEC = importlib.util.spec_from_file_location(
    "scientific_workflow_service_under_test",
    SERVICE_MODULE_PATH,
)
assert SERVICE_SPEC is not None
scientific_workflow_service = importlib.util.module_from_spec(SERVICE_SPEC)
assert SERVICE_SPEC.loader is not None
sys.modules[SERVICE_SPEC.name] = scientific_workflow_service
SERVICE_SPEC.loader.exec_module(scientific_workflow_service)

WORKFLOW_COMPLETED = scientific_workflow_service.WORKFLOW_COMPLETED
WORKFLOW_DATA_MISSING = scientific_workflow_service.WORKFLOW_DATA_MISSING
WORKFLOW_VALIDATION_FAILED = scientific_workflow_service.WORKFLOW_VALIDATION_FAILED
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
    """Build explicit fake standards for Step C."""

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
            {
                "use_case": "surface_discharge",
                "parameter": "DO",
                "limit_low": 5.0,
                "unit": "mg/L",
            },
        ]
    )


def nbs_profile(
    *,
    nbs_id: int,
    solution: str,
    removal_rows: list[dict[str, Any]] | None = None,
    implementation_rows: list[dict[str, Any]] | None = None,
    option_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a raw Step E profile shaped like NbsCatalogService output."""

    option = {
        "id": nbs_id,
        "solution": solution,
        "family": "Test family",
        "description": "Fake workflow-service catalogue row",
        "source_id": 10,
    }
    option.update(option_extra or {})
    implementation = implementation_rows
    if implementation is None:
        implementation = [
            {
                "nbs_id": nbs_id,
                "implementation_steps": "Build and maintain as documented.",
                "source_id": 20,
            }
        ]
    return {
        "option": option,
        "removal_efficiencies": removal_rows or [],
        "implementation": implementation,
        "footprint": [],
        "criteria": [],
        "missing_sections": [] if implementation else ["implementation"],
    }


def fake_nbs_provider() -> FakeNbsCatalogService:
    """Build fake NbS profiles that exercise Step E statuses."""

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
                solution="Catalogue-only polishing system",
                option_extra={"supported_treatment_needs": ["nutrients"]},
            ),
            3: nbs_profile(
                nbs_id=3,
                solution="Metal-only polishing unit",
                removal_rows=[
                    {"parameter": "arsenic", "eff_low": 30.0, "source_id": 33}
                ],
            ),
        }
    )


def workflow_service() -> ScientificWorkflowService:
    """Return the workflow service with fake read-only providers."""

    return ScientificWorkflowService(
        standards_service=fake_standards_service(),
        nbs_provider=fake_nbs_provider(),
    )


def build_raw_input() -> dict[str, Any]:
    """Return request-like raw input for the A-E workflow."""

    return {
        "use_case": " surface discharge ",
        "selected_parameters": [" BOD ", " TSS ", " nitrate ", " DO "],
        "measured_observations": [
            {"parameter": "BOD", "value": "12.0", "unit": "mg/L", "source_id": 101},
            {"parameter": "TSS", "value": 75.0, "unit": "mg/L", "source_id": 101},
            {"parameter": "nitrate", "value": 18.0, "unit": "mg/L", "source_id": 102},
            {"parameter": "DO", "value": 3.0, "unit": "mg/L", "source_id": 102},
        ],
    }


def assert_successful_ae_workflow() -> None:
    """The workflow service should run Steps A-E in order."""

    result = workflow_service().run(build_raw_input())

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "E"
    assert result.input_context is not None
    assert result.water_input_bundle is not None
    assert result.pollutant_gap_bundle is not None
    assert result.treatment_need_bundle is not None
    assert result.candidate_filter_bundle is not None
    assert result.input_context.normalized_input["use_case"] == "surface_discharge"
    assert result.water_input_bundle.selected_source_type == "user_measured"
    assert result.water_input_bundle.observation_count == 4
    assert result.water_input_bundle.source_ids == [101, 102]
    assert result.pollutant_gap_bundle.exceedance_count == 4
    assert result.candidate_filter_bundle.candidate_count == 3


def assert_missing_use_case_stops_at_step_a() -> None:
    """A missing required use_case should stop safely after Step A."""

    result = workflow_service().run({"measured_observations": []})

    assert result.workflow_status == WORKFLOW_VALIDATION_FAILED
    assert result.step_completed == "A"
    assert result.input_context is not None
    assert result.water_input_bundle is None
    assert result.candidate_filter_bundle is None
    assert "use_case" in result.input_context.missing_inputs
    assert result.errors


def assert_missing_water_data_returns_safe_status() -> None:
    """No measured, station, or basin water data should stop safely at Step B."""

    result = workflow_service().run({"use_case": "surface_discharge"})

    assert result.workflow_status == WORKFLOW_DATA_MISSING
    assert result.step_completed == "B"
    assert result.water_input_bundle is not None
    assert result.water_input_bundle.selected_source_type == "missing"
    assert result.water_input_bundle.observation_count == 0
    assert result.pollutant_gap_bundle is None
    assert result.candidate_filter_bundle is None


def assert_candidate_filtering_output_is_included() -> None:
    """Completed workflows should include the Step E candidate filter bundle."""

    result = workflow_service().run(build_raw_input())
    assert result.candidate_filter_bundle is not None

    statuses = {
        candidate.eligibility_status
        for candidate in result.candidate_filter_bundle.results
    }

    assert statuses == {"eligible", "data_pending", "ineligible"}
    assert result.candidate_filter_bundle.eligible_count == 1
    assert result.candidate_filter_bundle.data_pending_count == 1
    assert result.candidate_filter_bundle.ineligible_count == 1


def assert_forbidden_fields_are_absent() -> None:
    """Workflow output must not expose final recommendation or scoring fields."""

    result = workflow_service().run(build_raw_input())
    found = _find_forbidden_keys(result.to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"Scientific workflow leaked future fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The workflow service test should stay out of API route modules."""

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
    """Run all workflow service smoke checks."""

    assert_successful_ae_workflow()
    assert_missing_use_case_stops_at_step_a()
    assert_missing_water_data_returns_safe_status()
    assert_candidate_filtering_output_is_included()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("scientific workflow service checks ok: internal A-E orchestration only")


if __name__ == "__main__":
    main()

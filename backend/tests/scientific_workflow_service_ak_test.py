r"""Smoke tests for A-K orchestration in the internal Scientific Workflow service.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_workflow_service_ak_test.py

These tests use fake standards, fake NbS catalogue profiles, fake numeric MCDA
criteria, fake temporary weights, and fake explicit plant mappings. They do not
connect to Azure, mutate data, call API routes, create final recommendations,
create match_score fields, classify health risk, or calculate AHP pairwise
weights.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

SERVICE_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "services"
    / "scientific_workflow_service.py"
)
SERVICE_SPEC = importlib.util.spec_from_file_location(
    "scientific_workflow_service_ak_under_test",
    SERVICE_MODULE_PATH,
)
assert SERVICE_SPEC is not None
scientific_workflow_service = importlib.util.module_from_spec(SERVICE_SPEC)
assert SERVICE_SPEC.loader is not None
sys.modules[SERVICE_SPEC.name] = scientific_workflow_service
SERVICE_SPEC.loader.exec_module(scientific_workflow_service)

WORKFLOW_COMPLETED = scientific_workflow_service.WORKFLOW_COMPLETED
ScientificWorkflowService = scientific_workflow_service.ScientificWorkflowService

from scientific_engine_ai_integration_test import (
    add_fake_numeric_criteria,
    build_raw_input,
    fake_nbs_provider,
    fake_standards_service,
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

WEIGHT_KEYS = [
    "removal_evidence",
    "footprint",
    "cost_indicator",
    "maintenance_indicator",
    "implementation_complexity",
    "climate_site_suitability",
    "co_benefit_indicator",
    "catalogue_criteria",
    "removal_evidence_coverage",
    "removal_evidence_score",
    "site_suitability",
]


class FakePlantMappingProvider:
    """Small provider-shaped fake with explicit plant mappings only."""

    def get_plants_for_nbs(
        self,
        nbs_id: int,
        *,
        include_invasive: bool = False,
    ) -> list[dict[str, Any]]:
        """Return fake plants only for explicitly mapped NbS IDs."""

        mappings = {
            1: [
                {
                    "plant_id": 501,
                    "scientific_name": "Typha latifolia",
                    "common_name": "Broadleaf cattail",
                    "basis": "Explicit workflow-service test mapping.",
                    "source_ids": [701, 702],
                }
            ]
        }
        return list(mappings.get(nbs_id, []))


def workflow_service(
    plant_provider: FakePlantMappingProvider | None = None,
) -> ScientificWorkflowService:
    """Return the workflow service with fake read-only providers."""

    return ScientificWorkflowService(
        standards_service=fake_standards_service(),
        nbs_provider=fake_nbs_provider(),
        plant_provider=plant_provider,
    )


def temporary_weights() -> dict[str, float]:
    """Return fake temporary weights for every expected Step G criterion."""

    weights = {criterion_name: 0.0 for criterion_name in WEIGHT_KEYS}
    weights.update(
        {
            "removal_evidence_score": 5.0,
            "removal_evidence_coverage": 5.0,
            "site_suitability": 3.0,
            "cost_indicator": 2.0,
        }
    )
    return weights


def run_ak_workflow() -> Any:
    """Run the internal service through Step K."""

    return workflow_service(FakePlantMappingProvider()).run(
        build_raw_input(),
        max_step="K",
        supplied_weights=temporary_weights(),
        weights_source="temporary_workflow_ak_test_weights",
        expert_validated=False,
        matrix_transform=add_fake_numeric_criteria,
    )


def run_aj_workflow() -> Any:
    """Run the same service through Step J only."""

    return workflow_service(FakePlantMappingProvider()).run(
        build_raw_input(),
        max_step="J",
        supplied_weights=temporary_weights(),
        weights_source="temporary_workflow_ak_test_weights",
        expert_validated=False,
        matrix_transform=add_fake_numeric_criteria,
    )


def assert_default_behavior_still_stops_at_step_e() -> None:
    """Existing callers should keep the original A-E default behavior."""

    result = workflow_service(FakePlantMappingProvider()).run(build_raw_input())

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "E"
    assert result.candidate_filter_bundle is not None
    assert result.confidence_scoring_bundle is None
    assert result.plant_matching_bundle is None


def assert_max_step_j_does_not_include_plant_matching() -> None:
    """Explicit A-J behavior should remain unchanged."""

    result = run_aj_workflow()

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "J"
    assert result.confidence_scoring_bundle is not None
    assert result.plant_matching_bundle is None


def assert_max_step_k_includes_plant_matching() -> None:
    """Explicit A-K behavior should attach Step K plant matching output."""

    result = run_ak_workflow()

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "K"
    assert result.topsis_ranking_bundle is not None
    assert result.confidence_scoring_bundle is not None
    assert result.plant_matching_bundle is not None
    assert result.plant_matching_bundle.plant_matching_method == "explicit_mapping_v1"
    assert result.plant_matching_bundle.candidate_matches


def assert_step_k_preserves_rank_closeness_and_confidence() -> None:
    """Plant matching must not change upstream ranking or confidence fields."""

    result = run_ak_workflow()
    assert result.topsis_ranking_bundle is not None
    assert result.confidence_scoring_bundle is not None
    assert result.plant_matching_bundle is not None

    ranked_candidates = result.topsis_ranking_bundle.ranked_candidates
    confidence_results = result.confidence_scoring_bundle.results
    plant_matches = result.plant_matching_bundle.candidate_matches

    assert [candidate.rank for candidate in plant_matches] == [
        candidate.rank for candidate in ranked_candidates
    ]
    assert [candidate.topsis_closeness for candidate in plant_matches] == [
        candidate.topsis_closeness for candidate in ranked_candidates
    ]
    assert [candidate.confidence_score for candidate in plant_matches] == [
        candidate.confidence_score for candidate in confidence_results
    ]
    assert [candidate.confidence_label for candidate in plant_matches] == [
        candidate.confidence_label for candidate in confidence_results
    ]


def assert_missing_mapping_returns_empty_list_plus_warning() -> None:
    """Missing plant mappings should warn without guessing records."""

    result = run_ak_workflow()
    assert result.plant_matching_bundle is not None

    empty_matches = [
        candidate
        for candidate in result.plant_matching_bundle.candidate_matches
        if not candidate.plant_matches
    ]
    assert empty_matches
    assert any(
        "No explicit plant mappings" in warning
        for warning in result.plant_matching_bundle.warnings
    )


def assert_forbidden_fields_are_absent() -> None:
    """A-K workflow output must not include final recommendation fields."""

    found = _find_forbidden_keys(run_ak_workflow().to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"A-K workflow service leaked forbidden fields: {sorted(found)}"


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
    """Run all A-K workflow service checks."""

    assert_default_behavior_still_stops_at_step_e()
    assert_max_step_j_does_not_include_plant_matching()
    assert_max_step_k_includes_plant_matching()
    assert_step_k_preserves_rank_closeness_and_confidence()
    assert_missing_mapping_returns_empty_list_plus_warning()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("scientific workflow service A-K checks ok: explicit plant matching only")


if __name__ == "__main__":
    main()

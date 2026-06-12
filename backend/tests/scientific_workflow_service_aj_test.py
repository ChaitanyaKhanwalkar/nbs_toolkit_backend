r"""Smoke tests for A-J orchestration in the internal Scientific Workflow service.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_workflow_service_aj_test.py

These tests use fake standards, fake NbS catalogue profiles, fake numeric MCDA
criteria, and fake temporary weights. They do not connect to Azure, mutate data,
call API routes, create final recommendations, recommend plants, classify
health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

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
    "scientific_workflow_service_aj_under_test",
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
    "site_suitability",
]


def workflow_service() -> ScientificWorkflowService:
    """Return the workflow service with fake read-only providers."""

    return ScientificWorkflowService(
        standards_service=fake_standards_service(),
        nbs_provider=fake_nbs_provider(),
    )


def temporary_weights() -> dict[str, float]:
    """Return fake temporary weights for every expected Step G criterion."""

    weights = {criterion_name: 0.0 for criterion_name in WEIGHT_KEYS}
    weights.update(
        {
            "removal_evidence_coverage": 5.0,
            "site_suitability": 3.0,
            "cost_indicator": 2.0,
        }
    )
    return weights


def run_aj_workflow() -> Any:
    """Run the internal service through Step J."""

    return workflow_service().run(
        build_raw_input(),
        max_step="J",
        supplied_weights=temporary_weights(),
        weights_source="temporary_workflow_aj_test_weights",
        expert_validated=False,
        matrix_transform=add_fake_numeric_criteria,
    )


def assert_default_behavior_still_stops_at_step_e() -> None:
    """Existing callers should keep the original A-E default behavior."""

    result = workflow_service().run(build_raw_input())

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "E"
    assert result.candidate_filter_bundle is not None
    assert result.mcda_matrix_bundle is None
    assert result.topsis_ranking_bundle is None
    assert result.confidence_scoring_bundle is None


def assert_aj_workflow_completes_all_stages() -> None:
    """The service should run A-J when explicitly requested."""

    result = run_aj_workflow()

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "J"
    assert result.input_context is not None
    assert result.water_input_bundle is not None
    assert result.pollutant_gap_bundle is not None
    assert result.treatment_need_bundle is not None
    assert result.candidate_filter_bundle is not None
    assert result.mcda_matrix_bundle is not None
    assert result.normalized_mcda_matrix_bundle is not None
    assert result.mcda_weights_bundle is not None
    assert result.topsis_ranking_bundle is not None
    assert result.confidence_scoring_bundle is not None


def assert_weight_and_method_statuses_are_preserved() -> None:
    """A-J output should keep weight, ranking, and confidence status visible."""

    result = run_aj_workflow()
    assert result.mcda_weights_bundle is not None
    assert result.topsis_ranking_bundle is not None
    assert result.confidence_scoring_bundle is not None

    assert result.mcda_weights_bundle.weights_status == "temporary_not_expert_validated"
    assert result.mcda_weights_bundle.expert_validated is False
    assert result.topsis_ranking_bundle.ranking_method == "topsis"
    assert result.topsis_ranking_bundle.weights_status == "temporary_not_expert_validated"
    assert result.confidence_scoring_bundle.confidence_method == "rule_based_v1"
    assert result.confidence_scoring_bundle.weights_status == (
        "temporary_not_expert_validated"
    )
    assert result.confidence_scoring_bundle.expert_validated is False
    assert result.warnings


def assert_confidence_does_not_change_rank() -> None:
    """Step J confidence should preserve Step I rank values."""

    result = run_aj_workflow()
    assert result.topsis_ranking_bundle is not None
    assert result.confidence_scoring_bundle is not None

    ranking_ranks = [
        candidate.rank
        for candidate in result.topsis_ranking_bundle.ranked_candidates
    ]
    confidence_ranks = [
        candidate.rank
        for candidate in result.confidence_scoring_bundle.results
    ]

    assert ranking_ranks
    assert confidence_ranks == ranking_ranks
    assert all(
        confidence.confidence_score != confidence.topsis_closeness
        for confidence in result.confidence_scoring_bundle.results
    )


def assert_forbidden_fields_are_absent() -> None:
    """A-J workflow output must not include final recommendation fields."""

    result = run_aj_workflow()
    found = _find_forbidden_keys(result.to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"A-J workflow service leaked forbidden fields: {sorted(found)}"


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
    """Run all A-J workflow service checks."""

    assert_default_behavior_still_stops_at_step_e()
    assert_aj_workflow_completes_all_stages()
    assert_weight_and_method_statuses_are_preserved()
    assert_confidence_does_not_change_rank()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("scientific workflow service A-J checks ok: staged output only")


if __name__ == "__main__":
    main()

r"""Smoke tests for A-L orchestration in the internal Scientific Workflow service.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_workflow_service_al_test.py

These tests use fake standards, fake NbS catalogue profiles, fake numeric MCDA
criteria, fake temporary weights, and fake explicit plant mappings. They do not
connect to Azure, mutate data, call API routes, create `/recommend`, classify
health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from scientific_workflow_service_ak_test import (
    FakePlantMappingProvider,
    WORKFLOW_COMPLETED,
    add_fake_numeric_criteria,
    build_raw_input,
    run_aj_workflow,
    run_ak_workflow,
    temporary_weights,
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


def run_al_workflow() -> Any:
    """Run the internal service through explicit Step L."""

    return workflow_service(FakePlantMappingProvider()).run(
        build_raw_input(),
        max_step="L",
        supplied_weights=temporary_weights(),
        weights_source="temporary_workflow_al_test_weights",
        expert_validated=False,
        matrix_transform=add_fake_numeric_criteria,
    )


def assert_default_behavior_still_stops_at_step_e() -> None:
    """The default workflow should remain the safe A-E path."""

    result = workflow_service(FakePlantMappingProvider()).run(build_raw_input())

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "E"
    assert result.candidate_filter_bundle is not None
    assert result.plant_matching_bundle is None
    assert result.recommendation_assembly_bundle is None


def assert_max_step_j_and_k_remain_unchanged() -> None:
    """J should not include plants or assembly, while K should include plants only."""

    j_result = run_aj_workflow()
    k_result = run_ak_workflow()

    assert j_result.workflow_status == WORKFLOW_COMPLETED
    assert j_result.step_completed == "J"
    assert j_result.plant_matching_bundle is None
    assert j_result.recommendation_assembly_bundle is None

    assert k_result.workflow_status == WORKFLOW_COMPLETED
    assert k_result.step_completed == "K"
    assert k_result.plant_matching_bundle is not None
    assert k_result.recommendation_assembly_bundle is None


def assert_max_step_l_includes_recommendation_assembly() -> None:
    """Explicit L should run A-K and then internal recommendation assembly."""

    result = run_al_workflow()

    assert result.workflow_status == WORKFLOW_COMPLETED
    assert result.step_completed == "L"
    assert result.topsis_ranking_bundle is not None
    assert result.confidence_scoring_bundle is not None
    assert result.plant_matching_bundle is not None
    assert result.recommendation_assembly_bundle is not None
    assert result.recommendation_assembly_bundle.assembly_method == (
        "rank_confidence_plants_v1"
    )
    assert result.recommendation_assembly_bundle.recommendations


def assert_rank_match_score_and_confidence_are_preserved() -> None:
    """Step L should preserve rank and keep confidence separate from match score."""

    result = run_al_workflow()
    assert result.topsis_ranking_bundle is not None
    assert result.confidence_scoring_bundle is not None
    assert result.recommendation_assembly_bundle is not None

    ranked_candidates = result.topsis_ranking_bundle.ranked_candidates
    confidence_results = result.confidence_scoring_bundle.results
    assembled = result.recommendation_assembly_bundle.recommendations

    assert [item.rank for item in assembled] == [
        candidate.rank for candidate in ranked_candidates
    ]
    assert [item.match_score for item in assembled] == [
        candidate.topsis_closeness for candidate in ranked_candidates
    ]
    assert [item.topsis_closeness for item in assembled] == [
        candidate.topsis_closeness for candidate in ranked_candidates
    ]
    assert [item.confidence_score for item in assembled] == [
        confidence.confidence_score for confidence in confidence_results
    ]
    assert all(item.confidence_score != item.match_score for item in assembled)


def assert_plants_do_not_affect_rank() -> None:
    """Step L should attach supporting plants without changing ranking."""

    result = run_al_workflow()
    assert result.plant_matching_bundle is not None
    assert result.recommendation_assembly_bundle is not None

    plant_ranks = [
        candidate.rank for candidate in result.plant_matching_bundle.candidate_matches
    ]
    assembled_ranks = [
        recommendation.rank
        for recommendation in result.recommendation_assembly_bundle.recommendations
    ]

    assert assembled_ranks == plant_ranks


def assert_temporary_weights_remain_visibly_provisional() -> None:
    """Temporary weights should remain marked as non-expert validated."""

    result = run_al_workflow()
    assert result.recommendation_assembly_bundle is not None

    bundle = result.recommendation_assembly_bundle
    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False
    assert any("provisional" in warning for warning in bundle.warnings)
    assert all(
        recommendation.weights_status == "temporary_not_expert_validated"
        for recommendation in bundle.recommendations
    )


def assert_forbidden_fields_are_absent() -> None:
    """A-L workflow output must not include API, AHP, or health-risk fields."""

    found = _find_forbidden_keys(run_al_workflow().to_dict(), FORBIDDEN_FIELDS)
    assert not found, f"A-L workflow service leaked forbidden fields: {sorted(found)}"


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
    """Run all A-L workflow service checks."""

    assert_default_behavior_still_stops_at_step_e()
    assert_max_step_j_and_k_remain_unchanged()
    assert_max_step_l_includes_recommendation_assembly()
    assert_rank_match_score_and_confidence_are_preserved()
    assert_plants_do_not_affect_rank()
    assert_temporary_weights_remain_visibly_provisional()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("scientific workflow service A-L checks ok: internal assembly only")


if __name__ == "__main__":
    main()

r"""Integration smoke test for Scientific Engine Steps A through L-A.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_engine_al_integration_test.py

This test uses fake standards, fake NbS catalogue profiles, fake numeric MCDA
criteria, fake temporary weights, fake confidence scoring, fake explicit plant
mappings, and user measured observations. It does not connect to Azure, read or
mutate database records, call API routes, implement AHP pairwise weights, change
TOPSIS ranking, change confidence scores, classify health risk, or create
`/recommend`.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import RecommendationAssemblyEngine
from scientific_engine_ak_integration_test import run_ak_chain


FORBIDDEN_FIELDS = {
    "health_risk",
    "api_route",
    "recommend_endpoint",
    "endpoint",
    "route",
    "ahp",
    "ahp_weight",
}


def run_al_chain() -> dict[str, Any]:
    """Run Steps A through L-A with fake/local objects only."""

    result = run_ak_chain()
    assembly_bundle = RecommendationAssemblyEngine().assemble(
        result["ranking_bundle"],
        result["confidence_bundle"],
        result["plant_matching_bundle"],
    )
    result["assembly_bundle"] = assembly_bundle
    return result


def assert_engine_chain_runs_through_step_l_a() -> None:
    """A-L should run together and preserve staged outputs."""

    result = run_al_chain()

    assert result["ranking_bundle"].ranking_method == "topsis"
    assert result["confidence_bundle"].confidence_method == "rule_based_v1"
    assert result["plant_matching_bundle"].plant_matching_method == "explicit_mapping_v1"
    assert result["assembly_bundle"].assembly_method == "rank_confidence_plants_v1"
    assert result["assembly_bundle"].recommendations


def assert_match_score_confidence_and_rank_are_preserved() -> None:
    """Step L-A should copy TOPSIS match score and keep confidence separate."""

    result = run_al_chain()
    ranked_candidates = result["ranking_bundle"].ranked_candidates
    confidence_results = result["confidence_bundle"].results
    recommendations = result["assembly_bundle"].recommendations

    assert [recommendation.rank for recommendation in recommendations] == [
        candidate.rank for candidate in ranked_candidates
    ]
    assert [recommendation.match_score for recommendation in recommendations] == [
        candidate.topsis_closeness for candidate in ranked_candidates
    ]
    assert [recommendation.topsis_closeness for recommendation in recommendations] == [
        candidate.topsis_closeness for candidate in ranked_candidates
    ]
    assert [recommendation.confidence_score for recommendation in recommendations] == [
        confidence.confidence_score for confidence in confidence_results
    ]
    assert all(
        recommendation.confidence_score != recommendation.match_score
        for recommendation in recommendations
    )


def assert_plants_are_supporting_only() -> None:
    """Plant matches should be attached without changing rank."""

    result = run_al_chain()
    plant_candidates = result["plant_matching_bundle"].candidate_matches
    recommendations = result["assembly_bundle"].recommendations

    assert [recommendation.rank for recommendation in recommendations] == [
        candidate.rank for candidate in plant_candidates
    ]
    assert [
        [plant.plant_id for plant in recommendation.plant_matches]
        for recommendation in recommendations
    ] == [
        [plant.plant_id for plant in candidate.plant_matches]
        for candidate in plant_candidates
    ]


def assert_temporary_weights_remain_visible() -> None:
    """Temporary Step H/I weights should remain visibly provisional."""

    bundle = run_al_chain()["assembly_bundle"]

    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False
    assert all(
        recommendation.weights_status == "temporary_not_expert_validated"
        for recommendation in bundle.recommendations
    )
    assert any("provisional" in warning for warning in bundle.warnings)


def assert_no_forbidden_future_fields() -> None:
    """A-L output must not include API, AHP, or health-risk fields."""

    result = run_al_chain()
    payloads = [
        result["context"].to_dict(),
        result["water_bundle"].to_dict(),
        result["gap_bundle"].to_dict(),
        result["treatment_bundle"].to_dict(),
        result["candidate_bundle"].to_dict(),
        result["raw_matrix_bundle"].to_dict(),
        result["matrix_bundle"].to_dict(),
        result["normalized_bundle"].to_dict(),
        result["weights_bundle"].to_dict(),
        result["ranking_bundle"].to_dict(),
        result["confidence_bundle"].to_dict(),
        result["plant_matching_bundle"].to_dict(),
        result["assembly_bundle"].to_dict(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))

    assert not found, f"A-L integration leaked forbidden fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The integration test should stay in engines and avoid API behavior."""

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
    """Run the A-L integration smoke checks."""

    assert_engine_chain_runs_through_step_l_a()
    assert_match_score_confidence_and_rank_are_preserved()
    assert_plants_are_supporting_only()
    assert_temporary_weights_remain_visible()
    assert_no_forbidden_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-L integration checks ok: internal assembly only")


if __name__ == "__main__":
    main()

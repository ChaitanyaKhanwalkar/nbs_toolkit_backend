r"""Smoke tests for Scientific Engine Step L-A.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\recommendation_assembly_test.py

These tests use fake Step I ranking, fake Step J confidence, and fake Step K
plant matching only. They do not connect to Azure, mutate data, call API routes,
change TOPSIS rank, change confidence scores, classify health risk, calculate
AHP pairwise weights, or create `/recommend`.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import PlantMatchingEngine, RecommendationAssemblyEngine
from confidence_scoring_test import ranking_bundle, score_complete_expert_case
from plant_matching_test import fake_provider


FORBIDDEN_FIELDS = {
    "health_risk",
    "api_route",
    "recommend_endpoint",
    "endpoint",
    "route",
    "ahp",
    "ahp_weight",
}


def plant_bundle() -> Any:
    """Return fake Step K output for assembly tests."""

    return PlantMatchingEngine(fake_provider()).match_plants(
        ranking_bundle(),
        score_complete_expert_case(),
    )


def assembled_bundle() -> Any:
    """Run Step L-A with complete fake staged inputs."""

    return RecommendationAssemblyEngine().assemble(
        ranking_bundle(),
        score_complete_expert_case(),
        plant_bundle(),
    )


def assert_match_score_equals_topsis_closeness() -> None:
    """Step L-A should copy match_score directly from TOPSIS closeness."""

    bundle = assembled_bundle()

    assert bundle.recommendations
    for recommendation in bundle.recommendations:
        assert recommendation.match_score == recommendation.topsis_closeness


def assert_confidence_score_remains_separate() -> None:
    """Confidence should remain separate from match_score."""

    bundle = assembled_bundle()

    assert all(
        recommendation.confidence_score != recommendation.match_score
        for recommendation in bundle.recommendations
        if recommendation.confidence_score is not None
    )


def assert_rank_is_preserved_and_plants_do_not_affect_rank() -> None:
    """Ranks should match Step I whether plants are supplied or missing."""

    original_ranking = ranking_bundle()
    with_plants = assembled_bundle()
    without_plants = RecommendationAssemblyEngine().assemble(
        original_ranking,
        score_complete_expert_case(),
    )

    expected_ranks = [
        candidate.rank
        for candidate in original_ranking.ranked_candidates
    ]
    assert [recommendation.rank for recommendation in with_plants.recommendations] == expected_ranks
    assert [recommendation.rank for recommendation in without_plants.recommendations] == expected_ranks
    assert with_plants.recommendations[0].plant_matches
    assert without_plants.recommendations[0].plant_matches == []


def assert_missing_plant_bundle_is_safe() -> None:
    """Missing Step K output should produce empty plant matches and warnings."""

    bundle = RecommendationAssemblyEngine().assemble(
        ranking_bundle(),
        score_complete_expert_case(),
    )

    assert bundle.plant_matching_method is None
    assert all(not recommendation.plant_matches for recommendation in bundle.recommendations)
    assert any("PlantMatchingBundle was not provided" in warning for warning in bundle.warnings)


def assert_missing_confidence_is_safe() -> None:
    """Missing Step J output should leave confidence fields empty with warnings."""

    bundle = RecommendationAssemblyEngine().assemble(
        ranking_bundle(),
        plant_matching_bundle=plant_bundle(),
    )

    assert bundle.confidence_method is None
    assert all(
        recommendation.confidence_score is None
        for recommendation in bundle.recommendations
    )
    assert any("ConfidenceScoringBundle was not provided" in warning for warning in bundle.warnings)


def assert_temporary_weights_remain_provisional() -> None:
    """Assembly should preserve temporary Step H/I weight status."""

    bundle = RecommendationAssemblyEngine().assemble(
        ranking_bundle(
            weights_status="temporary_not_expert_validated",
            expert_validated=False,
        )
    )

    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False
    assert all(
        recommendation.weights_status == "temporary_not_expert_validated"
        for recommendation in bundle.recommendations
    )
    assert any("provisional" in warning for warning in bundle.warnings)


def assert_evidence_summary_preserves_sources_and_cautions() -> None:
    """Assembly should carry source IDs and caution flags into evidence summary."""

    recommendation = assembled_bundle().recommendations[1]

    assert recommendation.evidence_summary.source_ids
    assert recommendation.evidence_summary.caution_flags
    assert recommendation.evidence_summary.warnings


def assert_no_forbidden_fields() -> None:
    """Step L-A output must not include API, AHP, or health-risk fields."""

    found = _find_forbidden_keys(assembled_bundle().to_dict(), FORBIDDEN_FIELDS)
    assert not found, f"Step L-A leaked forbidden fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The Step L-A test should stay in engines and avoid API behavior."""

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
    """Run all Step L-A assembly checks."""

    assert_match_score_equals_topsis_closeness()
    assert_confidence_score_remains_separate()
    assert_rank_is_preserved_and_plants_do_not_affect_rank()
    assert_missing_plant_bundle_is_safe()
    assert_missing_confidence_is_safe()
    assert_temporary_weights_remain_provisional()
    assert_evidence_summary_preserves_sources_and_cautions()
    assert_no_forbidden_fields()
    assert_no_api_or_recommend_route_involved()
    print("recommendation assembly checks ok: Step L-A internal objects only")


if __name__ == "__main__":
    main()

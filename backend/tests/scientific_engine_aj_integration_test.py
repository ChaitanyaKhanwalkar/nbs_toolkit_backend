r"""Integration smoke test for Scientific Engine Steps A through J.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_engine_aj_integration_test.py

This test uses fake standards, fake NbS catalogue profiles, fake numeric MCDA
criteria, fake temporary weights, and user measured observations. It does not
connect to Azure, read or mutate database records, call API routes, calculate
AHP pairwise weights, recommend plants, classify health risk, or create final
recommendations.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import ConfidenceScoringEngine
from scientific_engine_ai_integration_test import run_ai_chain


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


def run_aj_chain() -> dict[str, Any]:
    """Run Steps A through J with fake/local objects only."""

    result = run_ai_chain()
    confidence_bundle = ConfidenceScoringEngine().score(
        result["ranking_bundle"],
        water_bundle=result["water_bundle"],
        candidate_bundle=result["candidate_bundle"],
        normalized_bundle=result["normalized_bundle"],
        weights_bundle=result["weights_bundle"],
    )
    result["confidence_bundle"] = confidence_bundle
    return result


def assert_engine_chain_runs_through_step_j() -> None:
    """A-J should run together and preserve staged outputs."""

    result = run_aj_chain()

    assert result["context"].validation_status == "valid"
    assert result["water_bundle"].selected_source_type == "user_measured"
    assert result["gap_bundle"].total_observations_checked == 4
    assert result["candidate_bundle"].candidate_count == 3
    assert result["normalized_bundle"].normalization_method == "min_max_unweighted"
    assert result["ranking_bundle"].ranking_method == "topsis"
    assert result["confidence_bundle"].confidence_method == "rule_based_v1"
    assert result["confidence_bundle"].results


def assert_confidence_preserves_topsis_rank_and_closeness() -> None:
    """Step J should report confidence without changing Step I ranking."""

    result = run_aj_chain()
    ranked_candidates = result["ranking_bundle"].ranked_candidates
    confidence_results = result["confidence_bundle"].results

    assert [candidate.rank for candidate in ranked_candidates] == [
        confidence.rank for confidence in confidence_results
    ]
    assert [candidate.topsis_closeness for candidate in ranked_candidates] == [
        confidence.topsis_closeness for confidence in confidence_results
    ]
    assert all(
        confidence.confidence_score != confidence.topsis_closeness
        for confidence in confidence_results
    )
    assert all(
        confidence.confidence_label in {"high", "medium", "low"}
        for confidence in confidence_results
    )


def assert_temporary_weights_remain_provisional() -> None:
    """Temporary Step H weights should remain visible in Step J output."""

    confidence_bundle = run_aj_chain()["confidence_bundle"]

    assert confidence_bundle.weights_status == "temporary_not_expert_validated"
    assert confidence_bundle.expert_validated is False
    assert any("provisional" in warning for warning in confidence_bundle.warnings)


def assert_no_forbidden_future_fields() -> None:
    """A-J outputs must not include final recommendation/match/plant fields."""

    result = run_aj_chain()
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
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))

    assert not found, f"A-J integration leaked forbidden fields: {sorted(found)}"


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
    """Run the A-J integration smoke checks."""

    assert_engine_chain_runs_through_step_j()
    assert_confidence_preserves_topsis_rank_and_closeness()
    assert_temporary_weights_remain_provisional()
    assert_no_forbidden_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-J integration checks ok: confidence only, no recommendation path")


if __name__ == "__main__":
    main()

r"""Smoke tests for Scientific Engine Step I.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\topsis_ranking_test.py

These tests use fake Step G normalized MCDA data and fake Step H weights only.
They do not connect to Azure, mutate data, call API routes, calculate AHP
pairwise weights, calculate confidence scores, recommend plants, classify
health risk, or create final recommendations.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import (
    McdaWeightsHandler,
    NormalizedMcdaCriterion,
    NormalizedMcdaMatrixBundle,
    NormalizedMcdaMatrixRow,
    TopsisRankingEngine,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "confidence_score",
    "plant_recommendation",
    "plant_recommendations",
    "plants",
    "health_risk",
}

CRITERIA_NAMES = [
    "removal_evidence_coverage",
    "site_suitability",
    "cost_indicator",
    "maintenance_indicator",
    "custom_metric",
    "climate_suitability",
]


def fake_normalized_bundle() -> NormalizedMcdaMatrixBundle:
    """Build fake Step G output with usable and skipped criteria."""

    rows = [
        normalized_row(
            nbs_id=1,
            nbs_name="Wetland A",
            eligibility_status="eligible",
            removal=1.0,
            site=0.8,
            cost=0.4,
        ),
        normalized_row(
            nbs_id=2,
            nbs_name="Wetland B",
            eligibility_status="data_pending",
            removal=0.2,
            site=0.6,
            cost=1.0,
        ),
        normalized_row(
            nbs_id=3,
            nbs_name="Wetland C",
            eligibility_status="eligible",
            removal=0.5,
            site=0.4,
            cost=0.6,
        ),
    ]
    return NormalizedMcdaMatrixBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=len(rows),
        criteria_names=CRITERIA_NAMES,
        rows=rows,
        normalization_method="min_max_unweighted",
        weights_status="not_applied",
        normalized_criteria_count=9,
        skipped_criteria_count=9,
        warnings=["Criterion 'climate_suitability' has no variation."],
    )


def normalized_row(
    *,
    nbs_id: int,
    nbs_name: str,
    eligibility_status: str,
    removal: float,
    site: float,
    cost: float,
) -> NormalizedMcdaMatrixRow:
    """Build one normalized row with three usable and three skipped criteria."""

    return NormalizedMcdaMatrixRow(
        nbs_id=nbs_id,
        nbs_name=nbs_name,
        eligibility_status=eligibility_status,
        supported_treatment_needs=["organic_load"],
        normalized_criteria=[
            NormalizedMcdaCriterion(
                criterion_name="removal_evidence_coverage",
                raw_value=removal,
                normalized_value=removal,
                direction="benefit",
                normalization_status="normalized",
            ),
            NormalizedMcdaCriterion(
                criterion_name="site_suitability",
                raw_value=site,
                normalized_value=site,
                direction="benefit",
                normalization_status="normalized",
            ),
            NormalizedMcdaCriterion(
                criterion_name="cost_indicator",
                raw_value=cost,
                normalized_value=cost,
                direction="cost",
                normalization_status="normalized",
            ),
            NormalizedMcdaCriterion(
                criterion_name="maintenance_indicator",
                raw_value="medium",
                normalized_value=None,
                direction="cost",
                normalization_status="non_numeric",
            ),
            NormalizedMcdaCriterion(
                criterion_name="custom_metric",
                raw_value=4.0,
                normalized_value=None,
                direction="unknown",
                normalization_status="direction_unknown",
            ),
            NormalizedMcdaCriterion(
                criterion_name="climate_suitability",
                raw_value=0.5,
                normalized_value=None,
                direction="benefit",
                normalization_status="no_variation",
            ),
        ],
        source_ids=[nbs_id + 100],
        notes=["Fake Step G row for TOPSIS testing."],
    )


def fake_temporary_weights() -> Any:
    """Build temporary Step H weights that are intentionally not expert-final."""

    return McdaWeightsHandler().prepare_weights(
        CRITERIA_NAMES,
        supplied_weights={
            "removal_evidence_coverage": 5,
            "site_suitability": 3,
            "cost_indicator": 2,
            "maintenance_indicator": 0,
            "custom_metric": 0,
            "climate_suitability": 0,
        },
        weights_source="temporary_topsis_test_weights",
        expert_validated=False,
    )


def fake_missing_weights() -> Any:
    """Build a safe missing-weights Step H bundle."""

    return McdaWeightsHandler().prepare_weights(CRITERIA_NAMES)


def rank_with_temporary_weights() -> Any:
    """Run Step I with fake normalized data and temporary weights."""

    return TopsisRankingEngine().rank(
        fake_normalized_bundle(),
        fake_temporary_weights(),
    )


def assert_missing_weights_prevent_ranking_safely() -> None:
    """Missing weights should return no ranked candidates and a warning."""

    bundle = TopsisRankingEngine().rank(
        fake_normalized_bundle(),
        fake_missing_weights(),
    )

    assert bundle.weights_status == "weights_missing"
    assert bundle.ranked_count == 0
    assert bundle.ranked_candidates == []
    assert bundle.criteria_used == []
    assert bundle.criteria_skipped == CRITERIA_NAMES
    assert any("weights are missing" in warning for warning in bundle.warnings)


def assert_temporary_weights_allow_provisional_ranking() -> None:
    """Temporary weights may rank, but the result must stay provisional."""

    bundle = rank_with_temporary_weights()

    assert bundle.ranking_method == "topsis"
    assert bundle.ranked_count == 3
    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.weights_source == "temporary_topsis_test_weights"
    assert bundle.expert_validated is False
    assert any("provisional" in warning for warning in bundle.warnings)


def assert_weights_carry_correctly_from_step_h() -> None:
    """Step H weights should be normalized before Step I uses them."""

    weights_bundle = fake_temporary_weights()
    ranking_bundle = TopsisRankingEngine().rank(
        fake_normalized_bundle(),
        weights_bundle,
    )

    assert_close(sum(weights_bundle.weights.values()), 1.0)
    assert ranking_bundle.weights_status == weights_bundle.weights_status
    assert ranking_bundle.weights_source == weights_bundle.weights_source
    assert ranking_bundle.expert_validated == weights_bundle.expert_validated


def assert_skipped_criteria_are_not_used() -> None:
    """Criteria not normalized by Step G should not enter TOPSIS."""

    bundle = rank_with_temporary_weights()

    assert bundle.criteria_used == [
        "removal_evidence_coverage",
        "site_suitability",
        "cost_indicator",
    ]
    assert bundle.criteria_skipped == [
        "maintenance_indicator",
        "custom_metric",
        "climate_suitability",
    ]
    for candidate in bundle.ranked_candidates:
        contribution_names = {
            contribution.criterion_name
            for contribution in candidate.criterion_contributions
        }
        assert contribution_names == set(bundle.criteria_used)


def assert_ranking_order_follows_closeness_descending() -> None:
    """Candidates should be ordered by highest TOPSIS closeness first."""

    bundle = rank_with_temporary_weights()
    ranked_ids = [candidate.nbs_id for candidate in bundle.ranked_candidates]
    closeness_values = [
        candidate.topsis_closeness
        for candidate in bundle.ranked_candidates
    ]

    assert ranked_ids == [1, 3, 2]
    assert closeness_values == sorted(closeness_values, reverse=True)


def assert_rank_values_are_assigned() -> None:
    """Rank numbers should start at 1 and follow sorted order."""

    bundle = rank_with_temporary_weights()

    assert [candidate.rank for candidate in bundle.ranked_candidates] == [1, 2, 3]
    for candidate in bundle.ranked_candidates:
        assert candidate.distance_to_ideal_best is not None
        assert candidate.distance_to_ideal_worst is not None
        assert candidate.topsis_closeness is not None


def assert_no_future_forbidden_fields() -> None:
    """Step I output must not include final recommendation/confidence fields."""

    found = _find_forbidden_keys(
        rank_with_temporary_weights().to_dict(),
        FORBIDDEN_FIELDS,
    )

    assert not found, f"Step I leaked future fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The Step I test should stay in engines and avoid API behavior."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def assert_close(actual: float | None, expected: float) -> None:
    """Assert float equality with a tiny tolerance."""

    assert actual is not None
    assert abs(actual - expected) < 0.000001


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
    """Run all Step I checks."""

    assert_missing_weights_prevent_ranking_safely()
    assert_temporary_weights_allow_provisional_ranking()
    assert_weights_carry_correctly_from_step_h()
    assert_skipped_criteria_are_not_used()
    assert_ranking_order_follows_closeness_descending()
    assert_rank_values_are_assigned()
    assert_no_future_forbidden_fields()
    assert_no_api_or_recommend_route_involved()
    print("topsis ranking checks ok: Step I ranking only, no recommendation path")


if __name__ == "__main__":
    main()

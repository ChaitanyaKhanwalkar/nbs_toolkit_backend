r"""Smoke tests for Scientific Engine Step J.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\confidence_scoring_test.py

These tests use fake Step I ranking and supporting bundles only. They do not
connect to Azure, mutate data, call API routes, change TOPSIS rank, implement
AHP pairwise weights, recommend plants, classify health risk, or create final
recommendations.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from typing import Any

from app.engines import (
    CandidateFilterBundle,
    CandidateFilterResult,
    ConfidenceScoringEngine,
    McdaWeightsHandler,
    NormalizedMcdaCriterion,
    NormalizedMcdaMatrixBundle,
    NormalizedMcdaMatrixRow,
    TopsisCriterionContribution,
    TopsisRankedCandidate,
    TopsisRankingBundle,
    WaterInputBundle,
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
    "ahp",
    "ahp_weight",
}

CRITERIA_NAMES = [
    "removal_evidence_coverage",
    "site_suitability",
    "cost_indicator",
]


def ranked_candidate(
    *,
    nbs_id: int,
    nbs_name: str,
    rank: int,
    closeness: float,
    caution_flags: list[str] | None = None,
) -> TopsisRankedCandidate:
    """Build one fake Step I ranked candidate."""

    return TopsisRankedCandidate(
        nbs_id=nbs_id,
        nbs_name=nbs_name,
        eligibility_status="eligible" if nbs_id == 1 else "data_pending",
        rank=rank,
        topsis_closeness=closeness,
        distance_to_ideal_best=0.10 * rank,
        distance_to_ideal_worst=0.40,
        criterion_contributions=[
            TopsisCriterionContribution(
                criterion_name="removal_evidence_coverage",
                normalized_value=0.8,
                weight=0.5,
                weighted_value=0.4,
            )
        ],
        caution_flags=caution_flags or [],
        source_ids=[100 + nbs_id],
        notes=["Fake Step I ranked candidate for confidence testing."],
    )


def ranking_bundle(
    *,
    candidates: list[TopsisRankedCandidate] | None = None,
    weights_status: str = "expert_validated",
    expert_validated: bool = True,
    criteria_used: list[str] | None = None,
    criteria_skipped: list[str] | None = None,
) -> TopsisRankingBundle:
    """Build fake Step I output without running TOPSIS."""

    ranked_candidates = candidates
    if ranked_candidates is None:
        ranked_candidates = [
            ranked_candidate(
                nbs_id=1,
                nbs_name="High confidence wetland",
                rank=1,
                closeness=0.82,
            ),
            ranked_candidate(
                nbs_id=2,
                nbs_name="Data pending polishing system",
                rank=2,
                closeness=0.61,
                caution_flags=["Pathogen contact caution."],
            ),
        ]
    return TopsisRankingBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=len(ranked_candidates),
        ranked_count=len(ranked_candidates),
        criteria_used=criteria_used if criteria_used is not None else list(CRITERIA_NAMES),
        criteria_skipped=criteria_skipped if criteria_skipped is not None else [],
        weights_status=weights_status,
        weights_source="fake_confidence_test_weights",
        expert_validated=expert_validated,
        ranking_method="topsis",
        ranked_candidates=ranked_candidates,
        warnings=[],
    )


def candidate_bundle() -> CandidateFilterBundle:
    """Build fake Step E output with one strong and one data-pending candidate."""

    results = [
        CandidateFilterResult(
            nbs_id=1,
            nbs_name="High confidence wetland",
            eligibility_status="eligible",
            supported_treatment_needs=["organic_load", "solids"],
            evidence_source_ids=[31, 32],
            implementation_source_ids=[41],
        ),
        CandidateFilterResult(
            nbs_id=2,
            nbs_name="Data pending polishing system",
            eligibility_status="data_pending",
            supported_treatment_needs=["organic_load"],
            unsupported_treatment_needs=["solids"],
            data_pending_reasons=["Implementation guidance is missing."],
            caution_flags=["Pathogen contact caution."],
        ),
    ]
    return CandidateFilterBundle(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        treatment_need_groups=["organic_load", "solids"],
        candidate_count=len(results),
        eligible_count=1,
        data_pending_count=1,
        results=results,
        warnings=[],
    )


def water_bundle(
    *,
    selected_source_type: str = "user_measured",
    observation_count: int = 3,
) -> WaterInputBundle:
    """Build fake Step B water input output."""

    observations = [
        {"parameter": "BOD", "value": 12.0, "unit": "mg/L", "source_id": 101},
        {"parameter": "TSS", "value": 75.0, "unit": "mg/L", "source_id": 102},
        {"parameter": "nitrate", "value": 18.0, "unit": "mg/L", "source_id": 103},
    ][:observation_count]
    return WaterInputBundle(
        selected_source_type=selected_source_type,
        observations=observations,
        observation_count=observation_count,
        selected_parameters=["BOD", "TSS", "nitrate"],
        source_ids=[101, 102, 103][:observation_count],
        use_case="surface_discharge",
    )


def normalized_bundle(
    *,
    normalized_count: int = 6,
    skipped_count: int = 0,
) -> NormalizedMcdaMatrixBundle:
    """Build fake Step G normalized matrix output."""

    rows = [
        NormalizedMcdaMatrixRow(
            nbs_id=1,
            nbs_name="High confidence wetland",
            eligibility_status="eligible",
            supported_treatment_needs=["organic_load", "solids"],
            normalized_criteria=[
                NormalizedMcdaCriterion(
                    criterion_name=criterion_name,
                    raw_value=1.0,
                    normalized_value=1.0,
                    direction="benefit",
                    normalization_status="normalized",
                )
                for criterion_name in CRITERIA_NAMES
            ],
            source_ids=[31, 32],
        ),
        NormalizedMcdaMatrixRow(
            nbs_id=2,
            nbs_name="Data pending polishing system",
            eligibility_status="data_pending",
            supported_treatment_needs=["organic_load"],
            normalized_criteria=[
                NormalizedMcdaCriterion(
                    criterion_name=criterion_name,
                    raw_value=0.5,
                    normalized_value=0.5,
                    direction="benefit",
                    normalization_status="normalized",
                )
                for criterion_name in CRITERIA_NAMES
            ],
            caution_flags=["Pathogen contact caution."],
            source_ids=[61],
        ),
    ]
    return NormalizedMcdaMatrixBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=len(rows),
        criteria_names=list(CRITERIA_NAMES),
        rows=rows,
        normalization_method="min_max_unweighted",
        weights_status="not_applied",
        normalized_criteria_count=normalized_count,
        skipped_criteria_count=skipped_count,
        warnings=[],
    )


def expert_weights() -> Any:
    """Build explicitly expert-marked fake Step H weights."""

    return McdaWeightsHandler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 5,
            "site_suitability": 3,
            "cost_indicator": 2,
        },
        weights_source="fake_expert_sheet",
        expert_validated=True,
    )


def temporary_weights() -> Any:
    """Build temporary fake Step H weights."""

    return McdaWeightsHandler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 5,
            "site_suitability": 3,
            "cost_indicator": 2,
        },
        weights_source="temporary_confidence_test_weights",
        expert_validated=False,
    )


def missing_weights() -> Any:
    """Build safe missing Step H weights."""

    return McdaWeightsHandler().prepare_weights(CRITERIA_NAMES)


def score_complete_expert_case() -> Any:
    """Run Step J with complete fake supporting bundles."""

    return ConfidenceScoringEngine().score(
        ranking_bundle(),
        water_bundle=water_bundle(),
        candidate_bundle=candidate_bundle(),
        normalized_bundle=normalized_bundle(),
        weights_bundle=expert_weights(),
    )


def assert_confidence_score_is_separate_from_topsis_closeness() -> None:
    """Confidence should be generated but not equal to TOPSIS closeness."""

    bundle = score_complete_expert_case()
    first = bundle.results[0]

    assert 0.0 <= first.confidence_score <= 1.0
    assert first.confidence_score != first.topsis_closeness
    assert first.topsis_closeness == 0.82


def assert_confidence_labels_high_medium_low_work() -> None:
    """Rule-based labels should cover high, medium, and low confidence."""

    high_bundle = score_complete_expert_case()
    medium_bundle = ConfidenceScoringEngine().score(
        ranking_bundle(
            candidates=[
                ranked_candidate(
                    nbs_id=2,
                    nbs_name="Data pending polishing system",
                    rank=1,
                    closeness=0.61,
                    caution_flags=["Pathogen contact caution."],
                )
            ],
            weights_status="temporary_not_expert_validated",
            expert_validated=False,
        ),
        water_bundle=water_bundle(selected_source_type="station_observations"),
        candidate_bundle=candidate_bundle(),
        normalized_bundle=normalized_bundle(),
        weights_bundle=temporary_weights(),
    )
    low_bundle = ConfidenceScoringEngine().score(
        ranking_bundle(
            candidates=[
                ranked_candidate(
                    nbs_id=99,
                    nbs_name="Sparse evidence candidate",
                    rank=1,
                    closeness=0.40,
                    caution_flags=["Caution one.", "Caution two.", "Caution three."],
                )
            ],
            weights_status="weights_missing",
            expert_validated=False,
            criteria_used=[],
            criteria_skipped=list(CRITERIA_NAMES),
        ),
        weights_bundle=missing_weights(),
    )

    assert high_bundle.results[0].confidence_label == "high"
    assert medium_bundle.results[0].confidence_label == "medium"
    assert low_bundle.results[0].confidence_label == "low"


def assert_temporary_weights_reduce_reliability_and_warn() -> None:
    """Temporary weights should reduce reliability and stay visibly provisional."""

    bundle = ConfidenceScoringEngine().score(
        ranking_bundle(
            weights_status="temporary_not_expert_validated",
            expert_validated=False,
        ),
        water_bundle=water_bundle(),
        candidate_bundle=candidate_bundle(),
        normalized_bundle=normalized_bundle(),
        weights_bundle=temporary_weights(),
    )
    factors = {
        factor.factor_name: factor
        for factor in bundle.results[0].factors
    }

    assert factors["weights_reliability"].factor_score < 1.0
    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False
    assert any("provisional" in warning for warning in bundle.warnings)
    assert any("provisional" in warning for warning in bundle.results[0].warnings)


def assert_caution_flags_reduce_confidence() -> None:
    """Caution flags should reduce confidence without removing the candidate."""

    plain_candidate = ranked_candidate(
        nbs_id=1,
        nbs_name="High confidence wetland",
        rank=1,
        closeness=0.82,
    )
    cautious_candidate = replace(
        plain_candidate,
        caution_flags=["Caution one.", "Caution two."],
    )
    plain = ConfidenceScoringEngine().score(
        ranking_bundle(candidates=[plain_candidate]),
        water_bundle=water_bundle(),
        candidate_bundle=candidate_bundle(),
        normalized_bundle=normalized_bundle(),
        weights_bundle=expert_weights(),
    ).results[0]
    cautious = ConfidenceScoringEngine().score(
        ranking_bundle(candidates=[cautious_candidate]),
        water_bundle=water_bundle(),
        candidate_bundle=candidate_bundle(),
        normalized_bundle=normalized_bundle(),
        weights_bundle=expert_weights(),
    ).results[0]

    assert cautious.confidence_score < plain.confidence_score
    assert cautious.rank == plain.rank


def assert_missing_optional_bundles_handled_safely() -> None:
    """Missing optional bundles should warn and still return safe results."""

    bundle = ConfidenceScoringEngine().score(ranking_bundle())

    assert bundle.results
    assert bundle.warnings
    assert all(0.0 <= result.confidence_score <= 1.0 for result in bundle.results)


def assert_confidence_does_not_change_rank() -> None:
    """Step J should preserve Step I rank values exactly."""

    original_ranking = ranking_bundle()
    original_ranks = [
        candidate.rank
        for candidate in original_ranking.ranked_candidates
    ]
    scored = ConfidenceScoringEngine().score(
        original_ranking,
        water_bundle=water_bundle(),
        candidate_bundle=candidate_bundle(),
        normalized_bundle=normalized_bundle(),
        weights_bundle=expert_weights(),
    )

    assert [result.rank for result in scored.results] == original_ranks
    assert [candidate.rank for candidate in original_ranking.ranked_candidates] == original_ranks


def assert_no_future_forbidden_fields() -> None:
    """Step J output must not include final recommendation or plant fields."""

    found = _find_forbidden_keys(
        score_complete_expert_case().to_dict(),
        FORBIDDEN_FIELDS,
    )

    assert not found, f"Step J leaked forbidden fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The Step J test should stay in engines and avoid API behavior."""

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
    """Run all Step J checks."""

    assert_confidence_score_is_separate_from_topsis_closeness()
    assert_confidence_labels_high_medium_low_work()
    assert_temporary_weights_reduce_reliability_and_warn()
    assert_caution_flags_reduce_confidence()
    assert_missing_optional_bundles_handled_safely()
    assert_confidence_does_not_change_rank()
    assert_no_future_forbidden_fields()
    assert_no_api_or_recommend_route_involved()
    print("confidence scoring checks ok: Step J confidence only, no recommendation path")


if __name__ == "__main__":
    main()

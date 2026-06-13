"""Smoke tests for Scientific Engine Step H.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_weights_test.py

These tests use fake criteria names only. They do not connect to Azure, mutate
data, call API routes, calculate AHP pairwise weights, calculate TOPSIS, rank
candidates, calculate match/confidence scores, recommend plants, or create
final recommendations.
"""

from typing import Any

from app.engines import McdaWeightsHandler


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "ranking",
    "rank",
    "match_score",
    "confidence_score",
    "topsis",
    "topsis_score",
    "ahp",
    "ahp_weight",
}


CRITERIA_NAMES = [
    "removal_evidence_coverage",
    "site_suitability",
    "cost_indicator",
]


def build_handler() -> McdaWeightsHandler:
    """Return a fresh Step H handler for each check."""

    return McdaWeightsHandler()


def assert_missing_weights_handled_safely() -> None:
    """No supplied weights should return a safe missing-weights bundle."""

    bundle = build_handler().prepare_weights(CRITERIA_NAMES)

    assert bundle.weights_status == "weights_missing"
    assert bundle.weights == {}
    assert bundle.expert_validated is False
    assert bundle.missing_weight_criteria == CRITERIA_NAMES
    assert bundle.extra_weight_criteria == []
    assert bundle.warnings


def assert_temporary_weights_normalized_to_one() -> None:
    """Temporary supplied weights should be normalized to sum to 1.0."""

    bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 2,
            "site_suitability": 1,
            "cost_indicator": 1,
        },
    )

    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.expert_validated is False
    assert_close(sum(bundle.weights.values()), 1.0)
    assert_close(bundle.weights["removal_evidence_coverage"], 0.5)
    assert_close(bundle.weights["site_suitability"], 0.25)
    assert_close(bundle.weights["cost_indicator"], 0.25)


def assert_expert_validated_flag_requires_explicit_input() -> None:
    """Weights should be expert_validated only when the flag is explicit."""

    temporary_bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 1,
            "site_suitability": 1,
            "cost_indicator": 1,
        },
    )
    expert_bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 1,
            "site_suitability": 1,
            "cost_indicator": 1,
        },
        weights_source="supervisor_approved_ahp_sheet",
        expert_validated=True,
    )

    assert temporary_bundle.weights_status == "temporary_not_expert_validated"
    assert temporary_bundle.expert_validated is False
    assert expert_bundle.weights_status == "expert_validated"
    assert expert_bundle.expert_validated is True
    assert expert_bundle.weights_source == "supervisor_approved_ahp_sheet"


def assert_negative_weights_rejected() -> None:
    """Negative weights should be invalid and should not be normalized."""

    bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 1,
            "site_suitability": -1,
            "cost_indicator": 1,
        },
    )

    assert bundle.weights_status == "invalid_weights"
    assert bundle.weights == {}
    assert any("non-negative" in warning for warning in bundle.warnings)


def assert_non_numeric_weights_rejected() -> None:
    """Non-numeric weights should be invalid and should not be normalized."""

    bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 1,
            "site_suitability": "high",
            "cost_indicator": 1,
        },
    )

    assert bundle.weights_status == "invalid_weights"
    assert bundle.weights == {}
    assert any("numeric" in warning for warning in bundle.warnings)


def assert_missing_criteria_weights_reported() -> None:
    """Criteria without supplied weights should be reported clearly."""

    bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 2,
            "site_suitability": 1,
        },
    )

    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.missing_weight_criteria == ["cost_indicator"]
    assert_close(sum(bundle.weights.values()), 1.0)
    assert "cost_indicator" not in bundle.weights


def assert_extra_criteria_weights_reported() -> None:
    """Extra supplied weights should be reported and not used."""

    bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 2,
            "site_suitability": 1,
            "cost_indicator": 1,
            "unknown_future_criterion": 10,
        },
    )

    assert bundle.weights_status == "temporary_not_expert_validated"
    assert bundle.extra_weight_criteria == ["unknown_future_criterion"]
    assert "unknown_future_criterion" not in bundle.weights
    assert_close(sum(bundle.weights.values()), 1.0)


def assert_no_future_fields() -> None:
    """Step H output must not include recommendation/ranking/scoring fields."""

    bundle = build_handler().prepare_weights(
        CRITERIA_NAMES,
        {
            "removal_evidence_coverage": 1,
            "site_suitability": 1,
            "cost_indicator": 1,
        },
    )
    found = _find_forbidden_keys(bundle.to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"Step H leaked future fields: {sorted(found)}"


def assert_close(actual: float, expected: float) -> None:
    """Assert float equality with a tiny tolerance."""

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
    """Run all Step H checks."""

    assert_missing_weights_handled_safely()
    assert_temporary_weights_normalized_to_one()
    assert_expert_validated_flag_requires_explicit_input()
    assert_negative_weights_rejected()
    assert_non_numeric_weights_rejected()
    assert_missing_criteria_weights_reported()
    assert_extra_criteria_weights_reported()
    assert_no_future_fields()
    print("mcda weights checks ok: Step H criteria weight handling only")


if __name__ == "__main__":
    main()

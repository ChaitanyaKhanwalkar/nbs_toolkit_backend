"""Smoke tests for Scientific Engine Step G.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_normalization_test.py

These tests use fake Step F matrix data. They do not connect to Azure, mutate
data, call API routes, apply weights, calculate TOPSIS/AHP, rank candidates,
calculate match/confidence scores, recommend plants, or create final
recommendations.
"""

import sys
from typing import Any

from app.engines import (
    McdaMatrixBundle,
    McdaMatrixRow,
    McdaNormalizationEngine,
)


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


def fake_matrix_bundle() -> McdaMatrixBundle:
    """Build fake Step F output with numeric and skipped criteria cases."""

    criteria_names = [
        "removal_evidence_coverage",
        "cost_indicator",
        "site_suitability",
        "maintenance_indicator",
        "custom_metric",
        "climate_suitability",
    ]
    rows = [
        McdaMatrixRow(
            nbs_id=1,
            nbs_name="Wetland A",
            eligibility_status="eligible",
            supported_treatment_needs=["organic_load"],
            criteria_values={
                "removal_evidence_coverage": 0.2,
                "cost_indicator": 10.0,
                "site_suitability": 0.1,
                "maintenance_indicator": "medium",
                "custom_metric": 3.0,
                "climate_suitability": 0.5,
            },
            source_ids=[11],
        ),
        McdaMatrixRow(
            nbs_id=2,
            nbs_name="Wetland B",
            eligibility_status="data_pending",
            supported_treatment_needs=["organic_load"],
            criteria_values={
                "removal_evidence_coverage": 0.8,
                "cost_indicator": 5.0,
                "maintenance_indicator": "low",
                "custom_metric": 6.0,
                "climate_suitability": 0.5,
            },
            missing_criteria=["site_suitability"],
            source_ids=[12],
        ),
        McdaMatrixRow(
            nbs_id=3,
            nbs_name="Wetland C",
            eligibility_status="eligible",
            supported_treatment_needs=["solids"],
            criteria_values={
                "removal_evidence_coverage": 0.5,
                "cost_indicator": 7.5,
                "site_suitability": 0.9,
                "custom_metric": 9.0,
                "climate_suitability": 0.5,
            },
            source_ids=[13],
        ),
    ]
    return McdaMatrixBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=len(rows),
        criteria_names=criteria_names,
        rows=rows,
        weights_status="not_applied",
    )


def build_normalized_bundle() -> Any:
    """Run Step G against fake Step F output."""

    return McdaNormalizationEngine().normalize(fake_matrix_bundle())


def assert_benefit_criterion_normalization() -> None:
    """Higher benefit values should normalize closer to 1."""

    bundle = build_normalized_bundle()
    rows = [criteria_by_name(row) for row in bundle.rows]

    assert_close(rows[0]["removal_evidence_coverage"].normalized_value, 0.0)
    assert_close(rows[1]["removal_evidence_coverage"].normalized_value, 1.0)
    assert_close(rows[2]["removal_evidence_coverage"].normalized_value, 0.5)


def assert_cost_criterion_normalization() -> None:
    """Lower cost values should normalize closer to 1."""

    bundle = build_normalized_bundle()
    rows = [criteria_by_name(row) for row in bundle.rows]

    assert_close(rows[0]["cost_indicator"].normalized_value, 0.0)
    assert_close(rows[1]["cost_indicator"].normalized_value, 1.0)
    assert_close(rows[2]["cost_indicator"].normalized_value, 0.5)


def assert_missing_criterion_handled_safely() -> None:
    """Missing values should be marked missing and not crash."""

    bundle = build_normalized_bundle()
    row_two = criteria_by_name(bundle.rows[1])

    criterion = row_two["site_suitability"]
    assert criterion.normalization_status == "missing"
    assert criterion.normalized_value is None


def assert_non_numeric_criterion_handled_safely() -> None:
    """Non-numeric values should be visible as non_numeric."""

    bundle = build_normalized_bundle()
    row_one = criteria_by_name(bundle.rows[0])

    criterion = row_one["maintenance_indicator"]
    assert criterion.normalization_status == "non_numeric"
    assert criterion.normalized_value is None


def assert_unknown_direction_handled_safely() -> None:
    """Criteria outside the direction map should not be guessed."""

    bundle = build_normalized_bundle()

    for row in bundle.rows:
        criterion = criteria_by_name(row)["custom_metric"]
        assert criterion.direction == "unknown"
        assert criterion.normalization_status == "direction_unknown"
        assert criterion.normalized_value is None


def assert_no_variation_handled_safely() -> None:
    """Same numeric values across rows should not be normalized."""

    bundle = build_normalized_bundle()

    for row in bundle.rows:
        criterion = criteria_by_name(row)["climate_suitability"]
        assert criterion.normalization_status == "no_variation"
        assert criterion.normalized_value is None
    assert any("no variation" in warning for warning in bundle.warnings)


def assert_weights_status_remains_not_applied() -> None:
    """Step G must not apply AHP or any other criteria weights."""

    bundle = build_normalized_bundle()

    assert bundle.normalization_method == "min_max_unweighted"
    assert bundle.weights_status == "not_applied"


def assert_no_future_fields() -> None:
    """Step G output must not include recommendation/ranking/scoring fields."""

    bundle = build_normalized_bundle()
    found = _find_forbidden_keys(bundle.to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"Step G leaked future fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The Step G test should stay in engines and avoid API behavior."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def criteria_by_name(row: Any) -> dict[str, Any]:
    """Index normalized criteria by name for simple assertions."""

    return {
        criterion.criterion_name: criterion
        for criterion in row.normalized_criteria
    }


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
    """Run all Step G checks."""

    assert_benefit_criterion_normalization()
    assert_cost_criterion_normalization()
    assert_missing_criterion_handled_safely()
    assert_non_numeric_criterion_handled_safely()
    assert_unknown_direction_handled_safely()
    assert_no_variation_handled_safely()
    assert_weights_status_remains_not_applied()
    assert_no_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("mcda normalization checks ok: Step G unweighted normalization only")


if __name__ == "__main__":
    main()

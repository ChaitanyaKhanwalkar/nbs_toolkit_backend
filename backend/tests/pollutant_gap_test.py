"""Smoke tests for Scientific Engine Step C.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\pollutant_gap_test.py

These tests use fake standards and fake water bundles. They do not connect to
Azure, do not need production data, and do not create recommendations.
"""

from app.engines import PollutantGapEngine, WaterInputBundle


class FakeStandardsService:
    """Small service-shaped test double for standards rows."""

    def __init__(self, standards: list[dict[str, object]]) -> None:
        self._standards = standards

    def get_standards_for_use_case(self, use_case: str) -> list[dict[str, object]]:
        """Return fake standards for the requested use case."""

        return [
            standard
            for standard in self._standards
            if standard.get("use_case") == use_case
        ]


def make_bundle(observations: list[dict[str, object]]) -> WaterInputBundle:
    """Build a Step B-style water bundle for tests."""

    return WaterInputBundle(
        selected_source_type="user_measured",
        observations=observations,
        observation_count=len(observations),
        use_case="surface_discharge",
        source_ids=[4],
    )


def make_engine() -> PollutantGapEngine:
    """Build a pollutant gap engine with test standards."""

    return PollutantGapEngine(
        FakeStandardsService(
            [
                {
                    "use_case": "surface_discharge",
                    "parameter": "BOD",
                    "limit_high": 3.0,
                    "unit": "mg/L",
                },
                {
                    "use_case": "surface_discharge",
                    "parameter": "DO",
                    "limit_low": 5.0,
                    "unit": "mg/L",
                },
                {
                    "use_case": "surface_discharge",
                    "parameter": "pH",
                    "limit_low": 6.5,
                    "limit_high": 8.5,
                    "unit": "pH",
                },
                {
                    "use_case": "surface_discharge",
                    "parameter": "TSS",
                    "limit_high": 30.0,
                    "unit": "mg/L",
                },
            ]
        )
    )


def assert_max_limit_exceedance() -> None:
    """A max-limit pollutant above limit should calculate removal need."""

    bundle = make_bundle([
        {"parameter": "BOD", "value": 12.0, "unit": "mg/L", "source_id": 9}
    ])
    result = make_engine().calculate(bundle).results[0]

    assert result.comparison_type == "max_limit"
    assert result.status == "exceeds_standard"
    assert result.gap_value == 9.0
    assert result.gap_ratio == 3.0
    assert result.required_removal_fraction == 0.75
    assert result.required_removal_percent == 75.0
    assert result.direction == "reduce"
    assert result.source_ids == [9, 4]


def assert_max_limit_within_standard() -> None:
    """A max-limit pollutant at or below limit should be within standard."""

    bundle = make_bundle([
        {"parameter": "BOD", "value": 2.5, "unit": "mg/L"}
    ])
    result = make_engine().calculate(bundle).results[0]

    assert result.status == "within_standard"
    assert result.gap_value == 0.0
    assert result.required_removal_fraction == 0.0


def assert_min_limit_deficit() -> None:
    """A min-limit parameter below limit should calculate a deficit."""

    bundle = make_bundle([
        {"parameter": "DO", "value": 3.0, "unit": "mg/L"}
    ])
    result = make_engine().calculate(bundle).results[0]

    assert result.comparison_type == "min_limit"
    assert result.status == "below_minimum"
    assert result.gap_value == 2.0
    assert result.gap_ratio == 0.4
    assert result.required_removal_fraction is None
    assert result.direction == "increase"


def assert_range_limit_outside_range() -> None:
    """A range-limit parameter outside bounds should show nearest-boundary gap."""

    bundle = make_bundle([
        {"parameter": "pH", "value": 9.0, "unit": "pH"}
    ])
    result = make_engine().calculate(bundle).results[0]

    assert result.comparison_type == "range_limit"
    assert result.status == "outside_range"
    assert result.gap_value == 0.5
    assert result.direction == "adjust_range"
    assert result.required_removal_fraction is None


def assert_missing_standard_safe() -> None:
    """An observation without a matching standard should not crash."""

    bundle = make_bundle([
        {"parameter": "Unknown", "value": 1.0, "unit": "mg/L"}
    ])
    pollutant_bundle = make_engine().calculate(bundle)
    result = pollutant_bundle.results[0]

    assert result.status == "standard_missing"
    assert pollutant_bundle.missing_standard_count == 1
    assert result.gap_value is None


def assert_unit_mismatch_safe() -> None:
    """Mismatched units should warn and avoid calculation."""

    bundle = make_bundle([
        {"parameter": "BOD", "value": 12.0, "unit": "ug/L"}
    ])
    pollutant_bundle = make_engine().calculate(bundle)
    result = pollutant_bundle.results[0]

    assert result.status == "unit_mismatch"
    assert pollutant_bundle.unit_mismatch_count == 1
    assert result.gap_value is None
    assert any("Unit mismatch" in warning for warning in pollutant_bundle.warnings)


def assert_invalid_observed_value_safe() -> None:
    """Non-numeric observed values should be reported safely."""

    bundle = make_bundle([
        {"parameter": "BOD", "value": "not-a-number", "unit": "mg/L"}
    ])
    result = make_engine().calculate(bundle).results[0]

    assert result.status == "invalid_value"
    assert result.comparison_type == "invalid_value"
    assert result.gap_ratio is None


def assert_empty_bundle_safe() -> None:
    """An empty water bundle should return an empty pollutant-gap bundle."""

    bundle = make_bundle([])
    pollutant_bundle = make_engine().calculate(bundle)

    assert pollutant_bundle.total_observations_checked == 0
    assert pollutant_bundle.results == []
    assert pollutant_bundle.exceedance_count == 0
    assert any("No water observations" in warning for warning in pollutant_bundle.warnings)


def assert_no_future_fields() -> None:
    """Step C output must not include treatment/recommendation/ranking fields."""

    forbidden_fields = {
        "treatment_need",
        "recommendation",
        "recommendations",
        "match_score",
        "confidence_score",
        "ranking",
        "rank",
        "topsis",
        "topsis_score",
        "ahp",
        "ahp_weight",
    }

    bundle = make_bundle([
        {"parameter": "BOD", "value": 12.0, "unit": "mg/L"}
    ])
    payload = make_engine().calculate(bundle).to_dict()
    found = forbidden_fields.intersection(payload)
    for result in payload["results"]:
        found.update(forbidden_fields.intersection(result))
    assert not found, f"Step C leaked future fields: {sorted(found)}"


def main() -> None:
    """Run all Step C checks."""

    assert_max_limit_exceedance()
    assert_max_limit_within_standard()
    assert_min_limit_deficit()
    assert_range_limit_outside_range()
    assert_missing_standard_safe()
    assert_unit_mismatch_safe()
    assert_invalid_observed_value_safe()
    assert_empty_bundle_safe()
    assert_no_future_fields()
    print("pollutant gap checks ok: Step C only")


if __name__ == "__main__":
    main()

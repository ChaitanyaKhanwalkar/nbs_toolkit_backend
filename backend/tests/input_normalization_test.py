"""Smoke tests for Scientific Engine Step A.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\input_normalization_test.py

These tests do not connect to Azure or production databases. They validate only
input normalization and target-use-case checking.
"""

from app.engines import InputNormalizationEngine, TargetUseCaseValidator


class FakeStandardsService:
    """Tiny service-shaped test double for standards use cases."""

    def __init__(self, use_cases: list[str]) -> None:
        self._use_cases = use_cases

    def list_use_cases(self) -> list[str]:
        """Return test use cases without querying a database."""

        return self._use_cases


def assert_valid_use_case() -> None:
    """A stored use case should validate after transparent normalization."""

    context = InputNormalizationEngine().normalize(use_case=" surface discharge ")
    result = TargetUseCaseValidator(
        FakeStandardsService(["surface_discharge"])
    ).validate(context)

    assert result.validation_status == "valid"
    assert result.normalized_input["use_case"] == "surface_discharge"
    assert result.available_use_cases == ["surface_discharge"]


def assert_missing_use_case() -> None:
    """Missing use_case should produce a clear validation error."""

    context = InputNormalizationEngine().normalize(station="Example")
    result = TargetUseCaseValidator(
        FakeStandardsService(["surface_discharge"])
    ).validate(context)

    assert result.validation_status == "invalid"
    assert "use_case" in result.missing_inputs
    assert "use_case is required." in result.errors


def assert_unknown_use_case() -> None:
    """Unknown use_case should not be silently mapped to another target."""

    context = InputNormalizationEngine().normalize(use_case="unknown target")
    result = TargetUseCaseValidator(
        FakeStandardsService(["surface_discharge"])
    ).validate(context)

    assert result.validation_status == "invalid"
    assert any("Unknown use_case" in error for error in result.errors)


def assert_numeric_measured_observation() -> None:
    """Numeric measured values should be accepted without scientific scoring."""

    context = InputNormalizationEngine().normalize(
        use_case="surface_discharge",
        measured_observations=[
            {"parameter": " BOD ", "value": "12.5", "unit": "mg/L"},
        ],
    )

    observation = context.normalized_input["measured_observations"][0]
    assert context.validation_status == "valid"
    assert observation["parameter"] == "BOD"
    assert observation["parameter_match_key"] == "bod"
    assert observation["value"] == 12.5
    assert observation["source"] == "user_measured"


def assert_non_numeric_measured_observation_rejected() -> None:
    """Non-numeric measured values should be rejected before future science."""

    context = InputNormalizationEngine().normalize(
        use_case="surface_discharge",
        measured_observations=[
            {"parameter": "BOD", "value": "not-a-number", "unit": "mg/L"},
        ],
    )

    assert context.validation_status == "invalid"
    assert any(".value must be numeric" in error for error in context.errors)


def assert_whitespace_normalization() -> None:
    """Station and use_case whitespace should be normalized transparently."""

    context = InputNormalizationEngine().normalize(
        station="  Narmada   Station  ",
        use_case=" Surface   Discharge ",
        selected_parameters=[" pH ", " Total   Nitrogen "],
    )

    assert context.normalized_input["station"] == "Narmada Station"
    assert context.normalized_input["station_match_key"] == "narmada_station"
    assert context.normalized_input["use_case"] == "surface_discharge"
    assert context.normalized_input["selected_parameters"][0]["parameter"] == "pH"
    assert (
        context.normalized_input["selected_parameters"][1]["parameter_match_key"]
        == "total_nitrogen"
    )


def assert_no_future_scoring_fields() -> None:
    """Step A output must not contain future recommendation/scoring fields."""

    forbidden_fields = {
        "recommendations",
        "recommendation_score",
        "match_score",
        "confidence_score",
        "confidence_label",
        "topsis_score",
        "ahp_weight",
        "criteria_weights",
        "exceedance",
        "exceedance_ratio",
        "treatment_need",
        "health_risk",
    }

    context = InputNormalizationEngine().normalize(use_case="surface_discharge")
    payload = context.to_dict()
    found = forbidden_fields.intersection(payload)
    found.update(forbidden_fields.intersection(context.normalized_input))
    assert not found, f"Step A leaked future scoring fields: {sorted(found)}"


def assert_unit_conversion_warning() -> None:
    """Unit conversion should warn instead of silently changing values."""

    context = InputNormalizationEngine().normalize(
        use_case="surface_discharge",
        measured_observations=[
            {
                "parameter": "BOD",
                "value": 10,
                "unit": "mg/L",
                "target_unit": "g/m3",
            },
        ],
    )

    assert context.validation_status == "valid"
    assert any("Unit conversion was requested" in warning for warning in context.warnings)


def main() -> None:
    """Run all Step A checks."""

    assert_valid_use_case()
    assert_missing_use_case()
    assert_unknown_use_case()
    assert_numeric_measured_observation()
    assert_non_numeric_measured_observation_rejected()
    assert_whitespace_normalization()
    assert_no_future_scoring_fields()
    assert_unit_conversion_warning()
    print("input normalization checks ok: Step A only")


if __name__ == "__main__":
    main()

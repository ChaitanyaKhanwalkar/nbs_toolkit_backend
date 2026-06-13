"""Smoke tests for Scientific Engine Step D.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\treatment_need_test.py

These tests build fake Step C gap bundles. They do not connect to Azure, do not
mutate data, and do not recommend NbS technologies or plants.
"""

from app.engines import (
    ParameterGapResult,
    PollutantGapBundle,
    TreatmentNeedClassifier,
)


def gap(
    parameter: str,
    status: str,
    *,
    gap_ratio: float | None = 1.0,
    required_removal_percent: float | None = 50.0,
    direction: str = "reduce",
) -> ParameterGapResult:
    """Create a tiny Step C-style result for tests."""

    return ParameterGapResult(
        parameter=parameter,
        observed_value=10.0,
        observed_unit="mg/L",
        standard_unit="mg/L",
        limit_low=None,
        limit_high=5.0,
        comparison_type="max_limit",
        status=status,
        gap_value=5.0,
        gap_ratio=gap_ratio,
        required_removal_fraction=None,
        required_removal_percent=required_removal_percent,
        direction=direction,
        source_type="user_measured",
        source_ids=[4],
    )


def classify(results: list[ParameterGapResult]):
    """Classify a fake Step C bundle."""

    bundle = PollutantGapBundle(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        total_observations_checked=len(results),
        comparable_count=len(results),
        exceedance_count=len(results),
        missing_standard_count=0,
        unit_mismatch_count=0,
        results=results,
    )
    return TreatmentNeedClassifier().classify(bundle)


def need_groups(bundle) -> list[str]:
    """Return classified treatment need group names."""

    return [need.need_group for need in bundle.treatment_needs]


def assert_bod_cod_triggers_organic_load() -> None:
    """BOD and COD should map explicitly to organic_load."""

    bundle = classify([gap("BOD", "exceeds_standard"), gap("COD", "exceeds_standard")])

    assert need_groups(bundle) == ["organic_load"]
    need = bundle.treatment_needs[0]
    assert need.triggering_parameters == ["BOD", "COD"]
    assert need.max_gap_ratio == 1.0
    assert need.required_removal_percent_max == 50.0


def assert_tss_turbidity_triggers_solids() -> None:
    """TSS and turbidity should map explicitly to solids."""

    bundle = classify([
        gap("TSS", "exceeds_standard"),
        gap("turbidity", "exceeds_standard"),
    ])

    assert need_groups(bundle) == ["solids"]


def assert_nitrate_phosphate_triggers_nutrients() -> None:
    """Nitrate and phosphate should map explicitly to nutrients."""

    bundle = classify([
        gap("nitrate", "exceeds_standard"),
        gap("phosphate", "exceeds_standard"),
    ])

    assert need_groups(bundle) == ["nutrients"]


def assert_coliform_ecoli_triggers_pathogens() -> None:
    """Coliform and E. coli should map explicitly to pathogens."""

    bundle = classify([
        gap("fecal coliform", "exceeds_standard"),
        gap("E. coli", "exceeds_standard"),
    ])

    assert need_groups(bundle) == ["pathogens"]


def assert_ph_outside_range_triggers_ph_correction() -> None:
    """pH outside range should map to pH correction."""

    bundle = classify([
        gap("pH", "outside_range", required_removal_percent=None, direction="adjust_range")
    ])

    assert need_groups(bundle) == ["ph_correction"]
    assert bundle.treatment_needs[0].direction == "adjust_range"


def assert_do_below_minimum_triggers_oxygen_deficit() -> None:
    """DO below minimum should map to oxygen deficit."""

    bundle = classify([
        gap("DO", "below_minimum", required_removal_percent=None, direction="increase")
    ])

    assert need_groups(bundle) == ["oxygen_deficit"]
    assert bundle.treatment_needs[0].direction == "increase"


def assert_within_standard_triggers_no_need() -> None:
    """within_standard results should not trigger treatment needs."""

    bundle = classify([gap("BOD", "within_standard", gap_ratio=0.0)])

    assert bundle.treatment_needs == []
    assert bundle.unclassified_parameters == []


def assert_missing_standard_warning_only() -> None:
    """Missing standards should create warnings, not fake treatment needs."""

    bundle = classify([gap("BOD", "standard_missing", gap_ratio=None)])

    assert bundle.treatment_needs == []
    assert bundle.unclassified_parameters == []
    assert any("Standard missing" in warning for warning in bundle.warnings)


def assert_unknown_parameter_unclassified() -> None:
    """Unknown exceeded parameters should be listed as unclassified."""

    bundle = classify([gap("mystery parameter", "exceeds_standard")])

    assert bundle.treatment_needs == []
    assert bundle.unclassified_parameters == ["mystery parameter"]


def assert_no_future_fields() -> None:
    """Step D output must not include recommendation/ranking/scoring fields."""

    forbidden_fields = {
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
    bundle = classify([gap("BOD", "exceeds_standard")])
    payload = bundle.to_dict()
    found = forbidden_fields.intersection(payload)
    for result in payload["treatment_needs"]:
        found.update(forbidden_fields.intersection(result))

    assert not found, f"Step D leaked future fields: {sorted(found)}"


def main() -> None:
    """Run all Step D checks."""

    assert_bod_cod_triggers_organic_load()
    assert_tss_turbidity_triggers_solids()
    assert_nitrate_phosphate_triggers_nutrients()
    assert_coliform_ecoli_triggers_pathogens()
    assert_ph_outside_range_triggers_ph_correction()
    assert_do_below_minimum_triggers_oxygen_deficit()
    assert_within_standard_triggers_no_need()
    assert_missing_standard_warning_only()
    assert_unknown_parameter_unclassified()
    assert_no_future_fields()
    print("treatment need checks ok: Step D only")


if __name__ == "__main__":
    main()

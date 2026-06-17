r"""Smoke tests for the C8 evidence strength engine.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\evidence_strength_test.py

Fake evidence facts only. No Azure, no DB mutation, no invented values.
"""

from __future__ import annotations

from app.engines import compute_evidence_strength


def sourced_removal() -> dict:
    return {"row_count": 2, "rows_with_numeric_efficiency": 2}


def assert_best_case_scores_full() -> None:
    result = compute_evidence_strength(
        removal_evidence=sourced_removal(),
        source_ids=[10, 31],
        implementation_sourced=True,
        site_context={"soil_type": "clay"},
        selected_source_type="user_measured",
    )

    assert result.evidence_strength == 1.00
    assert result.water_quality_level == "measured"
    assert result.removal_sourced is True


def assert_measured_partial_scores_0_80() -> None:
    result = compute_evidence_strength(
        removal_evidence=sourced_removal(),
        source_ids=[10],
        implementation_sourced=False,
        site_context={"soil_type": "clay"},
        selected_source_type="station_observations",
    )

    assert result.evidence_strength == 0.80


def assert_regional_water_scores_0_70() -> None:
    result = compute_evidence_strength(
        removal_evidence=sourced_removal(),
        source_ids=[10],
        implementation_sourced=False,
        site_context=None,
        selected_source_type="basin_observations",
    )

    assert result.water_quality_level == "regional"
    assert result.evidence_strength == 0.70


def assert_fallback_water_scores_0_55() -> None:
    result = compute_evidence_strength(
        removal_evidence=sourced_removal(),
        source_ids=[10],
        implementation_sourced=False,
        site_context=None,
        selected_source_type="missing",
    )

    assert result.water_quality_level == "fallback"
    assert result.evidence_strength == 0.55


def assert_unsourced_removal_is_capped() -> None:
    with_source = compute_evidence_strength(
        removal_evidence={"rows_with_numeric_efficiency": 0},
        source_ids=[10],
        implementation_sourced=True,
        site_context={"soil_type": "clay"},
        selected_source_type="user_measured",
    )
    without_source = compute_evidence_strength(
        removal_evidence=None,
        source_ids=[],
        implementation_sourced=False,
        site_context=None,
        selected_source_type="user_measured",
    )

    assert with_source.evidence_strength == 0.30
    assert without_source.evidence_strength == 0.20


def main() -> None:
    assert_best_case_scores_full()
    assert_measured_partial_scores_0_80()
    assert_regional_water_scores_0_70()
    assert_fallback_water_scores_0_55()
    assert_unsourced_removal_is_capped()
    print("evidence strength (C8) checks ok: provenance-based, no invention")


if __name__ == "__main__":
    main()

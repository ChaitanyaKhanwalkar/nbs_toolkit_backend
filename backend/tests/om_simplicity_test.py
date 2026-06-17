r"""Smoke tests for the C7 O&M simplicity engine.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\om_simplicity_test.py

Fake criteria rows only. No Azure, no DB mutation, no invented values.
"""

from __future__ import annotations

from app.engines import compute_om_simplicity
from app.engines.om_simplicity import OM_STATUS_DATA_PENDING, OM_STATUS_SOURCED


def assert_simple_level_scores_high() -> None:
    result = compute_om_simplicity(
        [{"criterion": "O&M simplicity", "value_qual": "simple"}]
    )

    assert result.om_simplicity == 0.80
    assert result.om_level == "simple"
    assert result.status == OM_STATUS_SOURCED


def assert_level_table_is_applied() -> None:
    cases = {
        "very simple": 1.00,
        "moderate": 0.60,
        "complex": 0.35,
        "expert": 0.20,
        "energy intensive": 0.20,
        "very high": 0.20,
    }
    for level, expected in cases.items():
        result = compute_om_simplicity([{"criterion": "maintenance", "value_qual": level}])
        assert result.om_simplicity == expected, (level, result.om_simplicity)


def assert_non_om_criteria_are_ignored() -> None:
    result = compute_om_simplicity([{"criterion": "cost", "value_qual": "medium"}])

    assert result.om_simplicity is None
    assert result.status == OM_STATUS_DATA_PENDING


def assert_missing_om_is_data_pending() -> None:
    result = compute_om_simplicity([])

    assert result.om_simplicity is None
    assert "om_level" in result.missing_inputs
    assert any("confidence lowered" in note for note in result.notes)


def assert_unknown_level_word_is_unscored() -> None:
    result = compute_om_simplicity(
        [{"criterion": "maintenance", "value_qual": "indeterminate"}]
    )

    assert result.om_simplicity is None


def main() -> None:
    assert_simple_level_scores_high()
    assert_level_table_is_applied()
    assert_non_om_criteria_are_ignored()
    assert_missing_om_is_data_pending()
    assert_unknown_level_word_is_unscored()
    print("om simplicity (C7) checks ok: documented level table, no invention")


if __name__ == "__main__":
    main()

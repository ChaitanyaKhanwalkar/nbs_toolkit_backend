r"""Smoke tests for the C6 footprint feasibility engine.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\footprint_feasibility_test.py

Fake footprint rows only. No Azure, no DB mutation, no invented values.
"""

from __future__ import annotations

from app.engines import compute_footprint_requirement
from app.engines.footprint_feasibility import (
    FOOTPRINT_STATUS_DATA_PENDING,
    FOOTPRINT_STATUS_SOURCED,
)


def assert_area_per_pe_range_is_averaged() -> None:
    result = compute_footprint_requirement(
        [{"area_per_pe_low": 2.0, "area_per_pe_high": 6.0}]
    )

    assert result.footprint_requirement == 4.0
    assert result.basis == "area_per_pe"
    assert result.status == FOOTPRINT_STATUS_SOURCED


def assert_single_bound_is_used() -> None:
    result = compute_footprint_requirement([{"area_per_pe_low": 3.0}])

    assert result.footprint_requirement == 3.0


def assert_multiple_rows_are_meaned() -> None:
    result = compute_footprint_requirement(
        [
            {"area_per_pe_low": 2.0, "area_per_pe_high": 4.0},  # mid 3.0
            {"area_per_pe_low": 5.0, "area_per_pe_high": 5.0},  # mid 5.0
        ]
    )

    assert result.footprint_requirement == 4.0


def assert_missing_footprint_is_data_pending() -> None:
    result = compute_footprint_requirement([])

    assert result.footprint_requirement is None
    assert result.status == FOOTPRINT_STATUS_DATA_PENDING
    assert "footprint_area_per_pe" in result.missing_inputs
    assert any("confidence lowered" in note for note in result.notes)


def assert_non_numeric_footprint_is_ignored() -> None:
    result = compute_footprint_requirement(
        [{"area_per_pe_low": "n/a", "note": "no value"}]
    )

    assert result.footprint_requirement is None


def main() -> None:
    assert_area_per_pe_range_is_averaged()
    assert_single_bound_is_used()
    assert_multiple_rows_are_meaned()
    assert_missing_footprint_is_data_pending()
    assert_non_numeric_footprint_is_ignored()
    print("footprint feasibility (C6) checks ok: sourced land requirement, no invention")


if __name__ == "__main__":
    main()

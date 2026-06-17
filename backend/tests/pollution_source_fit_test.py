r"""Smoke tests for the C5 pollution-source fit engine.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\pollution_source_fit_test.py

Fake options and contexts only. No Azure, no DB mutation, no invented values.
"""

from __future__ import annotations

from typing import Any

from app.engines import compute_pollution_source_fit
from app.engines.pollution_source_fit import (
    POLLUTION_FIT_STATUS_DATA_PENDING,
    POLLUTION_FIT_STATUS_PROVISIONAL,
)


def buffer_option() -> dict[str, Any]:
    return {"id": 1, "solution": "Riparian buffer strip", "family": "Vegetated buffer"}


def infiltration_option() -> dict[str, Any]:
    return {"id": 2, "solution": "Bioretention rain garden", "family": "Infiltration system"}


def subsurface_option() -> dict[str, Any]:
    return {"id": 3, "solution": "Subsurface flow reed bed", "family": "Wetland"}


def assert_metals_need_drives_industrial_context() -> None:
    result = compute_pollution_source_fit(subsurface_option(), {}, ["metals"])

    assert result.pollution_context == "industrial_metals"
    assert result.context_source == "treatment_need_groups"
    assert result.pollution_source_fit == 1.0  # subsurface is the strong family
    assert result.status == POLLUTION_FIT_STATUS_PROVISIONAL


def assert_metals_caution_for_weak_family() -> None:
    result = compute_pollution_source_fit(infiltration_option(), {}, ["metals"])

    assert result.pollution_source_fit == 0.4
    assert any("Industrial/metals" in caution for caution in result.cautions)


def assert_pathogens_drive_sewage_context() -> None:
    result = compute_pollution_source_fit(subsurface_option(), {}, ["pathogens"])

    assert result.pollution_context == "sewage_domestic"
    assert result.pollution_source_fit == 1.0


def assert_land_cover_drives_agri_vs_urban() -> None:
    agri = compute_pollution_source_fit(buffer_option(), {"agri_frac": 0.8}, ["solids"])
    urban = compute_pollution_source_fit(
        infiltration_option(), {"builtup_frac": 0.7}, ["solids"]
    )

    assert agri.pollution_context == "agricultural_runoff"
    assert agri.pollution_source_fit == 1.0  # buffer strong for agri
    assert urban.pollution_context == "urban_runoff"
    assert urban.pollution_source_fit == 1.0  # infiltration strong for urban


def assert_mixed_context_is_neutral() -> None:
    result = compute_pollution_source_fit(
        buffer_option(), {"agri_frac": 0.3, "builtup_frac": 0.3}, ["solids"]
    )

    assert result.pollution_context == "mixed"
    assert result.pollution_source_fit == 0.6


def assert_no_signal_is_data_pending() -> None:
    result = compute_pollution_source_fit(buffer_option(), {}, [])

    assert result.pollution_source_fit is None
    assert result.status == POLLUTION_FIT_STATUS_DATA_PENDING
    assert "pollution_context" in result.missing_inputs


def assert_unclassified_family_is_data_pending() -> None:
    result = compute_pollution_source_fit(
        {"solution": "Mystery", "family": "Other"}, {"agri_frac": 0.9}, ["solids"]
    )

    assert result.pollution_source_fit is None
    assert "nbs_family_profile" in result.missing_inputs


def assert_provisional_flag_present() -> None:
    result = compute_pollution_source_fit(buffer_option(), {"agri_frac": 0.9}, ["solids"])

    assert any("provisional" in note.lower() for note in result.notes)


def main() -> None:
    assert_metals_need_drives_industrial_context()
    assert_metals_caution_for_weak_family()
    assert_pathogens_drive_sewage_context()
    assert_land_cover_drives_agri_vs_urban()
    assert_mixed_context_is_neutral()
    assert_no_signal_is_data_pending()
    assert_unclassified_family_is_data_pending()
    assert_provisional_flag_present()
    print("pollution source fit (C5) checks ok: transparent provisional context scoring")


if __name__ == "__main__":
    main()

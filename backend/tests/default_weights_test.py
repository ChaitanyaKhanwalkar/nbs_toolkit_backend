r"""Smoke tests for provisional default MCDA criteria weights.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\default_weights_test.py

These tests check the transparent provisional weight config only. They do not
connect to Azure, mutate data, invent expert/AHP weights, or rank candidates.
"""

from __future__ import annotations

from app.core.default_weights import (
    DEFAULT_TEMPORARY_CRITERIA_WEIGHTS,
    DEFAULT_WEIGHTS_SOURCE,
    WEIGHTS_STATUS_TEMPORARY,
    get_default_weights,
    select_default_weights,
)


def assert_treatment_performance_is_dominant() -> None:
    """Removal-evidence (C1 proxy) should carry the largest provisional weight."""

    weights = get_default_weights("surface_discharge")
    dominant = max(weights, key=weights.get)

    assert dominant == "removal_evidence_score"
    assert all(value >= 0 for value in weights.values())


def assert_use_case_aliases_resolve() -> None:
    """Known aliases should map onto provisional profiles, not crash."""

    assert get_default_weights("surface_discharge") == (
        DEFAULT_TEMPORARY_CRITERIA_WEIGHTS["discharge_inland"]
    )
    assert get_default_weights("drinking_domestic") == (
        DEFAULT_TEMPORARY_CRITERIA_WEIGHTS["drinking"]
    )
    assert get_default_weights("irrigation_reuse") == (
        DEFAULT_TEMPORARY_CRITERIA_WEIGHTS["irrigation"]
    )
    # Unknown use case falls back to the generic default profile.
    assert get_default_weights("totally_unknown") == (
        DEFAULT_TEMPORARY_CRITERIA_WEIGHTS["_default"]
    )


def assert_new_criteria_have_weights() -> None:
    """C3-C8 criteria should all appear in the default profile."""

    weights = get_default_weights("surface_discharge")
    for criterion in [
        "site_suitability",
        "hydrological_suitability",
        "pollution_source_fit",
        "footprint_requirement",
        "om_simplicity",
        "evidence_strength",
    ]:
        assert criterion in weights, criterion


def assert_select_filters_to_present_criteria() -> None:
    """select_default_weights should keep only criteria present in the run."""

    selected = select_default_weights(
        "surface_discharge",
        ["removal_evidence_score", "site_suitability", "not_a_real_criterion"],
    )

    assert set(selected) == {"removal_evidence_score", "site_suitability"}


def assert_select_returns_empty_when_no_match() -> None:
    """No matching criteria should yield an empty dict (safe weights-missing path)."""

    assert select_default_weights("surface_discharge", ["nothing_matches"]) == {}


def assert_provenance_labels_are_stable() -> None:
    """Provenance labels must stay the documented provisional values."""

    assert WEIGHTS_STATUS_TEMPORARY == "temporary_not_expert_validated"
    assert DEFAULT_WEIGHTS_SOURCE == "default_temporary_literature_informed_v1"


def main() -> None:
    assert_treatment_performance_is_dominant()
    assert_use_case_aliases_resolve()
    assert_new_criteria_have_weights()
    assert_select_filters_to_present_criteria()
    assert_select_returns_empty_when_no_match()
    assert_provenance_labels_are_stable()
    print("default weights checks ok: provisional, transparent, filtered to present criteria")


if __name__ == "__main__":
    main()

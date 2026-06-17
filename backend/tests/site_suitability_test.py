r"""Smoke tests for the C3 site-suitability engine and its matrix wiring.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\site_suitability_test.py

These tests use fake NbS options and fake site-context dictionaries only. They
do not connect to Azure, mutate data, invent site values, calculate AHP weights,
rank candidates, or classify health risk.
"""

from __future__ import annotations

from typing import Any

from app.engines import (
    CandidateFilterBundle,
    CandidateFilterResult,
    McdaMatrixBuilder,
    McdaNumericProjectionEngine,
    classify_family,
    compute_site_suitability,
)
from app.engines.site_suitability import (
    SITE_SUITABILITY_STATUS_DATA_PENDING,
    SITE_SUITABILITY_STATUS_PROVISIONAL,
)


FORBIDDEN_FIELDS = {
    "health_risk",
    "ahp",
    "ahp_weight",
    "match_score",
    "confidence_score",
    "topsis",
    "rank",
}


def wetland_option() -> dict[str, Any]:
    """Return a surface-flow constructed-wetland option."""

    return {"id": 1, "solution": "Free water surface constructed wetland", "family": "Constructed Wetlands"}


def infiltration_option() -> dict[str, Any]:
    """Return an infiltration-based option."""

    return {"id": 2, "solution": "Bioretention rain garden", "family": "Infiltration system"}


def buffer_option() -> dict[str, Any]:
    """Return a vegetated-buffer option."""

    return {"id": 3, "solution": "Riparian buffer strip", "family": "Vegetated buffer"}


def good_wetland_site() -> dict[str, Any]:
    """Flat, wet, low-permeability, agricultural site: ideal for a wetland."""

    return {
        "infiltration_class": "low",
        "aridity_P_PET": 0.9,
        "slope_mean": 1.0,
        "dom_land_cover": "cropland",
    }


def assert_family_classification_is_transparent() -> None:
    """Family classification should follow documented keyword tokens."""

    assert classify_family(wetland_option()) == "surface_water_wetland_pond"
    assert classify_family(infiltration_option()) == "infiltration_based"
    assert classify_family(buffer_option()) == "vegetated_buffer"
    assert classify_family({"solution": "Subsurface flow reed bed", "family": "Wetland"}) == (
        "subsurface_wetland"
    )
    assert classify_family({"solution": "Mystery unit", "family": "Other"}) == "unclassified"


def assert_full_sitescore_uses_all_sub_scores() -> None:
    """A complete site context should produce all four sub-scores and an average."""

    result = compute_site_suitability(wetland_option(), good_wetland_site())

    assert result.status == SITE_SUITABILITY_STATUS_PROVISIONAL
    assert result.soil_fit == 1.0  # wetland prefers low permeability; site is low
    assert result.slope_fit == 1.0  # flat site within ideal slope
    assert result.climate_fit == 1.0  # high water dependency met by wet site
    assert result.land_cover_fit == 0.8  # wetland accepts any land cover
    expected = (1.0 + 1.0 + 1.0 + 0.8) / 4
    assert abs(result.site_suitability - expected) < 1e-9
    assert all(0.0 <= value <= 1.0 for value in [
        result.soil_fit,
        result.slope_fit,
        result.climate_fit,
        result.land_cover_fit,
        result.site_suitability,
    ])


def assert_soil_mismatch_lowers_soil_fit() -> None:
    """An infiltration system on low-permeability soil should score poorly on soil."""

    site = {"infiltration_class": "low", "slope_mean": 2.0}
    result = compute_site_suitability(infiltration_option(), site)

    assert result.soil_fit == 0.2  # prefers high permeability, site is low (opposite)


def assert_steep_slope_penalizes_pond() -> None:
    """A steep slope should drop slope_fit below the flat-site score for a pond."""

    flat = compute_site_suitability(wetland_option(), {"slope_mean": 1.0})
    steep = compute_site_suitability(wetland_option(), {"slope_mean": 12.0})

    assert flat.slope_fit == 1.0
    assert steep.slope_fit == 0.1  # beyond the wetland hard slope max
    assert steep.slope_fit < flat.slope_fit


def assert_missing_inputs_are_flagged_not_invented() -> None:
    """Missing site data should yield None sub-scores and recorded gaps."""

    result = compute_site_suitability(wetland_option(), {"slope_mean": 1.0})

    assert result.slope_fit == 1.0
    assert result.soil_fit is None
    assert result.climate_fit is None
    assert result.land_cover_fit is None
    assert "soil_permeability" in result.missing_inputs
    assert "climate_wetness" in result.missing_inputs
    assert "land_cover" in result.missing_inputs
    # One usable sub-score still yields an average.
    assert result.site_suitability == 1.0


def assert_no_site_data_is_data_pending() -> None:
    """An empty site context should leave C3 unscored, not guessed."""

    result = compute_site_suitability(wetland_option(), {})

    assert result.site_suitability is None
    assert result.status == SITE_SUITABILITY_STATUS_DATA_PENDING


def assert_unclassified_family_is_data_pending() -> None:
    """An unmatched NbS family should not be scored against a guessed profile."""

    result = compute_site_suitability({"solution": "Mystery", "family": "Other"}, good_wetland_site())

    assert result.site_suitability is None
    assert result.status == SITE_SUITABILITY_STATUS_DATA_PENDING
    assert "nbs_family_profile" in result.missing_inputs


def assert_provisional_flag_is_always_present() -> None:
    """Every scored result must carry the provisional, not-expert-validated note."""

    result = compute_site_suitability(wetland_option(), good_wetland_site())

    assert any("provisional" in note.lower() for note in result.notes)


# --- Matrix + projection wiring --------------------------------------------


class FakeNbsCatalogService:
    """Provider-shaped double returning fake NbS profiles."""

    def __init__(self, profiles: dict[int, dict[str, Any]]) -> None:
        self.profiles = profiles

    def list_options(self) -> list[dict[str, Any]]:
        return [profile["option"] for profile in self.profiles.values()]

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        return self.profiles.get(nbs_id, {})


def fake_provider() -> FakeNbsCatalogService:
    """Two eligible candidates: one wetland, one infiltration system."""

    return FakeNbsCatalogService(
        {
            1: {
                "option": {
                    "id": 1,
                    "solution": "Free water surface constructed wetland",
                    "family": "Constructed Wetlands",
                    "optimal_water_type": "domestic wastewater",
                    "climate_suitability": "tropical",
                },
                "removal_efficiencies": [{"parameter": "BOD", "eff_low": 60.0}],
                "implementation": [],
                "footprint": [],
                "criteria": [],
                "missing_sections": [],
            },
            2: {
                "option": {
                    "id": 2,
                    "solution": "Bioretention rain garden",
                    "family": "Infiltration system",
                    "optimal_water_type": "stormwater",
                },
                "removal_efficiencies": [{"parameter": "TSS", "eff_high": 70.0}],
                "implementation": [],
                "footprint": [],
                "criteria": [],
                "missing_sections": [],
            },
        }
    )


def candidate_bundle() -> CandidateFilterBundle:
    """Two eligible candidates for matrix preparation."""

    return CandidateFilterBundle(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        treatment_need_groups=["organic_load", "solids"],
        candidate_count=2,
        eligible_count=2,
        results=[
            CandidateFilterResult(
                nbs_id=1,
                nbs_name="Free water surface constructed wetland",
                eligibility_status="eligible",
                supported_treatment_needs=["organic_load"],
            ),
            CandidateFilterResult(
                nbs_id=2,
                nbs_name="Bioretention rain garden",
                eligibility_status="eligible",
                supported_treatment_needs=["solids"],
            ),
        ],
    )


def assert_matrix_without_site_context_skips_c3() -> None:
    """Without a site context the matrix must not carry C3 site_suitability."""

    bundle = McdaMatrixBuilder(fake_provider()).build(candidate_bundle())

    assert bundle.site_context_applied is False
    for row in bundle.rows:
        assert "site_suitability" not in row.criteria_values
        assert "site_suitability_breakdown" not in row.criteria_values


def assert_matrix_with_site_context_adds_c3() -> None:
    """With a site context every classified row gets a numeric C3 + breakdown."""

    bundle = McdaMatrixBuilder(fake_provider()).build(
        candidate_bundle(),
        site_context=good_wetland_site(),
    )

    assert bundle.site_context_applied is True
    assert "site_suitability" in bundle.criteria_names
    for row in bundle.rows:
        breakdown = row.criteria_values["site_suitability_breakdown"]
        assert breakdown["status"] == SITE_SUITABILITY_STATUS_PROVISIONAL
        assert isinstance(row.criteria_values["site_suitability"], float)

    wetland_row = next(row for row in bundle.rows if row.nbs_id == 1)
    infiltration_row = next(row for row in bundle.rows if row.nbs_id == 2)
    # The same site favours the wetland over the infiltration system here, so C3
    # actually discriminates between candidates instead of being constant.
    assert wetland_row.criteria_values["site_suitability"] > (
        infiltration_row.criteria_values["site_suitability"]
    )


def assert_projection_skips_proxy_when_real_c3_present() -> None:
    """The metadata-completeness proxy must not overwrite the real C3 values."""

    bundle = McdaMatrixBuilder(fake_provider()).build(
        candidate_bundle(),
        site_context=good_wetland_site(),
    )
    before = {row.nbs_id: row.criteria_values["site_suitability"] for row in bundle.rows}

    projected = McdaNumericProjectionEngine().project(bundle)
    after = {row.nbs_id: row.criteria_values["site_suitability"] for row in projected.rows}

    assert before == after
    assert not any("metadata completeness" in warning for warning in projected.warnings)


def assert_forbidden_fields_are_absent() -> None:
    """C3 output must not leak health-risk, AHP, ranking, or score fields."""

    bundle = McdaMatrixBuilder(fake_provider()).build(
        candidate_bundle(),
        site_context=good_wetland_site(),
    )
    found = _find_forbidden_keys(bundle.to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"C3 site suitability leaked forbidden fields: {sorted(found)}"


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
    """Run all C3 site-suitability checks."""

    assert_family_classification_is_transparent()
    assert_full_sitescore_uses_all_sub_scores()
    assert_soil_mismatch_lowers_soil_fit()
    assert_steep_slope_penalizes_pond()
    assert_missing_inputs_are_flagged_not_invented()
    assert_no_site_data_is_data_pending()
    assert_unclassified_family_is_data_pending()
    assert_provisional_flag_is_always_present()
    assert_matrix_without_site_context_skips_c3()
    assert_matrix_with_site_context_adds_c3()
    assert_projection_skips_proxy_when_real_c3_present()
    assert_forbidden_fields_are_absent()
    print("site suitability (C3) checks ok: transparent provisional site scoring")


if __name__ == "__main__":
    main()

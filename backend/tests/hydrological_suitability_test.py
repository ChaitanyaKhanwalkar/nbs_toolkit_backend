r"""Smoke tests for the C4 hydrological-suitability engine and its matrix wiring.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\hydrological_suitability_test.py

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
    compute_hydrological_suitability,
)
from app.engines.hydrological_suitability import (
    HYDRO_STATUS_DATA_PENDING,
    HYDRO_STATUS_PROVISIONAL,
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


def pond_option() -> dict[str, Any]:
    """A high-flow-capacity family (surface wetland/pond)."""

    return {"id": 1, "solution": "Stabilization pond", "family": "Pond"}


def rain_garden_option() -> dict[str, Any]:
    """A low-flow-capacity family (infiltration-based)."""

    return {"id": 2, "solution": "Bioretention rain garden", "family": "Infiltration system"}


def assert_true_stream_order_is_used_without_proxy() -> None:
    """A real stream_order should be used and never flagged as a proxy."""

    result = compute_hydrological_suitability(pond_option(), {"stream_order": 6})

    assert result.status == HYDRO_STATUS_PROVISIONAL
    assert result.flow_scale == "high"
    assert result.flow_capacity == "high"
    assert result.flow_metric_used == "stream_order"
    assert result.proxy_used is False
    assert result.hydrological_suitability == 1.0


def assert_drainage_area_is_used_as_reported_proxy() -> None:
    """With no stream order, drainage area is a proxy and must be reported."""

    result = compute_hydrological_suitability(pond_option(), {"drainage_area_km2": 2500.0})

    assert result.flow_scale == "high"
    assert result.flow_metric_used == "drainage_area_km2"
    assert result.proxy_used is True
    assert any("dilution proxy" in note for note in result.notes)


def assert_dilution_proxy_is_last_resort() -> None:
    """dilution_proxy is used only when stream order and drainage area are absent."""

    result = compute_hydrological_suitability(pond_option(), {"dilution_proxy": 50.0})

    assert result.flow_scale == "low"
    assert result.flow_metric_used == "dilution_proxy"
    assert result.proxy_used is True


def assert_capacity_matches_scale_discriminates() -> None:
    """A high-flow site should favour the large-flow family over the small one."""

    site = {"stream_order": 6}
    pond = compute_hydrological_suitability(pond_option(), site)
    rain_garden = compute_hydrological_suitability(rain_garden_option(), site)

    assert pond.hydrological_suitability > rain_garden.hydrological_suitability

    small_site = {"stream_order": 1}
    pond_small = compute_hydrological_suitability(pond_option(), small_site)
    rain_garden_small = compute_hydrological_suitability(rain_garden_option(), small_site)

    assert rain_garden_small.hydrological_suitability > pond_small.hydrological_suitability


def assert_missing_flow_data_is_data_pending() -> None:
    """No stream order or drainage area should leave C4 unscored, not guessed."""

    result = compute_hydrological_suitability(pond_option(), {"slope_mean": 2.0})

    assert result.hydrological_suitability is None
    assert result.status == HYDRO_STATUS_DATA_PENDING
    assert "flow_scale" in result.missing_inputs


def assert_unclassified_family_is_data_pending() -> None:
    """An unmatched family must not be scored against a guessed capacity profile."""

    result = compute_hydrological_suitability(
        {"solution": "Mystery", "family": "Other"}, {"stream_order": 4}
    )

    assert result.hydrological_suitability is None
    assert result.status == HYDRO_STATUS_DATA_PENDING
    assert "nbs_family_profile" in result.missing_inputs


def assert_provisional_flag_is_always_present() -> None:
    """Every scored result must carry the provisional, not-expert-validated note."""

    result = compute_hydrological_suitability(pond_option(), {"stream_order": 4})

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
    """One pond and one rain garden candidate."""

    return FakeNbsCatalogService(
        {
            1: {
                "option": {"id": 1, "solution": "Stabilization pond", "family": "Pond"},
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
                nbs_name="Stabilization pond",
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


def assert_matrix_without_site_context_skips_c4() -> None:
    """Without a site context the matrix must not carry C4 hydrological_suitability."""

    bundle = McdaMatrixBuilder(fake_provider()).build(candidate_bundle())

    for row in bundle.rows:
        assert "hydrological_suitability" not in row.criteria_values
        assert "hydrological_suitability_breakdown" not in row.criteria_values


def assert_matrix_with_site_context_adds_c4() -> None:
    """With a high-flow site, C4 is added and discriminates between families."""

    bundle = McdaMatrixBuilder(fake_provider()).build(
        candidate_bundle(),
        site_context={"stream_order": 6},
    )

    assert "hydrological_suitability" in bundle.criteria_names
    for row in bundle.rows:
        breakdown = row.criteria_values["hydrological_suitability_breakdown"]
        assert breakdown["status"] == HYDRO_STATUS_PROVISIONAL
        assert breakdown["proxy_used"] is False
        assert isinstance(row.criteria_values["hydrological_suitability"], float)

    pond_row = next(row for row in bundle.rows if row.nbs_id == 1)
    rain_garden_row = next(row for row in bundle.rows if row.nbs_id == 2)
    assert pond_row.criteria_values["hydrological_suitability"] > (
        rain_garden_row.criteria_values["hydrological_suitability"]
    )


def assert_projection_preserves_c4() -> None:
    """The numeric projection must not disturb the real C4 values."""

    bundle = McdaMatrixBuilder(fake_provider()).build(
        candidate_bundle(),
        site_context={"stream_order": 6},
    )
    before = {
        row.nbs_id: row.criteria_values["hydrological_suitability"] for row in bundle.rows
    }

    projected = McdaNumericProjectionEngine().project(bundle)
    after = {
        row.nbs_id: row.criteria_values["hydrological_suitability"]
        for row in projected.rows
    }

    assert before == after


def assert_forbidden_fields_are_absent() -> None:
    """C4 output must not leak health-risk, AHP, ranking, or score fields."""

    bundle = McdaMatrixBuilder(fake_provider()).build(
        candidate_bundle(),
        site_context={"drainage_area_km2": 2500.0},
    )
    found = _find_forbidden_keys(bundle.to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"C4 hydrological suitability leaked forbidden fields: {sorted(found)}"


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
    """Run all C4 hydrological-suitability checks."""

    assert_true_stream_order_is_used_without_proxy()
    assert_drainage_area_is_used_as_reported_proxy()
    assert_dilution_proxy_is_last_resort()
    assert_capacity_matches_scale_discriminates()
    assert_missing_flow_data_is_data_pending()
    assert_unclassified_family_is_data_pending()
    assert_provisional_flag_is_always_present()
    assert_matrix_without_site_context_skips_c4()
    assert_matrix_with_site_context_adds_c4()
    assert_projection_preserves_c4()
    assert_forbidden_fields_are_absent()
    print("hydrological suitability (C4) checks ok: transparent provisional flow scoring")


if __name__ == "__main__":
    main()

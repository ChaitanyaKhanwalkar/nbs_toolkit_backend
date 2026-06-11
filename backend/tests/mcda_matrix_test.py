"""Smoke tests for Scientific Engine Step F.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_matrix_test.py

These tests use fake NbS catalogue/profile data. They do not connect to Azure,
mutate data, rank candidates, calculate TOPSIS/AHP, calculate match/confidence
scores, recommend plants, or create final recommendations.
"""

import sys
from typing import Any

from app.engines import (
    CandidateFilterBundle,
    CandidateFilterResult,
    McdaMatrixBuilder,
)


FORBIDDEN_FIELDS = {
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


class FakeNbsCatalogService:
    """Small provider-shaped test double for raw NbS catalogue profiles."""

    def __init__(self, profiles: dict[int, dict[str, Any]]) -> None:
        self.profiles = profiles
        self.requested_ids: list[int] = []

    def list_options(self) -> list[dict[str, Any]]:
        """Return fake options without querying a database."""

        return [
            profile["option"]
            for profile in self.profiles.values()
            if profile.get("option")
        ]

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return one fake raw profile and remember that it was requested."""

        self.requested_ids.append(nbs_id)
        return self.profiles.get(nbs_id, {})


def profile(
    *,
    nbs_id: int,
    solution: str,
    removal_rows: list[dict[str, Any]] | None = None,
    implementation_rows: list[dict[str, Any]] | None = None,
    footprint_rows: list[dict[str, Any]] | None = None,
    criteria_rows: list[dict[str, Any]] | None = None,
    option_extra: dict[str, Any] | None = None,
    missing_sections: list[str] | None = None,
) -> dict[str, Any]:
    """Create a raw NbS profile shaped like NbsCatalogService output."""

    option = {
        "id": nbs_id,
        "solution": solution,
        "family": "Constructed Wetlands",
        "description": "Test-only catalogue row",
        "optimal_water_type": "domestic wastewater",
        "location_suitability": 0.8,
        "climate_suitability": "tropical",
        "soil_type": 0.6,
        "resource_requirements": "moderate earthwork",
        "source_id": 10,
    }
    option.update(option_extra or {})
    implementation = implementation_rows
    if implementation is None:
        implementation = [
            {
                "nbs_id": nbs_id,
                "implementation_steps": "Build lined cells and install vegetation media.",
                "maintenance_requirements": "Remove litter and inspect flow monthly.",
                "source_id": 20,
            }
        ]
    return {
        "option": option,
        "removal_efficiencies": removal_rows or [],
        "implementation": implementation,
        "footprint": footprint_rows or [],
        "criteria": criteria_rows or [],
        "missing_sections": missing_sections or [],
    }


def fake_provider() -> FakeNbsCatalogService:
    """Build fake profiles with mixed raw criterion availability."""

    return FakeNbsCatalogService(
        {
            1: profile(
                nbs_id=1,
                solution="Horizontal wetland",
                removal_rows=[
                    {"parameter": "BOD", "eff_low": 60.0, "eff_high": 85.0, "source_id": 31},
                    {"parameter": "TSS", "eff_low": 55.0, "eff_high": 80.0, "source_id": 32},
                ],
                footprint_rows=[
                    {
                        "area_per_pe_low": 2.0,
                        "area_per_pe_high": 5.0,
                        "hlr_m3_m2_d": 0.08,
                        "source_id": 41,
                    }
                ],
                criteria_rows=[
                    {
                        "criterion": "cost",
                        "value_qual": "medium",
                        "confidence": "literature",
                        "source_id": 51,
                    },
                    {
                        "criterion": "O&M simplicity",
                        "value_qual": "simple",
                        "confidence": "literature",
                        "source_id": 52,
                    },
                    {
                        "criterion": "co-benefits",
                        "value_qual": "habitat and cooling",
                        "confidence": "literature",
                        "source_id": 53,
                    },
                ],
            ),
            2: profile(
                nbs_id=2,
                solution="Catalogue-only nutrient system",
                removal_rows=[],
                implementation_rows=[],
                footprint_rows=[],
                criteria_rows=[
                    {
                        "criterion": "maintenance",
                        "value_qual": "unknown",
                        "confidence": "low",
                        "source_id": 61,
                    }
                ],
                option_extra={
                    "supported_treatment_needs": ["nutrients"],
                    "resource_requirements": None,
                },
                missing_sections=["removal_efficiency", "implementation", "footprint"],
            ),
            3: profile(
                nbs_id=3,
                solution="Metal-only polishing unit",
                removal_rows=[
                    {"parameter": "arsenic", "eff_low": 40.0, "source_id": 71}
                ],
            ),
        }
    )


def candidate_bundle() -> CandidateFilterBundle:
    """Return a Step E-style candidate bundle for Step F tests."""

    results = [
        CandidateFilterResult(
            nbs_id=1,
            nbs_name="Horizontal wetland",
            eligibility_status="eligible",
            supported_treatment_needs=["organic_load", "solids"],
            unsupported_treatment_needs=["nutrients"],
            caution_flags=["Requires pre-treatment if solids are high."],
            evidence_source_ids=[10, 31, 32],
            implementation_source_ids=[20],
        ),
        CandidateFilterResult(
            nbs_id=2,
            nbs_name="Catalogue-only nutrient system",
            eligibility_status="data_pending",
            supported_treatment_needs=["nutrients"],
            data_pending_reasons=["Catalogue support exists but removal evidence is missing."],
            evidence_source_ids=[10],
            implementation_source_ids=[],
        ),
        CandidateFilterResult(
            nbs_id=3,
            nbs_name="Metal-only polishing unit",
            eligibility_status="ineligible",
            unsupported_treatment_needs=["organic_load"],
            exclusion_reasons=["No explicit support was found."],
            evidence_source_ids=[10, 71],
        ),
    ]
    return CandidateFilterBundle(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        treatment_need_groups=["organic_load", "solids", "nutrients"],
        candidate_count=3,
        eligible_count=1,
        data_pending_count=1,
        ineligible_count=1,
        results=results,
    )


def build_matrix() -> tuple[Any, FakeNbsCatalogService]:
    """Build a Step F matrix bundle with fake provider data."""

    provider = fake_provider()
    bundle = McdaMatrixBuilder(provider).build(candidate_bundle())
    return bundle, provider


def assert_eligible_candidates_become_matrix_rows() -> None:
    """Eligible and data-pending candidates should become matrix rows."""

    bundle, _provider = build_matrix()
    row_ids = [row.nbs_id for row in bundle.rows]

    assert bundle.row_count == 2
    assert row_ids == [1, 2]
    assert bundle.rows[0].eligibility_status == "eligible"
    assert bundle.rows[1].eligibility_status == "data_pending"


def assert_data_pending_candidate_has_missing_criteria() -> None:
    """Data-pending rows should keep missing raw criteria visible."""

    bundle, _provider = build_matrix()
    data_pending_row = next(row for row in bundle.rows if row.nbs_id == 2)

    assert "removal_evidence" in data_pending_row.missing_criteria
    assert "footprint" in data_pending_row.missing_criteria
    assert "implementation_complexity" in data_pending_row.missing_criteria
    assert data_pending_row.criteria_values["maintenance_indicator"]["criteria_rows"]


def assert_ineligible_candidates_are_excluded_and_counted() -> None:
    """Ineligible candidates should not become rows or trigger profile fetches."""

    bundle, provider = build_matrix()

    assert bundle.excluded_ineligible_count == 1
    assert 3 not in [row.nbs_id for row in bundle.rows]
    assert 3 not in provider.requested_ids


def assert_criteria_names_are_collected() -> None:
    """Criteria names should reflect raw buckets present in matrix rows."""

    bundle, _provider = build_matrix()

    assert "removal_evidence" in bundle.criteria_names
    assert "footprint" in bundle.criteria_names
    assert "maintenance_indicator" in bundle.criteria_names
    assert "climate_site_suitability" in bundle.criteria_names
    assert "catalogue_criteria" in bundle.criteria_names


def assert_missing_criteria_summary_works() -> None:
    """The missing criteria summary should count gaps across included rows."""

    bundle, _provider = build_matrix()

    assert bundle.missing_criteria_summary["removal_evidence"] == 1
    assert bundle.missing_criteria_summary["footprint"] == 1
    assert bundle.missing_criteria_summary["co_benefit_indicator"] == 1


def assert_weights_status_is_not_applied() -> None:
    """Step F must not apply AHP or any other criteria weights."""

    bundle, _provider = build_matrix()

    assert bundle.weights_status == "not_applied"


def assert_no_future_fields() -> None:
    """Step F output must not include recommendation/ranking/scoring fields."""

    bundle, _provider = build_matrix()
    found = _find_forbidden_keys(bundle.to_dict(), FORBIDDEN_FIELDS)

    assert not found, f"Step F leaked future fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The Step F test should stay in engines and avoid API behavior."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


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
    """Run all Step F checks."""

    assert_eligible_candidates_become_matrix_rows()
    assert_data_pending_candidate_has_missing_criteria()
    assert_ineligible_candidates_are_excluded_and_counted()
    assert_criteria_names_are_collected()
    assert_missing_criteria_summary_works()
    assert_weights_status_is_not_applied()
    assert_no_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("mcda matrix checks ok: Step F raw matrix preparation only")


if __name__ == "__main__":
    main()

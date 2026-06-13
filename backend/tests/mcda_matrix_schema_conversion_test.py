"""Conversion test from Step F MCDA matrix output to response schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_matrix_schema_conversion_test.py

This test uses fake NbS catalogue/profile data. It does not connect to Azure,
mutate data, call API routes, rank candidates, calculate TOPSIS/AHP, calculate
match/confidence scores, recommend plants, or create final recommendations.
"""

import sys
from typing import Any

from app.engines import (
    CandidateFilterBundle,
    CandidateFilterResult,
    McdaMatrixBuilder,
)
from app.schemas import McdaMatrixBundleResponse


FORBIDDEN_FIELDS = {
    "recommendation",
    "ranking",
    "match_score",
    "confidence_score",
    "topsis",
    "ahp",
}


class FakeNbsCatalogService:
    """Small provider-shaped test double for raw NbS catalogue profiles."""

    def __init__(self, profiles: dict[int, dict[str, Any]]) -> None:
        self.profiles = profiles

    def list_options(self) -> list[dict[str, Any]]:
        """Return fake options without querying a database."""

        return [
            profile["option"]
            for profile in self.profiles.values()
            if profile.get("option")
        ]

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return one fake raw profile."""

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
        "description": "Test-only conversion catalogue row",
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
    """Return a Step E-style candidate bundle for conversion tests."""

    return CandidateFilterBundle(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        treatment_need_groups=["organic_load", "solids", "nutrients"],
        candidate_count=3,
        eligible_count=1,
        data_pending_count=1,
        ineligible_count=1,
        results=[
            CandidateFilterResult(
                nbs_id=1,
                nbs_name="Horizontal wetland",
                eligibility_status="eligible",
                supported_treatment_needs=["organic_load", "solids"],
                unsupported_treatment_needs=["nutrients"],
                evidence_source_ids=[10, 31, 32],
                implementation_source_ids=[20],
            ),
            CandidateFilterResult(
                nbs_id=2,
                nbs_name="Catalogue-only nutrient system",
                eligibility_status="data_pending",
                supported_treatment_needs=["nutrients"],
                data_pending_reasons=[
                    "Catalogue support exists but removal evidence is missing."
                ],
                evidence_source_ids=[10],
            ),
            CandidateFilterResult(
                nbs_id=3,
                nbs_name="Metal-only polishing unit",
                eligibility_status="ineligible",
                unsupported_treatment_needs=["organic_load"],
                exclusion_reasons=["No explicit support was found."],
                evidence_source_ids=[10, 71],
            ),
        ],
    )


def build_actual_matrix_payload() -> dict[str, Any]:
    """Build a real Step F dataclass bundle and return its dictionary output."""

    bundle = McdaMatrixBuilder(fake_provider()).build(candidate_bundle())
    return bundle.to_dict()


def assert_actual_matrix_output_validates_against_schema() -> None:
    """Actual Step F output should validate as McdaMatrixBundleResponse."""

    response = McdaMatrixBundleResponse(**build_actual_matrix_payload())
    dump = response.model_dump()

    assert dump["use_case"] == "surface_discharge"
    assert dump["row_count"] == 2
    assert dump["excluded_ineligible_count"] == 1
    assert dump["weights_status"] == "not_applied"


def assert_eligible_and_data_pending_rows_are_present() -> None:
    """Converted schema should preserve eligible and data-pending matrix rows."""

    response = McdaMatrixBundleResponse(**build_actual_matrix_payload())
    rows = response.model_dump()["rows"]
    statuses = {row["eligibility_status"] for row in rows}
    row_ids = [row["nbs_id"] for row in rows]

    assert statuses == {"eligible", "data_pending"}
    assert row_ids == [1, 2]


def assert_ineligible_candidate_is_excluded_and_counted() -> None:
    """Converted schema should not include the ineligible candidate row."""

    response = McdaMatrixBundleResponse(**build_actual_matrix_payload())
    dump = response.model_dump()

    assert dump["excluded_ineligible_count"] == 1
    assert 3 not in [row["nbs_id"] for row in dump["rows"]]


def assert_forbidden_fields_are_absent() -> None:
    """Converted Step F schema dump must not include future scoring fields."""

    response = McdaMatrixBundleResponse(**build_actual_matrix_payload())
    found = _find_forbidden_keys(response.model_dump(), FORBIDDEN_FIELDS)
    found.update(
        key.lower()
        for key in McdaMatrixBundleResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"MCDA matrix schema conversion leaked fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay in engines/schemas and avoid API behavior."""

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
    """Run all Step F schema conversion checks."""

    assert_actual_matrix_output_validates_against_schema()
    assert_eligible_and_data_pending_rows_are_present()
    assert_ineligible_candidate_is_excluded_and_counted()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("mcda matrix schema conversion checks ok: real Step F output validates")


if __name__ == "__main__":
    main()

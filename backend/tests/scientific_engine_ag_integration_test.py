"""Integration smoke test for Scientific Engine Steps A through G.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\scientific_engine_ag_integration_test.py

This test uses fake standards, fake NbS catalogue profiles, and user measured
observations. It does not connect to Azure, does not read or mutate database
records, does not call API routes, does not apply weights, does not rank
candidates, and does not create final recommendations.
"""

import sys
from typing import Any

from app.engines import (
    CandidateFilteringEngine,
    InputNormalizationEngine,
    McdaMatrixBuilder,
    McdaNormalizationEngine,
    PollutantGapEngine,
    TreatmentNeedClassifier,
    WaterInputAssemblyEngine,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "ranking",
    "rank",
    "match_score",
    "confidence_score",
    "topsis",
    "topsis_score",
    "ahp",
    "ahp_weight",
}


class FakeStandardsService:
    """Small provider-shaped test double for Step C standards."""

    def __init__(self, standards: list[dict[str, Any]]) -> None:
        self._standards = standards

    def get_standards_for_use_case(self, use_case: str) -> list[dict[str, Any]]:
        """Return fake standard rows for the requested use case only."""

        return [
            standard
            for standard in self._standards
            if standard.get("use_case") == use_case
        ]


class FakeNbsCatalogService:
    """Small provider-shaped test double for Step E and Step F profiles."""

    def __init__(self, profiles: dict[int, dict[str, Any]]) -> None:
        self.profiles = profiles

    def list_options(self) -> list[dict[str, Any]]:
        """Return fake NbS options without querying a database."""

        return [
            profile["option"]
            for profile in self.profiles.values()
            if profile.get("option")
        ]

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return one fake NbS profile."""

        return self.profiles.get(nbs_id, {})


def fake_standards_service() -> FakeStandardsService:
    """Build explicit fake standards for Step C."""

    return FakeStandardsService(
        [
            {
                "use_case": "surface_discharge",
                "parameter": "BOD",
                "limit_high": 3.0,
                "unit": "mg/L",
            },
            {
                "use_case": "surface_discharge",
                "parameter": "TSS",
                "limit_high": 30.0,
                "unit": "mg/L",
            },
            {
                "use_case": "surface_discharge",
                "parameter": "nitrate",
                "limit_high": 10.0,
                "unit": "mg/L",
            },
            {
                "use_case": "surface_discharge",
                "parameter": "DO",
                "limit_low": 5.0,
                "unit": "mg/L",
            },
        ]
    )


def nbs_profile(
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
    """Create a raw profile shaped like NbsCatalogService output."""

    option = {
        "id": nbs_id,
        "solution": solution,
        "family": "Test family",
        "description": "Fake A-G integration catalogue row",
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
                "implementation_steps": "Build and maintain as documented.",
                "maintenance_requirements": "Inspect flow and remove litter monthly.",
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


def fake_nbs_provider() -> FakeNbsCatalogService:
    """Build fake NbS profiles that exercise Steps E, F, and G states."""

    return FakeNbsCatalogService(
        {
            1: nbs_profile(
                nbs_id=1,
                solution="Horizontal wetland",
                removal_rows=[
                    {"parameter": "BOD", "eff_low": 60.0, "source_id": 31},
                    {"parameter": "TSS", "eff_high": 80.0, "source_id": 32},
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
                    {
                        "criterion": "co-benefits",
                        "value_qual": "habitat",
                        "confidence": "literature",
                        "source_id": 53,
                    },
                ],
            ),
            2: nbs_profile(
                nbs_id=2,
                solution="Catalogue-only polishing system",
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
            3: nbs_profile(
                nbs_id=3,
                solution="Metal-only polishing unit",
                removal_rows=[
                    {"parameter": "arsenic", "eff_low": 30.0, "source_id": 33}
                ],
            ),
        }
    )


def build_raw_input() -> dict[str, Any]:
    """Return request-like raw input for the A-G engine chain."""

    return {
        "use_case": " surface discharge ",
        "selected_parameters": [" BOD ", " TSS ", " nitrate ", " DO "],
        "measured_observations": [
            {"parameter": "BOD", "value": "12.0", "unit": "mg/L", "source_id": 101},
            {"parameter": "TSS", "value": 75.0, "unit": "mg/L", "source_id": 101},
            {"parameter": "nitrate", "value": 18.0, "unit": "mg/L", "source_id": 102},
            {"parameter": "DO", "value": 3.0, "unit": "mg/L", "source_id": 102},
        ],
    }


def run_ag_chain() -> dict[str, Any]:
    """Run Steps A, B, C, D, E, F, and G with fake/local objects only."""

    nbs_provider = fake_nbs_provider()
    context = InputNormalizationEngine().normalize(build_raw_input())
    water_bundle = WaterInputAssemblyEngine().assemble(context)
    gap_bundle = PollutantGapEngine(fake_standards_service()).calculate(
        water_bundle,
        use_case=context.normalized_input["use_case"],
    )
    treatment_bundle = TreatmentNeedClassifier().classify(gap_bundle)
    candidate_bundle = CandidateFilteringEngine(nbs_provider).filter_candidates(
        treatment_bundle,
    )
    matrix_bundle = McdaMatrixBuilder(nbs_provider).build(candidate_bundle)
    normalized_bundle = McdaNormalizationEngine().normalize(matrix_bundle)
    return {
        "context": context,
        "water_bundle": water_bundle,
        "gap_bundle": gap_bundle,
        "treatment_bundle": treatment_bundle,
        "candidate_bundle": candidate_bundle,
        "matrix_bundle": matrix_bundle,
        "normalized_bundle": normalized_bundle,
    }


def assert_engine_chain_runs_through_step_g() -> None:
    """A-G should run together and preserve expected staged output."""

    result = run_ag_chain()
    context = result["context"]
    water_bundle = result["water_bundle"]
    gap_bundle = result["gap_bundle"]
    matrix_bundle = result["matrix_bundle"]
    normalized_bundle = result["normalized_bundle"]

    assert context.validation_status == "valid"
    assert context.normalized_input["use_case"] == "surface_discharge"
    assert water_bundle.selected_source_type == "user_measured"
    assert gap_bundle.total_observations_checked == 4
    assert matrix_bundle.row_count == 2
    assert normalized_bundle.row_count == 2


def assert_expected_treatment_groups() -> None:
    """Treatment groups should come from Step C and Step D only."""

    treatment_bundle = run_ag_chain()["treatment_bundle"]
    groups = {need.need_group for need in treatment_bundle.treatment_needs}

    assert "organic_load" in groups
    assert "solids" in groups
    assert "nutrients" in groups
    assert "oxygen_deficit" in groups
    assert treatment_bundle.unclassified_parameters == []


def assert_candidate_filtering_status_mix() -> None:
    """Step E should include eligible, data_pending, and ineligible statuses."""

    candidate_bundle = run_ag_chain()["candidate_bundle"]
    statuses = {result.eligibility_status for result in candidate_bundle.results}

    assert statuses == {"eligible", "data_pending", "ineligible"}
    assert candidate_bundle.eligible_count == 1
    assert candidate_bundle.data_pending_count == 1
    assert candidate_bundle.ineligible_count == 1


def assert_matrix_includes_only_eligible_and_data_pending() -> None:
    """Step F matrix rows should exclude ineligible candidates."""

    matrix_bundle = run_ag_chain()["matrix_bundle"]
    statuses = {row.eligibility_status for row in matrix_bundle.rows}
    row_ids = [row.nbs_id for row in matrix_bundle.rows]

    assert statuses == {"eligible", "data_pending"}
    assert row_ids == [1, 2]
    assert 3 not in row_ids
    assert matrix_bundle.excluded_ineligible_count == 1


def assert_normalization_statuses_are_safe() -> None:
    """Step G should produce a normalized bundle without weights or ranking."""

    normalized_bundle = run_ag_chain()["normalized_bundle"]
    statuses = {
        criterion.normalization_status
        for row in normalized_bundle.rows
        for criterion in row.normalized_criteria
    }

    assert normalized_bundle.normalization_method == "min_max_unweighted"
    assert normalized_bundle.weights_status == "not_applied"
    assert normalized_bundle.skipped_criteria_count > 0
    assert "direction_unknown" in statuses
    assert "non_numeric" in statuses


def assert_no_future_fields() -> None:
    """A-G outputs must not include final recommendation or scoring fields."""

    result = run_ag_chain()
    payloads = [
        result["context"].to_dict(),
        result["water_bundle"].to_dict(),
        result["gap_bundle"].to_dict(),
        result["treatment_bundle"].to_dict(),
        result["candidate_bundle"].to_dict(),
        result["matrix_bundle"].to_dict(),
        result["normalized_bundle"].to_dict(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))

    assert not found, f"A-G integration leaked future fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The integration test should stay in engines and avoid API behavior."""

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
    """Run the A-G integration smoke checks."""

    assert_engine_chain_runs_through_step_g()
    assert_expected_treatment_groups()
    assert_candidate_filtering_status_mix()
    assert_matrix_includes_only_eligible_and_data_pending()
    assert_normalization_statuses_are_safe()
    assert_no_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-G integration checks ok: no recommendation path")


if __name__ == "__main__":
    main()

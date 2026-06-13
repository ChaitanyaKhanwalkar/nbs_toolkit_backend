r"""Integration smoke test for Scientific Engine Steps A through H.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_engine_ah_integration_test.py

This test uses fake standards, fake NbS catalogue profiles, fake temporary
weights, and user measured observations. It does not connect to Azure, read or
mutate database records, call API routes, calculate AHP pairwise weights,
calculate TOPSIS, rank candidates, calculate match/confidence scores,
recommend plants, or create final recommendations.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import (
    CandidateFilteringEngine,
    InputNormalizationEngine,
    McdaMatrixBuilder,
    McdaNormalizationEngine,
    McdaWeightsHandler,
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
        "description": "Fake A-H integration catalogue row",
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
    """Build fake NbS profiles that exercise Steps E through H states."""

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
    """Return request-like raw input for the A-H engine chain."""

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


def temporary_weights_for(criteria_names: list[str]) -> dict[str, float]:
    """Create fake temporary weights for every Step G criterion name."""

    return {
        criterion_name: float(index + 1)
        for index, criterion_name in enumerate(criteria_names)
    }


def run_ah_chain() -> dict[str, Any]:
    """Run Steps A through H with fake/local objects only."""

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
    weights_handler = McdaWeightsHandler()
    missing_weights_bundle = weights_handler.prepare_from_normalized_bundle(
        normalized_bundle,
    )
    temporary_weights_bundle = weights_handler.prepare_from_normalized_bundle(
        normalized_bundle,
        supplied_weights=temporary_weights_for(normalized_bundle.criteria_names),
        weights_source="temporary_integration_test_weights",
        expert_validated=False,
    )
    return {
        "context": context,
        "water_bundle": water_bundle,
        "gap_bundle": gap_bundle,
        "treatment_bundle": treatment_bundle,
        "candidate_bundle": candidate_bundle,
        "matrix_bundle": matrix_bundle,
        "normalized_bundle": normalized_bundle,
        "missing_weights_bundle": missing_weights_bundle,
        "temporary_weights_bundle": temporary_weights_bundle,
    }


def assert_engine_chain_runs_through_step_h() -> None:
    """A-H should run together and preserve expected staged output."""

    result = run_ah_chain()
    assert result["context"].validation_status == "valid"
    assert result["context"].normalized_input["use_case"] == "surface_discharge"
    assert result["water_bundle"].selected_source_type == "user_measured"
    assert result["gap_bundle"].total_observations_checked == 4
    assert result["candidate_bundle"].candidate_count == 3
    assert result["matrix_bundle"].row_count == 2
    assert result["normalized_bundle"].row_count == 2
    assert result["missing_weights_bundle"].criteria_names
    assert result["temporary_weights_bundle"].criteria_names


def assert_normalized_bundle_is_unweighted() -> None:
    """Step G should normalize only and keep weights unapplied."""

    normalized_bundle = run_ah_chain()["normalized_bundle"]

    assert normalized_bundle.normalization_method == "min_max_unweighted"
    assert normalized_bundle.weights_status == "not_applied"
    assert normalized_bundle.criteria_names


def assert_missing_weights_are_safe() -> None:
    """Step H should report missing weights without inventing values."""

    missing_weights_bundle = run_ah_chain()["missing_weights_bundle"]

    assert missing_weights_bundle.weights_status == "weights_missing"
    assert missing_weights_bundle.weights == {}
    assert missing_weights_bundle.expert_validated is False
    assert missing_weights_bundle.missing_weight_criteria == (
        missing_weights_bundle.criteria_names
    )


def assert_temporary_weights_are_not_final() -> None:
    """Temporary Step H weights should normalize but stay non-expert."""

    temporary_weights_bundle = run_ah_chain()["temporary_weights_bundle"]

    assert temporary_weights_bundle.weights_status == "temporary_not_expert_validated"
    assert temporary_weights_bundle.expert_validated is False
    assert temporary_weights_bundle.weights_source == "temporary_integration_test_weights"
    assert abs(sum(temporary_weights_bundle.weights.values()) - 1.0) < 0.000001
    assert temporary_weights_bundle.missing_weight_criteria == []
    assert temporary_weights_bundle.extra_weight_criteria == []


def assert_no_future_fields() -> None:
    """A-H outputs must not include final recommendation or scoring fields."""

    result = run_ah_chain()
    payloads = [
        result["context"].to_dict(),
        result["water_bundle"].to_dict(),
        result["gap_bundle"].to_dict(),
        result["treatment_bundle"].to_dict(),
        result["candidate_bundle"].to_dict(),
        result["matrix_bundle"].to_dict(),
        result["normalized_bundle"].to_dict(),
        result["missing_weights_bundle"].to_dict(),
        result["temporary_weights_bundle"].to_dict(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))

    assert not found, f"A-H integration leaked future fields: {sorted(found)}"


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
    """Run the A-H integration smoke checks."""

    assert_engine_chain_runs_through_step_h()
    assert_normalized_bundle_is_unweighted()
    assert_missing_weights_are_safe()
    assert_temporary_weights_are_not_final()
    assert_no_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-H integration checks ok: no recommendation path")


if __name__ == "__main__":
    main()

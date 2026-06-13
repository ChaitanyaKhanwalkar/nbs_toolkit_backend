r"""Integration smoke test for Scientific Engine Steps A through I.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_engine_ai_integration_test.py

This test uses fake standards, fake NbS catalogue profiles, fake numeric MCDA
criteria, fake temporary weights, and user measured observations. It does not
connect to Azure, read or mutate database records, call API routes, calculate
AHP pairwise weights, calculate confidence scores, recommend plants, classify
health risk, or create final recommendations.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from typing import Any

from app.engines import (
    CandidateFilteringEngine,
    InputNormalizationEngine,
    McdaMatrixBuilder,
    McdaMatrixBundle,
    McdaNormalizationEngine,
    McdaWeightsHandler,
    PollutantGapEngine,
    TreatmentNeedClassifier,
    TopsisRankingEngine,
    WaterInputAssemblyEngine,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "confidence_score",
    "plant_recommendation",
    "plant_recommendations",
    "plants",
    "health_risk",
    "ahp",
    "ahp_weight",
}

NUMERIC_CRITERIA_BY_NBS_ID = {
    1: {
        "removal_evidence_coverage": 0.95,
        "site_suitability": 0.80,
        "cost_indicator": 0.40,
    },
    2: {
        "removal_evidence_coverage": 0.45,
        "site_suitability": 0.55,
        "cost_indicator": 0.90,
    },
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
        "description": "Fake A-I integration catalogue row",
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
    """Build fake NbS profiles that exercise Steps E through I states."""

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
    """Return request-like raw input for the A-I engine chain."""

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


def add_fake_numeric_criteria(matrix_bundle: McdaMatrixBundle) -> McdaMatrixBundle:
    """Return a test-only matrix copy with numeric Step G criteria available."""

    rows = []
    criteria_names = list(matrix_bundle.criteria_names)
    for criterion_name in [
        "removal_evidence_coverage",
        "site_suitability",
        "cost_indicator",
    ]:
        if criterion_name not in criteria_names:
            criteria_names.append(criterion_name)

    for row in matrix_bundle.rows:
        criteria_values = dict(row.criteria_values)
        criteria_values.update(NUMERIC_CRITERIA_BY_NBS_ID.get(row.nbs_id, {}))
        rows.append(replace(row, criteria_values=criteria_values))

    return replace(matrix_bundle, rows=rows, criteria_names=criteria_names)


def temporary_weights_for(criteria_names: list[str]) -> dict[str, float]:
    """Create fake temporary weights for Step G criteria names."""

    weights = {criterion_name: 0.0 for criterion_name in criteria_names}
    weights.update(
        {
            "removal_evidence_coverage": 5.0,
            "site_suitability": 3.0,
            "cost_indicator": 2.0,
        }
    )
    return weights


def run_ai_chain() -> dict[str, Any]:
    """Run Steps A through I with fake/local objects only."""

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
    raw_matrix_bundle = McdaMatrixBuilder(nbs_provider).build(candidate_bundle)
    matrix_bundle = add_fake_numeric_criteria(raw_matrix_bundle)
    normalized_bundle = McdaNormalizationEngine().normalize(matrix_bundle)
    weights_bundle = McdaWeightsHandler().prepare_from_normalized_bundle(
        normalized_bundle,
        supplied_weights=temporary_weights_for(normalized_bundle.criteria_names),
        weights_source="temporary_ai_integration_test_weights",
        expert_validated=False,
    )
    ranking_bundle = TopsisRankingEngine().rank(normalized_bundle, weights_bundle)
    return {
        "context": context,
        "water_bundle": water_bundle,
        "gap_bundle": gap_bundle,
        "treatment_bundle": treatment_bundle,
        "candidate_bundle": candidate_bundle,
        "raw_matrix_bundle": raw_matrix_bundle,
        "matrix_bundle": matrix_bundle,
        "normalized_bundle": normalized_bundle,
        "weights_bundle": weights_bundle,
        "ranking_bundle": ranking_bundle,
    }


def assert_engine_chain_runs_through_step_i() -> None:
    """A-I should run together and preserve expected staged output."""

    result = run_ai_chain()
    assert result["context"].validation_status == "valid"
    assert result["context"].normalized_input["use_case"] == "surface_discharge"
    assert result["water_bundle"].selected_source_type == "user_measured"
    assert result["gap_bundle"].total_observations_checked == 4
    assert result["candidate_bundle"].candidate_count == 3
    assert result["raw_matrix_bundle"].row_count == 2
    assert result["matrix_bundle"].row_count == 2
    assert result["normalized_bundle"].normalization_method == "min_max_unweighted"
    assert result["ranking_bundle"].ranking_method == "topsis"


def assert_topsis_ranking_is_provisional() -> None:
    """Step I should rank with temporary weights but keep status honest."""

    ranking_bundle = run_ai_chain()["ranking_bundle"]

    assert ranking_bundle.weights_status == "temporary_not_expert_validated"
    assert ranking_bundle.weights_source == "temporary_ai_integration_test_weights"
    assert ranking_bundle.expert_validated is False
    assert any("provisional" in warning for warning in ranking_bundle.warnings)


def assert_ranked_candidates_have_rank_and_closeness() -> None:
    """Step I should produce ranked candidates with TOPSIS closeness."""

    ranking_bundle = run_ai_chain()["ranking_bundle"]

    assert ranking_bundle.ranked_candidates
    assert ranking_bundle.ranked_count == len(ranking_bundle.ranked_candidates)
    assert [candidate.rank for candidate in ranking_bundle.ranked_candidates] == [1, 2]
    assert all(
        candidate.topsis_closeness is not None
        for candidate in ranking_bundle.ranked_candidates
    )
    assert ranking_bundle.criteria_used == [
        "cost_indicator",
        "removal_evidence_coverage",
        "site_suitability",
    ]


def assert_no_future_fields() -> None:
    """A-I outputs must not include final recommendation/confidence fields."""

    result = run_ai_chain()
    payloads = [
        result["context"].to_dict(),
        result["water_bundle"].to_dict(),
        result["gap_bundle"].to_dict(),
        result["treatment_bundle"].to_dict(),
        result["candidate_bundle"].to_dict(),
        result["raw_matrix_bundle"].to_dict(),
        result["matrix_bundle"].to_dict(),
        result["normalized_bundle"].to_dict(),
        result["weights_bundle"].to_dict(),
        result["ranking_bundle"].to_dict(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))

    assert not found, f"A-I integration leaked future fields: {sorted(found)}"


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
    """Run the A-I integration smoke checks."""

    assert_engine_chain_runs_through_step_i()
    assert_topsis_ranking_is_provisional()
    assert_ranked_candidates_have_rank_and_closeness()
    assert_no_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-I integration checks ok: TOPSIS only, no recommendation path")


if __name__ == "__main__":
    main()

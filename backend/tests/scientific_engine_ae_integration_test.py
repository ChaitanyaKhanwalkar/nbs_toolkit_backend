"""Integration smoke test for Scientific Engine Steps A through E.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\scientific_engine_ae_integration_test.py

This test uses fake standards, fake NbS catalogue profiles, and user measured
observations. It does not connect to Azure, does not read or mutate database
records, does not call API routes, and does not create final recommendations.
"""

import sys
from typing import Any

from app.engines import (
    CandidateFilteringEngine,
    InputNormalizationEngine,
    PollutantGapEngine,
    TreatmentNeedClassifier,
    WaterInputAssemblyEngine,
)


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
    """Small provider-shaped test double for Step E candidate profiles."""

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
    option_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a raw Step E profile shaped like NbsCatalogService output."""

    option = {
        "id": nbs_id,
        "solution": solution,
        "family": "Test family",
        "description": "Fake integration-test catalogue row",
        "source_id": 10,
    }
    option.update(option_extra or {})
    implementation = implementation_rows
    if implementation is None:
        implementation = [
            {
                "nbs_id": nbs_id,
                "implementation_steps": "Build and maintain as documented.",
                "source_id": 20,
            }
        ]
    return {
        "option": option,
        "removal_efficiencies": removal_rows or [],
        "implementation": implementation,
        "footprint": [],
        "criteria": [],
        "missing_sections": [] if implementation else ["implementation"],
    }


def fake_nbs_provider() -> FakeNbsCatalogService:
    """Build fake NbS profiles that exercise Step E statuses."""

    return FakeNbsCatalogService(
        {
            1: nbs_profile(
                nbs_id=1,
                solution="Horizontal wetland",
                removal_rows=[
                    {"parameter": "BOD", "eff_low": 60.0, "source_id": 31},
                    {"parameter": "TSS", "eff_high": 80.0, "source_id": 32},
                ],
            ),
            2: nbs_profile(
                nbs_id=2,
                solution="Catalogue-only polishing system",
                option_extra={"supported_treatment_needs": ["nutrients"]},
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
    """Return request-like raw input for the A-E engine chain."""

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


def run_ae_chain() -> dict[str, Any]:
    """Run Steps A, B, C, D, and E with fake/local objects only."""

    context = InputNormalizationEngine().normalize(build_raw_input())
    water_bundle = WaterInputAssemblyEngine().assemble(context)
    gap_bundle = PollutantGapEngine(fake_standards_service()).calculate(
        water_bundle,
        use_case=context.normalized_input["use_case"],
    )
    treatment_bundle = TreatmentNeedClassifier().classify(gap_bundle)
    candidate_bundle = CandidateFilteringEngine(fake_nbs_provider()).filter_candidates(
        treatment_bundle,
    )
    return {
        "context": context,
        "water_bundle": water_bundle,
        "gap_bundle": gap_bundle,
        "treatment_bundle": treatment_bundle,
        "candidate_bundle": candidate_bundle,
    }


def assert_engine_chain_runs() -> None:
    """A-E should run together and preserve expected staged output."""

    result = run_ae_chain()
    context = result["context"]
    water_bundle = result["water_bundle"]
    gap_bundle = result["gap_bundle"]
    candidate_bundle = result["candidate_bundle"]

    assert context.validation_status == "valid"
    assert context.normalized_input["use_case"] == "surface_discharge"
    assert water_bundle.selected_source_type == "user_measured"
    assert water_bundle.observation_count == 4
    assert gap_bundle.total_observations_checked == 4
    assert gap_bundle.exceedance_count == 4
    assert candidate_bundle.candidate_count == 3


def assert_expected_treatment_groups() -> None:
    """Treatment groups should come from Step C gap results only."""

    treatment_bundle = run_ae_chain()["treatment_bundle"]
    groups = {need.need_group for need in treatment_bundle.treatment_needs}

    assert "organic_load" in groups
    assert "solids" in groups
    assert "nutrients" in groups
    assert "oxygen_deficit" in groups
    assert treatment_bundle.unclassified_parameters == []


def assert_candidate_status_mix() -> None:
    """Step E should return eligible, ineligible, and data_pending results."""

    candidate_bundle = run_ae_chain()["candidate_bundle"]
    statuses = {result.eligibility_status for result in candidate_bundle.results}
    by_name = {result.nbs_name: result for result in candidate_bundle.results}

    assert statuses == {"eligible", "data_pending", "ineligible"}
    assert candidate_bundle.eligible_count == 1
    assert candidate_bundle.data_pending_count == 1
    assert candidate_bundle.ineligible_count == 1
    assert by_name["Horizontal wetland"].supported_treatment_needs == [
        "organic_load",
        "solids",
    ]
    assert by_name["Catalogue-only polishing system"].supported_treatment_needs == [
        "nutrients"
    ]
    assert "oxygen_deficit" in by_name["Metal-only polishing unit"].unsupported_treatment_needs


def assert_no_future_fields() -> None:
    """A-E outputs must not include final recommendation or scoring fields."""

    forbidden_fields = {
        "recommendation",
        "recommendations",
        "final_recommendation",
        "match_score",
        "confidence_score",
        "ranking",
        "rank",
        "topsis",
        "topsis_score",
        "ahp",
        "ahp_weight",
    }
    result = run_ae_chain()
    payloads = [
        result["context"].to_dict(),
        result["water_bundle"].to_dict(),
        result["gap_bundle"].to_dict(),
        result["treatment_bundle"].to_dict(),
        result["candidate_bundle"].to_dict(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, forbidden_fields))

    assert not found, f"A-E integration leaked future fields: {sorted(found)}"


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
    """Run the A-E integration smoke checks."""

    assert_engine_chain_runs()
    assert_expected_treatment_groups()
    assert_candidate_status_mix()
    assert_no_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-E integration checks ok: no recommendation path")


if __name__ == "__main__":
    main()

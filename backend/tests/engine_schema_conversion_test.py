"""Conversion tests from real A-E engine outputs to response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\engine_schema_conversion_test.py

These tests use fake providers and user measured observations. They do not
connect to Azure, do not mutate data, do not call API routes, and do not create
workflow or final recommendation behavior.
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
from app.schemas import (
    CandidateFilterBundleResponse,
    CandidateFilterResultResponse,
    InputContextResponse,
    ParameterGapResultResponse,
    PollutantGapBundleResponse,
    TreatmentNeedBundleResponse,
    TreatmentNeedResultResponse,
    WaterInputBundleResponse,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "ranking",
    "match_score",
    "confidence_score",
    "topsis",
    "ahp",
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
        ]
    )


def nbs_profile(
    *,
    nbs_id: int,
    solution: str,
    removal_rows: list[dict[str, Any]] | None = None,
    option_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a raw Step E profile shaped like NbsCatalogService output."""

    option = {
        "id": nbs_id,
        "solution": solution,
        "family": "Test family",
        "description": "Fake conversion-test catalogue row",
        "source_id": 10,
    }
    option.update(option_extra or {})
    return {
        "option": option,
        "removal_efficiencies": removal_rows or [],
        "implementation": [
            {
                "nbs_id": nbs_id,
                "implementation_steps": "Build and maintain as documented.",
                "source_id": 20,
            }
        ],
        "footprint": [],
        "criteria": [],
        "missing_sections": [],
    }


def fake_nbs_provider() -> FakeNbsCatalogService:
    """Build fake NbS profiles for Step E schema conversion."""

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
                solution="Catalogue-only nutrient system",
                option_extra={"supported_treatment_needs": ["nutrients"]},
            ),
        }
    )


def build_raw_input() -> dict[str, Any]:
    """Return request-like raw input for the A-E engine chain."""

    return {
        "use_case": " surface discharge ",
        "selected_parameters": [" BOD ", " TSS ", " nitrate "],
        "measured_observations": [
            {"parameter": "BOD", "value": "12.0", "unit": "mg/L", "source_id": 101},
            {"parameter": "TSS", "value": 75.0, "unit": "mg/L", "source_id": 101},
            {"parameter": "nitrate", "value": 18.0, "unit": "mg/L", "source_id": 102},
        ],
    }


def run_ae_chain() -> dict[str, Any]:
    """Run Steps A-E and return real engine dataclass outputs."""

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


def convert_outputs(result: dict[str, Any]) -> list[object]:
    """Convert real engine dataclass outputs into Pydantic response schemas."""

    gap_results = [
        ParameterGapResultResponse(**gap_result.to_dict())
        for gap_result in result["gap_bundle"].results
    ]
    treatment_need_results = [
        TreatmentNeedResultResponse(**need_result.to_dict())
        for need_result in result["treatment_bundle"].treatment_needs
    ]
    candidate_results = [
        CandidateFilterResultResponse(**candidate_result.to_dict())
        for candidate_result in result["candidate_bundle"].results
    ]

    return [
        InputContextResponse(**result["context"].to_dict()),
        WaterInputBundleResponse(**result["water_bundle"].to_dict()),
        *gap_results,
        PollutantGapBundleResponse(**result["gap_bundle"].to_dict()),
        *treatment_need_results,
        TreatmentNeedBundleResponse(**result["treatment_bundle"].to_dict()),
        *candidate_results,
        CandidateFilterBundleResponse(**result["candidate_bundle"].to_dict()),
    ]


def assert_real_outputs_validate_against_schemas() -> None:
    """Real A-E dataclass outputs should validate against engine schemas."""

    result = run_ae_chain()
    schemas = convert_outputs(result)
    dumps = [schema.model_dump() for schema in schemas]

    assert result["context"].validation_status == "valid"
    assert result["water_bundle"].selected_source_type == "user_measured"
    assert result["gap_bundle"].exceedance_count == 3
    assert result["candidate_bundle"].candidate_count == 2
    assert len(dumps) == 13


def assert_nested_schema_conversion_preserves_key_fields() -> None:
    """Converted schemas should preserve core staged output fields."""

    schemas = convert_outputs(run_ae_chain())
    candidate_bundle = next(
        schema for schema in schemas if isinstance(schema, CandidateFilterBundleResponse)
    )
    treatment_bundle = next(
        schema for schema in schemas if isinstance(schema, TreatmentNeedBundleResponse)
    )

    groups = {need.need_group for need in treatment_bundle.treatment_needs}
    statuses = {candidate.eligibility_status for candidate in candidate_bundle.results}

    assert groups == {"organic_load", "solids", "nutrients"}
    assert statuses == {"eligible", "data_pending"}
    assert candidate_bundle.eligible_count == 1
    assert candidate_bundle.data_pending_count == 1


def assert_forbidden_fields_are_absent() -> None:
    """Converted schema dumps must not include future recommendation/scoring fields."""

    found = set()
    for schema in convert_outputs(run_ae_chain()):
        found.update(_find_forbidden_keys(schema.model_dump(), FORBIDDEN_FIELDS))

    assert not found, f"Engine schema conversion leaked fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay in engines/schemas and avoid API behavior."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def _find_forbidden_keys(value: Any, forbidden_fields: set[str]) -> set[str]:
    """Recursively find forbidden dictionary keys."""

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
    """Run all engine schema conversion checks."""

    assert_real_outputs_validate_against_schemas()
    assert_nested_schema_conversion_preserves_key_fields()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("engine schema conversion checks ok: real A-E outputs validate")


if __name__ == "__main__":
    main()

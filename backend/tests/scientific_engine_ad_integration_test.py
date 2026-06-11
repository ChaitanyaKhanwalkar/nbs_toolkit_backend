"""Integration smoke test for Scientific Engine Steps A through D.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\scientific_engine_ad_integration_test.py

This test uses fake standards and user measured observations. It does not
connect to Azure, does not read or mutate database records, does not call API
routes, and does not create recommendations.
"""

import sys
from typing import Any

from app.engines import (
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


def fake_standards_service() -> FakeStandardsService:
    """Build explicit fake standards for the integration smoke test."""

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
            {
                "use_case": "surface_discharge",
                "parameter": "pH",
                "limit_low": 6.5,
                "limit_high": 8.5,
                "unit": "pH",
            },
        ]
    )


def build_raw_input() -> dict[str, Any]:
    """Return request-like raw input for the A-D engine chain."""

    return {
        "use_case": " surface discharge ",
        "station": "  Local Test Station  ",
        "selected_parameters": [" BOD ", " TSS ", " nitrate ", " DO ", " pH "],
        "measured_observations": [
            {"parameter": "BOD", "value": "12.0", "unit": "mg/L", "source_id": 101},
            {"parameter": "TSS", "value": 75.0, "unit": "mg/L", "source_id": 101},
            {"parameter": "nitrate", "value": 18.0, "unit": "mg/L", "source_id": 102},
            {"parameter": "DO", "value": 3.0, "unit": "mg/L", "source_id": 102},
            {"parameter": "pH", "value": 9.2, "unit": "pH", "source_id": 103},
        ],
    }


def run_ad_chain() -> dict[str, Any]:
    """Run Steps A, B, C, and D with fake/local objects only."""

    context = InputNormalizationEngine().normalize(build_raw_input())
    water_bundle = WaterInputAssemblyEngine().assemble(context)
    gap_bundle = PollutantGapEngine(fake_standards_service()).calculate(
        water_bundle,
        use_case=context.normalized_input["use_case"],
    )
    treatment_bundle = TreatmentNeedClassifier().classify(gap_bundle)
    return {
        "context": context,
        "water_bundle": water_bundle,
        "gap_bundle": gap_bundle,
        "treatment_bundle": treatment_bundle,
    }


def assert_engine_chain_runs() -> None:
    """A-D should run together and preserve the expected flow state."""

    result = run_ad_chain()
    context = result["context"]
    water_bundle = result["water_bundle"]
    gap_bundle = result["gap_bundle"]

    assert context.validation_status == "valid"
    assert context.normalized_input["use_case"] == "surface_discharge"
    assert context.normalized_input["station"] == "Local Test Station"
    assert water_bundle.selected_source_type == "user_measured"
    assert water_bundle.observation_count == 5
    assert gap_bundle.total_observations_checked == 5
    assert gap_bundle.exceedance_count == 5


def assert_expected_treatment_groups() -> None:
    """Treatment groups should come from Step C gap results only."""

    treatment_bundle = run_ad_chain()["treatment_bundle"]
    groups = {need.need_group for need in treatment_bundle.treatment_needs}

    assert "organic_load" in groups
    assert "solids" in groups
    assert "nutrients" in groups
    assert "oxygen_deficit" in groups
    assert "ph_correction" in groups
    assert treatment_bundle.unclassified_parameters == []


def assert_no_future_fields() -> None:
    """A-D outputs must not include recommendation or ranking fields."""

    forbidden_fields = {
        "recommendation",
        "recommendations",
        "match_score",
        "confidence_score",
        "ranking",
        "rank",
        "topsis",
        "topsis_score",
        "ahp",
        "ahp_weight",
    }
    result = run_ad_chain()
    payloads = [
        result["context"].to_dict(),
        result["water_bundle"].to_dict(),
        result["gap_bundle"].to_dict(),
        result["treatment_bundle"].to_dict(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, forbidden_fields))

    assert not found, f"A-D integration leaked future fields: {sorted(found)}"


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
    """Run the A-D integration smoke checks."""

    assert_engine_chain_runs()
    assert_expected_treatment_groups()
    assert_no_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-D integration checks ok: no recommendation path")


if __name__ == "__main__":
    main()

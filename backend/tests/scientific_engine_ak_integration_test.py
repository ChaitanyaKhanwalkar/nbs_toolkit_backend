r"""Integration smoke test for Scientific Engine Steps A through K.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\scientific_engine_ak_integration_test.py

This test uses fake standards, fake NbS catalogue profiles, fake numeric MCDA
criteria, fake temporary weights, fake confidence scoring, fake explicit plant
mappings, and user measured observations. It does not connect to Azure, read or
mutate database records, call API routes, implement AHP pairwise weights, change
TOPSIS ranking, change confidence scores, classify health risk, or create final
recommendations.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import PlantMatchingEngine
from scientific_engine_aj_integration_test import run_aj_chain


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "plant_recommendation",
    "plant_recommendations",
    "health_risk",
    "api_route",
    "recommend_endpoint",
    "endpoint",
    "route",
    "ahp",
    "ahp_weight",
}


class FakePlantMappingProvider:
    """Small provider-shaped fake with explicit plant mappings only."""

    def get_plants_for_nbs(
        self,
        nbs_id: int,
        *,
        include_invasive: bool = False,
    ) -> list[dict[str, Any]]:
        """Return fake plants only for explicitly mapped NbS IDs."""

        mappings = {
            1: [
                {
                    "plant_id": 501,
                    "scientific_name": "Typha latifolia",
                    "common_name": "Broadleaf cattail",
                    "basis": "Explicit mapping for wetland organic-load polishing.",
                    "source_ids": [701, 702],
                }
            ],
            2: [
                {
                    "plant_id": 601,
                    "scientific_name": "Cyperus alternifolius",
                    "common_name": "Umbrella papyrus",
                    "basis": "Explicit mapping for polishing-system vegetation.",
                    "source_id": 703,
                }
            ],
        }
        return list(mappings.get(nbs_id, []))


def run_ak_chain() -> dict[str, Any]:
    """Run Steps A through K with fake/local objects only."""

    result = run_aj_chain()
    plant_matching_bundle = PlantMatchingEngine(
        FakePlantMappingProvider()
    ).match_plants(
        result["ranking_bundle"],
        result["confidence_bundle"],
    )
    result["plant_matching_bundle"] = plant_matching_bundle
    return result


def assert_engine_chain_runs_through_step_k() -> None:
    """A-K should run together and preserve staged outputs."""

    result = run_ak_chain()

    assert result["context"].validation_status == "valid"
    assert result["ranking_bundle"].ranking_method == "topsis"
    assert result["confidence_bundle"].confidence_method == "rule_based_v1"
    assert result["plant_matching_bundle"].plant_matching_method == "explicit_mapping_v1"
    assert result["plant_matching_bundle"].candidate_matches
    assert all(
        candidate.plant_matches
        for candidate in result["plant_matching_bundle"].candidate_matches
    )


def assert_plant_matching_preserves_ranking_and_confidence() -> None:
    """Step K should not change Step I or Step J values."""

    result = run_ak_chain()
    ranked_candidates = result["ranking_bundle"].ranked_candidates
    confidence_results = result["confidence_bundle"].results
    plant_matches = result["plant_matching_bundle"].candidate_matches

    assert [candidate.rank for candidate in plant_matches] == [
        candidate.rank for candidate in ranked_candidates
    ]
    assert [candidate.topsis_closeness for candidate in plant_matches] == [
        candidate.topsis_closeness for candidate in ranked_candidates
    ]
    assert [candidate.confidence_score for candidate in plant_matches] == [
        candidate.confidence_score for candidate in confidence_results
    ]


def assert_only_explicit_plant_mappings_are_attached() -> None:
    """The fake provider should control exactly which plants appear."""

    bundle = run_ak_chain()["plant_matching_bundle"]
    plant_ids = [
        plant.plant_id
        for candidate in bundle.candidate_matches
        for plant in candidate.plant_matches
    ]

    assert plant_ids == [501, 601]


def assert_no_forbidden_future_fields() -> None:
    """A-K outputs must not include final recommendation or match-score fields."""

    result = run_ak_chain()
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
        result["confidence_bundle"].to_dict(),
        result["plant_matching_bundle"].to_dict(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))

    assert not found, f"A-K integration leaked forbidden fields: {sorted(found)}"


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
    """Run the A-K integration smoke checks."""

    assert_engine_chain_runs_through_step_k()
    assert_plant_matching_preserves_ranking_and_confidence()
    assert_only_explicit_plant_mappings_are_attached()
    assert_no_forbidden_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("scientific engine A-K integration checks ok: explicit plant matching only")


if __name__ == "__main__":
    main()

r"""Smoke tests for Scientific Engine Step K.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\plant_matching_test.py

These tests use fake Step I ranking, fake Step J confidence, and fake explicit
plant mappings only. They do not connect to Azure, mutate data, call API
routes, change TOPSIS rank, change confidence scores, calculate match_score,
classify health risk, or create final recommendations.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import PlantMatchingEngine
from confidence_scoring_test import ranking_bundle, score_complete_expert_case


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

    def __init__(self, mappings: dict[int, list[dict[str, Any]]]) -> None:
        self.mappings = mappings

    def get_plants_for_nbs(
        self,
        nbs_id: int,
        *,
        include_invasive: bool = False,
    ) -> list[dict[str, Any]]:
        """Return only the explicit fake mappings for this NbS ID."""

        return list(self.mappings.get(nbs_id, []))


def fake_provider() -> FakePlantMappingProvider:
    """Build fake plant mappings for the ranked candidates."""

    return FakePlantMappingProvider(
        {
            1: [
                {
                    "plant_id": 501,
                    "scientific_name": "Typha latifolia",
                    "common_name": "Broadleaf cattail",
                    "local_name": "Cattail",
                    "basis": "Explicit wetland planting map for organic load polishing.",
                    "source_ids": [701],
                    "mapping_source_id": 702,
                },
                {
                    "id": 502,
                    "plant_species": "Phragmites karka",
                    "common_name": "Common reed",
                    "evidence_note": "Mapped to wetland vegetation list.",
                    "source_id": 703,
                },
            ],
            99: [
                {
                    "plant_id": 999,
                    "scientific_name": "Unranked plant",
                    "basis": "Should never appear because candidate 99 is not ranked.",
                    "source_id": 999,
                }
            ],
        }
    )


def matched_bundle() -> Any:
    """Run Step K using fake explicit plant mappings."""

    return PlantMatchingEngine(fake_provider()).match_plants(
        ranking_bundle(),
        score_complete_expert_case(),
    )


def assert_plant_matching_uses_explicit_mappings_only() -> None:
    """Step K should attach only provider-returned mappings for ranked NbS IDs."""

    bundle = matched_bundle()
    first_candidate = bundle.candidate_matches[0]

    assert bundle.plant_matching_method == "explicit_mapping_v1"
    assert [plant.plant_id for plant in first_candidate.plant_matches] == [501, 502]
    assert all(plant.nbs_id == first_candidate.nbs_id for plant in first_candidate.plant_matches)
    assert 999 not in {
        plant.plant_id
        for candidate in bundle.candidate_matches
        for plant in candidate.plant_matches
    }


def assert_missing_mapping_returns_empty_list_plus_warning() -> None:
    """Missing plant mappings should warn without guessing plants."""

    bundle = matched_bundle()
    second_candidate = bundle.candidate_matches[1]

    assert second_candidate.nbs_id == 2
    assert second_candidate.plant_matches == []
    assert any("No explicit plant mappings" in warning for warning in second_candidate.warnings)
    assert any("No explicit plant mappings" in warning for warning in bundle.warnings)


def assert_rank_closeness_and_confidence_are_preserved() -> None:
    """Plant matching must not change Step I rank or Step J confidence."""

    original_ranking = ranking_bundle()
    original_confidence = score_complete_expert_case()
    bundle = PlantMatchingEngine(fake_provider()).match_plants(
        original_ranking,
        original_confidence,
    )

    assert [candidate.rank for candidate in bundle.candidate_matches] == [
        candidate.rank for candidate in original_ranking.ranked_candidates
    ]
    assert [candidate.topsis_closeness for candidate in bundle.candidate_matches] == [
        candidate.topsis_closeness
        for candidate in original_ranking.ranked_candidates
    ]
    assert [candidate.confidence_score for candidate in bundle.candidate_matches] == [
        candidate.confidence_score
        for candidate in original_confidence.results
    ]


def assert_missing_confidence_bundle_is_safe() -> None:
    """Step K should still run when Step J confidence is not supplied."""

    bundle = PlantMatchingEngine(fake_provider()).match_plants(ranking_bundle())

    assert bundle.confidence_method is None
    assert all(candidate.confidence_score is None for candidate in bundle.candidate_matches)
    assert any("confidence fields are None" in warning for warning in bundle.warnings)


def assert_no_forbidden_future_fields() -> None:
    """Step K output must not include final recommendation or match-score fields."""

    found = _find_forbidden_keys(matched_bundle().to_dict(), FORBIDDEN_FIELDS)
    assert not found, f"Step K leaked forbidden fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The Step K test should stay in engines and avoid API behavior."""

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
    """Run all Step K checks."""

    assert_plant_matching_uses_explicit_mappings_only()
    assert_missing_mapping_returns_empty_list_plus_warning()
    assert_rank_closeness_and_confidence_are_preserved()
    assert_missing_confidence_bundle_is_safe()
    assert_no_forbidden_future_fields()
    assert_no_api_or_recommend_route_involved()
    print("plant matching checks ok: Step K explicit mappings only, no recommendation path")


if __name__ == "__main__":
    main()

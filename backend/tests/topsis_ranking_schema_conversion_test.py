r"""Conversion checks for real Step I TOPSIS ranking output.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\topsis_ranking_schema_conversion_test.py

These tests use fake Step G normalized MCDA data and fake Step H temporary
weights only. They validate that actual TopsisRankingBundle.to_dict() output
can be serialized by the Step I Pydantic response schema. They do not create
routes, final recommendations, confidence scores, plant recommendations,
health-risk classifications, or AHP pairwise weights.
"""

from __future__ import annotations

import sys
from typing import Any

from app.engines import (
    McdaWeightsHandler,
    NormalizedMcdaCriterion,
    NormalizedMcdaMatrixBundle,
    NormalizedMcdaMatrixRow,
    TopsisRankingEngine,
)
from app.schemas import TopsisRankingBundleResponse


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "final_recommendation",
    "match_score",
    "confidence_score",
    "plant_recommendation",
    "plant_recommendations",
    "health_risk",
    "ahp",
    "ahp_weight",
}

CRITERIA_NAMES = [
    "removal_evidence_coverage",
    "site_suitability",
    "cost_indicator",
    "maintenance_indicator",
]


def model_to_dict(model: Any) -> dict[str, Any]:
    """Support both Pydantic v1 and v2 style dumping."""

    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def schema_fields(model_class: Any) -> set[str]:
    """Return field names for Pydantic v1 or v2 models."""

    fields = getattr(model_class, "model_fields", None)
    if fields is None:
        fields = getattr(model_class, "__fields__", {})
    return set(fields)


def fake_normalized_bundle() -> NormalizedMcdaMatrixBundle:
    """Build fake Step G output with at least two ranked candidates."""

    rows = [
        normalized_row(
            nbs_id=1,
            nbs_name="Wetland A",
            eligibility_status="eligible",
            removal=1.0,
            site=0.9,
            cost=0.3,
        ),
        normalized_row(
            nbs_id=2,
            nbs_name="Wetland B",
            eligibility_status="data_pending",
            removal=0.4,
            site=0.5,
            cost=1.0,
        ),
    ]
    return NormalizedMcdaMatrixBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load"],
        row_count=len(rows),
        criteria_names=CRITERIA_NAMES,
        rows=rows,
        normalization_method="min_max_unweighted",
        weights_status="not_applied",
        normalized_criteria_count=6,
        skipped_criteria_count=2,
        warnings=["Fake normalized bundle for Step I schema conversion."],
    )


def normalized_row(
    *,
    nbs_id: int,
    nbs_name: str,
    eligibility_status: str,
    removal: float,
    site: float,
    cost: float,
) -> NormalizedMcdaMatrixRow:
    """Build one fake Step G row with usable and skipped criteria."""

    return NormalizedMcdaMatrixRow(
        nbs_id=nbs_id,
        nbs_name=nbs_name,
        eligibility_status=eligibility_status,
        supported_treatment_needs=["organic_load"],
        normalized_criteria=[
            NormalizedMcdaCriterion(
                criterion_name="removal_evidence_coverage",
                raw_value=removal,
                normalized_value=removal,
                direction="benefit",
                normalization_status="normalized",
            ),
            NormalizedMcdaCriterion(
                criterion_name="site_suitability",
                raw_value=site,
                normalized_value=site,
                direction="benefit",
                normalization_status="normalized",
            ),
            NormalizedMcdaCriterion(
                criterion_name="cost_indicator",
                raw_value=cost,
                normalized_value=cost,
                direction="cost",
                normalization_status="normalized",
            ),
            NormalizedMcdaCriterion(
                criterion_name="maintenance_indicator",
                raw_value="medium",
                normalized_value=None,
                direction="cost",
                normalization_status="non_numeric",
            ),
        ],
        caution_flags=["Temporary ranking only."],
        source_ids=[100 + nbs_id],
        notes=["Fake Step G row for conversion testing."],
    )


def fake_temporary_weights() -> Any:
    """Build fake Step H temporary weights through the real handler."""

    return McdaWeightsHandler().prepare_weights(
        CRITERIA_NAMES,
        supplied_weights={
            "removal_evidence_coverage": 5,
            "site_suitability": 3,
            "cost_indicator": 2,
            "maintenance_indicator": 0,
        },
        weights_source="temporary_schema_conversion_weights",
        expert_validated=False,
    )


def actual_ranking_payload() -> dict[str, Any]:
    """Run Step I and return the actual dataclass dictionary output."""

    ranking_bundle = TopsisRankingEngine().rank(
        fake_normalized_bundle(),
        fake_temporary_weights(),
    )
    return ranking_bundle.to_dict()


def assert_actual_output_converts_to_schema() -> None:
    """Actual Step I output should validate as the response schema."""

    payload = actual_ranking_payload()
    response = TopsisRankingBundleResponse(**payload)
    serialized = model_to_dict(response)

    assert response.ranking_method == "topsis"
    assert response.weights_status == "temporary_not_expert_validated"
    assert response.expert_validated is False
    assert response.ranked_candidates
    assert response.ranked_count == len(response.ranked_candidates)
    assert [candidate.rank for candidate in response.ranked_candidates] == [1, 2]
    assert all(
        candidate.topsis_closeness is not None
        for candidate in response.ranked_candidates
    )
    assert response.ranked_candidates[0].criterion_contributions
    assert response.weights_source == "temporary_schema_conversion_weights"

    assert_forbidden_fields_absent(payload)
    assert_forbidden_fields_absent(serialized)
    assert_schema_has_no_forbidden_fields()


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay in engines/schemas only."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def assert_forbidden_fields_absent(payload: Any) -> None:
    """Recursively confirm future output fields are absent."""

    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Step I conversion leaked future fields: {sorted(found)}"


def assert_schema_has_no_forbidden_fields() -> None:
    """Check schema declarations, not just serialized sample payloads."""

    forbidden_present = FORBIDDEN_FIELDS.intersection(
        schema_fields(TopsisRankingBundleResponse)
    )
    assert not forbidden_present, f"Forbidden schema fields found: {forbidden_present}"


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
    """Run all Step I schema conversion checks."""

    assert_actual_output_converts_to_schema()
    assert_no_api_or_recommend_route_involved()
    print("topsis ranking schema conversion checks ok: real Step I output validates")


if __name__ == "__main__":
    main()

"""Conversion test from Step G normalized MCDA output to response schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_normalization_schema_conversion_test.py

This test uses fake Step F matrix data only. It does not connect to Azure,
mutate data, call API routes, apply weights, calculate TOPSIS/AHP, rank
candidates, calculate match/confidence scores, recommend plants, classify
health risk, or create final recommendations.
"""

import sys
from typing import Any

from app.engines import (
    McdaMatrixBundle,
    McdaMatrixRow,
    McdaNormalizationEngine,
)
from app.schemas import NormalizedMcdaMatrixBundleResponse


FORBIDDEN_FIELDS = {
    "recommendation",
    "recommendations",
    "ranking",
    "rank",
    "match_score",
    "confidence_score",
    "topsis",
    "topsis_score",
    "ahp",
    "ahp_weight",
}


def fake_matrix_bundle() -> McdaMatrixBundle:
    """Build fake Step F output for Step G schema conversion checks."""

    criteria_names = [
        "removal_evidence_coverage",
        "cost_indicator",
        "site_suitability",
        "custom_metric",
        "climate_suitability",
        "maintenance_indicator",
    ]
    rows = [
        McdaMatrixRow(
            nbs_id=1,
            nbs_name="Horizontal wetland",
            eligibility_status="eligible",
            supported_treatment_needs=["organic_load"],
            criteria_values={
                "removal_evidence_coverage": 0.2,
                "cost_indicator": 10.0,
                "site_suitability": 0.1,
                "custom_metric": 3.0,
                "climate_suitability": 0.5,
                "maintenance_indicator": "medium",
            },
            caution_flags=["Check pre-treatment if solids are high."],
            source_ids=[10, 31],
            notes=["Fake Step F row for conversion testing."],
        ),
        McdaMatrixRow(
            nbs_id=2,
            nbs_name="Catalogue-only polishing system",
            eligibility_status="data_pending",
            supported_treatment_needs=["nutrients"],
            criteria_values={
                "removal_evidence_coverage": 0.8,
                "cost_indicator": 5.0,
                "custom_metric": 6.0,
                "climate_suitability": 0.5,
                "maintenance_indicator": "low",
            },
            missing_criteria=["site_suitability"],
            caution_flags=["Removal evidence is incomplete."],
            source_ids=[10, 61],
            notes=["Fake Step F data-pending row for conversion testing."],
        ),
    ]
    return McdaMatrixBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "nutrients"],
        row_count=len(rows),
        criteria_names=criteria_names,
        rows=rows,
        warnings=["Fake matrix warning preserved into Step G."],
        weights_status="not_applied",
    )


def build_actual_normalized_payload() -> dict[str, Any]:
    """Run the real Step G engine and return its dictionary output."""

    bundle = McdaNormalizationEngine().normalize(fake_matrix_bundle())
    return bundle.to_dict()


def assert_actual_step_g_output_validates_against_schema() -> None:
    """Actual Step G dataclass output should validate as a response schema."""

    payload = build_actual_normalized_payload()
    response = NormalizedMcdaMatrixBundleResponse(**payload)
    dump = response.model_dump()

    assert dump["use_case"] == "surface_discharge"
    assert dump["row_count"] == 2
    assert dump["normalization_method"] == "min_max_unweighted"
    assert dump["weights_status"] == "not_applied"
    assert len(dump["rows"]) == 2


def assert_normalized_and_skipped_counts_are_preserved() -> None:
    """Schema conversion should preserve Step G criterion counts exactly."""

    payload = build_actual_normalized_payload()
    response = NormalizedMcdaMatrixBundleResponse(**payload)
    dump = response.model_dump()

    assert dump["normalized_criteria_count"] == payload["normalized_criteria_count"]
    assert dump["skipped_criteria_count"] == payload["skipped_criteria_count"]
    assert dump["normalized_criteria_count"] == 4
    assert dump["skipped_criteria_count"] == 8


def assert_expected_normalization_statuses_are_serialized() -> None:
    """Converted schema should preserve normalized and skipped statuses."""

    response = NormalizedMcdaMatrixBundleResponse(**build_actual_normalized_payload())
    rows = response.model_dump()["rows"]
    criteria = [
        criterion
        for row in rows
        for criterion in row["normalized_criteria"]
    ]
    statuses = {criterion["normalization_status"] for criterion in criteria}

    assert "normalized" in statuses
    assert "missing" in statuses
    assert "direction_unknown" in statuses
    assert "no_variation" in statuses
    assert "non_numeric" in statuses


def assert_benefit_and_cost_values_survive_conversion() -> None:
    """Benefit and cost normalized values should survive schema conversion."""

    response = NormalizedMcdaMatrixBundleResponse(**build_actual_normalized_payload())
    rows = response.model_dump()["rows"]
    row_one = criteria_by_name(rows[0])
    row_two = criteria_by_name(rows[1])

    assert_close(row_one["removal_evidence_coverage"]["normalized_value"], 0.0)
    assert_close(row_two["removal_evidence_coverage"]["normalized_value"], 1.0)
    assert_close(row_one["cost_indicator"]["normalized_value"], 0.0)
    assert_close(row_two["cost_indicator"]["normalized_value"], 1.0)


def assert_forbidden_fields_are_absent() -> None:
    """Converted Step G schema dump must not include future scoring fields."""

    response = NormalizedMcdaMatrixBundleResponse(**build_actual_normalized_payload())
    found = _find_forbidden_keys(response.model_dump(), FORBIDDEN_FIELDS)
    found.update(
        key.lower()
        for key in NormalizedMcdaMatrixBundleResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"MCDA normalization conversion leaked fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The conversion test should stay in engines/schemas and avoid API behavior."""

    assert "app.api" not in sys.modules
    assert "app.main" not in sys.modules


def criteria_by_name(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index normalized criteria dictionaries by criterion name."""

    return {
        criterion["criterion_name"]: criterion
        for criterion in row["normalized_criteria"]
    }


def assert_close(actual: float | None, expected: float) -> None:
    """Assert float equality with a tiny tolerance."""

    assert actual is not None
    assert abs(actual - expected) < 0.000001


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
    """Run all Step G schema conversion checks."""

    assert_actual_step_g_output_validates_against_schema()
    assert_normalized_and_skipped_counts_are_preserved()
    assert_expected_normalization_statuses_are_serialized()
    assert_benefit_and_cost_values_survive_conversion()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("mcda normalization schema conversion checks ok: real Step G output validates")


if __name__ == "__main__":
    main()

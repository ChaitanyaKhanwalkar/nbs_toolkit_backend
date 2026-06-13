"""Smoke tests for Step G normalized MCDA response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_normalization_schema_test.py

These tests only validate Pydantic response shapes. They do not connect to
Azure, mutate data, call API routes, apply weights, calculate TOPSIS/AHP, rank
candidates, calculate match/confidence scores, recommend plants, or create
final recommendations.
"""

import sys
from typing import Any

from app.schemas import (
    NormalizedMcdaCriterionResponse,
    NormalizedMcdaMatrixBundleResponse,
    NormalizedMcdaMatrixRowResponse,
)


FORBIDDEN_FIELDS = {
    "recommendation",
    "ranking",
    "match_score",
    "confidence_score",
    "topsis",
    "ahp",
}


def criterion_payload() -> dict[str, Any]:
    """Return a minimal Step G normalized criterion response payload."""

    return {
        "criterion_name": "removal_evidence_coverage",
        "raw_value": 0.8,
        "normalized_value": 1.0,
        "direction": "benefit",
        "normalization_status": "normalized",
        "notes": ["Normalized with unweighted min-max normalization."],
    }


def row_payload() -> dict[str, Any]:
    """Return a minimal Step G normalized matrix row response payload."""

    return {
        "nbs_id": 1,
        "nbs_name": "Horizontal wetland",
        "eligibility_status": "eligible",
        "supported_treatment_needs": ["organic_load", "solids"],
        "normalized_criteria": [criterion_payload()],
        "missing_criteria": ["site_suitability"],
        "caution_flags": ["Check pre-treatment if solids are high."],
        "source_ids": [10, 31],
        "notes": ["Step G normalized matrix row only."],
    }


def assert_criterion_schema_validates() -> None:
    """A minimal normalized criterion should validate."""

    criterion = NormalizedMcdaCriterionResponse(**criterion_payload())
    dump = criterion.model_dump()

    assert dump["criterion_name"] == "removal_evidence_coverage"
    assert dump["normalized_value"] == 1.0
    assert dump["direction"] == "benefit"
    assert dump["normalization_status"] == "normalized"


def assert_row_schema_validates() -> None:
    """A minimal normalized matrix row should validate."""

    row = NormalizedMcdaMatrixRowResponse(**row_payload())
    dump = row.model_dump()

    assert dump["nbs_id"] == 1
    assert dump["eligibility_status"] == "eligible"
    assert dump["normalized_criteria"][0]["criterion_name"] == "removal_evidence_coverage"


def assert_bundle_schema_validates() -> None:
    """A minimal normalized matrix bundle should validate."""

    bundle = NormalizedMcdaMatrixBundleResponse(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=1,
        criteria_names=["removal_evidence_coverage"],
        rows=[row_payload()],
        normalization_method="min_max_unweighted",
        weights_status="not_applied",
        normalized_criteria_count=1,
        skipped_criteria_count=0,
        warnings=[],
    )
    dump = bundle.model_dump()

    assert dump["use_case"] == "surface_discharge"
    assert dump["row_count"] == 1
    assert dump["normalization_method"] == "min_max_unweighted"
    assert dump["weights_status"] == "not_applied"
    assert dump["rows"][0]["nbs_name"] == "Horizontal wetland"


def assert_status_values_are_allowed() -> None:
    """Step G schema should allow the explicit non-weighted status values."""

    bundle = NormalizedMcdaMatrixBundleResponse(
        use_case="surface_discharge",
        normalization_method="min_max_unweighted",
        weights_status="not_applied",
    )

    assert bundle.normalization_method == "min_max_unweighted"
    assert bundle.weights_status == "not_applied"


def assert_forbidden_fields_are_absent() -> None:
    """Step G schema dumps must not include future recommendation/scoring fields."""

    criterion = NormalizedMcdaCriterionResponse(**criterion_payload())
    row = NormalizedMcdaMatrixRowResponse(**row_payload())
    bundle = NormalizedMcdaMatrixBundleResponse(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=1,
        criteria_names=["removal_evidence_coverage"],
        rows=[row_payload()],
        normalization_method="min_max_unweighted",
        weights_status="not_applied",
    )
    payloads = [
        criterion.model_dump(),
        row.model_dump(),
        bundle.model_dump(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))
    found.update(
        key.lower()
        for model in (
            NormalizedMcdaCriterionResponse,
            NormalizedMcdaMatrixRowResponse,
            NormalizedMcdaMatrixBundleResponse,
        )
        for key in model.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"MCDA normalization schemas leaked future fields: {sorted(found)}"


def assert_no_api_or_recommend_route_involved() -> None:
    """The Step G schema test should stay in schemas and avoid API behavior."""

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
    """Run all Step G schema smoke checks."""

    assert_criterion_schema_validates()
    assert_row_schema_validates()
    assert_bundle_schema_validates()
    assert_status_values_are_allowed()
    assert_forbidden_fields_are_absent()
    assert_no_api_or_recommend_route_involved()
    print("mcda normalization schema checks ok: Step G response schemas only")


if __name__ == "__main__":
    main()

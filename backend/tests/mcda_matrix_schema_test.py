"""Smoke tests for Step F MCDA matrix response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_matrix_schema_test.py

These tests only validate Pydantic response shapes. They do not connect to
Azure, mutate data, call API routes, rank candidates, calculate TOPSIS/AHP,
calculate match/confidence scores, recommend plants, or create final
recommendations.
"""

from typing import Any

from app.schemas import McdaMatrixBundleResponse, McdaMatrixRowResponse


FORBIDDEN_FIELDS = {
    "recommendation",
    "ranking",
    "match_score",
    "confidence_score",
    "topsis",
    "ahp",
}


def row_payload() -> dict[str, Any]:
    """Return a minimal Step F row response payload."""

    return {
        "nbs_id": 1,
        "nbs_name": "Horizontal wetland",
        "eligibility_status": "eligible",
        "supported_treatment_needs": ["organic_load", "solids"],
        "criteria_values": {
            "removal_evidence": {
                "row_count": 2,
                "parameters": ["BOD", "TSS"],
            },
            "footprint": {
                "row_count": 1,
                "raw_rows": [{"area_per_pe_low": 2.0, "source_id": 41}],
            },
        },
        "missing_criteria": ["co_benefit_indicator"],
        "caution_flags": ["Check pre-treatment if solids are high."],
        "source_ids": [10, 31, 41],
        "notes": ["Step F raw matrix row only."],
    }


def assert_row_schema_validates() -> None:
    """A minimal MCDA matrix row should validate."""

    row = McdaMatrixRowResponse(**row_payload())
    dump = row.model_dump()

    assert dump["nbs_id"] == 1
    assert dump["eligibility_status"] == "eligible"
    assert "removal_evidence" in dump["criteria_values"]


def assert_bundle_schema_validates() -> None:
    """A minimal MCDA matrix bundle should validate."""

    bundle = McdaMatrixBundleResponse(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=1,
        excluded_ineligible_count=1,
        criteria_names=["removal_evidence", "footprint"],
        rows=[row_payload()],
        missing_criteria_summary={"co_benefit_indicator": 1},
        warnings=[],
        weights_status="not_applied",
    )
    dump = bundle.model_dump()

    assert dump["use_case"] == "surface_discharge"
    assert dump["row_count"] == 1
    assert dump["excluded_ineligible_count"] == 1
    assert dump["weights_status"] == "not_applied"
    assert dump["rows"][0]["nbs_name"] == "Horizontal wetland"


def assert_weights_status_allows_not_applied() -> None:
    """Step F schema should allow the non-weighted status value."""

    bundle = McdaMatrixBundleResponse(
        use_case="surface_discharge",
        weights_status="not_applied",
    )

    assert bundle.weights_status == "not_applied"


def assert_forbidden_fields_are_absent() -> None:
    """Step F schema dumps must not include future recommendation/scoring fields."""

    row = McdaMatrixRowResponse(**row_payload())
    bundle = McdaMatrixBundleResponse(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load", "solids"],
        row_count=1,
        rows=[row_payload()],
        weights_status="not_applied",
    )
    payloads = [
        row.model_dump(),
        bundle.model_dump(),
    ]

    found = set()
    for payload in payloads:
        found.update(_find_forbidden_keys(payload, FORBIDDEN_FIELDS))
    found.update(
        key.lower()
        for model in (McdaMatrixRowResponse, McdaMatrixBundleResponse)
        for key in model.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"MCDA matrix schemas leaked future fields: {sorted(found)}"


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
    """Run all Step F schema smoke checks."""

    assert_row_schema_validates()
    assert_bundle_schema_validates()
    assert_weights_status_allows_not_applied()
    assert_forbidden_fields_are_absent()
    print("mcda matrix schema checks ok: Step F response schemas only")


if __name__ == "__main__":
    main()

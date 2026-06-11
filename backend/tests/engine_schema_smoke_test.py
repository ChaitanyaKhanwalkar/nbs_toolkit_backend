"""Smoke test for internal scientific engine response schemas.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\engine_schema_smoke_test.py

These tests instantiate schema objects only. They do not connect to Azure, do
not mutate data, do not call API routes, and do not run recommendation logic.
"""

from typing import Any

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


def build_schema_objects() -> list[object]:
    """Create minimal valid Step A-E schema objects."""

    input_context = InputContextResponse(
        original_input={"use_case": "surface discharge"},
        normalized_input={"use_case": "surface_discharge"},
        validation_status="valid",
        data_priority_note="user measured data has priority",
    )
    water_bundle = WaterInputBundleResponse(
        selected_source_type="user_measured",
        observations=[{"parameter": "BOD", "value": 12.0, "unit": "mg/L"}],
        observation_count=1,
        selected_parameters=["BOD"],
        use_case="surface_discharge",
        source_ids=[101],
    )
    gap_result = ParameterGapResultResponse(
        parameter="BOD",
        observed_value=12.0,
        observed_unit="mg/L",
        standard_unit="mg/L",
        limit_high=3.0,
        comparison_type="max_limit",
        status="exceeds_standard",
        gap_value=9.0,
        gap_ratio=3.0,
        required_removal_fraction=0.75,
        required_removal_percent=75.0,
        direction="reduce",
        source_type="user_measured",
        source_ids=[101],
    )
    gap_bundle = PollutantGapBundleResponse(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        total_observations_checked=1,
        comparable_count=1,
        exceedance_count=1,
        results=[gap_result],
    )
    need_result = TreatmentNeedResultResponse(
        need_group="organic_load",
        triggering_parameters=["BOD"],
        triggering_statuses=["exceeds_standard"],
        max_gap_ratio=3.0,
        required_removal_percent_max=75.0,
        direction="reduce",
    )
    need_bundle = TreatmentNeedBundleResponse(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        treatment_needs=[need_result],
        source_ids=[101],
    )
    candidate_result = CandidateFilterResultResponse(
        nbs_id=1,
        nbs_name="Horizontal wetland",
        eligibility_status="eligible",
        supported_treatment_needs=["organic_load"],
        evidence_source_ids=[31],
        implementation_source_ids=[20],
    )
    candidate_bundle = CandidateFilterBundleResponse(
        use_case="surface_discharge",
        selected_source_type="user_measured",
        treatment_need_groups=["organic_load"],
        candidate_count=1,
        eligible_count=1,
        results=[candidate_result],
    )

    return [
        input_context,
        water_bundle,
        gap_result,
        gap_bundle,
        need_result,
        need_bundle,
        candidate_result,
        candidate_bundle,
    ]


def assert_all_schema_objects_import_and_dump() -> None:
    """All new schemas should instantiate and serialize safely."""

    objects = build_schema_objects()
    dumps = [schema.model_dump() for schema in objects]

    assert len(dumps) == 8
    assert dumps[0]["validation_status"] == "valid"
    assert dumps[-1]["eligible_count"] == 1


def assert_forbidden_fields_are_absent() -> None:
    """Engine schemas must not define future recommendation/scoring fields."""

    found = set()
    for schema in build_schema_objects():
        found.update(_find_forbidden_keys(schema.model_dump(), FORBIDDEN_FIELDS))

    assert not found, f"Engine schemas leaked future fields: {sorted(found)}"


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
    """Run all engine schema smoke checks."""

    assert_all_schema_objects_import_and_dump()
    assert_forbidden_fields_are_absent()
    print("engine schema imports ok: Step A-E response shapes only")


if __name__ == "__main__":
    main()

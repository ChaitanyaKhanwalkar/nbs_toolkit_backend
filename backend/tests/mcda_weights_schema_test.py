"""Smoke tests for Step H MCDA weights response schema.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\mcda_weights_schema_test.py

These tests only validate Pydantic response shapes. They do not connect to
Azure, mutate data, call API routes, calculate AHP pairwise weights, calculate
TOPSIS, rank candidates, calculate match/confidence scores, recommend plants,
or create final recommendations.
"""

from typing import Any

from app.schemas import McdaWeightsBundleResponse


FORBIDDEN_FIELDS = {
    "recommendation",
    "ranking",
    "match_score",
    "confidence_score",
    "topsis",
    "ahp",
}


def assert_missing_weights_response_validates() -> None:
    """A missing-weights Step H response should validate safely."""

    response = McdaWeightsBundleResponse(
        criteria_names=["removal_evidence_coverage", "site_suitability"],
        weights={},
        weights_status="weights_missing",
        weights_source=None,
        expert_validated=False,
        missing_weight_criteria=[
            "removal_evidence_coverage",
            "site_suitability",
        ],
        extra_weight_criteria=[],
        warnings=["No MCDA criteria weights were supplied."],
        notes=["Step H validates supplied weights only."],
    )
    dump = response.model_dump()

    assert dump["weights_status"] == "weights_missing"
    assert dump["expert_validated"] is False
    assert dump["weights"] == {}


def assert_temporary_weights_response_validates() -> None:
    """A temporary-weights Step H response should validate without final claims."""

    response = McdaWeightsBundleResponse(
        criteria_names=["removal_evidence_coverage", "site_suitability"],
        weights={
            "removal_evidence_coverage": 0.75,
            "site_suitability": 0.25,
        },
        weights_status="temporary_not_expert_validated",
        weights_source="temporary_supplied",
        expert_validated=False,
        missing_weight_criteria=[],
        extra_weight_criteria=[],
        warnings=[
            "Supplied weights are marked temporary_not_expert_validated."
        ],
        notes=["Temporary weights are not final expert weights."],
    )
    dump = response.model_dump()

    assert dump["weights_status"] == "temporary_not_expert_validated"
    assert dump["expert_validated"] is False
    assert sum(dump["weights"].values()) == 1.0


def assert_expert_validated_response_validates() -> None:
    """An expert-validated response should require explicit true flag."""

    response = McdaWeightsBundleResponse(
        criteria_names=["removal_evidence_coverage", "site_suitability"],
        weights={
            "removal_evidence_coverage": 0.6,
            "site_suitability": 0.4,
        },
        weights_status="expert_validated",
        weights_source="supervisor_approved_weights_sheet",
        expert_validated=True,
        missing_weight_criteria=[],
        extra_weight_criteria=[],
        warnings=[],
        notes=["Weights were explicitly marked expert validated."],
    )
    dump = response.model_dump()

    assert dump["weights_status"] == "expert_validated"
    assert dump["expert_validated"] is True
    assert dump["weights_source"] == "supervisor_approved_weights_sheet"


def assert_invalid_status_response_validates() -> None:
    """The invalid_weights status should also be accepted."""

    response = McdaWeightsBundleResponse(
        criteria_names=["removal_evidence_coverage"],
        weights={},
        weights_status="invalid_weights",
        expert_validated=False,
        warnings=["Weight for criterion must be numeric."],
    )

    assert response.weights_status == "invalid_weights"


def assert_forbidden_fields_are_absent() -> None:
    """Step H schema dumps must not include future recommendation/scoring fields."""

    response = McdaWeightsBundleResponse(
        criteria_names=["removal_evidence_coverage"],
        weights={"removal_evidence_coverage": 1.0},
        weights_status="temporary_not_expert_validated",
        weights_source="temporary_supplied",
        expert_validated=False,
    )
    found = _find_forbidden_keys(response.model_dump(), FORBIDDEN_FIELDS)
    found.update(
        key.lower()
        for key in McdaWeightsBundleResponse.model_fields
        if key.lower() in FORBIDDEN_FIELDS
    )

    assert not found, f"MCDA weights schema leaked future fields: {sorted(found)}"


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
    """Run all Step H schema smoke checks."""

    assert_missing_weights_response_validates()
    assert_temporary_weights_response_validates()
    assert_expert_validated_response_validates()
    assert_invalid_status_response_validates()
    assert_forbidden_fields_are_absent()
    print("mcda weights schema checks ok: Step H response schema only")


if __name__ == "__main__":
    main()

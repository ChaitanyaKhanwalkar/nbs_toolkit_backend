r"""Smoke tests for Step M.1 MCDA numeric projection.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\mcda_numeric_projection_test.py

These tests use fake Step F matrix data only. They do not connect to Azure,
mutate data, invent scientific values, calculate AHP weights, or classify
health risk.
"""

from __future__ import annotations

from typing import Any

from app.engines import McdaNumericProjectionEngine
from app.engines.mcda_matrix import McdaMatrixBundle, McdaMatrixRow


FORBIDDEN_FIELDS = {
    "health_risk",
    "ahp",
    "ahp_weight",
    "azure",
    "deployment",
}


def fake_matrix_bundle() -> McdaMatrixBundle:
    """Return fake Step F rows with raw criteria objects."""

    return McdaMatrixBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load"],
        row_count=2,
        excluded_ineligible_count=0,
        criteria_names=[
            "removal_evidence",
            "climate_site_suitability",
            "cost_indicator",
        ],
        rows=[
            McdaMatrixRow(
                nbs_id=1,
                nbs_name="Horizontal wetland",
                eligibility_status="eligible",
                supported_treatment_needs=["organic_load"],
                criteria_values={
                    "removal_evidence": {
                        "row_count": 3,
                        "rows_with_numeric_efficiency": 2,
                        "raw_rows": [
                            {"parameter": "BOD", "eff_low": 60.0},
                            {"parameter": "TSS", "eff_high": "80"},
                            {"parameter": "nitrate"},
                        ],
                    },
                    "climate_site_suitability": {
                        "optimal_water_type": "domestic wastewater",
                        "climate_suitability": "tropical",
                        "location_suitability": 0.8,
                    },
                    "cost_indicator": {
                        "criteria_rows": [
                            {"criterion": "cost", "value_qual": "medium"}
                        ]
                    },
                },
                missing_criteria=[],
                source_ids=[31, 32],
                notes=["Raw Step F row."],
            ),
            McdaMatrixRow(
                nbs_id=2,
                nbs_name="Catalogue-only polishing system",
                eligibility_status="data_pending",
                supported_treatment_needs=["organic_load"],
                criteria_values={
                    "removal_evidence": {
                        "raw_rows": [
                            {"parameter": "BOD", "eff_low": None},
                            {"parameter": "TSS", "eff_high": 40.0},
                        ],
                    },
                    "climate_site_suitability": {
                        "optimal_water_type": "greywater",
                        "soil_type": 0.5,
                    },
                },
                missing_criteria=["cost_indicator"],
                source_ids=[33],
                notes=["Second raw Step F row."],
            ),
        ],
        missing_criteria_summary={"cost_indicator": 1},
        warnings=[],
    )


def project_bundle() -> McdaMatrixBundle:
    """Project fake Step F criteria into safe numeric proxies."""

    return McdaNumericProjectionEngine().project(fake_matrix_bundle())


def assert_removal_evidence_coverage_added() -> None:
    """Numeric removal coverage should come from explicit evidence counts."""

    projected = project_bundle()
    first_row = projected.rows[0]
    second_row = projected.rows[1]

    assert first_row.criteria_values["removal_evidence_coverage"] == 2 / 3
    assert second_row.criteria_values["removal_evidence_coverage"] == 1 / 2


def assert_removal_evidence_score_added() -> None:
    """Average removal efficiency score should come from raw evidence rows."""

    projected = project_bundle()
    first_row = projected.rows[0]
    second_row = projected.rows[1]

    assert first_row.criteria_values["removal_evidence_score"] == 0.7
    assert second_row.criteria_values["removal_evidence_score"] == 0.4


def assert_removal_evidence_score_varies_between_candidates() -> None:
    """Different existing efficiency values should produce different scores."""

    projected = project_bundle()
    scores = [
        row.criteria_values["removal_evidence_score"]
        for row in projected.rows
    ]

    assert len(set(scores)) == 2


def assert_removal_evidence_score_is_clamped() -> None:
    """Projected efficiency scores should stay in the safe 0-1 range."""

    bundle = McdaMatrixBundle(
        use_case="surface_discharge",
        treatment_need_groups=["organic_load"],
        row_count=1,
        excluded_ineligible_count=0,
        criteria_names=["removal_evidence"],
        rows=[
            McdaMatrixRow(
                nbs_id=99,
                nbs_name="High reported efficiency test row",
                eligibility_status="eligible",
                supported_treatment_needs=["organic_load"],
                criteria_values={
                    "removal_evidence": {
                        "raw_rows": [
                            {"parameter": "BOD", "eff_low": 140, "eff_high": 160}
                        ]
                    }
                },
            )
        ],
    )

    projected = McdaNumericProjectionEngine().project(bundle)

    assert projected.rows[0].criteria_values["removal_evidence_score"] == 1.0


def assert_site_suitability_added_from_metadata_completeness_only() -> None:
    """Site proxy should count metadata completeness, not interpret words."""

    projected = project_bundle()
    first_row = projected.rows[0]
    second_row = projected.rows[1]

    assert first_row.criteria_values["site_suitability"] == 3 / 4
    assert second_row.criteria_values["site_suitability"] == 2 / 4
    assert any("metadata completeness" in note for note in first_row.notes)
    assert any("metadata completeness" in warning for warning in projected.warnings)


def assert_cost_indicator_is_not_invented() -> None:
    """Non-numeric or missing cost should stay non-numeric/missing."""

    projected = project_bundle()

    assert isinstance(projected.rows[0].criteria_values["cost_indicator"], dict)
    assert "cost_indicator" not in projected.rows[1].criteria_values


def assert_raw_criteria_are_preserved_and_original_is_not_mutated() -> None:
    """Projection should copy rows and preserve Step F raw criteria."""

    original = fake_matrix_bundle()
    projected = McdaNumericProjectionEngine().project(original)

    assert "removal_evidence" in projected.rows[0].criteria_values
    assert "climate_site_suitability" in projected.rows[0].criteria_values
    assert "removal_evidence_coverage" not in original.rows[0].criteria_values
    assert "removal_evidence_score" not in original.rows[0].criteria_values
    assert "site_suitability" not in original.rows[0].criteria_values
    assert projected.rows[0] is not original.rows[0]


def assert_projected_criteria_names_are_appended() -> None:
    """Projected numeric criteria should appear in matrix criteria_names."""

    projected = project_bundle()

    assert "removal_evidence_coverage" in projected.criteria_names
    assert "removal_evidence_score" in projected.criteria_names
    assert "site_suitability" in projected.criteria_names
    assert projected.criteria_names.index("removal_evidence_coverage") > (
        projected.criteria_names.index("removal_evidence")
    )
    assert projected.criteria_names.index("removal_evidence_score") > (
        projected.criteria_names.index("removal_evidence")
    )


def assert_forbidden_fields_are_absent() -> None:
    """Projection output must not include health-risk, AHP, Azure, or deployment fields."""

    found = _find_forbidden_keys(project_bundle().to_dict(), FORBIDDEN_FIELDS)
    assert not found, f"MCDA numeric projection leaked forbidden fields: {sorted(found)}"


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
    """Run all Step M.1 projection checks."""

    assert_removal_evidence_coverage_added()
    assert_removal_evidence_score_added()
    assert_removal_evidence_score_varies_between_candidates()
    assert_removal_evidence_score_is_clamped()
    assert_site_suitability_added_from_metadata_completeness_only()
    assert_cost_indicator_is_not_invented()
    assert_raw_criteria_are_preserved_and_original_is_not_mutated()
    assert_projected_criteria_names_are_appended()
    assert_forbidden_fields_are_absent()
    print("mcda numeric projection checks ok: conservative Step F to Step G bridge")


if __name__ == "__main__":
    main()

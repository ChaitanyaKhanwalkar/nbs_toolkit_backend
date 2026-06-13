"""Smoke tests for Scientific Engine Step E.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\candidate_filtering_test.py

These tests use fake NbS catalogue data. They do not connect to Azure, do not
mutate data, do not rank candidates, and do not create final recommendations.
"""

from typing import Any

from app.engines import (
    CandidateFilteringEngine,
    TreatmentNeedBundle,
    TreatmentNeedResult,
)


class FakeNbsCatalogService:
    """Small provider-shaped test double for raw NbS catalogue profiles."""

    def __init__(self, profiles: dict[int, dict[str, Any]]) -> None:
        self.profiles = profiles

    def list_options(self) -> list[dict[str, Any]]:
        """Return fake options without querying a database."""

        return [
            profile["option"]
            for profile in self.profiles.values()
            if profile.get("option")
        ]

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return one fake raw profile."""

        return self.profiles.get(nbs_id, {})


def treatment_bundle(
    groups: list[str],
    *,
    use_case: str = "surface_discharge",
) -> TreatmentNeedBundle:
    """Build a Step D-style treatment bundle for tests."""

    return TreatmentNeedBundle(
        use_case=use_case,
        selected_source_type="user_measured",
        treatment_needs=[
            TreatmentNeedResult(need_group=group)
            for group in groups
        ],
    )


def profile(
    *,
    nbs_id: int,
    solution: str,
    removal_rows: list[dict[str, Any]] | None = None,
    implementation_rows: list[dict[str, Any]] | None = None,
    option_extra: dict[str, Any] | None = None,
    criteria_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a raw NbS profile shaped like NbsCatalogService output."""

    option = {
        "id": nbs_id,
        "solution": solution,
        "family": "Constructed Wetlands",
        "description": "Test-only catalogue row",
        "source_id": 10,
    }
    option.update(option_extra or {})
    implementation = implementation_rows
    if implementation is None:
        implementation = [
            {
                "nbs_id": nbs_id,
                "implementation_steps": "Build and maintain as documented.",
                "source_id": 20,
            }
        ]
    return {
        "option": option,
        "removal_efficiencies": removal_rows or [],
        "implementation": implementation,
        "footprint": [],
        "criteria": criteria_rows or [],
        "missing_sections": [] if implementation else ["implementation"],
    }


def run_filter(
    groups: list[str],
    profiles: dict[int, dict[str, Any]],
    *,
    use_case: str = "surface_discharge",
):
    """Run Step E with fake treatment needs and fake catalogue profiles."""

    return CandidateFilteringEngine(
        FakeNbsCatalogService(profiles)
    ).filter_candidates(treatment_bundle(groups, use_case=use_case))


def only_result(bundle):
    """Return the single candidate result from a test bundle."""

    assert len(bundle.results) == 1
    return bundle.results[0]


def assert_eligible_with_explicit_organic_load_support() -> None:
    """A BOD removal row should make organic_load explicitly eligible."""

    bundle = run_filter(
        ["organic_load"],
        {
            1: profile(
                nbs_id=1,
                solution="Horizontal wetland",
                removal_rows=[
                    {
                        "nbs_id": 1,
                        "parameter": "BOD",
                        "eff_low": 60.0,
                        "eff_high": 85.0,
                        "source_id": 31,
                    }
                ],
            )
        },
    )
    result = only_result(bundle)

    assert result.eligibility_status == "eligible"
    assert result.supported_treatment_needs == ["organic_load"]
    assert result.unsupported_treatment_needs == []
    assert result.evidence_source_ids == [10, 31]
    assert result.implementation_source_ids == [20]
    assert bundle.eligible_count == 1


def assert_data_pending_when_evidence_missing() -> None:
    """Catalogue-only support should stay data_pending without removal rows."""

    bundle = run_filter(
        ["organic_load"],
        {
            2: profile(
                nbs_id=2,
                solution="Catalogue-only system",
                option_extra={"supported_treatment_needs": ["organic_load"]},
            )
        },
    )
    result = only_result(bundle)

    assert result.eligibility_status == "data_pending"
    assert result.supported_treatment_needs == ["organic_load"]
    assert any("Catalogue support exists" in reason for reason in result.data_pending_reasons)
    assert bundle.data_pending_count == 1


def assert_ineligible_when_no_support_exists() -> None:
    """Evidence for another need should not support the requested need."""

    bundle = run_filter(
        ["organic_load"],
        {
            3: profile(
                nbs_id=3,
                solution="Metal polishing unit",
                removal_rows=[
                    {
                        "nbs_id": 3,
                        "parameter": "arsenic",
                        "eff_low": 40.0,
                        "eff_high": 60.0,
                        "source_id": 32,
                    }
                ],
            )
        },
    )
    result = only_result(bundle)

    assert result.eligibility_status == "ineligible"
    assert result.supported_treatment_needs == []
    assert result.unsupported_treatment_needs == ["organic_load"]
    assert any("No explicit support" in reason for reason in result.exclusion_reasons)
    assert bundle.ineligible_count == 1


def assert_multiple_treatment_needs_handled() -> None:
    """A candidate may support some needs and leave others unsupported."""

    bundle = run_filter(
        ["organic_load", "solids", "nutrients"],
        {
            4: profile(
                nbs_id=4,
                solution="Wetland with settling",
                removal_rows=[
                    {"parameter": "BOD", "eff_low": 50, "source_id": 31},
                    {"parameter": "TSS", "eff_high": 80, "source_id": 32},
                ],
            )
        },
    )
    result = only_result(bundle)

    assert result.eligibility_status == "eligible"
    assert result.supported_treatment_needs == ["organic_load", "solids"]
    assert result.unsupported_treatment_needs == ["nutrients"]


def assert_pathogen_caution_flag() -> None:
    """Pathogens with open-contact/open-water systems should raise caution."""

    bundle = run_filter(
        ["pathogens"],
        {
            5: profile(
                nbs_id=5,
                solution="Open polishing pond",
                option_extra={"description": "Open pond with public contact limits."},
                removal_rows=[
                    {"parameter": "fecal coliform", "eff_low": 70, "source_id": 33}
                ],
            )
        },
    )
    result = only_result(bundle)

    assert result.eligibility_status == "eligible"
    assert any("Pathogen treatment need" in flag for flag in result.caution_flags)


def assert_metal_food_chain_caution_flag() -> None:
    """Metals with food-chain/aquaculture pathways should raise caution."""

    bundle = run_filter(
        ["metals"],
        {
            6: profile(
                nbs_id=6,
                solution="Aquaculture polishing system",
                option_extra={"description": "Aquaculture fish food chain pathway."},
                removal_rows=[
                    {"parameter": "lead", "eff_low": 30, "source_id": 34}
                ],
            )
        },
    )
    result = only_result(bundle)

    assert result.eligibility_status == "eligible"
    assert any("Metal treatment need" in flag for flag in result.caution_flags)


def assert_drinking_domestic_caution_flag() -> None:
    """Drinking/domestic use cases should raise an engineered-treatment caution."""

    bundle = run_filter(
        ["organic_load"],
        {
            7: profile(
                nbs_id=7,
                solution="Wetland polishing",
                removal_rows=[
                    {"parameter": "BOD", "eff_low": 50, "source_id": 35}
                ],
            )
        },
        use_case="drinking_domestic",
    )
    result = only_result(bundle)

    assert result.eligibility_status == "eligible"
    assert any("Drinking/domestic target use case" in flag for flag in result.caution_flags)


def assert_no_future_fields() -> None:
    """Step E output must not include recommendation/ranking/scoring fields."""

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
    bundle = run_filter(
        ["organic_load"],
        {
            8: profile(
                nbs_id=8,
                solution="Wetland polishing",
                removal_rows=[
                    {"parameter": "BOD", "eff_low": 50, "source_id": 36}
                ],
            )
        },
    )
    found = _find_forbidden_keys(bundle.to_dict(), forbidden_fields)

    assert not found, f"Step E leaked future fields: {sorted(found)}"


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
    """Run all Step E checks."""

    assert_eligible_with_explicit_organic_load_support()
    assert_data_pending_when_evidence_missing()
    assert_ineligible_when_no_support_exists()
    assert_multiple_treatment_needs_handled()
    assert_pathogen_caution_flag()
    assert_metal_food_chain_caution_flag()
    assert_drinking_domestic_caution_flag()
    assert_no_future_fields()
    print("candidate filtering checks ok: Step E only")


if __name__ == "__main__":
    main()

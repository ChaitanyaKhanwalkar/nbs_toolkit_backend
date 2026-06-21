"""Acceptance tests for screening sizing and alternative comparison outputs."""

from app.engines.scenario_comparison import ScenarioComparisonEngine
from app.engines.sizing_estimator import SizingEstimator


class FakeFootprintRepository:
    """Return small stored-style footprint rows without database access."""

    def __init__(self, rows):
        self.rows = rows

    def list_train_component_footprints(self):
        """Return configured footprint evidence rows."""

        return self.rows


def _train(train_id=1, components=(10, 11)):
    """Return a compact already-ranked train payload."""

    return {
        "train_id": train_id,
        "name": f"Train {train_id}",
        "rank": train_id,
        "match_score": 0.8 - train_id * 0.05,
        "confidence_score": 0.6,
        "confidence_label": "medium",
        "om_intensity": "Lower" if train_id == 1 else "Moderate",
        "nbs_components": [{"nbs_id": value} for value in components],
        "applicability_result": {"status": "allowed"},
        "caveats": [],
    }


def test_population_without_flow_does_not_invent_absolute_area() -> None:
    """Population-only evidence must not become a precise area or land-fit claim."""

    repository = FakeFootprintRepository(
        [
            {
                "train_id": 1,
                "nbs_id": 10,
                "solution": "Component A",
                "area_per_pe_low": 1,
                "area_per_pe_high": 2,
                "source_id": 1,
            },
            {
                "train_id": 1,
                "nbs_id": 11,
                "solution": "Component B",
                "area_per_pe_low": 0.5,
                "area_per_pe_high": 1,
                "source_id": 2,
            },
        ]
    )
    result = SizingEstimator(repository).estimate(
        ranked_trains=[_train()],
        context={"population_equivalent": 100, "available_land_m2": 350},
    )[0]

    assert result["estimated_area_low_m2"] is None
    assert result["estimated_area_high_m2"] is None
    assert result["land_fit"] == "insufficient_data"
    assert result["flow_status"] == "missing"
    assert "provide design flow" in result["estimate_label"]
    assert result["full_component_coverage"] is True
    assert result["source_ids"] == [1, 2]


def test_partial_footprint_coverage_never_claims_land_fit() -> None:
    """A partial estimate must remain insufficient even when land is supplied."""

    repository = FakeFootprintRepository(
        [
            {
                "train_id": 1,
                "nbs_id": 10,
                "area_per_pe_low": 1,
                "area_per_pe_high": 2,
            }
        ]
    )
    result = SizingEstimator(repository).estimate(
        ranked_trains=[_train()],
        context={"population_equivalent": 100, "available_land_m2": 1000},
    )[0]

    assert result["full_component_coverage"] is False
    assert result["land_fit"] == "insufficient_data"
    assert "Known components only" in result["estimate_label"]


def test_flow_estimate_uses_only_stored_hydraulic_loading_rates() -> None:
    """User flow divided by stored HLR should produce a transparent range."""

    repository = FakeFootprintRepository(
        [
            {"train_id": 1, "nbs_id": 10, "hlr_m3_m2_d": 0.1},
            {"train_id": 1, "nbs_id": 11, "hlr_m3_m2_d": 0.05},
        ]
    )
    result = SizingEstimator(repository).estimate(
        ranked_trains=[_train()],
        context={"design_flow_m3_d": 10, "available_land_m2": 250},
    )[0]

    assert result["basis"] == "design_flow"
    assert result["estimated_area_low_m2"] == 300
    assert result["estimated_area_high_m2"] == 300
    assert result["land_fit"] == "likely_too_little_land"


def test_missing_footprint_evidence_keeps_sizing_unavailable() -> None:
    """A supplied flow must not create area when no canonical footprint exists."""

    result = SizingEstimator(FakeFootprintRepository([])).estimate(
        ranked_trains=[_train()],
        context={"design_flow_m3_d": 10, "available_land_m2": 500},
    )[0]

    assert result["estimated_area_low_m2"] is None
    assert result["estimated_area_high_m2"] is None
    assert result["land_fit"] == "insufficient_data"
    assert result["sizing_confidence"] == "insufficient_data"


def test_comparison_preserves_rank_and_exposes_takeaways() -> None:
    """Comparison rows should package alternatives without reranking them."""

    trains = [_train(1, (10,)), _train(2, (20,))]
    sizing = [
        {
            "train_id": 1,
            "train_name": "Train 1",
            "estimate_label": "Estimated: 100-200 m2",
            "estimated_area_high_m2": 200,
            "full_component_coverage": True,
            "land_fit": "fits",
        },
        {
            "train_id": 2,
            "train_name": "Train 2",
            "estimate_label": "Estimated: 80-100 m2",
            "estimated_area_high_m2": 100,
            "full_component_coverage": True,
            "land_fit": "fits",
        },
    ]
    result = ScenarioComparisonEngine().compare(
        ranked_trains=trains,
        component_recommendations=[
            {
                "nbs_id": 10,
                "name": "Filter strip",
                "role": "source_control",
                "suitability_score": None,
                "standalone_suitability": "source_control_only",
                "applicability_status": "allowed",
                "key_constraints": ["Not raw sewage treatment"],
            }
        ],
        sizing_estimates=sizing,
        design_readiness={"short_label": "Ready for planning"},
        context={"workflow_mode": "uploaded_water_quality"},
    )

    assert [row["rank"] for row in result["options"]] == [1, 2]
    assert result["takeaways"][0]["label"] == "Best overall fit"
    assert any(
        row["label"] == "Lower land demand" and row["train_id"] == 2
        for row in result["takeaways"]
    )
    assert result["comparison_scope"] == "current_ranked_alternatives"
    assert result["component_options"][0]["name"] == "Filter strip"
    assert result["options"][0]["key_strength"] is None
    assert "confirming flow" in result["options"][0]["when_to_choose"]
    assert any(row["label"] == "Strongest evidence" for row in result["takeaways"])

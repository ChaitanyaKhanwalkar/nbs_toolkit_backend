"""Tests for screening-level non-monetary Cost-Benefit Ratio v1."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from pytest import approx

from app.api.routes.recommendation import _attach_cost_benefit
from app.engines.cost_benefit_analysis import (
    CostBenefitAnalysisEngine,
    CostBenefitComponent,
    CostBenefitInput,
    map_missing_data_to_burden,
    weighted_average_available,
)
from app.engines.train_recommendation import TrainRecommendationEngine
from app.repositories import EngineDataRepository


DATABASE_URL = "sqlite:///../canonical db/narmada_nbs_canonical.db"


def test_formula_with_known_values() -> None:
    """Known benefit/cost values should produce the documented ratio."""

    benefit = weighted_average_available(
        [
            CostBenefitComponent(
                key="benefit",
                label="Benefit",
                value=0.78,
                weight=1.0,
                direction="higher_better",
                status="available",
                explanation="test",
            )
        ]
    )
    burden = weighted_average_available(
        [
            CostBenefitComponent(
                key="cost",
                label="Cost burden",
                value=0.45,
                weight=1.0,
                direction="higher_worse",
                status="available",
                explanation="test",
            )
        ]
    )

    assert benefit == 0.78
    assert burden == 0.45
    assert round(benefit / burden, 2) == 1.73


def test_denominator_floor_is_used_for_low_cost_burden() -> None:
    engine = CostBenefitAnalysisEngine(
        component_weights=[
            _weight("C1", "Benefit", "benefit", 1.0, "higher_better"),
            _weight("C7", "Footprint burden", "cost_burden", 1.0, "higher_worse"),
        ]
    )
    result = engine.analyze(
        CostBenefitInput(
            train={
                "criteria_breakdown": [
                    _criterion("C1", 0.80, "benefit"),
                    _criterion("C7", 0.95, "cost"),
                ]
            }
        )
    )

    assert result.denominator_floor_used is True
    assert result.screening_cbr == 4.0


def test_missing_footprint_does_not_become_zero_burden() -> None:
    burden, explanation = map_missing_data_to_burden(
        {
            "criteria_breakdown": [_criterion("C7", None, "cost", missing=True)],
            "data_gaps": [],
            "sizing_estimate": {"land_fit": "insufficient_data"},
        }
    )

    assert burden > 0
    assert "evidence gaps" in explanation or "incomplete" in explanation


def test_high_burden_lowers_ratio() -> None:
    low_burden = _run_simple(benefit_value=0.80, cost_suitability=0.80)
    high_burden = _run_simple(benefit_value=0.80, cost_suitability=0.10)

    assert high_burden.screening_cbr < low_burden.screening_cbr


def test_hard_safety_warning_caps_label() -> None:
    result = CostBenefitAnalysisEngine(
        component_weights=[
            _weight("C1", "Benefit", "benefit", 1.0, "higher_better"),
            _weight("C7", "Footprint burden", "cost_burden", 1.0, "higher_worse"),
        ]
    ).analyze(
        CostBenefitInput(
            train={
                "criteria_breakdown": [
                    _criterion("C1", 0.95, "benefit"),
                    _criterion("C7", 0.95, "cost"),
                ],
                "applicability_result": {"status": "rejected"},
            }
        )
    )

    assert result.label == "Needs expert review"


def test_industrial_and_drinking_caveats_appear() -> None:
    industrial = _run_simple(
        benefit_value=0.80,
        cost_suitability=0.80,
        context={"pollution_source_type": "industrial_or_mixed_industrial"},
    )
    drinking = _run_simple(
        benefit_value=0.80,
        cost_suitability=0.80,
        context={"use_case": "drinking"},
    )

    assert industrial.label == "Needs expert review"
    assert "Pretreatment required; NbS polishing only." in industrial.caveats
    assert drinking.label == "Needs expert review"
    assert (
        "Expert-review only; not standalone potable treatment."
        in drinking.caveats
    )


def test_c7_c8_cost_suitability_is_inverted_to_burden() -> None:
    result = CostBenefitAnalysisEngine(
        component_weights=[
            _weight("C1", "Benefit", "benefit", 1.0, "higher_better"),
            _weight("C7", "Footprint burden", "cost_burden", 0.5, "higher_worse"),
            _weight("C8", "O&M burden", "cost_burden", 0.5, "higher_worse"),
        ]
    ).analyze(
        CostBenefitInput(
            train={
                "criteria_breakdown": [
                    _criterion("C1", 0.80, "benefit"),
                    _criterion("C7", 0.70, "cost"),
                    _criterion("C8", 0.40, "cost"),
                ]
            }
        )
    )

    burden_by_key = {row.key: row.value for row in result.cost_components}
    assert burden_by_key["C7"] == approx(0.30)
    assert burden_by_key["C8"] == approx(0.60)


def test_db_method_tables_are_available_and_non_monetary() -> None:
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        repo = EngineDataRepository(session)
        method = repo.get_cost_benefit_method()
        weights = repo.list_cost_benefit_component_weights()
        integrity = session.execute(text("PRAGMA integrity_check")).scalar_one()
        foreign_keys = session.execute(text("PRAGMA foreign_key_check")).all()

    assert method is not None
    assert method["method_key"] == "screening_non_monetary_v1"
    assert method["is_monetary"] == 0
    assert round(sum(row["weight"] for row in weights if row["side"] == "benefit"), 6) == 1.0
    assert round(sum(row["weight"] for row in weights if row["side"] == "cost_burden"), 6) == 1.0
    assert integrity == "ok"
    assert foreign_keys == []


def test_topsis_order_is_unchanged_after_cbr_attachment() -> None:
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        repo = EngineDataRepository(session)
        ranked = TrainRecommendationEngine(repo).rank(
            use_case="discharge_inland",
            contaminant_gaps=[
                {
                    "parameter": "bod",
                    "observed_value": 100,
                    "direction": "reduce",
                    "required_removal_percent": 70,
                }
            ],
            context={"pollution_source_type": "domestic_sewage"},
            region_id=27,
            input_source_type="water_type_profile",
        )["ranked_trains"]
        before = [(row["rank"], row["name"], row["match_score"]) for row in ranked]
        _attach_cost_benefit(
            ranked_trains=ranked,
            engine_data=repo,
            design_readiness={"level": "planning_level_result"},
            context={"pollution_source_type": "domestic_sewage", "use_case": "discharge_inland"},
            location_context={"context_flags": {"mainstem_or_high_order": True}},
        )
        after = [(row["rank"], row["name"], row["match_score"]) for row in ranked]

    assert after == before
    assert all(row["cost_benefit"]["official_ranking_unchanged"] for row in ranked)


def _run_simple(
    *,
    benefit_value: float,
    cost_suitability: float,
    context: dict | None = None,
) -> object:
    return CostBenefitAnalysisEngine(
        component_weights=[
            _weight("C1", "Benefit", "benefit", 1.0, "higher_better"),
            _weight("C7", "Footprint burden", "cost_burden", 1.0, "higher_worse"),
        ]
    ).analyze(
        CostBenefitInput(
            train={
                "criteria_breakdown": [
                    _criterion("C1", benefit_value, "benefit"),
                    _criterion("C7", cost_suitability, "cost"),
                ]
            },
            context=context or {},
        )
    )


def _weight(
    key: str,
    label: str,
    side: str,
    weight: float,
    direction: str,
) -> dict:
    return {
        "component_key": key,
        "component_label": label,
        "side": side,
        "weight": weight,
        "direction": direction,
    }


def _criterion(
    code: str,
    normalized_value: float | None,
    benefit_or_cost: str,
    *,
    missing: bool = False,
) -> dict:
    return {
        "criterion_code": code,
        "criterion_name": code,
        "normalized_value": normalized_value,
        "benefit_or_cost": benefit_or_cost,
        "data_status": "unknown_median_imputed" if missing else "known",
    }

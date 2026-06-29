"""Smoke tests for canonical recommendation-engine support data.

These checks protect the engine-ready canonical DB contract: A0 applicability
rules, canonical criteria weights, all-use-case train summaries, and unknown
performance gaps must be visible to backend code before ranking work continues.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.repositories import EngineDataRepository


ROOT_DIR = Path(__file__).resolve().parents[2]
CANONICAL_DB = ROOT_DIR / "canonical db" / "narmada_nbs_canonical.db"
DATABASE_URL = f"sqlite:///{CANONICAL_DB.as_posix()}"
USE_CASES = {"drinking", "irrigation", "discharge_inland"}


def _repository() -> EngineDataRepository:
    """Return an engine data repository connected to the canonical DB."""

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    session = Session(engine)
    return EngineDataRepository(session)


def test_engine_ready_tables_and_views_have_expected_counts() -> None:
    """Verify the canonical DB exposes the newly patched engine data."""

    repository = _repository()
    try:
        assert len(repository.list_applicability_rules()) == 46
        assert len(repository.list_criteria_weights()) == 21
        assert len(repository.list_engine_usecase_matrix()) == 24
        assert len(repository.list_train_cards()) == 8
        assert len(repository.list_train_usecase_summary()) == 24
    finally:
        repository.session.close()


def test_criteria_weights_cover_three_use_cases() -> None:
    """Verify DB weights cover all active use cases."""

    repository = _repository()
    try:
        weights = repository.list_criteria_weights()
    finally:
        repository.session.close()

    assert {row["use_case"] for row in weights} == USE_CASES
    statuses_by_use_case = {
        use_case: {row["status"] for row in weights if row["use_case"] == use_case}
        for use_case in USE_CASES
    }
    assert statuses_by_use_case["irrigation"] <= {
        "FINAL_V1_AHP_FUZZY_ENSEMBLE",
        "temporary_not_expert_validated",
    }
    assert statuses_by_use_case["drinking"] == {"FINAL_V1_AHP_FUZZY_ENSEMBLE"}
    assert statuses_by_use_case["discharge_inland"] == {
        "FINAL_V1_AHP_FUZZY_ENSEMBLE"
    }
    assert all(0 <= row["weight"] <= 1 for row in weights)


def test_canonical_weights_have_required_active_criteria() -> None:
    """Verify each use case has seven active criteria and no active C5."""

    repository = _repository()
    try:
        for use_case in USE_CASES:
            weights = repository.list_criteria_weights(use_case)
            codes = {row["criterion_code"] for row in weights}
            total = sum(float(row["weight"]) for row in weights)

            assert len(weights) == 7
            assert codes == {"C1", "C2", "C3", "C4", "C6", "C7", "C8"}
            assert "C5" not in codes
            tolerance = 0.00011 if use_case == "irrigation" else 0.000002
            assert abs(total - 1.0) <= tolerance
            assert {
                row["criterion_code"]: row["benefit_or_cost"] for row in weights
            }["C7"] == "cost"
            assert {
                row["criterion_code"]: row["benefit_or_cost"] for row in weights
            }["C8"] == "cost"
    finally:
        repository.session.close()


def test_final_v1_weights_differ_by_selected_use_case() -> None:
    """Verify selected target use cases load their own criteria weights."""

    repository = _repository()
    try:
        profiles = {
            use_case: {
                row["criterion_code"]: round(float(row["weight"]), 6)
                for row in repository.list_criteria_weights(use_case)
            }
            for use_case in USE_CASES
        }
    finally:
        repository.session.close()

    assert profiles["drinking"] != profiles["irrigation"]
    assert profiles["drinking"] != profiles["discharge_inland"]
    assert profiles["irrigation"] != profiles["discharge_inland"]


def test_usecase_matrix_returns_three_verdicts_per_train() -> None:
    """Verify each train can display drinking/irrigation/discharge together."""

    repository = _repository()
    try:
        matrix = repository.list_engine_usecase_matrix()
    finally:
        repository.session.close()

    train_ids = {row["train_id"] for row in matrix}
    for train_id in train_ids:
        use_cases = {
            row["use_case"]
            for row in matrix
            if row["train_id"] == train_id
        }
        assert use_cases == USE_CASES


def test_missing_removal_data_is_unknown_not_zero() -> None:
    """Verify frontend train cards label missing rows as unknown data gaps."""

    repository = _repository()
    try:
        cards = repository.list_train_cards()
        summaries = repository.list_train_usecase_summary()
    finally:
        repository.session.close()

    assert any(
        "unknown (data gap)" in (card["removal_summary"] or "")
        for card in cards
    )
    assert any(row["unknown_count"] > 0 for row in summaries)

"""Smoke tests for canonical recommendation-engine support data.

These checks protect the engine-ready canonical DB contract: A0 applicability
rules, provisional criteria weights, all-use-case train summaries, and unknown
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
    """Verify provisional DB weights cover all active use cases."""

    repository = _repository()
    try:
        weights = repository.list_criteria_weights()
    finally:
        repository.session.close()

    assert {row["use_case"] for row in weights} == USE_CASES
    assert {
        row["status"]
        for row in weights
    } == {"UNVERIFIED_PROVISIONAL"}
    assert all(0 <= row["weight"] <= 1 for row in weights)


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

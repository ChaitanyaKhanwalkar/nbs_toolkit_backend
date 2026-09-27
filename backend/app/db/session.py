"""Database engine and session helpers.

Beginners: set `DATABASE_URL` in `backend/.env` when you want to override the
default bundled SQLite database. PostgreSQL is also supported through SQLAlchemy
URLs such as `postgresql+psycopg://user:password@host:5432/dbname`. Do not
hard-code production credentials here.
"""

from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


BUNDLED_SQLITE_PATH = Path(__file__).resolve().parents[2] / "data" / "narmada_nbs_canonical.db"


def _bundled_sqlite_url() -> str:
    """Return a Linux/Windows-safe SQLAlchemy URL for the bundled SQLite DB."""

    return f"sqlite:///{BUNDLED_SQLITE_PATH.as_posix()}"


def _normalize_database_url(database_url: str) -> str:
    """Make common PostgreSQL URLs use the installed psycopg driver."""

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def _connect_args(database_url: str) -> dict[str, bool]:
    """Return driver-specific connection options."""

    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


@lru_cache
def get_engine() -> Engine:
    """Create and cache the SQLAlchemy engine from env or bundled SQLite."""

    settings = get_settings()
    database_url = _normalize_database_url(settings.database_url or _bundled_sqlite_url())
    return create_engine(
        database_url,
        connect_args=_connect_args(database_url),
        pool_pre_ping=True,
    )


def get_session_factory() -> sessionmaker[Session]:
    """Create a SQLAlchemy session factory bound to the configured engine."""

    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=get_engine(),
    )


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""

    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()

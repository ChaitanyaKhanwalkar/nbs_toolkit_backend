"""Database health-check helpers.

The health check only verifies that a connection can run `SELECT 1`.
It does not inspect scientific tables and does not implement recommendation
logic.
"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_engine


def check_database_connection() -> dict[str, str]:
    """Return a small status dictionary for the `/health/db` endpoint."""

    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except RuntimeError as exc:
        return {
            "status": "error",
            "database": "not_configured",
            "detail": str(exc),
        }
    except SQLAlchemyError as exc:
        return {
            "status": "error",
            "database": "unreachable",
            "detail": str(exc),
        }

    return {
        "status": "ok",
        "database": "reachable",
    }

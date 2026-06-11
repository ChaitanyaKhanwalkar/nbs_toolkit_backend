"""Smoke test for importing and calling read-only API routes.

This test uses an in-memory SQLite database so it never connects to production
and never needs real scientific data. It checks route wiring only.
"""

from collections.abc import Generator

try:
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.pool import StaticPool
except ModuleNotFoundError as exc:
    print(
        "api smoke test skipped: install backend requirements first "
        f"({exc.name} is missing)."
    )
    raise SystemExit(0) from exc

from app import models  # noqa: F401  # Import models so Base.metadata knows the tables.
from app.db.base import Base
from app.db.session import get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Yield a temporary local database session for route smoke tests."""

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def main() -> None:
    """Call representative routes and verify they are mounted."""

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)

        health_response = client.get("/health")
        assert health_response.status_code == 200, health_response.text

        reference_response = client.get("/api/v1/reference")
        assert reference_response.status_code == 200, reference_response.text

        payload = reference_response.json()
        assert "basins" in payload
        assert "regions" in payload
        assert "sources" in payload
        print("api routes ok: /health and /api/v1/reference")
    finally:
        app.dependency_overrides.clear()


if __name__ == "__main__":
    main()

"""Smoke test for the read-only API route layer.

This test uses an in-memory SQLite database so it never connects to production
and never needs real scientific data. It checks route wiring, route order,
missing-resource responses, OpenAPI output, the raw-data read-only route
guarantee, and the local recommendation POST route exception.
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Iterator

try:
    from fastapi.testclient import TestClient
    from sqlalchemy import event
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
import app.main as main_module
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Keep this route smoke test focused on route wiring. The API should not write
# during these checks, so fail clearly if anything tries to run INSERT/UPDATE/etc.
WRITE_SQL_PREFIXES = ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE")


@event.listens_for(engine, "before_cursor_execute")
def block_write_sql(
    _connection: object,
    _cursor: object,
    statement: str,
    _parameters: object,
    _context: object,
    _executemany: bool,
) -> None:
    """Block accidental writes after the in-memory schema is created."""

    if statement.lstrip().upper().startswith(WRITE_SQL_PREFIXES):
        raise AssertionError(f"Read-only API smoke test blocked write SQL: {statement}")


def override_get_db() -> Generator[Session, None, None]:
    """Yield a temporary local database session for route smoke tests."""

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def route_test_client() -> Iterator[TestClient]:
    """Return a TestClient with safe local overrides installed."""

    original_health_checker = main_module.check_database_connection
    app.dependency_overrides[get_db] = override_get_db

    def fake_database_health() -> dict[str, str]:
        """Avoid using any real configured database in route smoke tests."""

        return {
            "status": "error",
            "database": "not_configured",
            "detail": "route smoke test uses a local in-memory database override",
        }

    main_module.check_database_connection = fake_database_health
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        main_module.check_database_connection = original_health_checker


def assert_status(
    client: TestClient,
    path: str,
    expected_status: int = 200,
) -> dict[str, object] | list[object]:
    """Call a path and assert its status code with a helpful error."""

    response = client.get(path)
    assert response.status_code == expected_status, (
        f"{path} returned {response.status_code}: {response.text}"
    )
    return response.json()


def check_core_smoke_routes(client: TestClient) -> None:
    """Check health and raw-data index routes."""

    assert_status(client, "/health")

    db_health = client.get("/health/db")
    assert db_health.status_code in {200, 503}, db_health.text
    db_payload = db_health.json()
    assert db_payload["status"] in {"ok", "error"}
    if db_payload["status"] == "error":
        assert db_payload.get("detail")

    for path in [
        "/api/v1/reference",
        "/api/v1/reference/basins",
        "/api/v1/reference/regions",
        "/api/v1/reference/sources",
        "/api/v1/reference/stations",
        "/api/v1/reference/use-cases",
        "/api/v1/water/parameters",
        "/api/v1/standards/use-cases",
        "/api/v1/nbs/options",
        "/api/v1/plants",
        "/api/v1/availability",
    ]:
        assert_status(client, path)


def check_route_order(client: TestClient) -> None:
    """Confirm literal paths are not swallowed by dynamic ID routes."""

    assert_status(client, "/api/v1/nbs/options")
    assert_status(client, "/api/v1/plants/nbs/1")
    assert_status(client, "/api/v1/standards/use-cases")


def check_missing_resources(client: TestClient) -> None:
    """Confirm missing single resources return safe 404 responses."""

    assert_status(client, "/api/v1/sites/999999", expected_status=404)
    assert_status(client, "/api/v1/nbs/999999", expected_status=404)
    assert_status(client, "/api/v1/plants/999999", expected_status=404)


def check_read_only_guarantee() -> None:
    """Confirm raw-data API routes stay GET-only."""

    versioned_routes = {
        path: set(methods)
        for path, methods in app.openapi()["paths"].items()
        if path.startswith("/api/v1")
    }
    assert versioned_routes, "No /api/v1 routes are registered."
    for path, methods in versioned_routes.items():
        if path in {"/api/v1/recommend", "/api/v1/water/upload"}:
            assert methods == {"post"}, f"{path} exposes unexpected methods: {methods}"
        else:
            assert methods == {"get"}, f"{path} exposes non-GET methods: {methods}"


def check_openapi(client: TestClient) -> None:
    """Confirm OpenAPI exposes raw routes and the local recommendation route."""

    payload = assert_status(client, "/openapi.json")
    paths = payload["paths"]
    assert "/api/v1/reference" in paths
    assert "/api/v1/recommend" in paths
    assert "post" in paths["/api/v1/recommend"]


def main() -> None:
    """Run all beginner-readable API hardening checks."""

    with route_test_client() as client:
        check_core_smoke_routes(client)
        check_route_order(client)
        check_missing_resources(client)
        check_read_only_guarantee()
        check_openapi(client)

    print("api route smoke checks ok: health, raw routes, order, 404s, OpenAPI")


if __name__ == "__main__":
    main()

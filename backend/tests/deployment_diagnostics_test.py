"""Tests for the /__version deployment diagnostic endpoint.

These assertions also act as a guard that the served app object is the real
backend (versioned /api/v1 routes), not the legacy repo-root app.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_version_endpoint_identifies_real_backend_app() -> None:
    response = TestClient(app).get("/__version")

    assert response.status_code == 200, response.text
    payload = response.json()

    # Discriminators vs. the legacy repo-root "NBS Toolkit API" v1.0.0 app.
    assert payload["app_version"] == "0.1.0"
    assert payload["app_name"] == "Narmada NbS Backend"
    assert isinstance(payload["database_url_set"], bool)
    assert payload["route_count"] >= 28
    assert "/api/v1/reference" in payload["first_20_routes"]


def test_expected_routes_are_registered() -> None:
    paths = set(app.openapi()["paths"].keys())
    for expected in (
        "/health",
        "/health/db",
        "/api/v1/reference",
        "/api/v1/sites/options",
    ):
        assert expected in paths, f"missing route {expected}"

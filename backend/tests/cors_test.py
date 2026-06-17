r"""Smoke test for CORS so the Flutter web client can reach the API.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\cors_test.py

The Flutter web app runs on a random localhost port (or behind a Cloudflare
tunnel), so the browser needs CORS headers from the backend. This test does not
connect to Azure, mutate data, or change deployment.
"""

from __future__ import annotations

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError as exc:
    print(f"cors test skipped: install backend requirements first ({exc.name} is missing).")
    raise SystemExit(0) from exc

from app.core.config import Settings
from app.main import app


def assert_settings_parse_origins() -> None:
    """The settings helper should parse '*' and explicit comma lists."""

    assert Settings(CORS_ALLOW_ORIGINS="*").cors_origins_list == ["*"]
    assert Settings(CORS_ALLOW_ORIGINS="").cors_origins_list == ["*"]
    assert Settings(
        CORS_ALLOW_ORIGINS="http://localhost:5000, https://x.trycloudflare.com"
    ).cors_origins_list == [
        "http://localhost:5000",
        "https://x.trycloudflare.com",
    ]


def assert_simple_request_gets_cors_header() -> None:
    """A browser-style request with an Origin should get an allow-origin header."""

    client = TestClient(app)
    response = client.get("/health", headers={"Origin": "http://localhost:54321"})

    assert response.status_code == 200
    assert "access-control-allow-origin" in {
        key.lower() for key in response.headers
    }


def assert_preflight_is_allowed() -> None:
    """A CORS preflight for the recommend route should be permitted."""

    client = TestClient(app)
    response = client.options(
        "/api/v1/recommend",
        headers={
            "Origin": "http://localhost:54321",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code in (200, 204), response.status_code
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin is not None


def main() -> None:
    assert_settings_parse_origins()
    assert_simple_request_gets_cors_header()
    assert_preflight_is_allowed()
    print("cors checks ok: browser clients can reach the API")


if __name__ == "__main__":
    main()

r"""Route safety checks for the local recommendation API endpoint.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\recommendation_api_route_safety_test.py

These checks inspect route registration and OpenAPI only. They do not connect
to Azure, mutate data, deploy anything, classify health risk, or calculate AHP
pairwise weights.
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError as exc:
    print(
        "recommendation route safety test skipped: install backend requirements first "
        f"({exc.name} is missing)."
    )
    raise SystemExit(0) from exc

from app.main import app


FORBIDDEN_FIELDS = {
    "health_risk",
    "ahp",
    "ahp_weight",
    "azure",
    "deployment",
}


def assert_recommend_route_appears_in_openapi() -> None:
    """OpenAPI should expose the local POST recommendation endpoint."""

    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200, response.text

    payload = response.json()
    paths = payload["paths"]
    assert "/api/v1/recommend" in paths
    assert "post" in paths["/api/v1/recommend"]
    assert "get" not in paths["/api/v1/recommend"]

    found = _find_forbidden_keys(paths["/api/v1/recommend"], FORBIDDEN_FIELDS)
    assert not found, f"OpenAPI leaked forbidden fields: {sorted(found)}"


def assert_recommend_is_only_versioned_post_route() -> None:
    """No unrelated versioned routes should gain non-GET methods."""

    versioned_routes = {
        path: set(methods)
        for path, methods in app.openapi()["paths"].items()
        if path.startswith("/api/v1")
    }
    assert versioned_routes, "No /api/v1 routes are registered."

    for path, methods in versioned_routes.items():
        if path in {"/api/v1/recommend", "/api/v1/water/upload"}:
            assert methods == {"post"}, f"{path} methods changed: {methods}"
        else:
            assert methods == {"get"}, f"{path} exposes unexpected methods: {methods}"


def assert_existing_literal_route_order_still_safe() -> None:
    """Existing literal routes should still be registered as normal GET routes."""

    paths_by_method = {
        (path, tuple(sorted(methods)))
        for path, methods in app.openapi()["paths"].items()
    }

    assert ("/api/v1/nbs/options", ("get",)) in paths_by_method
    assert ("/api/v1/plants/nbs/{nbs_id}", ("get",)) in paths_by_method
    assert ("/api/v1/standards/use-cases", ("get",)) in paths_by_method
    assert ("/api/v1/recommend", ("post",)) in paths_by_method


def _find_forbidden_keys(value: Any, forbidden_fields: set[str]) -> set[str]:
    """Recursively find forbidden keys in dictionaries/lists."""

    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in forbidden_fields:
                found.add(key_text)
            found.update(_find_forbidden_keys(child, forbidden_fields))
    elif isinstance(value, list):
        for child in value:
            found.update(_find_forbidden_keys(child, forbidden_fields))
    return found


def main() -> None:
    """Run all local recommendation route safety checks."""

    assert_recommend_route_appears_in_openapi()
    assert_recommend_is_only_versioned_post_route()
    assert_existing_literal_route_order_still_safe()
    print("recommendation route safety checks ok: local POST route only")


if __name__ == "__main__":
    main()

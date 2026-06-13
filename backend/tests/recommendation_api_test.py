r"""Local API tests for the staged recommendation endpoint.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\recommendation_api_test.py

These tests use FastAPI TestClient with dependency overrides and fake local
providers. They do not connect to Azure, mutate data, deploy anything, classify
health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError as exc:
    print(
        "recommendation api test skipped: install backend requirements first "
        f"({exc.name} is missing)."
    )
    raise SystemExit(0) from exc

from app.api.routes.recommendation import get_scientific_workflow_service
from app.main import app
from app.services import ScientificWorkflowService
from scientific_engine_ai_integration_test import (
    add_fake_numeric_criteria,
    build_raw_input,
    fake_nbs_provider,
    fake_standards_service,
)
from scientific_workflow_service_ak_test import (
    FakePlantMappingProvider,
    temporary_weights,
)


FORBIDDEN_FIELDS = {
    "health_risk",
    "ahp",
    "ahp_weight",
    "azure",
    "deployment",
}


class FakeWorkflowService:
    """Workflow-service test double that still runs the real staged engines."""

    def __init__(self) -> None:
        self.service = ScientificWorkflowService(
            standards_service=fake_standards_service(),
            nbs_provider=fake_nbs_provider(),
            plant_provider=FakePlantMappingProvider(),
        )

    def run(self, raw_input: dict[str, Any], **kwargs: Any) -> Any:
        """Run the real workflow with fake local providers and numeric criteria."""

        assert kwargs.get("max_step") == "L"
        return self.service.run(
            raw_input,
            matrix_transform=add_fake_numeric_criteria,
            **kwargs,
        )


def fake_workflow_service() -> FakeWorkflowService:
    """Return the local fake workflow service for dependency overrides."""

    return FakeWorkflowService()


@contextmanager
def recommendation_test_client() -> Iterator[TestClient]:
    """Return a client with the recommendation workflow dependency overridden."""

    app.dependency_overrides[get_scientific_workflow_service] = fake_workflow_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def valid_payload(*, include_weights: bool = True) -> dict[str, Any]:
    """Return a request payload shaped like a local frontend request."""

    raw_input = build_raw_input()
    payload = {
        "use_case": raw_input["use_case"],
        "measured_observations": raw_input["measured_observations"],
        "selected_parameters": raw_input["selected_parameters"],
        "notes": "Local API test request.",
    }
    if include_weights:
        payload["temporary_weights"] = temporary_weights()
    return payload


def post_recommend(
    client: TestClient,
    payload: dict[str, Any],
    expected_status: int = 200,
) -> dict[str, Any]:
    """POST the recommendation request and assert a useful response code."""

    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == expected_status, response.text
    return response.json()


def assert_recommendation_response_with_temporary_weights() -> None:
    """Temporary weights should produce an assembled recommendation bundle."""

    with recommendation_test_client() as client:
        payload = post_recommend(client, valid_payload())

    assert payload["workflow_status"] == "completed"
    assert payload["step_completed"] == "L"
    assert payload["use_case"] == "surface_discharge"
    assert payload["recommendation_assembly_bundle"] is not None
    assert payload["weights_status"] == "temporary_not_expert_validated"
    assert payload["expert_validated"] is False
    assert payload["provisional_note"]

    bundle = payload["recommendation_assembly_bundle"]
    recommendations = bundle["recommendations"]
    assert recommendations
    assert bundle["weights_status"] == "temporary_not_expert_validated"
    assert bundle["expert_validated"] is False

    for recommendation in recommendations:
        assert recommendation["match_score"] == recommendation["topsis_closeness"]
        assert recommendation["confidence_score"] != recommendation["match_score"]
        assert recommendation["weights_status"] == "temporary_not_expert_validated"


def assert_plants_do_not_affect_rank() -> None:
    """Plant matches should be supporting output and should not change rank."""

    with recommendation_test_client() as client:
        payload = post_recommend(client, valid_payload())

    recommendations = payload["recommendation_assembly_bundle"]["recommendations"]
    ranks = [recommendation["rank"] for recommendation in recommendations]
    assert ranks == sorted(ranks)
    assert any(recommendation["plant_matches"] for recommendation in recommendations)
    assert all(
        recommendation["explanation"][-1]
        == "Plant matches are supporting explicit mappings only and do not affect rank."
        for recommendation in recommendations
    )


def assert_missing_weights_returns_safe_warning_response() -> None:
    """Missing weights should return a structured response instead of crashing."""

    with recommendation_test_client() as client:
        payload = post_recommend(client, valid_payload(include_weights=False))

    assert payload["workflow_status"] == "completed"
    assert payload["step_completed"] == "L"
    assert payload["weights_status"] == "weights_missing"
    assert payload["expert_validated"] is False
    assert payload["recommendation_assembly_bundle"] is not None
    assert payload["recommendation_assembly_bundle"]["recommendation_count"] == 0
    assert payload["provisional_note"]
    assert any("No MCDA criteria weights" in warning for warning in payload["warnings"])


def assert_forbidden_fields_are_absent() -> None:
    """The local response must not expose health-risk, AHP, Azure, or deployment fields."""

    with recommendation_test_client() as client:
        payload = post_recommend(client, valid_payload())

    found = _find_forbidden_keys(payload, FORBIDDEN_FIELDS)
    assert not found, f"Recommendation API leaked forbidden fields: {sorted(found)}"


def assert_no_stack_trace_for_failed_service() -> None:
    """Unexpected service exceptions should become safe structured responses."""

    class RaisingService:
        def run(self, *_args: Any, **_kwargs: Any) -> Any:
            raise RuntimeError("fake local failure")

    app.dependency_overrides[get_scientific_workflow_service] = lambda: RaisingService()
    try:
        client = TestClient(app)
        payload = post_recommend(client, valid_payload())
    finally:
        app.dependency_overrides.clear()

    assert payload["workflow_status"] == "failed"
    assert payload["recommendation_assembly_bundle"] is None
    assert payload["errors"]
    assert "Traceback" not in str(payload)


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
    """Run all local recommendation API checks."""

    assert_recommendation_response_with_temporary_weights()
    assert_plants_do_not_affect_rank()
    assert_missing_weights_returns_safe_warning_response()
    assert_forbidden_fields_are_absent()
    assert_no_stack_trace_for_failed_service()
    print("recommendation API checks ok: local max_step L wrapper only")


if __name__ == "__main__":
    main()

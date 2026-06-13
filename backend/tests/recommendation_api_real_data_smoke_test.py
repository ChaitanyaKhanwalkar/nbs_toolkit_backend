r"""Real-data smoke test for the local recommendation API endpoint.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\recommendation_api_real_data_smoke_test.py

This test uses FastAPI TestClient against app.main, so it does not require a
live Uvicorn server. It relies on the locally configured database and checks
that the staged Step L recommendation response can be produced without Azure,
deployment changes, database mutation, AHP expert weights, or health-risk
logic.
"""

from __future__ import annotations

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError as exc:
    print(
        "real-data recommendation API smoke test skipped: install backend "
        f"requirements first ({exc.name} is missing)."
    )
    raise SystemExit(0) from exc

from app.main import app


PAYLOAD = {
    "use_case": "discharge_inland",
    "selected_parameters": ["bod", "tss", "nitrate_n", "ph"],
    "measured_observations": [
        {"parameter": "bod", "value": 45.0, "unit": "mg_l", "source_id": 101},
        {"parameter": "tss", "value": 180.0, "unit": "mg_l", "source_id": 101},
        {"parameter": "nitrate_n", "value": 18.0, "unit": "mg_l", "source_id": 102},
        {"parameter": "ph", "value": 7.4, "unit": "ph_units", "source_id": 102},
    ],
    "temporary_weights": {
        "removal_evidence_score": 5.0,
        "removal_evidence_coverage": 1.0,
        "site_suitability": 1.0,
    },
    "notes": (
        "Real-data smoke test for local Step M recommendation endpoint. "
        "Temporary weights only. Not expert validated. No DB mutation."
    ),
    "context": {
        "test_type": "real_data_recommendation_api_smoke_test",
        "source": "testclient",
    },
}


def assert_real_data_recommendation_response() -> None:
    """POST the known-working local payload and validate Step L output."""

    client = TestClient(app)
    response = client.post("/api/v1/recommend", json=PAYLOAD)

    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["workflow_status"] == "completed"
    assert payload["step_completed"] == "L"
    assert payload["weights_status"] == "temporary_not_expert_validated"
    assert payload["expert_validated"] is False
    assert payload["errors"] == []

    bundle = payload["recommendation_assembly_bundle"]
    assert bundle is not None
    assert bundle["recommendation_count"] > 0
    assert bundle["recommendations"]

    for recommendation in bundle["recommendations"][:5]:
        assert recommendation.get("rank") is not None
        assert recommendation.get("nbs_id") is not None
        assert recommendation.get("nbs_name")
        assert recommendation["match_score"] == recommendation["topsis_closeness"]
        assert recommendation["confidence_score"] is not None
        assert recommendation["confidence_score"] != recommendation["match_score"]
        assert "plant_matches" in recommendation

    print(
        "real-data recommendation API smoke checks ok: "
        f"{bundle['recommendation_count']} ranked Step L recommendations"
    )


def main() -> None:
    """Run the real-data recommendation API smoke check."""

    assert_real_data_recommendation_response()


if __name__ == "__main__":
    main()

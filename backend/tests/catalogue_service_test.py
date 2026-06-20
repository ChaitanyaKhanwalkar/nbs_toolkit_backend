"""Acceptance checks for canonical learning catalogues."""

from fastapi.testclient import TestClient

from app.main import app


def test_learning_catalogue_exposes_all_canonical_sections() -> None:
    response = TestClient(app).get("/api/v1/catalogue")
    assert response.status_code == 200, response.text
    payload = response.json()

    assert len(payload["treatment_trains"]) == 8
    assert len(payload["nbs_components"]) == 28
    assert len(payload["plants"]) > 0
    assert payload["notes"]
    assert payload["evidence_records"]


def test_train_catalogue_includes_sequence_om_and_provenance() -> None:
    train = TestClient(app).get("/api/v1/catalogue").json()["treatment_trains"][0]

    assert train["sequence_steps"]
    assert train["intended_role"]
    assert len(train["use_case_suitability"]) == 3
    assert train["om_notes"]
    assert train["source_ids"]
    assert train["evidence_groups"]["Design guidance"]


def test_component_catalogue_preserves_missing_data_and_safety_boundaries() -> None:
    components = TestClient(app).get("/api/v1/catalogue").json()["nbs_components"]
    wetland = next(row for row in components if "Wetland" in row["solution"])

    assert wetland["catalogue_role"]
    assert wetland["pollutants_treated"]
    assert wetland["standalone_suitability"] == "Context-specific A0 screening required."
    assert any("in-channel" in value for value in wetland["where_not_suitable"])
    assert isinstance(wetland["missing_sections"], list)


def test_plant_catalogue_flags_invasive_rows_as_do_not_recommend() -> None:
    plants = TestClient(app).get("/api/v1/catalogue").json()["plants"]
    invasive = [row for row in plants if row["invasive"] == 1]
    non_invasive = [row for row in plants if row["invasive"] in {0, None}]

    assert invasive
    assert all(
        row["recommendation_status"] == "do_not_recommend_invasive"
        for row in invasive
    )
    assert all(
        row["recommendation_status"] == "eligible_for_local_validation"
        for row in non_invasive
    )
    assert any(row["mapped_components"] for row in plants)

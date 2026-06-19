"""Acceptance checks for canonical train ranking and safety behavior."""

from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.engines.train_recommendation import TrainRecommendationEngine
from app.api.routes.recommendation import _workflow_status
from app.main import app
from app.repositories import EngineDataRepository


ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = f"sqlite:///{(ROOT / 'canonical db' / 'narmada_nbs_canonical.db').as_posix()}"


def _rank(**overrides):
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        values = {
            "use_case": "discharge_inland",
            "contaminant_gaps": [
                {
                    "parameter": "bod",
                    "direction": "reduce",
                    "required_removal_percent": 70,
                }
            ],
            "context": {},
            "region_id": 20,
            "input_source_type": "user_measured",
        }
        values.update(overrides)
        return TrainRecommendationEngine(EngineDataRepository(session)).rank(**values)


def test_ranked_trains_have_dynamic_confidence_and_three_use_cases() -> None:
    result = _rank()
    assert result["ranked_trains"]
    assert {
        round(row["confidence_score"], 6) for row in result["ranked_trains"]
    } != {0.723}
    assert len({round(row["confidence_score"], 6) for row in result["ranked_trains"]}) > 1
    assert all(
        set(row["all_use_case_verdicts"])
        == {"drinking", "irrigation", "discharge_inland"}
        for row in result["ranked_trains"]
    )


def test_all_unknown_use_case_trains_follow_assessed_trains() -> None:
    result = _rank()
    flags = [row["all_use_cases_unknown"] for row in result["ranked_trains"]]
    assert all(
        not flags[index] or flags[index + 1]
        for index in range(len(flags) - 1)
    )
    for row in result["ranked_trains"]:
        expected = (
            "needs_data_for_use_case_assessment"
            if row["all_use_cases_unknown"]
            else "partially_or_fully_assessed"
        )
        assert row["use_case_assessment_status"] == expected


def test_high_order_in_channel_moves_component_trains_to_conditional() -> None:
    result = _rank(context={"intervention_position": "in_channel"})
    wetland_or_pond = [
        row
        for row in result["ranked_trains"]
        if any(
            component.get("family") in {"Constructed Wetlands", "Ponds & Lagoons"}
            for component in row["nbs_components"]
        )
    ]
    assert wetland_or_pond
    assert all(row["applicability_result"]["status"] == "conditional" for row in wetland_or_pond)
    assert any("not suitable inside" in " ".join(row["caveats"]).lower() for row in wetland_or_pond)


def test_industrial_context_requires_pretreatment() -> None:
    result = _rank(
        context={"pollution_source_type": "industrial_or_mixed_industrial"}
    )
    messages = " ".join(
        caveat
        for row in result["ranked_trains"]
        for caveat in row["caveats"]
    ).lower()
    assert "pretreatment" in messages or "etp/cetp" in messages


def test_industrial_extreme_ph_does_not_rank_wetland_only_train_first() -> None:
    """Industrial pH 3 must prioritize pretreatment-linked reactor pathways."""

    result = _rank(
        contaminant_gaps=[
            {
                "parameter": "cod",
                "direction": "reduce",
                "required_removal_percent": 85,
                "observed_value": 1000,
            },
            {
                "parameter": "ph",
                "direction": "adjust_range",
                "observed_value": 3,
            },
        ],
        context={
            "pollution_source_type": "industrial_or_mixed_industrial",
            "intervention_position": "standalone_primary_treatment",
        },
    )

    top = result["ranked_trains"][0]
    assert top["name"] in {"DEWATS modular train", "UASB-based STP"}
    caveats = " ".join(top["caveats"]).lower()
    assert "etp/cetp" in caveats
    assert "neutralization" in caveats


def test_top_train_changes_with_source_chemistry_and_high_order_context() -> None:
    """Ranking should respond to source, chemistry, and placement inputs."""

    domestic = _rank(
        contaminant_gaps=[
            {
                "parameter": "bod",
                "direction": "reduce",
                "required_removal_percent": 70,
                "observed_value": 80,
            },
            {"parameter": "ph", "direction": "none", "observed_value": 7.2},
        ],
        context={
            "pollution_source_type": "domestic_sewage",
            "intervention_position": "off_channel_or_stp_polishing",
        },
    )
    industrial = _rank(
        contaminant_gaps=[
            {
                "parameter": "cod",
                "direction": "reduce",
                "required_removal_percent": 85,
                "observed_value": 1000,
            },
            {"parameter": "ph", "direction": "adjust_range", "observed_value": 3},
        ],
        context={
            "pollution_source_type": "industrial_or_mixed_industrial",
            "intervention_position": "standalone_primary_treatment",
        },
    )
    high_order = _rank(
        contaminant_gaps=[],
        context={
            "workflow_mode": "site_context_only",
            "intervention_position": "in_channel",
        },
        input_source_type="missing",
    )

    domestic_top = domestic["ranked_trains"][0]["name"]
    industrial_top = industrial["ranked_trains"][0]["name"]
    high_order_top = high_order["ranked_trains"][0]["name"]
    assert len({domestic_top, industrial_top, high_order_top}) >= 2
    assert high_order_top != "VF nitrifying hybrid"


def test_unknown_performance_is_not_scored_as_zero() -> None:
    result = _rank()
    assert any(
        "unknown (data gap)" in (row.get("removal_summary") or "")
        for row in result["ranked_trains"]
    )


def test_ranked_trains_include_implementation_explanations() -> None:
    result = _rank(
        contaminant_gaps=[
            {"parameter": "ph", "direction": "adjust_range", "observed_value": 3}
        ],
        context={
            "pollution_source_type": "industrial_or_mixed_industrial",
            "intervention_position": "standalone_primary_treatment",
        },
    )
    top = result["ranked_trains"][0]
    assert top["implementation_role"] == "Polishing or buffer after ETP/CETP pretreatment"
    assert any("ETP/CETP" in item for item in top["pretreatment_requirements"])
    assert any("Neutralization" in item for item in top["pretreatment_requirements"])
    assert top["planting_guidance"]
    assert "data_gaps" in top


def test_agricultural_screening_prioritizes_source_control_context() -> None:
    result = _rank(
        contaminant_gaps=[],
        context={
            "workflow_mode": "pollution_source_screening",
            "pollution_source_type": "high_agriculture_only_no_water_data",
            "intervention_position": "off_channel_or_stp_polishing",
        },
        input_source_type="missing",
    )
    top = result["ranked_trains"][0]
    assert top["name"] != "VF nitrifying hybrid"
    assert top["implementation_role"] == "Source control and off-channel runoff polishing"
    assert any("farm-level" in item.lower() for item in top["implementation_guidance"])
    assert any("nutrient" in item.lower() and "source" in item.lower() for item in top["source_location_guidance"])
    assert any("off-channel polishing" in item.lower() for item in top["source_location_guidance"])

def test_source_location_guidance_is_separate_from_train_ranking() -> None:
    result = _rank(
        contaminant_gaps=[],
        context={
            "workflow_mode": "site_context_only",
            "intervention_position": "in_channel",
        },
        input_source_type="missing",
    )
    top = result["ranked_trains"][0]
    guidance = " ".join(top["source_location_guidance"]).lower()
    assert "context guidance" in guidance
    assert "measured water-quality data" in guidance
    assert "off-channel" in guidance
    assert "in-channel" in guidance
    wetland_like = [
        row
        for row in result["ranked_trains"]
        if any(
            component.get("family") in {"Constructed Wetlands", "Ponds & Lagoons"}
            for component in row["nbs_components"]
        )
    ]
    assert all(
        row["implementation_role"] == "Off-channel treatment or polishing only"
        for row in wetland_like
    )


def test_ranked_train_plants_exclude_invasive_catalogue_rows() -> None:
    result = _rank()
    plants = [
        plant
        for train in result["ranked_trains"]
        for plant in train["suitable_plants"]
    ]
    assert all(plant.get("invasive") in {0, None} for plant in plants)
    assert all("invasive" not in str(plant.get("native_status", "")).lower() for plant in plants)
    assert any(
        item["data_status"] == "unknown_median_imputed"
        for row in result["ranked_trains"]
        for item in row["criteria_breakdown"]
    )


def test_csv_upload_returns_contaminant_gaps() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/water/upload?use_case=discharge_inland",
        files={
            "file": (
                "water.csv",
                BytesIO(b"parameter,value,unit\nbod,80,mg_l\ntss,120,mg_l\n"),
                "text/csv",
            )
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["observation_count"] == 2
    assert payload["contaminant_gaps"]["results"]


def test_csv_upload_treats_blank_values_as_unknown() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/water/upload?use_case=discharge_inland",
        files={
            "file": (
                "water.csv",
                BytesIO(b"parameter,value,unit\nbod,80,mg_l\ntss,,mg_l\nph,7.2,ph_units\n"),
                "text/csv",
            )
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["observation_count"] == 2
    assert payload["unknown_parameter_count"] == 1
    assert payload["unknown_parameters"] == ["tss"]
    assert all(row["parameter"] != "tss" for row in payload["observations"])


def test_context_only_modes_are_labelled_as_guidance() -> None:
    """Useful context-only output should not present itself as a failed run."""

    assert _workflow_status(
        {"workflow_status": "data_missing"},
        {"workflow_mode": "site_context_only"},
        [{"train_id": 1}],
    ) == "context_guidance"
    assert _workflow_status(
        {"workflow_status": "data_missing"},
        {"workflow_mode": "pollution_source_screening"},
        [{"train_id": 1}],
    ) == "context_guidance"

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
                    "observed_value": 100,
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


def test_configured_canonical_database_has_expected_review_counts() -> None:
    """Guard against accidentally running the engine on a legacy database."""

    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        counts = EngineDataRepository(session).canonical_dataset_counts()

    assert counts == {
        "nbs_options": 28,
        "treatment_train": 8,
        "removal_efficiency": 167,
        "sources": 104,
        "nbs_footprint": 19,
        "plant_solution_map": 118,
        "site_attributes": 52,
    }


def test_pollutant_breakdown_covers_every_supplied_parameter() -> None:
    result = _rank(
        contaminant_gaps=[
            {
                "parameter": "bod",
                "observed_value": 80,
                "observed_unit": "mg_l",
                "limit_high": 30,
                "standard_unit": "mg_l",
                "status": "exceeds_standard",
                "direction": "reduce",
                "required_removal_percent": 62.5,
            },
            {
                "parameter": "ph",
                "observed_value": 7.2,
                "standard_unit": "ph_units",
                "limit_low": 5.5,
                "limit_high": 9,
                "status": "within_standard",
                "direction": "none",
            },
        ],
        context={"workflow_mode": "uploaded_water_quality"},
    )

    rows = result["ranked_trains"][0]["pollutant_gap_breakdown"]
    assert [row["parameter"] for row in rows] == ["bod", "ph"]
    assert rows[0]["gap_status"] == "exceeds_target"
    assert rows[1]["gap_status"] == "below_target"
    assert all(row["source"] == "user_csv" for row in rows)
    assert all("target_threshold" in row for row in rows)
    assert all("train_addresses_parameter" in row for row in rows)


def test_thin_input_confidence_is_capped_below_complete_panel() -> None:
    partial = _rank(
        contaminant_gaps=[
            {
                "parameter": "tss",
                "observed_value": 120,
                "status": "exceeds_standard",
                "direction": "reduce",
                "required_removal_percent": 20,
            }
        ]
    )
    complete = _rank(
        contaminant_gaps=[
            {
                "parameter": parameter,
                "observed_value": value,
                "status": "within_standard" if parameter == "ph" else "exceeds_standard",
                "direction": "none" if parameter == "ph" else "reduce",
                "required_removal_percent": None if parameter == "ph" else 50,
            }
            for parameter, value in (("bod", 80), ("cod", 200), ("tss", 120), ("ph", 7.2))
        ]
    )

    partial_by_id = {row["train_id"]: row for row in partial["ranked_trains"]}
    complete_by_id = {row["train_id"]: row for row in complete["ranked_trains"]}
    common_id = next(iter(partial_by_id.keys() & complete_by_id.keys()))
    partial_row = partial_by_id[common_id]
    complete_row = complete_by_id[common_id]
    assert partial_row["confidence_score"] <= 0.35
    assert partial_row["confidence_label"] == "low"
    assert complete_row["confidence_score"] > partial_row["confidence_score"]
    assert complete_row["confidence_factors"]["key_parameters_missing"] == []


def test_skipped_csv_rows_reduce_confidence_without_becoming_zero() -> None:
    gaps = [
        {
            "parameter": parameter,
            "observed_value": value,
            "status": "within_standard" if parameter == "ph" else "exceeds_standard",
            "direction": "none" if parameter == "ph" else "reduce",
            "required_removal_percent": None if parameter == "ph" else 50,
        }
        for parameter, value in (("bod", 80), ("cod", 200), ("tss", 120), ("ph", 7.2))
    ]
    clean = _rank(
        contaminant_gaps=gaps,
        context={"workflow_mode": "uploaded_water_quality"},
    )
    skipped = _rank(
        contaminant_gaps=gaps,
        context={
            "workflow_mode": "uploaded_water_quality",
            "csv_validation_summary": {
                "non_numeric_values": ["Row 6: NH4-N=unknown"],
                "unknown_parameters": ["Row 7: colour"],
            },
        },
    )

    clean_by_id = {row["train_id"]: row for row in clean["ranked_trains"]}
    skipped_by_id = {row["train_id"]: row for row in skipped["ranked_trains"]}
    common_id = next(iter(clean_by_id.keys() & skipped_by_id.keys()))
    assert skipped_by_id[common_id]["confidence_score"] < clean_by_id[common_id]["confidence_score"]
    assert skipped_by_id[common_id]["confidence_factors"]["skipped_row_count"] == 2


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


def _upload_csv(csv_text: str):
    """Upload one in-memory CSV through the public route."""

    return TestClient(app).post(
        "/api/v1/water/upload?use_case=discharge_inland",
        files={"file": ("water.csv", BytesIO(csv_text.encode()), "text/csv")},
    )


def test_csv_upload_accepts_optional_units_and_case_insensitive_headers() -> None:
    response = _upload_csv(
        " Parameter , VALUE , Unit \nBOD,30,mg/L\nCOD,100,mg/L\npH,7.2,\n"
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert [row["parameter"] for row in payload["observations_used"]] == [
        "bod",
        "cod",
        "ph",
    ]
    assert payload["csv_validation_summary"]["rows_used"] == 3
    assert payload["csv_validation_summary"]["is_valid"] is True
    assert [row["unit"] for row in payload["observations_used"][:2]] == [
        "mg_l",
        "mg_l",
    ]


def test_csv_upload_accepts_minimal_parameter_value_format() -> None:
    response = _upload_csv("parameter,value\nBOD,30\n")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["observations_used"][0]["parameter"] == "bod"
    assert payload["observations_used"][0]["unit"] == ""


def test_csv_upload_normalizes_common_parameter_aliases() -> None:
    response = _upload_csv(
        "parameter,value,unit\nBiological Oxygen Demand,35,mg/L\n"
        "chemical oxygen demand,120,mg/L\nNH4-N,8,mg/L\nNO3,4,mg/L\n"
        "total phosphorus,2,mg/L\nFC,100,MPN/100mL\n"
    )
    assert response.status_code == 200, response.text
    assert [row["parameter"] for row in response.json()["observations_used"]] == [
        "bod",
        "cod",
        "ammonia_n",
        "nitrate_n",
        "phosphate_p",
        "faecal_coliform",
    ]


def test_csv_upload_skips_non_numeric_and_unknown_rows_with_warnings() -> None:
    response = _upload_csv(
        "parameter,value,unit\nBOD,abc,mg/L\nrandom thing,123,mg/L\npH,7.1,\n"
    )
    assert response.status_code == 200, response.text
    summary = response.json()["csv_validation_summary"]
    assert summary["rows_used"] == 1
    assert summary["non_numeric_values"] == ["Row 2: BOD=abc"]
    assert summary["unknown_parameters"] == ["Row 3: random thing"]
    assert len(summary["warnings"]) == 2


def test_csv_upload_counts_blank_rows_parameters_and_values() -> None:
    response = _upload_csv(
        "parameter,value,unit\n,,\n,30,mg/L\nTSS,,mg/L\nBOD,30,mg/L\n"
    )
    assert response.status_code == 200, response.text
    summary = response.json()["csv_validation_summary"]
    assert summary["blank_rows"] == 1
    assert summary["blank_parameters"] == 1
    assert summary["blank_values"] == 1
    assert response.json()["unknown_parameters"] == ["tss"]


def test_csv_upload_reports_no_usable_values_without_crashing() -> None:
    response = _upload_csv(
        "parameter,value,unit\nBOD,abc,mg/L\nrandom thing,123,mg/L\nTSS,,mg/L\n"
    )
    assert response.status_code == 200, response.text
    summary = response.json()["csv_validation_summary"]
    assert summary["is_valid"] is False
    assert summary["rows_used"] == 0
    assert "No usable water-quality values found." in summary["errors"]


def test_csv_upload_wrong_headers_return_structured_validation_error() -> None:
    response = _upload_csv("name,amount\nBOD,30\n")
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "parameter and value columns" in detail["message"]
    assert detail["csv_validation_summary"]["missing_headers"] == [
        "parameter",
        "value",
    ]


def test_csv_template_units_feed_pollutant_gaps_and_change_ranking_inputs() -> None:
    client = TestClient(app)

    def recommend(csv_text: str) -> tuple[dict, dict]:
        upload = _upload_csv(csv_text)
        assert upload.status_code == 200, upload.text
        uploaded = upload.json()
        recommendation = client.post(
            "/api/v1/recommend",
            json={
                "use_case": "discharge_inland",
                "selected_parameters": [
                    row["parameter"] for row in uploaded["observations_used"]
                ],
                "measured_observations": uploaded["observations_used"],
                "context": {
                    "workflow_mode": "uploaded_water_quality",
                    "pollution_source_type": "domestic_sewage",
                    "intervention_position": "off_channel_or_stp_polishing",
                },
            },
        )
        assert recommendation.status_code == 200, recommendation.text
        return uploaded, recommendation.json()

    low_upload, low = recommend(
        "parameter,value,unit\nBOD,30,mg/L\nCOD,100,mg/L\nTSS,80,mg/L\npH,7.2,\n"
    )
    high_upload, high = recommend(
        "parameter,value,unit\nBOD,300,mg/L\nCOD,1000,mg/L\nTSS,800,mg/L\npH,7.2,\n"
    )

    assert all(
        row["unit"] == "mg_l"
        for row in high_upload["observations_used"]
        if row["parameter"] != "ph"
    )
    assert any(
        gap["parameter"] == "bod" and gap["required_removal_percent"] == 90
        for gap in high["contaminant_gaps"]
    )
    assert low["input_summary"]["data_used"] != high["input_summary"]["data_used"]
    assert low["ranked_trains"][0]["match_score"] != high["ranked_trains"][0]["match_score"]


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

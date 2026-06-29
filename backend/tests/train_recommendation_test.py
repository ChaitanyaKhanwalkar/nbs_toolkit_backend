"""Acceptance checks for canonical train ranking and safety behavior."""

from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.engines.train_recommendation import TrainRecommendationEngine
from app.engines.water_input_assembly import (
    MUNICIPAL_FALLBACK_NOTE,
    MUNICIPAL_PROFILE_NAME,
)
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
        "sources": 109,
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
    assert rows[0]["coverage_category"] == "used_in_scoring"
    assert rows[0]["coverage_label"] == "Used in scoring."


def test_recognized_parameter_without_target_is_read_not_silently_ignored() -> None:
    """A recognized unscored value must retain an explicit coverage category."""

    result = _rank(
        contaminant_gaps=[
            {
                "parameter": "phosphate_p",
                "observed_value": 2.5,
                "observed_unit": "mg_l",
                "status": "unknown_no_standard",
                "direction": "unknown",
            }
        ],
        context={"workflow_mode": "uploaded_water_quality"},
    )

    row = result["ranked_trains"][0]["pollutant_gap_breakdown"][0]
    assert row["coverage_category"] == "supporting_context"
    assert row["coverage_label"] == "Used as supporting context."
    assert row["observed_value"] == 2.5


def test_ph_is_scored_against_stored_discharge_range() -> None:
    """pH should compare against stored range standards without unit conversion."""

    client = TestClient(app)
    acidic = client.post(
        "/api/v1/recommend",
        json={
            "use_case": "discharge_inland",
            "selected_parameters": ["ph"],
            "measured_observations": [
                {"parameter": "ph", "value": 3, "unit": "ph_units"},
            ],
            "context": {"workflow_mode": "manual_measured_water_quality"},
        },
    )
    neutral = client.post(
        "/api/v1/recommend",
        json={
            "use_case": "discharge_inland",
            "selected_parameters": ["ph"],
            "measured_observations": [
                {"parameter": "ph", "value": 7, "unit": "ph_units"},
            ],
            "context": {"workflow_mode": "manual_measured_water_quality"},
        },
    )

    assert acidic.status_code == 200, acidic.text
    assert neutral.status_code == 200, neutral.text
    acidic_payload = acidic.json()
    neutral_payload = neutral.json()

    acidic_gap = acidic_payload["contaminant_gaps"][0]
    neutral_gap = neutral_payload["contaminant_gaps"][0]
    assert acidic_gap["parameter"] == "ph"
    assert acidic_gap["status"] == "outside_range"
    assert acidic_gap["limit_low"] == 5.5
    assert acidic_gap["limit_high"] == 9.0
    assert neutral_gap["status"] == "within_standard"

    acidic_coverage = acidic_payload["parameter_coverage"][0]
    neutral_coverage = neutral_payload["parameter_coverage"][0]
    assert acidic_coverage["target_available"] is True
    assert acidic_coverage["target_status"] == "exceeds_selected_target"
    assert acidic_coverage["scoring_role"] == "used_in_scoring"
    assert neutral_coverage["target_status"] == "within_selected_target"
    assert "pH adjustment or neutralization" in (
        acidic_payload["ranked_trains"][0]["pollutant_gap_breakdown"][0]["severity"]
    )


def test_irrigation_ec_alias_uses_stored_conductivity_target() -> None:
    """EC aliases should match the stored irrigation conductivity standard."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "irrigation",
            "selected_parameters": ["ec"],
            "measured_observations": [
                {"parameter": "ec", "value": 4200, "unit": "us_cm"},
            ],
            "context": {"workflow_mode": "manual_measured_water_quality"},
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    gap = payload["contaminant_gaps"][0]
    assert gap["parameter"] == "ec"
    assert gap["status"] == "exceeds_standard"
    assert gap["limit_high"] == 2250.0
    assert gap["standard_unit"] == "umho_cm"
    coverage = payload["parameter_coverage"][0]
    assert coverage["target_available"] is True
    assert coverage["target_status"] == "exceeds_selected_target"
    assert coverage["scoring_role"] == "used_in_scoring"


def test_drinking_bod_missing_target_remains_supporting_context() -> None:
    """Stored drinking standards do not contain a BOD target; do not invent one."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "drinking",
            "selected_parameters": ["bod"],
            "measured_observations": [
                {"parameter": "bod", "value": 8, "unit": "mg_l"},
            ],
            "context": {"workflow_mode": "manual_measured_water_quality"},
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    gap = payload["contaminant_gaps"][0]
    assert gap["status"] == "standard_missing"
    coverage = payload["parameter_coverage"][0]
    assert coverage["target_available"] is False
    assert coverage["target_status"] == "supporting_context_no_stored_target"
    assert coverage["scoring_role"] == "supporting_context"
    assert coverage["coverage_label"] == "Used as supporting context."


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


def test_indirasagar_low_infiltration_cautions_on_site_disposal() -> None:
    """APP_RULE_023 should reach train ranking through canonical site context."""

    result = _rank(
        region_id=27,
        context={"pollution_source_type": "domestic"},
    )

    on_site = next(
        row for row in result["ranked_trains"] if row["name"] == "On-site disposal"
    )
    triggered_ids = {
        rule["rule_id"]
        for rule in on_site["applicability_result"]["triggered_rules"]
    }

    assert on_site["applicability_result"]["status"] == "conditional"
    assert "APP_RULE_023" in triggered_ids
    assert any("low-infiltration" in caveat for caveat in on_site["caveats"])


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
    agricultural = _rank(
        contaminant_gaps=[
            {
                "parameter": "total_phosphorus",
                "direction": "reduce",
                "required_removal_percent": 80,
                "observed_value": 20,
            }
        ],
        context={
            "pollution_source_type": "high_agriculture_only_no_water_data",
            "intervention_position": "off_channel_or_stp_polishing",
        },
    )

    domestic_top = domestic["ranked_trains"][0]["name"]
    industrial_top = industrial["ranked_trains"][0]["name"]
    agricultural_top = agricultural["ranked_trains"][0]["name"]
    assert len({domestic_top, industrial_top, agricultural_top}) >= 2
    assert agricultural_top != "VF nitrifying hybrid"


def test_mandleshwar_industrial_acidic_mainstem_requires_expert_review() -> None:
    """Industrial acidic wastewater on a high-order river must stay off-channel."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "discharge_inland",
            "region_id": 35,
            "station": "Mandleshwar",
            "selected_parameters": ["cod", "ph"],
            "measured_observations": [
                {"parameter": "cod", "value": 1000, "unit": "mg_l"},
                {"parameter": "ph", "value": 3, "unit": "ph_units"},
            ],
            "context": {
                "workflow_mode": "manual_measured_water_quality",
                "pollution_source_type": "industrial_or_mixed_industrial",
                "intervention_position": "in_channel",
                "stream_order": 7,
            },
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["design_readiness"]["level"] == "needs_expert_review"
    guidance = " ".join(
        [
            *payload["design_readiness"]["required_next_steps"],
            *[
                text
                for train in payload["ranked_trains"][:3]
                for text in train["source_location_guidance"]
            ],
        ]
    ).lower()
    assert "etp/cetp" in guidance
    assert "neutralization" in guidance
    assert "off-channel" in guidance
    assert "in-channel" in guidance

    top_names = [row["name"].lower() for row in payload["ranked_trains"][:3]]
    assert all("green roof" not in name for name in top_names)
    assert all("green wall" not in name for name in top_names)
    assert all("rain garden" not in name for name in top_names)

    blocked_component_terms = (
        "green roof",
        "green wall",
        "rain garden",
        "bioswale",
        "filter strip",
    )
    component_names = [
        row["name"].lower() for row in payload["component_recommendations"]
    ]
    assert all(
        term not in name
        for name in component_names
        for term in blocked_component_terms
    )
    filtered = payload["filtered_components"]
    filtered_names = [row["name"].lower() for row in filtered]
    assert any("green roof" in name for name in filtered_names)
    filtered_reasons = " ".join(
        reason for row in filtered for reason in row["reasons"]
    ).lower()
    assert "etp/cetp" in filtered_reasons
    assert "neutralization" in filtered_reasons
    assert "off-channel" in filtered_reasons


def test_drinking_domestic_strict_use_requires_expert_review() -> None:
    """Drinking/strict-use screening must not look design-ready for wastewater."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "drinking",
            "region_id": 27,
            "selected_parameters": ["ammonia_n", "turbidity", "ph"],
            "measured_observations": [
                {"parameter": "ammonia_n", "value": 200, "unit": "mg_l"},
                {"parameter": "turbidity", "value": 5, "unit": "ntu"},
                {"parameter": "ph", "value": 7.4, "unit": "ph_units"},
            ],
            "context": {
                "workflow_mode": "manual_measured_water_quality",
                "pollution_source_type": "domestic_sewage",
            },
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["design_readiness"]["level"] == "needs_expert_review"
    assert payload["design_readiness"]["short_label"] == "Expert review needed"
    assert any("NbS alone" in warning for warning in payload["warnings"])
    assert any("advanced treatment" in warning.lower() for warning in payload["warnings"])
    assert payload["validation_notes"]["strict_use"]["selected_use_case_badge"]
    assert "NH4-N" in payload["validation_notes"]["strict_use"]["blockers"]
    assert "turbidity" in payload["validation_notes"]["strict_use"]["blockers"]


def test_drinking_strict_use_filters_unsuitable_support_components() -> None:
    """Strict-use wastewater output must not promote source-control components."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "drinking",
            "selected_parameters": ["ammonia_n"],
            "measured_observations": [
                {"parameter": "ammonia_n", "value": 200, "unit": "mg_l"},
            ],
            "context": {
                "workflow_mode": "manual_measured_water_quality",
                "pollution_source_type": "domestic_sewage",
            },
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    blocked_names = " ".join(
        str(row.get("name", "")).lower()
        for row in payload["filtered_components"]
        if row.get("status") == "not_suitable_for_drinking_strict_use"
    )
    assert "rain" in blocked_names or "filter" in blocked_names or "green" in blocked_names
    assert all(
        row.get("standalone_suitability") == "only_as_part_of_train"
        for row in payload["component_recommendations"]
    )


def test_irrigation_ec_exceedance_returns_salinity_warning() -> None:
    """Irrigation EC exceedance should disclose salinity limits of ordinary NbS."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "irrigation",
            "selected_parameters": ["ec"],
            "measured_observations": [
                {"parameter": "ec", "value": 4200, "unit": "us_cm"},
            ],
            "context": {"workflow_mode": "manual_measured_water_quality"},
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["validation_notes"]["salinity"]["active"] is True
    assert "Ordinary NbS treatment may not reliably remove dissolved salts" in (
        payload["validation_notes"]["salinity"]["warning"]
    )
    assert any("salinity" in warning.lower() for warning in payload["warnings"])


def test_domestic_endpoint_uses_municipal_profile_fallback() -> None:
    """Recommendation route should use municipal profile when domestic data is absent."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "irrigation",
            "selected_parameters": ["ammonia_n", "total_phosphorus"],
            "context": {
                "workflow_mode": "pollution_source_screening",
                "pollution_source_type": "domestic_sewage",
            },
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    summary = payload["input_summary"]
    assert summary["selected_source_type"] == "water_type_profile"
    assert MUNICIPAL_FALLBACK_NOTE in summary["data_quality_notes"]
    assert MUNICIPAL_FALLBACK_NOTE in payload["warnings"]
    rows = {row["parameter"]: row for row in summary["data_used"]}
    assert rows["ammonia_n"]["water_type"] == MUNICIPAL_PROFILE_NAME
    assert rows["ammonia_n"]["value_low"] == 25
    assert rows["ammonia_n"]["value_high"] == 50
    assert rows["total_phosphorus"]["value_low"] == 5
    assert rows["total_phosphorus"]["value_high"] == 15
    assert "Blackwater" not in rows["ammonia_n"]["water_type"]
    assert payload["ranked_trains"]


def test_irrigation_missing_standards_are_aggregated_supporting_context() -> None:
    """Missing selected-use-case standards should be grouped without failing."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "irrigation",
            "region_id": 27,
            "selected_parameters": ["cod", "ammonia_n", "total_phosphorus", "bod"],
            "measured_observations": [
                {"parameter": "cod", "value": 500, "unit": "mg_l"},
                {"parameter": "ammonia_n", "value": 200, "unit": "mg_l"},
                {"parameter": "total_phosphorus", "value": 40, "unit": "mg_l"},
                {"parameter": "bod", "value": 250, "unit": "mg_l"},
            ],
            "context": {
                "workflow_mode": "manual_measured_water_quality",
                "pollution_source_type": "domestic_sewage",
            },
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    coverage = payload["validation_notes"]["standards_coverage"]
    assert coverage["active"] is True
    assert {"COD", "NH4-N", "TP"}.issubset(set(coverage["parameters"]))
    assert "supporting context" in coverage["note"]


def test_match_vs_suitability_note_when_top_has_evidence_gap_and_lower_pass() -> None:
    """Keep ranking order but explain when confirmed suitability differs."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "irrigation",
            "region_id": 27,
            "selected_parameters": [
                "bod",
                "cod",
                "tss",
                "ammonia_n",
                "total_phosphorus",
                "ph",
            ],
            "measured_observations": [
                {"parameter": "bod", "value": 250, "unit": "mg_l"},
                {"parameter": "cod", "value": 500, "unit": "mg_l"},
                {"parameter": "tss", "value": 275, "unit": "mg_l"},
                {"parameter": "ammonia_n", "value": 200, "unit": "mg_l"},
                {"parameter": "total_phosphorus", "value": 40, "unit": "mg_l"},
                {"parameter": "ph", "value": 7.4, "unit": "ph_units"},
            ],
            "context": {
                "workflow_mode": "manual_measured_water_quality",
                "pollution_source_type": "domestic_sewage",
            },
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["ranked_trains"][0]["name"] == "WSP Train (pond series)"
    note = payload["validation_notes"]["match_vs_suitability"]["note"]
    assert note
    assert "highest confirmed-suitability option" in note.lower()


def test_soil_filter_conditional_caution_remains_visible() -> None:
    """APP_RULE_023 should stay visible as a validation caution."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "discharge_inland",
            "region_id": 27,
            "selected_parameters": ["bod"],
            "measured_observations": [
                {"parameter": "bod", "value": 250, "unit": "mg_l"},
            ],
            "context": {
                "workflow_mode": "manual_measured_water_quality",
                "pollution_source_type": "domestic_sewage",
            },
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert any(
        "soil/infiltration" in caution
        for caution in payload["validation_notes"]["soil_filter_cautions"]
    )
    on_site = next(row for row in payload["ranked_trains"] if row["name"] == "On-site disposal")
    assert any(
        rule["rule_id"] == "APP_RULE_023"
        for rule in on_site["applicability_result"]["triggered_rules"]
    )


def test_recommendation_route_requires_target_use_case() -> None:
    """Missing target use case should fail before recommendation assembly."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "selected_parameters": ["bod"],
            "measured_observations": [
                {"parameter": "bod", "value": 80, "unit": "mg_l"},
            ],
            "context": {"workflow_mode": "manual_measured_water_quality"},
        },
    )

    assert response.status_code == 422
    assert "use_case" in response.text


def test_recommendation_route_rejects_unknown_target_use_case() -> None:
    """Unknown target use cases must not silently fall back to discharge."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "unknown_target",
            "selected_parameters": ["bod"],
            "measured_observations": [
                {"parameter": "bod", "value": 80, "unit": "mg_l"},
            ],
            "context": {"workflow_mode": "manual_measured_water_quality"},
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert "Unknown use_case" in " ".join(payload["detail"]["errors"])
    assert {"discharge_inland", "irrigation", "drinking"}.issubset(
        set(payload["detail"]["available_use_cases"])
    )


def test_recommendation_route_accepts_explicit_active_target_use_cases() -> None:
    """Frontend target choices should all reach the recommendation workflow."""

    client = TestClient(app)
    for use_case in ("discharge_inland", "irrigation", "drinking"):
        response = client.post(
            "/api/v1/recommend",
            json={
                "use_case": use_case,
                "selected_parameters": ["bod", "ph"],
                "measured_observations": [
                    {"parameter": "bod", "value": 80, "unit": "mg_l"},
                    {"parameter": "ph", "value": 7.2, "unit": "ph_units"},
                ],
                "context": {"workflow_mode": "manual_measured_water_quality"},
            },
        )

        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["use_case"] == use_case
        assert payload["parameter_coverage"][0]["selected_use_case"] == use_case


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


def test_ranked_train_exposes_explainable_criteria_without_c5() -> None:
    result = _rank()
    top = result["ranked_trains"][0]
    explanation = top["criteria_explanation"]

    assert explanation
    assert {item["criterion_code"] for item in explanation}.issubset(
        {"C1", "C2", "C3", "C4", "C6", "C7", "C8"}
    )
    assert "C5" not in {item["criterion_code"] for item in explanation}
    assert all("weighted_contribution" in item for item in explanation)
    assert all("score" in item for item in explanation)


def test_train_pathway_preserves_step_order() -> None:
    result = _rank()
    train = next(row for row in result["ranked_trains"] if row["train_id"] == 3)
    pathway = train["train_pathway"]

    assert pathway
    assert [row["step_order"] for row in pathway] == sorted(
        row["step_order"] for row in pathway
    )
    assert pathway[0]["component_name"]
    assert all("nbs_id" in row for row in pathway)


def test_train_pathway_missing_steps_is_empty_not_invented() -> None:
    result = _rank()
    sequence_by_id = {
        int(row["train_id"]): row["train_pathway"]
        for row in result["ranked_trains"]
    }

    assert all(isinstance(pathway, list) for pathway in sequence_by_id.values())


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


def test_csv_upload_normalizes_conductivity_aliases_and_units() -> None:
    response = _upload_csv(
        "parameter,value,unit\nEC,4200,uS/cm\n"
        "Electrical conductivity,2100,micromho/cm\n"
        "specific conductance,1800,umho/cm\n"
    )

    assert response.status_code == 200, response.text
    rows = response.json()["observations_used"]
    assert [row["parameter"] for row in rows] == ["ec", "ec", "ec"]
    assert {row["unit"] for row in rows} == {"umho_cm"}


def test_csv_upload_normalizes_common_phosphorus_aliases() -> None:
    aliases = [
        "phosphate-P",
        "phosphate P",
        "phosphate phosphorus",
        "orthophosphate",
        "ortho-phosphate",
        "PO4 P",
        "PO4-P",
        "total phosphorus",
        "TP",
        "phosphorus",
    ]
    response = _upload_csv(
        "parameter,value,unit\n"
        + "\n".join(f"{alias},2,mg/L" for alias in aliases)
        + "\n"
    )

    assert response.status_code == 200, response.text
    rows = response.json()["observations_used"]
    assert len(rows) == len(aliases)
    assert {row["parameter"] for row in rows} == {"phosphate_p"}


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


def _recommend_components(
    *,
    context: dict,
    observations: list[dict] | None = None,
) -> dict:
    values = observations or []
    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "discharge_inland",
            "measured_observations": values,
            "selected_parameters": [row["parameter"] for row in values],
            "context": context,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_component_layer_is_separate_and_train_result_remains_primary() -> None:
    payload = _recommend_components(
        context={
            "workflow_mode": "manual_measured_water_quality",
            "pollution_source_type": "domestic_sewage",
            "intervention_position": "off_channel_or_stp_polishing",
        },
        observations=[
            {"parameter": "bod", "value": 80, "unit": "mg_l"},
            {"parameter": "cod", "value": 200, "unit": "mg_l"},
            {"parameter": "tss", "value": 120, "unit": "mg_l"},
            {"parameter": "ph", "value": 7.2},
        ],
    )

    assert payload["ranked_trains"]
    assert payload["component_recommendations"]
    assert payload["component_recommendation_method"] == "a0_screened_component_topsis"
    assert all(
        row["train_recommendation_remains_primary"]
        for row in payload["component_recommendations"]
    )
    assert all(
        row["standalone_suitability"] != "can_be_standalone"
        for row in payload["component_recommendations"]
    )


def test_industrial_components_are_polishing_only_after_pretreatment() -> None:
    payload = _recommend_components(
        context={
            "workflow_mode": "manual_measured_water_quality",
            "pollution_source_type": "industrial_or_mixed_industrial",
            "intervention_position": "standalone_primary_treatment",
        },
        observations=[
            {"parameter": "cod", "value": 1000, "unit": "mg_l"},
            {"parameter": "ph", "value": 3},
        ],
    )
    components = payload["component_recommendations"]

    assert components
    assert all(row["role"] == "polishing_or_buffer" for row in components)
    assert all(
        row["standalone_suitability"] == "only_as_part_of_train"
        for row in components
    )
    guidance = " ".join(
        text
        for row in components
        for text in [row["standalone_guidance"], *row["key_constraints"]]
    ).lower()
    assert "etp/cetp" in guidance
    assert "neutralization" in guidance


def test_mainstem_component_screen_blocks_in_channel_framing() -> None:
    payload = _recommend_components(
        context={
            "workflow_mode": "site_context_only",
            "pollution_source_type": "domestic_sewage",
            "intervention_position": "in_channel",
            "stream_order": 6,
        },
    )

    assert payload["component_recommendations"]
    assert payload["filtered_components"]
    assert all(
        not any(
            "in-channel" in suitable.lower()
            for suitable in row["where_suitable"]
        )
        for row in payload["component_recommendations"]
    )
    assert all(
        any("in-channel" in value.lower() for value in row["where_not_suitable"])
        for row in payload["component_recommendations"]
    )


def test_agricultural_context_prioritizes_source_control_components() -> None:
    payload = _recommend_components(
        context={
            "workflow_mode": "pollution_source_screening",
            "pollution_source_type": "high_agriculture_only_no_water_data",
            "intervention_position": "off_channel_or_stp_polishing",
        },
    )
    top = payload["component_recommendations"][:3]

    assert len(top) == 3
    assert all(row["role"] == "source_control" for row in top)
    assert all(
        row["standalone_suitability"] == "can_be_standalone_source_control"
        for row in top
    )
    assert all(
        "not standalone treatment" in row["standalone_guidance"].lower()
        for row in top
    )


def test_component_plant_links_exclude_invasive_species() -> None:
    payload = _recommend_components(
        context={
            "workflow_mode": "pollution_source_screening",
            "pollution_source_type": "high_agriculture_only_no_water_data",
        },
    )
    plants = [
        plant
        for row in payload["component_recommendations"]
        for plant in row["plants"]
    ]

    assert plants
    assert all(plant.get("invasive") in {0, None} for plant in plants)
    assert all(
        "invasive" not in str(plant.get("native_status", "")).lower()
        for plant in plants
    )

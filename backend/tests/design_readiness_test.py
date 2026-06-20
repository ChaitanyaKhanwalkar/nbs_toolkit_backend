"""Acceptance tests for location intelligence and design-readiness rules."""

from fastapi.testclient import TestClient

from app.engines.design_readiness import DesignReadinessEngine
from app.main import app
from app.services.location_context_service import build_location_context


def _assess(
    parameters: dict[str, float] | None = None,
    *,
    context: dict | None = None,
    location: dict | None = None,
):
    """Run the pure readiness engine with compact test inputs."""

    parameters = parameters or {}
    context = context or {}
    location = location or {
        "context_flags": {
            "mainstem_or_high_order": False,
            "off_channel_required": False,
            "industrial_pretreatment_required": False,
            "site_context_incomplete": True,
        }
    }
    return DesignReadinessEngine().assess(
        measured_observations=[
            {"parameter": key, "value": value} for key, value in parameters.items()
        ],
        context=context,
        location_context=location,
        ranked_trains=[{"name": "Test train", "confidence_label": "medium"}],
    )


def test_complete_core_panel_is_at_least_planning_level() -> None:
    """BOD/COD/TSS/pH should support comparison, but not imply design readiness."""

    result = _assess({"bod": 80, "cod": 200, "tss": 120, "ph": 7.2})
    assert result["level"] == "planning_level_result"
    assert result["short_label"] == "Ready for planning"
    assert "Flow rate / design flow" in result["missing_inputs"]


def test_one_parameter_input_remains_early_screening() -> None:
    """One usable result cannot become planning or design ready."""

    result = _assess({"bod": 80})
    assert result["level"] == "early_screening_only"
    assert result["expert_review_required"] is False


def test_industrial_acidic_input_requires_expert_review() -> None:
    """Industrial pH 3 must retain ETP/CETP and neutralization safeguards."""

    result = _assess(
        {"cod": 1000, "ph": 3},
        context={"pollution_source_type": "industrial_or_mixed_industrial"},
    )
    assert result["level"] == "needs_expert_review"
    assert result["expert_review_required"] is True
    reasons = " ".join(result["reasons"]).lower()
    assert "etp/cetp" in reasons
    assert "neutralization" in reasons


def test_high_order_context_requires_off_channel_expert_review() -> None:
    """Mainstem/high-order cases must not look ready for in-channel design."""

    result = _assess(
        {"bod": 80, "cod": 200, "tss": 120, "ph": 7.2},
        location={
            "context_flags": {
                "mainstem_or_high_order": True,
                "off_channel_required": True,
                "industrial_pretreatment_required": False,
            }
        },
    )
    assert result["level"] == "needs_expert_review"
    assert any("off-channel" in step.lower() for step in result["required_next_steps"])


def test_site_context_only_is_not_design_ready() -> None:
    """No measured values must remain early screening regardless of ranking."""

    result = _assess(context={"workflow_mode": "site_context_only"})
    assert result["level"] == "early_screening_only"
    assert result["short_label"] == "Needs field data"


def test_preliminary_design_requires_explicit_design_and_site_inputs() -> None:
    """Preliminary readiness is reachable only through supplied design context."""

    context = {
        "design_flow": 1,
        "peak_flow": 1,
        "available_land": 1,
        "groundwater_depth": 1,
        "flood_risk": "verified",
        "inlet_outlet_levels": "surveyed",
        "om_owner_capacity": "confirmed",
        "site_slope": 1,
        "soil_infiltration": "verified",
    }
    result = _assess(
        {
            "bod": 80,
            "cod": 200,
            "tss": 120,
            "ph": 7.2,
            "ammonia_n": 8,
            "do": 5,
            "faecal_coliform": 100,
        },
        context=context,
        location={
            "context_flags": {
                "mainstem_or_high_order": False,
                "off_channel_required": False,
                "industrial_pretreatment_required": False,
                "site_context_incomplete": False,
            }
        },
    )
    assert result["level"] == "preliminary_design_ready"
    assert result["expert_review_required"] is True


def test_location_context_never_invents_coordinates() -> None:
    """A station label without a verified profile must not create a map point."""

    result = build_location_context(
        profile=None,
        region_id=None,
        station="Reported station",
        context={"workflow_mode": "site_context_only"},
    )
    assert result["station"] == "Reported station"
    assert result["coordinates_available"] is False
    assert result["latitude"] is None
    assert result["longitude"] is None


def test_low_confidence_blocks_preliminary_design_readiness() -> None:
    """Complete-looking inputs cannot bypass an existing low-confidence label."""

    context = {
        "design_flow": 1,
        "peak_flow": 1,
        "available_land": 1,
        "groundwater_depth": 1,
        "flood_risk": "verified",
        "inlet_outlet_levels": "surveyed",
        "om_owner_capacity": "confirmed",
        "site_slope": 1,
        "soil_infiltration": "verified",
    }
    result = DesignReadinessEngine().assess(
        measured_observations=[
            {"parameter": key, "value": value}
            for key, value in {
                "bod": 80,
                "cod": 200,
                "tss": 120,
                "ph": 7.2,
                "ammonia_n": 8,
                "do": 5,
                "faecal_coliform": 100,
            }.items()
        ],
        context=context,
        location_context={
            "context_flags": {
                "mainstem_or_high_order": False,
                "site_context_incomplete": False,
            }
        },
        ranked_trains=[{"confidence_label": "low"}],
    )
    assert result["level"] == "planning_level_result"


def test_location_context_exposes_verified_profile_and_safety_flags() -> None:
    """Stored profile values and request safety context should remain distinct."""

    result = build_location_context(
        profile={
            "region": {
                "station": "Bharuch",
                "river": "Narmada",
                "district": "Bharuch",
                "lat": 21.7,
                "lon": 72.9,
                "soil_type": "stored soil class",
            },
            "basin": {"basin": "Narmada", "sub_basin": None},
            "site_attributes": {"stream_order": 6, "slope_mean": 2.1},
            "site_stream_attributes": [],
        },
        region_id=20,
        station="Bharuch",
        context={
            "intervention_position": "in_channel",
            "pollution_source_type": "domestic_sewage",
        },
    )
    assert result["coordinates_available"] is True
    assert result["context_flags"]["mainstem_or_high_order"] is True
    assert result["context_flags"]["off_channel_required"] is True
    assert any("Do not build" in note for note in result["context_notes"])


def test_recommendation_api_returns_location_and_readiness_objects() -> None:
    """The public response should carry both new objects through its schema."""

    response = TestClient(app).post(
        "/api/v1/recommend",
        json={
            "use_case": "discharge_inland",
            "station": "Test station",
            "selected_parameters": ["bod", "cod", "tss", "ph"],
            "measured_observations": [
                {"parameter": "bod", "value": 80, "unit": "mg_l"},
                {"parameter": "cod", "value": 200, "unit": "mg_l"},
                {"parameter": "tss", "value": 120, "unit": "mg_l"},
                {"parameter": "ph", "value": 7.2, "unit": "ph_units"},
            ],
            "context": {
                "workflow_mode": "uploaded_water_quality",
                "pollution_source_type": "domestic_sewage",
                "intervention_position": "off_channel_or_stp_polishing",
            },
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["location_context"]["station"] == "Test station"
    assert payload["location_context"]["coordinates_available"] is False
    assert payload["design_readiness"]["level"] == "planning_level_result"
    assert payload["design_readiness"]["input_checklist"]
    assert payload["sizing_estimates"]
    assert payload["scenario_comparison"]["options"]

"""Smoke tests for Scientific Engine Step B.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\water_input_assembly_test.py

These tests use a tiny fake water service. They do not connect to Azure, do not
need production data, and do not calculate exceedance or recommendations.
"""

from app.engines import InputNormalizationEngine, WaterInputAssemblyEngine
from app.engines.water_input_assembly import (
    BLACKWATER_PROFILE_NAME,
    MUNICIPAL_FALLBACK_NOTE,
    MUNICIPAL_PROFILE_NAME,
)


class FakeWaterDataService:
    """Small service-shaped test double for raw water observations."""

    def __init__(
        self,
        station_rows: dict[str, list[dict[str, object]]] | None = None,
        basin_rows: dict[int, list[dict[str, object]]] | None = None,
        profile_rows: dict[str, list[dict[str, object]]] | None = None,
    ) -> None:
        self.station_rows = station_rows or {}
        self.basin_rows = basin_rows or {}
        self.profile_rows = profile_rows or {}

    def get_observations_by_station(self, station: str) -> list[dict[str, object]]:
        """Return fake station observations."""

        return list(self.station_rows.get(station, []))

    def get_observations_by_basin(self, basin_id: int) -> list[dict[str, object]]:
        """Return fake basin observations."""

        return list(self.basin_rows.get(basin_id, []))

    def get_observations_for_parameters(
        self,
        station: str,
        parameters: list[str],
    ) -> dict[str, list[dict[str, object]]]:
        """Return fake station observations grouped by selected parameters."""

        rows = self.station_rows.get(station, [])
        return {
            parameter: [
                row for row in rows if row.get("parameter") == parameter
            ]
            for parameter in parameters
        }

    def get_water_type_profile(self, water_type: str) -> list[dict[str, object]]:
        """Return fake profile rows for one exact water type."""

        return list(self.profile_rows.get(water_type, []))


def make_context(**fields: object):
    """Normalize raw fields with Step A before Step B assembly."""

    defaults = {"use_case": "surface_discharge"}
    defaults.update(fields)
    return InputNormalizationEngine().normalize(**defaults)


def assert_user_measured_wins_over_station_data() -> None:
    """User measured observations always have first priority."""

    context = make_context(
        station="Station A",
        measured_observations=[
            {"parameter": "BOD", "value": 12.0, "unit": "mg/L", "source_id": 901},
        ],
    )
    service = FakeWaterDataService(
        station_rows={
            "Station A": [{"parameter": "pH", "value_mean": 7.2, "source_id": 4}]
        }
    )

    bundle = WaterInputAssemblyEngine(service).assemble(context)

    assert bundle.selected_source_type == "user_measured"
    assert bundle.observation_count == 1
    assert bundle.observations[0]["parameter"] == "BOD"
    assert bundle.source_ids == [901]


def assert_station_data_used_without_user_data() -> None:
    """Station data is used when user measured data is absent."""

    context = make_context(station="Station A")
    service = FakeWaterDataService(
        station_rows={
            "Station A": [{"parameter": "pH", "value_mean": 7.2, "source_id": 4}]
        }
    )

    bundle = WaterInputAssemblyEngine(service).assemble(context)

    assert bundle.selected_source_type == "station_observations"
    assert bundle.observation_count == 1
    assert bundle.source_ids == [4]


def assert_basin_data_used_after_user_and_station_absent() -> None:
    """Basin data is used only after user and station data are unavailable."""

    context = make_context(station="Missing Station", basin_id=2)
    service = FakeWaterDataService(
        station_rows={"Other Station": [{"parameter": "pH", "value_mean": 7.1}]},
        basin_rows={2: [{"parameter": "BOD", "value_mean": 8.0, "source_id": 7}]},
    )

    bundle = WaterInputAssemblyEngine(service).assemble(context)

    assert bundle.selected_source_type == "basin_observations"
    assert bundle.observation_count == 1
    assert any("No station observations" in warning for warning in bundle.warnings)
    assert bundle.source_ids == [7]


def assert_missing_returned_safely() -> None:
    """Missing water data should return a safe bundle, not crash."""

    context = make_context()

    bundle = WaterInputAssemblyEngine(FakeWaterDataService()).assemble(context)

    assert bundle.selected_source_type == "missing"
    assert bundle.observation_count == 0
    assert "water_observations" in bundle.missing_inputs
    assert any("water_type profile fallback" in note for note in bundle.data_quality_notes)


def assert_selected_parameters_filtering() -> None:
    """Selected parameters should filter assembled observations."""

    context = make_context(
        station="Station A",
        selected_parameters=[" BOD "],
    )
    service = FakeWaterDataService(
        station_rows={
            "Station A": [
                {"parameter": "BOD", "value_mean": 12.0, "source_id": 1},
                {"parameter": "pH", "value_mean": 7.0, "source_id": 1},
            ]
        }
    )

    bundle = WaterInputAssemblyEngine(service).assemble(context)

    assert bundle.selected_source_type == "station_observations"
    assert bundle.observation_count == 1
    assert bundle.selected_parameters == ["BOD"]
    assert bundle.observations[0]["parameter"] == "BOD"


def assert_nonexistent_station_does_not_crash() -> None:
    """A station with no rows should return missing safely."""

    context = make_context(station="Not A Station")

    bundle = WaterInputAssemblyEngine(FakeWaterDataService()).assemble(context)

    assert bundle.selected_source_type == "missing"
    assert any("No station observations" in warning for warning in bundle.warnings)


def assert_no_future_scoring_fields() -> None:
    """Step B output must not contain future recommendation/scoring fields."""

    forbidden_fields = {
        "recommendations",
        "recommendation_score",
        "match_score",
        "confidence_score",
        "confidence_label",
        "ranking",
        "rank",
        "topsis_score",
        "ahp_weight",
        "criteria_weights",
        "exceedance",
        "exceedance_ratio",
        "treatment_need",
        "health_risk",
    }

    context = make_context(station="Station A")
    service = FakeWaterDataService(
        station_rows={"Station A": [{"parameter": "pH", "value_mean": 7.0}]}
    )
    payload = WaterInputAssemblyEngine(service).assemble(context).to_dict()

    found = forbidden_fields.intersection(payload)
    assert not found, f"Step B leaked future scoring fields: {sorted(found)}"


def _profile_rows(water_type: str) -> list[dict[str, object]]:
    """Return compact fake municipal/blackwater profile rows."""

    if water_type == MUNICIPAL_PROFILE_NAME:
        return [
            {
                "id": 1,
                "water_type": water_type,
                "parameter": "ammonia_n",
                "value_low": 25,
                "value_high": 50,
                "unit": "mg_l",
                "source_id": 109,
            },
            {
                "id": 2,
                "water_type": water_type,
                "parameter": "total_phosphorus",
                "value_low": 5,
                "value_high": 15,
                "unit": "mg_l",
                "source_id": 109,
            },
        ]
    return [
        {
            "id": 3,
            "water_type": water_type,
            "parameter": "ammonia_n",
            "value_low": 100,
            "value_high": 300,
            "unit": "mg_l",
            "source_id": 9,
        },
        {
            "id": 4,
            "water_type": water_type,
            "parameter": "total_phosphorus",
            "value_low": 20,
            "value_high": 60,
            "unit": "mg_l",
            "source_id": 9,
        },
    ]


def _profile_service() -> FakeWaterDataService:
    """Return fake service with exact municipal and blackwater profiles."""

    return FakeWaterDataService(
        profile_rows={
            MUNICIPAL_PROFILE_NAME: _profile_rows(MUNICIPAL_PROFILE_NAME),
            BLACKWATER_PROFILE_NAME: _profile_rows(BLACKWATER_PROFILE_NAME),
        },
    )


def test_domestic_sewage_selects_combined_municipal_profile() -> None:
    """Domestic sewage fallback must use the municipal profile, not blackwater."""

    context = make_context(context={"pollution_source_type": "domestic_sewage"})

    bundle = WaterInputAssemblyEngine(_profile_service()).assemble(context)

    assert bundle.selected_source_type == "water_type_profile"
    assert {row["water_type"] for row in bundle.observations} == {
        MUNICIPAL_PROFILE_NAME
    }
    assert MUNICIPAL_FALLBACK_NOTE in bundle.warnings


def test_municipal_sewage_selects_combined_municipal_profile() -> None:
    """Municipal wording should map to the combined municipal profile."""

    context = make_context(context={"pollution_source_type": "municipal_sewage"})

    bundle = WaterInputAssemblyEngine(_profile_service()).assemble(context)

    assert bundle.selected_source_type == "water_type_profile"
    assert {row["water_type"] for row in bundle.observations} == {
        MUNICIPAL_PROFILE_NAME
    }


def test_explicit_blackwater_selects_concentrated_blackwater_profile() -> None:
    """Blackwater must be used only when blackwater is explicit."""

    context = make_context(context={"water_type": "toilet blackwater"})

    bundle = WaterInputAssemblyEngine(_profile_service()).assemble(context)

    assert bundle.selected_source_type == "water_type_profile"
    assert {row["water_type"] for row in bundle.observations} == {
        BLACKWATER_PROFILE_NAME
    }
    assert MUNICIPAL_FALLBACK_NOTE not in bundle.warnings


def test_domestic_sewage_does_not_match_blackwater_by_substring() -> None:
    """Ordinary domestic context must not select the concentrated profile."""

    context = make_context(context={"influent_basis": "domestic sewage default"})

    bundle = WaterInputAssemblyEngine(_profile_service()).assemble(context)

    assert all(
        row["water_type"] != BLACKWATER_PROFILE_NAME for row in bundle.observations
    )


def test_municipal_profile_keeps_ammonia_and_phosphorus_ranges() -> None:
    """Fallback observations should preserve profile ranges for review."""

    context = make_context(context={"source_type": "municipal wastewater"})

    bundle = WaterInputAssemblyEngine(_profile_service()).assemble(context)
    rows = {row["parameter"]: row for row in bundle.observations}

    assert rows["ammonia_n"]["value_low"] == 25
    assert rows["ammonia_n"]["value_high"] == 50
    assert rows["ammonia_n"]["value"] == 37.5
    assert rows["total_phosphorus"]["value_low"] == 5
    assert rows["total_phosphorus"]["value_high"] == 15
    assert rows["total_phosphorus"]["value"] == 10


def test_user_measured_parameters_override_profile_fallback() -> None:
    """User measured observations remain higher priority than profiles."""

    context = make_context(
        context={"pollution_source_type": "domestic_sewage"},
        measured_observations=[
            {"parameter": "ammonia_n", "value": 8, "unit": "mg_l"},
        ],
    )

    bundle = WaterInputAssemblyEngine(_profile_service()).assemble(context)

    assert bundle.selected_source_type == "user_measured"
    assert bundle.observations == [
        {
            "parameter": "ammonia_n",
            "parameter_match_key": "ammonia_n",
            "value": 8.0,
            "unit": "mg_l",
            "source": "user_measured",
            "original": {"parameter": "ammonia_n", "value": 8, "unit": "mg_l"},
        }
    ]


def main() -> None:
    """Run all Step B checks."""

    assert_user_measured_wins_over_station_data()
    assert_station_data_used_without_user_data()
    assert_basin_data_used_after_user_and_station_absent()
    assert_missing_returned_safely()
    assert_selected_parameters_filtering()
    assert_nonexistent_station_does_not_crash()
    assert_no_future_scoring_fields()
    print("water input assembly checks ok: Step B only")


if __name__ == "__main__":
    main()

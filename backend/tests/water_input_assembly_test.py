"""Smoke tests for Scientific Engine Step B.

Run from the backend folder:

    set PYTHONPATH=%CD%
    python tests\\water_input_assembly_test.py

These tests use a tiny fake water service. They do not connect to Azure, do not
need production data, and do not calculate exceedance or recommendations.
"""

from app.engines import InputNormalizationEngine, WaterInputAssemblyEngine


class FakeWaterDataService:
    """Small service-shaped test double for raw water observations."""

    def __init__(
        self,
        station_rows: dict[str, list[dict[str, object]]] | None = None,
        basin_rows: dict[int, list[dict[str, object]]] | None = None,
    ) -> None:
        self.station_rows = station_rows or {}
        self.basin_rows = basin_rows or {}

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
    assert any("water_type_profiles fallback" in note for note in bundle.data_quality_notes)


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

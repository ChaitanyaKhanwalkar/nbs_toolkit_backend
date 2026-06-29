"""Step B engine for assembling water inputs by source priority.

This module chooses which raw water observations should move forward in the
future recommendation workflow. It does not compare observations with
standards, calculate exceedance, classify treatment needs, score, rank, or
recommend anything.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from app.engines.input_normalization import InputContext, normalize_match_key


SOURCE_PRIORITY = [
    "user_measured",
    "station_observations",
    "basin_observations",
    "water_type_profile",
    "missing",
]

MUNICIPAL_PROFILE_NAME = "Domestic sewage — combined municipal (medium-strong, India)"
BLACKWATER_PROFILE_NAME = "Blackwater (concentrated, not town-scale)"
MUNICIPAL_FALLBACK_NOTE = (
    "Municipal influent fallback used: Domestic sewage — combined municipal "
    "(medium-strong, India). Concentrated blackwater is not used as town-scale "
    "municipal default."
)
MUNICIPAL_FALLBACK_OVERRIDE_NOTE = (
    "No measured influent was supplied; user-measured observations override this "
    "fallback. Concentrated blackwater is not used as town-scale municipal default."
)


@dataclass(slots=True)
class WaterInputBundle:
    """Raw water observation packet selected for later workflow steps."""

    selected_source_type: str
    observations: list[dict[str, Any]]
    observation_count: int
    selected_parameters: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_priority_applied: list[str] = field(default_factory=lambda: list(SOURCE_PRIORITY))
    data_quality_notes: list[str] = field(default_factory=list)
    provenance_notes: list[str] = field(default_factory=list)
    source_id: int | None = None
    source_ids: list[int] = field(default_factory=list)
    station: str | None = None
    basin_id: int | None = None
    use_case: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


class WaterObservationProvider(Protocol):
    """Small service interface needed by the water input assembler."""

    def get_observations_by_station(self, station: str) -> list[dict[str, Any]]:
        """Return raw station observations."""

    def get_observations_by_basin(self, basin_id: int) -> list[dict[str, Any]]:
        """Return raw basin observations."""

    def get_observations_for_parameters(
        self,
        station: str,
        parameters: list[str],
    ) -> dict[str, list[dict[str, Any]]]:
        """Return station observations grouped by selected parameters."""

    def get_water_type_profile(self, water_type: str) -> list[dict[str, Any]]:
        """Return fallback profile rows for one exact water type."""


class WaterInputAssemblyEngine:
    """Select raw water observations using the approved source priority."""

    def __init__(self, water_service: WaterObservationProvider | None = None) -> None:
        self.water_service = water_service

    @classmethod
    def from_session(cls, session: Any) -> "WaterInputAssemblyEngine":
        """Create the engine using the production WaterDataService layer."""

        from app.services import WaterDataService

        return cls(WaterDataService(session))

    def assemble(self, context: InputContext) -> WaterInputBundle:
        """Return a WaterInputBundle selected by source priority."""

        normalized = context.normalized_input
        selected_parameters = _selected_parameter_names(normalized)
        selected_parameter_keys = _selected_parameter_keys(normalized)
        station = normalized.get("station")
        basin_id = normalized.get("basin_id")
        use_case = normalized.get("use_case")
        context_values = _profile_context_values(normalized)
        warnings = list(context.warnings)
        missing_inputs = list(context.missing_inputs)

        user_observations = list(normalized.get("measured_observations") or [])
        if user_observations:
            observations = _filter_observations(user_observations, selected_parameter_keys)
            if selected_parameter_keys and not observations:
                warnings.append(
                    "User measured observations were supplied, but none matched "
                    "selected_parameters. Step B will not fall back to stored data "
                    "because user measured data has highest priority."
                )
            return self._bundle(
                selected_source_type="user_measured",
                observations=observations,
                selected_parameters=selected_parameters,
                missing_inputs=missing_inputs,
                warnings=warnings,
                data_quality_notes=[
                    "Using user measured observations because they have highest priority."
                ],
                provenance_notes=[
                    "User measured observations came from the request; source defaults "
                    "to user_measured unless the observation supplied a source."
                ],
                station=station,
                basin_id=basin_id,
                use_case=use_case,
            )

        if self.water_service is None and (station or basin_id is not None):
            warnings.append(
                "WaterDataService is unavailable, so stored station or basin "
                "observations could not be fetched."
            )

        if station and self.water_service is not None:
            station_observations = self._get_station_observations(
                station,
                selected_parameters,
                selected_parameter_keys,
            )
            if station_observations:
                return self._bundle(
                    selected_source_type="station_observations",
                    observations=station_observations,
                    selected_parameters=selected_parameters,
                    missing_inputs=missing_inputs,
                    warnings=warnings,
                    data_quality_notes=[
                        "Using stored station observations because no user measured "
                        "observations were supplied."
                    ],
                    provenance_notes=[
                        "Stored station observations come from water_observations rows; "
                        "source_id values are preserved where available."
                    ],
                    station=station,
                    basin_id=basin_id,
                    use_case=use_case,
                )
            warnings.append(f"No station observations were found for station '{station}'.")

        if basin_id is not None and self.water_service is not None:
            basin_observations = self.water_service.get_observations_by_basin(basin_id)
            basin_observations = _filter_observations(
                basin_observations,
                selected_parameter_keys,
            )
            if basin_observations:
                return self._bundle(
                    selected_source_type="basin_observations",
                    observations=basin_observations,
                    selected_parameters=selected_parameters,
                    missing_inputs=missing_inputs,
                    warnings=warnings,
                    data_quality_notes=[
                        "Using stored basin observations because user measured and "
                        "station observations were absent or unavailable."
                    ],
                    provenance_notes=[
                        "Stored basin observations come from water_observations rows; "
                        "source_id values are preserved where available."
                    ],
                    station=station,
                    basin_id=basin_id,
                    use_case=use_case,
                )
            warnings.append(f"No basin observations were found for basin_id {basin_id}.")

        profile_name = _select_profile_name(context_values)
        if profile_name and self.water_service is not None:
            profile_rows = self.water_service.get_water_type_profile(profile_name)
            profile_observations = _profile_rows_to_observations(profile_rows)
            profile_observations = _filter_observations(
                profile_observations,
                selected_parameter_keys,
            )
            if profile_observations:
                data_quality_notes = [
                    "Using water_type_profiles fallback because no user measured, "
                    "station, or basin observations were available."
                ]
                if profile_name == MUNICIPAL_PROFILE_NAME:
                    data_quality_notes.append(MUNICIPAL_FALLBACK_NOTE)
                    data_quality_notes.append(MUNICIPAL_FALLBACK_OVERRIDE_NOTE)
                    _append_once(warnings, MUNICIPAL_FALLBACK_NOTE)
                else:
                    data_quality_notes.append(
                        "Explicit blackwater profile selected from request context; "
                        "this profile is not used as the municipal default."
                    )
                return self._bundle(
                    selected_source_type="water_type_profile",
                    observations=profile_observations,
                    selected_parameters=selected_parameters,
                    missing_inputs=missing_inputs,
                    warnings=warnings,
                    data_quality_notes=data_quality_notes,
                    provenance_notes=[
                        "Fallback observations come from active water_type_profiles "
                        f"rows for exact water_type '{profile_name}'."
                    ],
                    station=station,
                    basin_id=basin_id,
                    use_case=use_case,
                )
            warnings.append(
                f"No active water_type_profiles rows were found for '{profile_name}'."
            )

        if not station and basin_id is None:
            _append_once(missing_inputs, "station_or_basin_id")
        _append_once(missing_inputs, "water_observations")
        return self._bundle(
            selected_source_type="missing",
            observations=[],
            selected_parameters=selected_parameters,
            missing_inputs=missing_inputs,
            warnings=warnings,
            data_quality_notes=[
                "No user measured, station, or basin observations were available.",
                "No matching domestic/municipal or explicit blackwater "
                "water_type profile fallback was selected.",
            ],
            provenance_notes=[
                "No water observation provenance is available because no observations "
                "were assembled."
            ],
            station=station,
            basin_id=basin_id,
            use_case=use_case,
        )

    def _get_station_observations(
        self,
        station: str,
        selected_parameters: list[str],
        selected_parameter_keys: set[str],
    ) -> list[dict[str, Any]]:
        """Fetch station observations, respecting selected parameters."""

        if self.water_service is None:
            return []
        if not selected_parameters:
            return self.water_service.get_observations_by_station(station)
        grouped = self.water_service.get_observations_for_parameters(
            station,
            selected_parameters,
        )
        flattened = [
            observation
            for parameter in selected_parameters
            for observation in grouped.get(parameter, [])
        ]
        return _filter_observations(flattened, selected_parameter_keys)

    def _bundle(
        self,
        *,
        selected_source_type: str,
        observations: list[dict[str, Any]],
        selected_parameters: list[str],
        missing_inputs: list[str],
        warnings: list[str],
        data_quality_notes: list[str],
        provenance_notes: list[str],
        station: str | None,
        basin_id: int | None,
        use_case: str | None,
    ) -> WaterInputBundle:
        """Build a bundle and attach source IDs where observations provide them."""

        source_ids = _collect_source_ids(observations)
        return WaterInputBundle(
            selected_source_type=selected_source_type,
            observations=observations,
            observation_count=len(observations),
            selected_parameters=selected_parameters,
            missing_inputs=missing_inputs,
            warnings=warnings,
            data_quality_notes=data_quality_notes,
            provenance_notes=provenance_notes,
            source_id=source_ids[0] if len(source_ids) == 1 else None,
            source_ids=source_ids,
            station=station,
            basin_id=basin_id,
            use_case=use_case,
        )


def _selected_parameter_names(normalized_input: dict[str, Any]) -> list[str]:
    """Return normalized selected parameter display names."""

    return [
        parameter["parameter"]
        for parameter in normalized_input.get("selected_parameters", [])
        if parameter.get("parameter")
    ]


def _selected_parameter_keys(normalized_input: dict[str, Any]) -> set[str]:
    """Return normalized selected parameter matching keys."""

    return {
        parameter["parameter_match_key"]
        for parameter in normalized_input.get("selected_parameters", [])
        if parameter.get("parameter_match_key")
    }


def _filter_observations(
    observations: Sequence[dict[str, Any]],
    selected_parameter_keys: set[str],
) -> list[dict[str, Any]]:
    """Filter observations by selected parameter names when requested."""

    if not selected_parameter_keys:
        return list(observations)
    return [
        dict(observation)
        for observation in observations
        if normalize_match_key(observation.get("parameter")) in selected_parameter_keys
    ]


def _collect_source_ids(observations: Sequence[dict[str, Any]]) -> list[int]:
    """Collect unique source IDs from raw observation dictionaries."""

    source_ids = []
    for observation in observations:
        source_id = observation.get("source_id")
        if source_id is None and isinstance(observation.get("original"), dict):
            source_id = observation["original"].get("source_id")
        if source_id is None:
            continue
        try:
            source_id_int = int(source_id)
        except (TypeError, ValueError):
            continue
        if source_id_int not in source_ids:
            source_ids.append(source_id_int)
    return source_ids


def _profile_context_values(normalized_input: dict[str, Any]) -> list[Any]:
    """Return request context fields used only for exact profile choice."""

    context = normalized_input.get("context") or {}
    values: list[Any] = [
        context.get("water_type"),
        context.get("influent_basis"),
        context.get("influent_profile"),
        context.get("sanitation_stream"),
        context.get("wastewater_stream"),
        context.get("pollution_source_type"),
        context.get("source_type"),
        context.get("pollution_source_type_requested"),
        context.get("workflow_mode"),
        normalized_input.get("notes"),
    ]
    return [value for value in values if value not in (None, "")]


def _select_profile_name(values: Sequence[Any]) -> str | None:
    """Select the approved fallback profile without fuzzy database matching."""

    keys = [normalize_match_key(value) or "" for value in values]
    if any(_is_explicit_blackwater_key(key) for key in keys):
        return BLACKWATER_PROFILE_NAME
    if any(_is_municipal_domestic_key(key) for key in keys):
        return MUNICIPAL_PROFILE_NAME
    return None


def _is_explicit_blackwater_key(key: str) -> bool:
    """Return whether the user explicitly asked for blackwater context."""

    return (
        "blackwater" in key
        or "black_water" in key
        or "toilet_waste" in key
        or "toilet_stream" in key
        or "sanitation_stream" in key
    )


def _is_municipal_domestic_key(key: str) -> bool:
    """Return whether ordinary domestic/municipal fallback is appropriate."""

    municipal_tokens = (
        "domestic",
        "municipal",
        "town_sewage",
        "town_wastewater",
        "combined_municipal",
        "domestic_sewage",
        "municipal_sewage",
        "municipal_wastewater",
    )
    return any(token in key for token in municipal_tokens)


def _profile_rows_to_observations(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert water_type_profiles rows into observation-like dictionaries."""

    observations = []
    for row in rows:
        low = _as_float(row.get("value_low"))
        high = _as_float(row.get("value_high"))
        value = _profile_midpoint(low, high)
        if value is None:
            continue
        observations.append(
            {
                "parameter": row.get("parameter"),
                "value": value,
                "value_mean": value,
                "value_low": low,
                "value_high": high,
                "unit": row.get("unit"),
                "source": "water_type_profile",
                "source_id": row.get("source_id"),
                "water_type": row.get("water_type"),
                "profile_note": row.get("note"),
                "original": dict(row),
            }
        )
    return observations


def _profile_midpoint(low: float | None, high: float | None) -> float | None:
    """Return a single fallback value for engines that expect observations."""

    if low is not None and high is not None:
        return (low + high) / 2.0
    return low if low is not None else high


def _as_float(value: Any) -> float | None:
    """Convert a profile value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _append_once(values: list[str], value: str) -> None:
    """Append a missing-input marker once."""

    if value not in values:
        values.append(value)

"""Step A engine for normalizing raw recommendation inputs.

This module only cleans and validates input fields. It does not compare water
quality with standards, calculate exceedance, classify treatment needs, rank
solutions, or recommend plants.
"""

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any


DATA_PRIORITY_NOTE = (
    "Future data priority: user measured data > station observations > "
    "regional/catchment fallback > water_type profile fallback. Step A only "
    "records this note and does not implement the fallback chain."
)


@dataclass(slots=True)
class InputContext:
    """Validated input packet passed to later scientific workflow steps."""

    original_input: dict[str, Any]
    normalized_input: dict[str, Any]
    validation_status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    available_use_cases: list[str] = field(default_factory=list)
    data_priority_note: str = DATA_PRIORITY_NOTE

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for future API responses or logs."""

        return asdict(self)


def normalize_text(value: Any) -> str | None:
    """Strip whitespace and collapse repeated spaces in a text value."""

    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


def normalize_match_key(value: Any) -> str | None:
    """Return a transparent matching key for use cases and parameters."""

    text = normalize_text(value)
    if text is None:
        return None
    return text.lower().replace("-", "_").replace(" ", "_")


def _as_optional_int(value: Any, field_name: str, errors: list[str]) -> int | None:
    """Convert optional numeric identifiers to int when possible."""

    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        errors.append(f"{field_name} must be an integer when provided.")
        return None


def _as_float(value: Any) -> float | None:
    """Convert a measured value to float, returning None when invalid."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class InputNormalizationEngine:
    """Clean raw site, standard, and measured-observation inputs."""

    def normalize(
        self,
        raw_input: Mapping[str, Any] | None = None,
        **fields: Any,
    ) -> InputContext:
        """Return an InputContext with normalized fields and validation issues."""

        original_input = dict(raw_input or {})
        original_input.update(fields)

        errors: list[str] = []
        warnings: list[str] = []
        missing_inputs: list[str] = []

        use_case_original = original_input.get("use_case")
        use_case = normalize_match_key(use_case_original)
        if use_case is None:
            errors.append("use_case is required.")
            missing_inputs.append("use_case")

        station = normalize_text(original_input.get("station"))
        selected_parameters = self._normalize_selected_parameters(
            original_input.get("selected_parameters"),
        )
        measured_observations = self._normalize_measured_observations(
            original_input.get("measured_observations"),
            errors,
            warnings,
        )

        normalized_input = {
            "region_id": _as_optional_int(original_input.get("region_id"), "region_id", errors),
            "station": station,
            "station_match_key": normalize_match_key(station),
            "basin_id": _as_optional_int(original_input.get("basin_id"), "basin_id", errors),
            "use_case": use_case,
            "use_case_original": normalize_text(use_case_original),
            "measured_observations": measured_observations,
            "selected_parameters": selected_parameters,
        }

        validation_status = "valid" if not errors else "invalid"
        return InputContext(
            original_input=original_input,
            normalized_input=normalized_input,
            validation_status=validation_status,
            errors=errors,
            warnings=warnings,
            missing_inputs=missing_inputs,
        )

    def _normalize_selected_parameters(self, value: Any) -> list[dict[str, str]]:
        """Normalize selected parameter names without changing their meaning."""

        if value in (None, ""):
            return []
        if isinstance(value, str):
            raw_parameters: Sequence[Any] = [value]
        else:
            raw_parameters = list(value)

        normalized = []
        for parameter in raw_parameters:
            text = normalize_text(parameter)
            if text is None:
                continue
            normalized.append(
                {
                    "parameter": text,
                    "parameter_match_key": normalize_match_key(text) or text,
                }
            )
        return normalized

    def _normalize_measured_observations(
        self,
        value: Any,
        errors: list[str],
        warnings: list[str],
    ) -> list[dict[str, Any]]:
        """Validate user measured observations without scientific comparison."""

        if value in (None, ""):
            return []
        if not isinstance(value, list):
            errors.append("measured_observations must be a list when provided.")
            return []

        normalized = []
        for index, observation in enumerate(value):
            if not isinstance(observation, Mapping):
                errors.append(f"measured_observations[{index}] must be an object.")
                continue

            parameter = normalize_text(observation.get("parameter"))
            if parameter is None:
                errors.append(f"measured_observations[{index}].parameter is required.")

            measured_value = _as_float(observation.get("value"))
            if measured_value is None:
                errors.append(f"measured_observations[{index}].value must be numeric.")

            unit = normalize_text(observation.get("unit"))
            target_unit = normalize_text(observation.get("target_unit"))
            if target_unit and unit and target_unit != unit:
                warnings.append(
                    "Unit conversion was requested for "
                    f"measured_observations[{index}], but no conversion table exists yet."
                )
            if observation.get("needs_unit_conversion") is True:
                warnings.append(
                    "Unit conversion was requested for "
                    f"measured_observations[{index}], but no conversion table exists yet."
                )

            source = normalize_text(observation.get("source")) or "user_measured"
            normalized.append(
                {
                    "parameter": parameter,
                    "parameter_match_key": normalize_match_key(parameter),
                    "value": measured_value,
                    "unit": unit,
                    "source": source,
                    "original": dict(observation),
                }
            )

        return normalized

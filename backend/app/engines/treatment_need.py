"""Step D engine for classifying treatment need groups.

This module reads pollutant gap results from Step C and groups clear water
quality problems into broad treatment-need categories. It does not recommend
NbS technologies, filter candidates, rank, score, use TOPSIS/AHP, recommend
plants, or classify health risk.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.input_normalization import normalize_match_key
from app.engines.pollutant_gap import ParameterGapResult, PollutantGapBundle


NEED_TRIGGER_STATUSES = {
    "exceeds_standard",
    "below_minimum",
    "outside_range",
}
WARNING_ONLY_STATUSES = {
    "unit_mismatch",
    "standard_missing",
    "invalid_value",
}

# These mappings are intentionally explicit. They use the normalized parameter
# key from normalize_match_key(), but they do not use fuzzy matching or hidden
# aliases. Add new names only when the data dictionary/schema or supervisor
# review makes them explicit.
PARAMETER_TO_NEED_GROUP = {
    "bod": "organic_load",
    "cod": "organic_load",
    "tss": "solids",
    "turbidity": "solids",
    "suspended_solids": "solids",
    "total_suspended_solids": "solids",
    "nitrate": "nutrients",
    "phosphate": "nutrients",
    "ammonia": "nutrients",
    "nitrogen": "nutrients",
    "total_nitrogen": "nutrients",
    "phosphorus": "nutrients",
    "total_phosphorus": "nutrients",
    "fecal_coliform": "pathogens",
    "faecal_coliform": "pathogens",
    "total_coliform": "pathogens",
    "e._coli": "pathogens",
    "e_coli": "pathogens",
    "ec": "salinity",
    "tds": "salinity",
    "chloride": "salinity",
    "salinity": "salinity",
    "iron": "metals",
    "lead": "metals",
    "chromium": "metals",
    "cadmium": "metals",
    "arsenic": "metals",
    "mercury": "metals",
    "heavy_metals": "metals",
    "ph": "ph_correction",
    "do": "oxygen_deficit",
    "dissolved_oxygen": "oxygen_deficit",
    "water_quality_index": "general_water_quality",
    "general_water_quality": "general_water_quality",
}


@dataclass(slots=True)
class TreatmentNeedResult:
    """One classified treatment need group from pollutant gaps."""

    need_group: str
    triggering_parameters: list[str] = field(default_factory=list)
    triggering_statuses: list[str] = field(default_factory=list)
    max_gap_ratio: float | None = None
    required_removal_percent_max: float | None = None
    direction: str = "unknown"
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class TreatmentNeedBundle:
    """Collection of treatment need groups from one pollutant gap bundle."""

    use_case: str
    selected_source_type: str
    treatment_needs: list[TreatmentNeedResult] = field(default_factory=list)
    unclassified_parameters: list[str] = field(default_factory=list)
    warning_count: int = 0
    warnings: list[str] = field(default_factory=list)
    source_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["treatment_needs"] = [
            result.to_dict() for result in self.treatment_needs
        ]
        return payload


class TreatmentNeedClassifier:
    """Classify broad treatment need groups from Step C gap results."""

    def classify(self, gap_bundle: PollutantGapBundle) -> TreatmentNeedBundle:
        """Return treatment need groups without recommending any technology."""

        grouped: dict[str, list[ParameterGapResult]] = {}
        warnings = list(gap_bundle.warnings)
        unclassified_parameters: list[str] = []
        source_ids: list[int] = []

        for result in gap_bundle.results:
            _extend_source_ids(source_ids, result.source_ids)
            if result.status == "within_standard":
                continue
            if result.status in WARNING_ONLY_STATUSES:
                _append_once(
                    warnings,
                    _warning_for_context_result(result),
                )
                if result.status == "invalid_value":
                    _append_once_if_value(unclassified_parameters, result.parameter)
                continue
            if result.status not in NEED_TRIGGER_STATUSES:
                _append_once_if_value(unclassified_parameters, result.parameter)
                continue

            need_group = _need_group_for_parameter(result.parameter, result.status)
            if need_group is None:
                _append_once_if_value(unclassified_parameters, result.parameter)
                continue
            grouped.setdefault(need_group, []).append(result)

        treatment_needs = [
            _build_need_result(need_group, results)
            for need_group, results in grouped.items()
        ]
        treatment_needs.sort(key=lambda result: result.need_group)

        return TreatmentNeedBundle(
            use_case=gap_bundle.use_case,
            selected_source_type=gap_bundle.selected_source_type,
            treatment_needs=treatment_needs,
            unclassified_parameters=unclassified_parameters,
            warning_count=len(warnings),
            warnings=warnings,
            source_ids=source_ids,
        )


def _need_group_for_parameter(parameter: str | None, status: str) -> str | None:
    """Return a need group for an explicit parameter name and status."""

    parameter_key = normalize_match_key(parameter)
    if not parameter_key:
        return None
    need_group = PARAMETER_TO_NEED_GROUP.get(parameter_key)
    # pH correction should only be triggered when pH is outside its range.
    if need_group == "ph_correction" and status != "outside_range":
        return None
    # Oxygen deficit should only be triggered when DO is below the minimum.
    if need_group == "oxygen_deficit" and status != "below_minimum":
        return None
    return need_group


def _build_need_result(
    need_group: str,
    results: list[ParameterGapResult],
) -> TreatmentNeedResult:
    """Build a treatment need result from grouped parameter gaps."""

    return TreatmentNeedResult(
        need_group=need_group,
        triggering_parameters=_unique_present(result.parameter for result in results),
        triggering_statuses=_unique_present(result.status for result in results),
        max_gap_ratio=_max_optional(result.gap_ratio for result in results),
        required_removal_percent_max=_max_optional(
            result.required_removal_percent for result in results
        ),
        direction=_direction_for_group(results),
        notes=[
            "Treatment need was classified from explicit parameter mapping and "
            "Step C gap status only.",
            "No NbS technology suitability, filtering, ranking, or recommendation "
            "was calculated.",
        ],
    )


def _direction_for_group(results: list[ParameterGapResult]) -> str:
    """Return one direction for a grouped treatment need."""

    directions = _unique_present(result.direction for result in results)
    if len(directions) == 1:
        return directions[0]
    if not directions:
        return "unknown"
    return "mixed"


def _warning_for_context_result(result: ParameterGapResult) -> str:
    """Create a warning for results that should not become treatment needs."""

    parameter = result.parameter or "unknown parameter"
    if result.status == "standard_missing":
        return f"Standard missing for {parameter}; no treatment need was inferred."
    if result.status == "unit_mismatch":
        return f"Unit mismatch for {parameter}; no treatment need was inferred."
    if result.status == "invalid_value":
        return f"Invalid observed value for {parameter}; no treatment need was inferred."
    return f"{parameter} could not be classified safely."


def _unique_present(values: Any) -> list[Any]:
    """Return unique non-empty values while preserving order."""

    unique = []
    for value in values:
        if value in (None, ""):
            continue
        if value not in unique:
            unique.append(value)
    return unique


def _max_optional(values: Any) -> float | None:
    """Return the maximum numeric value, ignoring None."""

    numeric_values = [value for value in values if value is not None]
    if not numeric_values:
        return None
    return max(numeric_values)


def _extend_source_ids(source_ids: list[int], values: list[int]) -> None:
    """Append unique source IDs from a result."""

    for value in values:
        if value not in source_ids:
            source_ids.append(value)


def _append_once(values: list[str], value: str) -> None:
    """Append a string once."""

    if value not in values:
        values.append(value)


def _append_once_if_value(values: list[str], value: str | None) -> None:
    """Append a non-empty string once."""

    if value and value not in values:
        values.append(value)

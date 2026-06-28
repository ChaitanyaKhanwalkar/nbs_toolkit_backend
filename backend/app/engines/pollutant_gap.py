"""Step C engine for pollutant gap and exceedance calculation.

This module compares assembled water observations against stored standards for
one explicit use case. It does not classify treatment needs, filter NbS
candidates, rank, score, use TOPSIS/AHP, recommend plants, or classify health
risk.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from app.engines.input_normalization import normalize_match_key, normalize_text
from app.engines.water_input_assembly import WaterInputBundle


PARAMETER_STANDARD_ALIASES = {
    "ec": "conductivity",
    "ec_fld": "conductivity",
    "ec_gen": "conductivity",
    "electrical_conductivity": "conductivity",
    "specific_conductance": "conductivity",
    "conductance": "conductivity",
    "ph_fld": "ph",
    "ph_gen": "ph",
    "po4": "total_phosphorus",
    "po4_p": "total_phosphorus",
    "o_po4_p": "total_phosphorus",
    "phosphate": "total_phosphorus",
    "phosphate_p": "total_phosphorus",
    "phosphate_phosphorus": "total_phosphorus",
    "orthophosphate": "total_phosphorus",
    "ortho_phosphate": "total_phosphorus",
    "p_tot": "total_phosphorus",
    "tp": "total_phosphorus",
    "p_total": "total_phosphorus",
}

UNIT_ALIASES = {
    "mg/l": "mg_l",
    "mgl": "mg_l",
    "mg_l": "mg_l",
    "ph": "ph_units",
    "ph_unit": "ph_units",
    "ph_units": "ph_units",
    "phunits": "ph_units",
    "us/cm": "umho_cm",
    "uS/cm": "umho_cm",
    "us_cm": "umho_cm",
    "µs/cm": "umho_cm",
    "μs/cm": "umho_cm",
    "micros/cm": "umho_cm",
    "microsiemens/cm": "umho_cm",
    "microsiemens_per_cm": "umho_cm",
    "micromho/cm": "umho_cm",
    "micromhos/cm": "umho_cm",
    "umho/cm": "umho_cm",
    "umhos/cm": "umho_cm",
    "umho_cm": "umho_cm",
    "mpn/100ml": "mpn_100ml",
    "mpn_100ml": "mpn_100ml",
    "per100ml": "per_100ml",
    "per_100ml": "per_100ml",
    "ntu": "ntu",
}


@dataclass(slots=True)
class ParameterGapResult:
    """Gap calculation for one observed parameter."""

    parameter: str | None
    observed_value: float | None
    observed_unit: str | None
    standard_unit: str | None
    limit_low: float | None
    limit_high: float | None
    comparison_type: str
    status: str
    gap_value: float | None
    gap_ratio: float | None
    required_removal_fraction: float | None
    required_removal_percent: float | None
    direction: str
    source_type: str
    source_id: int | None = None
    source_ids: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class PollutantGapBundle:
    """Collection of pollutant gap results for one use case."""

    use_case: str
    selected_source_type: str
    total_observations_checked: int
    comparable_count: int
    exceedance_count: int
    missing_standard_count: int
    unit_mismatch_count: int
    results: list[ParameterGapResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["results"] = [result.to_dict() for result in self.results]
        return payload


class StandardsProvider(Protocol):
    """Small service interface needed by the pollutant gap engine."""

    def get_standards_for_use_case(self, use_case: str) -> list[dict[str, Any]]:
        """Return raw standard rows for one explicit use case."""


class PollutantGapEngine:
    """Compare water observations with explicit standards."""

    def __init__(self, standards_service: StandardsProvider) -> None:
        self.standards_service = standards_service

    @classmethod
    def from_session(cls, session: Any) -> "PollutantGapEngine":
        """Create the engine using the production StandardsService layer."""

        from app.services import StandardsService

        return cls(StandardsService(session))

    def calculate(
        self,
        water_bundle: WaterInputBundle,
        use_case: str | None = None,
    ) -> PollutantGapBundle:
        """Calculate pollutant gaps for assembled water observations."""

        selected_use_case = use_case or water_bundle.use_case
        if not selected_use_case:
            return PollutantGapBundle(
                use_case="",
                selected_source_type=water_bundle.selected_source_type,
                total_observations_checked=water_bundle.observation_count,
                comparable_count=0,
                exceedance_count=0,
                missing_standard_count=water_bundle.observation_count,
                unit_mismatch_count=0,
                warnings=["use_case is required before pollutant gaps can be calculated."],
            )

        standards = self.standards_service.get_standards_for_use_case(selected_use_case)
        standards_by_parameter = _standards_by_parameter(standards)
        warnings = list(water_bundle.warnings)
        if water_bundle.observation_count == 0:
            warnings.append("No water observations were available for pollutant gap calculation.")
            return PollutantGapBundle(
                use_case=selected_use_case,
                selected_source_type=water_bundle.selected_source_type,
                total_observations_checked=0,
                comparable_count=0,
                exceedance_count=0,
                missing_standard_count=0,
                unit_mismatch_count=0,
                results=[],
                warnings=warnings,
            )

        results = [
            self._calculate_one(
                observation=observation,
                standard=standards_by_parameter.get(
                    _canonical_parameter_key(observation.get("parameter"))
                ),
                source_type=water_bundle.selected_source_type,
                bundle_source_ids=water_bundle.source_ids,
            )
            for observation in water_bundle.observations
        ]

        warnings.extend(
            warning
            for result in results
            for warning in result.warnings
            if warning not in warnings
        )
        return PollutantGapBundle(
            use_case=selected_use_case,
            selected_source_type=water_bundle.selected_source_type,
            total_observations_checked=len(results),
            comparable_count=sum(
                result.comparison_type in {"max_limit", "min_limit", "range_limit"}
                for result in results
            ),
            exceedance_count=sum(
                result.status
                in {"exceeds_standard", "below_minimum", "outside_range"}
                for result in results
            ),
            missing_standard_count=sum(
                result.status == "standard_missing" for result in results
            ),
            unit_mismatch_count=sum(
                result.status == "unit_mismatch" for result in results
            ),
            results=results,
            warnings=warnings,
        )

    def _calculate_one(
        self,
        *,
        observation: dict[str, Any],
        standard: dict[str, Any] | None,
        source_type: str,
        bundle_source_ids: list[int],
    ) -> ParameterGapResult:
        """Calculate one parameter gap without classifying treatment need."""

        parameter = normalize_text(observation.get("parameter"))
        observed_unit = normalize_text(observation.get("unit"))
        source_ids = _observation_source_ids(observation, bundle_source_ids)
        observed_value = _observed_value(observation)

        if observed_value is None:
            return ParameterGapResult(
                parameter=parameter,
                observed_value=None,
                observed_unit=observed_unit,
                standard_unit=None,
                limit_low=None,
                limit_high=None,
                comparison_type="invalid_value",
                status="invalid_value",
                gap_value=None,
                gap_ratio=None,
                required_removal_fraction=None,
                required_removal_percent=None,
                direction="unknown",
                source_type=source_type,
                source_id=source_ids[0] if len(source_ids) == 1 else None,
                source_ids=source_ids,
                warnings=[f"Observed value for '{parameter}' is missing or non-numeric."],
                notes=["No pollutant gap was calculated for this observation."],
            )

        if standard is None:
            return ParameterGapResult(
                parameter=parameter,
                observed_value=observed_value,
                observed_unit=observed_unit,
                standard_unit=None,
                limit_low=None,
                limit_high=None,
                comparison_type="standard_missing",
                status="standard_missing",
                gap_value=None,
                gap_ratio=None,
                required_removal_fraction=None,
                required_removal_percent=None,
                direction="unknown",
                source_type=source_type,
                source_id=source_ids[0] if len(source_ids) == 1 else None,
                source_ids=source_ids,
                warnings=[f"No standard was found for parameter '{parameter}'."],
                notes=["No pollutant gap was calculated because the standard is missing."],
            )

        standard_unit = normalize_text(standard.get("unit"))
        limit_low = _as_float(standard.get("limit_low"))
        limit_high = _as_float(standard.get("limit_high"))
        if _unit_mismatch(observed_unit, standard_unit):
            return ParameterGapResult(
                parameter=parameter,
                observed_value=observed_value,
                observed_unit=observed_unit,
                standard_unit=standard_unit,
                limit_low=limit_low,
                limit_high=limit_high,
                comparison_type="unit_mismatch",
                status="unit_mismatch",
                gap_value=None,
                gap_ratio=None,
                required_removal_fraction=None,
                required_removal_percent=None,
                direction="unknown",
                source_type=source_type,
                source_id=source_ids[0] if len(source_ids) == 1 else None,
                source_ids=source_ids,
                warnings=[
                    f"Unit mismatch for '{parameter}': observed '{observed_unit}', "
                    f"standard '{standard_unit}'. No conversion table exists yet."
                ],
                notes=["No pollutant gap was calculated because units differ."],
            )

        comparison_type = _comparison_type(standard, limit_low, limit_high)
        if comparison_type == "max_limit":
            return _max_limit_result(
                parameter,
                observed_value,
                observed_unit,
                standard_unit,
                limit_high,
                source_type,
                source_ids,
            )
        if comparison_type == "min_limit":
            return _min_limit_result(
                parameter,
                observed_value,
                observed_unit,
                standard_unit,
                limit_low,
                source_type,
                source_ids,
            )
        if comparison_type == "range_limit":
            return _range_limit_result(
                parameter,
                observed_value,
                observed_unit,
                standard_unit,
                limit_low,
                limit_high,
                source_type,
                source_ids,
            )
        return ParameterGapResult(
            parameter=parameter,
            observed_value=observed_value,
            observed_unit=observed_unit,
            standard_unit=standard_unit,
            limit_low=limit_low,
            limit_high=limit_high,
            comparison_type="standard_missing",
            status="standard_missing",
            gap_value=None,
            gap_ratio=None,
            required_removal_fraction=None,
            required_removal_percent=None,
            direction="unknown",
            source_type=source_type,
            source_id=source_ids[0] if len(source_ids) == 1 else None,
            source_ids=source_ids,
            warnings=[f"Standard for '{parameter}' has no usable limits."],
            notes=["No pollutant gap was calculated because limit values are missing."],
        )


def _max_limit_result(
    parameter: str | None,
    observed_value: float,
    observed_unit: str | None,
    standard_unit: str | None,
    limit_high: float | None,
    source_type: str,
    source_ids: list[int],
) -> ParameterGapResult:
    """Calculate a max-limit comparison."""

    if limit_high is None:
        raise ValueError("max-limit comparison requires limit_high")
    if observed_value <= limit_high:
        return _within_result(
            parameter,
            observed_value,
            observed_unit,
            standard_unit,
            None,
            limit_high,
            "max_limit",
            source_type,
            source_ids,
        )
    gap_value = observed_value - limit_high
    gap_ratio = gap_value / limit_high if limit_high else None
    required_removal_fraction = gap_value / observed_value if observed_value else None
    return ParameterGapResult(
        parameter=parameter,
        observed_value=observed_value,
        observed_unit=observed_unit,
        standard_unit=standard_unit,
        limit_low=None,
        limit_high=limit_high,
        comparison_type="max_limit",
        status="exceeds_standard",
        gap_value=gap_value,
        gap_ratio=gap_ratio,
        required_removal_fraction=required_removal_fraction,
        required_removal_percent=(
            required_removal_fraction * 100
            if required_removal_fraction is not None
            else None
        ),
        direction="reduce",
        source_type=source_type,
        source_id=source_ids[0] if len(source_ids) == 1 else None,
        source_ids=source_ids,
        notes=["Observed value is above the maximum standard limit."],
    )


def _min_limit_result(
    parameter: str | None,
    observed_value: float,
    observed_unit: str | None,
    standard_unit: str | None,
    limit_low: float | None,
    source_type: str,
    source_ids: list[int],
) -> ParameterGapResult:
    """Calculate a min-limit comparison."""

    if limit_low is None:
        raise ValueError("min-limit comparison requires limit_low")
    if observed_value >= limit_low:
        return _within_result(
            parameter,
            observed_value,
            observed_unit,
            standard_unit,
            limit_low,
            None,
            "min_limit",
            source_type,
            source_ids,
        )
    gap_value = limit_low - observed_value
    gap_ratio = gap_value / limit_low if limit_low else None
    return ParameterGapResult(
        parameter=parameter,
        observed_value=observed_value,
        observed_unit=observed_unit,
        standard_unit=standard_unit,
        limit_low=limit_low,
        limit_high=None,
        comparison_type="min_limit",
        status="below_minimum",
        gap_value=gap_value,
        gap_ratio=gap_ratio,
        required_removal_fraction=None,
        required_removal_percent=None,
        direction="increase",
        source_type=source_type,
        source_id=source_ids[0] if len(source_ids) == 1 else None,
        source_ids=source_ids,
        notes=["Observed value is below the minimum standard limit."],
    )


def _range_limit_result(
    parameter: str | None,
    observed_value: float,
    observed_unit: str | None,
    standard_unit: str | None,
    limit_low: float | None,
    limit_high: float | None,
    source_type: str,
    source_ids: list[int],
) -> ParameterGapResult:
    """Calculate a range-limit comparison."""

    if limit_low is None or limit_high is None:
        raise ValueError("range-limit comparison requires limit_low and limit_high")
    if limit_low <= observed_value <= limit_high:
        return _within_result(
            parameter,
            observed_value,
            observed_unit,
            standard_unit,
            limit_low,
            limit_high,
            "range_limit",
            source_type,
            source_ids,
        )
    if observed_value < limit_low:
        gap_value = limit_low - observed_value
        boundary = limit_low
    else:
        gap_value = observed_value - limit_high
        boundary = limit_high
    return ParameterGapResult(
        parameter=parameter,
        observed_value=observed_value,
        observed_unit=observed_unit,
        standard_unit=standard_unit,
        limit_low=limit_low,
        limit_high=limit_high,
        comparison_type="range_limit",
        status="outside_range",
        gap_value=gap_value,
        gap_ratio=gap_value / boundary if boundary else None,
        required_removal_fraction=None,
        required_removal_percent=None,
        direction="adjust_range",
        source_type=source_type,
        source_id=source_ids[0] if len(source_ids) == 1 else None,
        source_ids=source_ids,
        notes=["Observed value is outside the accepted standard range."],
    )


def _within_result(
    parameter: str | None,
    observed_value: float,
    observed_unit: str | None,
    standard_unit: str | None,
    limit_low: float | None,
    limit_high: float | None,
    comparison_type: str,
    source_type: str,
    source_ids: list[int],
) -> ParameterGapResult:
    """Return a within-standard result."""

    return ParameterGapResult(
        parameter=parameter,
        observed_value=observed_value,
        observed_unit=observed_unit,
        standard_unit=standard_unit,
        limit_low=limit_low,
        limit_high=limit_high,
        comparison_type=comparison_type,
        status="within_standard",
        gap_value=0.0,
        gap_ratio=0.0,
        required_removal_fraction=0.0 if comparison_type == "max_limit" else None,
        required_removal_percent=0.0 if comparison_type == "max_limit" else None,
        direction="none",
        source_type=source_type,
        source_id=source_ids[0] if len(source_ids) == 1 else None,
        source_ids=source_ids,
        notes=["Observed value is within the selected standard."],
    )


def _standards_by_parameter(standards: Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map standards by transparent normalized parameter names."""

    mapped = {}
    for standard in standards:
        parameter_key = _canonical_parameter_key(standard.get("parameter"))
        if parameter_key and parameter_key not in mapped:
            mapped[parameter_key] = standard
    return mapped


def _canonical_parameter_key(value: Any) -> str | None:
    """Return a standards-matching key using only controlled aliases."""

    key = normalize_match_key(value)
    if key is None:
        return None
    return PARAMETER_STANDARD_ALIASES.get(key, key)


def _comparison_type(
    standard: dict[str, Any],
    limit_low: float | None,
    limit_high: float | None,
) -> str:
    """Infer comparison type from explicit standard limits and direction."""

    direction = normalize_match_key(standard.get("direction"))
    if limit_low is not None and limit_high is not None:
        return "range_limit"
    if limit_high is not None:
        return "max_limit"
    if limit_low is not None:
        return "min_limit"
    if direction in {"max", "maximum", "upper"} and limit_high is not None:
        return "max_limit"
    if direction in {"min", "minimum", "lower"} and limit_low is not None:
        return "min_limit"
    return "standard_missing"


def _observed_value(observation: dict[str, Any]) -> float | None:
    """Return numeric observed value from common raw observation fields."""

    for key in ("observed_value", "value", "value_mean"):
        value = observation.get(key)
        if value is None:
            continue
        return _as_float(value)
    return None


def _as_float(value: Any) -> float | None:
    """Convert a value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _unit_mismatch(observed_unit: str | None, standard_unit: str | None) -> bool:
    """Return whether two present units differ under transparent normalization."""

    if not observed_unit or not standard_unit:
        return False
    return _unit_key(observed_unit) != _unit_key(standard_unit)


def _unit_key(value: str) -> str:
    """Normalize unit spellings that are equivalent without conversion."""

    text = value.strip().lower().replace(" ", "").replace("-", "_")
    return UNIT_ALIASES.get(text, text)


def _observation_source_ids(
    observation: dict[str, Any],
    bundle_source_ids: list[int],
) -> list[int]:
    """Collect source IDs from an observation, falling back to bundle IDs."""

    source_ids = []
    for value in (
        observation.get("source_id"),
        observation.get("source_ids"),
        observation.get("original", {}).get("source_id")
        if isinstance(observation.get("original"), dict)
        else None,
    ):
        if value is None:
            continue
        if isinstance(value, list):
            for item in value:
                _append_source_id(source_ids, item)
        else:
            _append_source_id(source_ids, value)
    for source_id in bundle_source_ids:
        _append_source_id(source_ids, source_id)
    return source_ids


def _append_source_id(source_ids: list[int], value: Any) -> None:
    """Append a unique integer source ID when possible."""

    try:
        source_id = int(value)
    except (TypeError, ValueError):
        return
    if source_id not in source_ids:
        source_ids.append(source_id)

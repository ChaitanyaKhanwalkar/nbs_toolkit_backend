"""Step G engine for unweighted MCDA criteria normalization.

This module normalizes raw numeric criteria from the Step F MCDA matrix so
future weighting and TOPSIS work can use comparable 0-1 values. It uses only
transparent min-max normalization. It does not apply weights, calculate TOPSIS,
rank candidates, calculate match/confidence scores, recommend plants, classify
health risk, or create final recommendations.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.mcda_matrix import McdaMatrixBundle


NORMALIZATION_METHOD = "min_max_unweighted"
WEIGHTS_NOT_APPLIED = "not_applied"

NORMALIZATION_NORMALIZED = "normalized"
NORMALIZATION_MISSING = "missing"
NORMALIZATION_NON_NUMERIC = "non_numeric"
NORMALIZATION_DIRECTION_UNKNOWN = "direction_unknown"
NORMALIZATION_NO_VARIATION = "no_variation"

DIRECTION_BENEFIT = "benefit"
DIRECTION_COST = "cost"
DIRECTION_UNKNOWN = "unknown"

# Explicit direction map only. Criteria outside this map are left unnormalized
# as direction_unknown so the engine does not silently guess scientific meaning.
CRITERION_DIRECTION_MAP = {
    "removal_evidence_coverage": DIRECTION_BENEFIT,
    "co_benefit_score": DIRECTION_BENEFIT,
    "climate_suitability": DIRECTION_BENEFIT,
    "site_suitability": DIRECTION_BENEFIT,
    "land_requirement": DIRECTION_COST,
    "footprint_requirement": DIRECTION_COST,
    "cost_indicator": DIRECTION_COST,
    "maintenance_indicator": DIRECTION_COST,
    "implementation_complexity": DIRECTION_COST,
}


@dataclass(slots=True)
class NormalizedMcdaCriterion:
    """One raw criterion value with its unweighted normalized value."""

    criterion_name: str
    raw_value: Any = None
    normalized_value: float | None = None
    direction: str = DIRECTION_UNKNOWN
    normalization_status: str = NORMALIZATION_MISSING
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class NormalizedMcdaMatrixRow:
    """Normalized Step G criteria for one Step F matrix row."""

    nbs_id: int | None
    nbs_name: str | None
    eligibility_status: str
    supported_treatment_needs: list[str] = field(default_factory=list)
    normalized_criteria: list[NormalizedMcdaCriterion] = field(default_factory=list)
    missing_criteria: list[str] = field(default_factory=list)
    caution_flags: list[str] = field(default_factory=list)
    source_ids: list[int] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["normalized_criteria"] = [
            criterion.to_dict() for criterion in self.normalized_criteria
        ]
        return payload


@dataclass(slots=True)
class NormalizedMcdaMatrixBundle:
    """Unweighted normalized Step G MCDA matrix bundle."""

    use_case: str
    treatment_need_groups: list[str] = field(default_factory=list)
    row_count: int = 0
    criteria_names: list[str] = field(default_factory=list)
    rows: list[NormalizedMcdaMatrixRow] = field(default_factory=list)
    normalization_method: str = NORMALIZATION_METHOD
    weights_status: str = WEIGHTS_NOT_APPLIED
    normalized_criteria_count: int = 0
    skipped_criteria_count: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["rows"] = [row.to_dict() for row in self.rows]
        return payload


class McdaNormalizationEngine:
    """Normalize numeric Step F MCDA matrix criteria without weighting."""

    def normalize(self, matrix_bundle: McdaMatrixBundle) -> NormalizedMcdaMatrixBundle:
        """Normalize raw matrix criteria using explicit min-max rules only."""

        criteria_names = _criteria_names(matrix_bundle)
        warnings = list(matrix_bundle.warnings)
        criterion_ranges = _criterion_ranges(matrix_bundle, criteria_names)

        for criterion_name, value_range in criterion_ranges.items():
            if value_range is None:
                continue
            minimum, maximum = value_range
            if maximum == minimum:
                warnings.append(
                    f"Criterion '{criterion_name}' has no variation and was not normalized."
                )

        rows = [
            _normalize_row(row, criteria_names, criterion_ranges)
            for row in matrix_bundle.rows
        ]
        normalized_count = _count_status(rows, NORMALIZATION_NORMALIZED)
        skipped_count = sum(
            _count_status(rows, status)
            for status in {
                NORMALIZATION_MISSING,
                NORMALIZATION_NON_NUMERIC,
                NORMALIZATION_DIRECTION_UNKNOWN,
                NORMALIZATION_NO_VARIATION,
            }
        )

        return NormalizedMcdaMatrixBundle(
            use_case=matrix_bundle.use_case,
            treatment_need_groups=list(matrix_bundle.treatment_need_groups),
            row_count=len(rows),
            criteria_names=criteria_names,
            rows=rows,
            normalization_method=NORMALIZATION_METHOD,
            weights_status=WEIGHTS_NOT_APPLIED,
            normalized_criteria_count=normalized_count,
            skipped_criteria_count=skipped_count,
            warnings=warnings,
        )


def _normalize_row(
    row: Any,
    criteria_names: list[str],
    criterion_ranges: dict[str, tuple[float, float] | None],
) -> NormalizedMcdaMatrixRow:
    """Normalize all known criteria for one Step F matrix row."""

    normalized_criteria = [
        _normalize_criterion(
            criterion_name,
            row.criteria_values.get(criterion_name),
            criterion_ranges.get(criterion_name),
        )
        for criterion_name in criteria_names
    ]

    return NormalizedMcdaMatrixRow(
        nbs_id=row.nbs_id,
        nbs_name=row.nbs_name,
        eligibility_status=row.eligibility_status,
        supported_treatment_needs=list(row.supported_treatment_needs),
        normalized_criteria=normalized_criteria,
        missing_criteria=list(row.missing_criteria),
        caution_flags=list(row.caution_flags),
        source_ids=list(row.source_ids),
        notes=[
            *list(row.notes),
            "Step G applies min-max normalization only; no weights, TOPSIS, "
            "ranking, match score, confidence score, or final recommendation "
            "was calculated.",
        ],
    )


def _normalize_criterion(
    criterion_name: str,
    raw_value: Any,
    value_range: tuple[float, float] | None,
) -> NormalizedMcdaCriterion:
    """Normalize one criterion value or explain why it was skipped."""

    direction = CRITERION_DIRECTION_MAP.get(criterion_name, DIRECTION_UNKNOWN)
    if not _has_value(raw_value):
        return NormalizedMcdaCriterion(
            criterion_name=criterion_name,
            raw_value=raw_value,
            direction=direction,
            normalization_status=NORMALIZATION_MISSING,
            notes=["Raw criterion value is missing."],
        )
    if direction == DIRECTION_UNKNOWN:
        return NormalizedMcdaCriterion(
            criterion_name=criterion_name,
            raw_value=raw_value,
            direction=DIRECTION_UNKNOWN,
            normalization_status=NORMALIZATION_DIRECTION_UNKNOWN,
            notes=["Criterion direction is not in the explicit direction map."],
        )

    numeric_value = _as_float(raw_value)
    if numeric_value is None:
        return NormalizedMcdaCriterion(
            criterion_name=criterion_name,
            raw_value=raw_value,
            direction=direction,
            normalization_status=NORMALIZATION_NON_NUMERIC,
            notes=["Raw criterion value is not numeric."],
        )
    if value_range is None:
        return NormalizedMcdaCriterion(
            criterion_name=criterion_name,
            raw_value=raw_value,
            direction=direction,
            normalization_status=NORMALIZATION_NON_NUMERIC,
            notes=["Criterion did not have numeric values available for normalization."],
        )

    minimum, maximum = value_range
    if maximum == minimum:
        return NormalizedMcdaCriterion(
            criterion_name=criterion_name,
            raw_value=raw_value,
            direction=direction,
            normalization_status=NORMALIZATION_NO_VARIATION,
            notes=["Criterion has no variation across matrix rows."],
        )

    normalized_value = (
        (numeric_value - minimum) / (maximum - minimum)
        if direction == DIRECTION_BENEFIT
        else (maximum - numeric_value) / (maximum - minimum)
    )
    return NormalizedMcdaCriterion(
        criterion_name=criterion_name,
        raw_value=raw_value,
        normalized_value=normalized_value,
        direction=direction,
        normalization_status=NORMALIZATION_NORMALIZED,
        notes=["Normalized with unweighted min-max normalization."],
    )


def _criterion_ranges(
    matrix_bundle: McdaMatrixBundle,
    criteria_names: list[str],
) -> dict[str, tuple[float, float] | None]:
    """Return numeric min/max ranges for known-direction criteria."""

    ranges: dict[str, tuple[float, float] | None] = {}
    for criterion_name in criteria_names:
        if criterion_name not in CRITERION_DIRECTION_MAP:
            ranges[criterion_name] = None
            continue
        numeric_values = [
            numeric_value
            for row in matrix_bundle.rows
            for numeric_value in [_as_float(row.criteria_values.get(criterion_name))]
            if numeric_value is not None
        ]
        ranges[criterion_name] = (
            (min(numeric_values), max(numeric_values))
            if numeric_values
            else None
        )
    return ranges


def _criteria_names(matrix_bundle: McdaMatrixBundle) -> list[str]:
    """Collect criterion names from the bundle and row dictionaries."""

    names: list[str] = []
    for name in matrix_bundle.criteria_names:
        _append_once(names, name)
    for row in matrix_bundle.rows:
        for name in row.criteria_values:
            _append_once(names, name)
    return names


def _count_status(rows: list[NormalizedMcdaMatrixRow], status: str) -> int:
    """Count criterion normalization statuses across all normalized rows."""

    return sum(
        criterion.normalization_status == status
        for row in rows
        for criterion in row.normalized_criteria
    )


def _as_float(value: Any) -> float | None:
    """Convert a scalar value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _has_value(value: Any) -> bool:
    """Return True for existing non-empty raw values, including zero."""

    return value is not None and value != ""


def _append_once(values: list[str], value: str) -> None:
    """Append a value once while preserving order."""

    if value not in values:
        values.append(value)

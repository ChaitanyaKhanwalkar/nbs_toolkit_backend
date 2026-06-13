"""Step M.1 engine for conservative numeric MCDA projection.

This module converts already-present Step F raw MCDA evidence into a few
transparent numeric proxy criteria that Step G can normalize. It does not
invent scientific values, weights, citations, standards, removal efficiencies,
health-risk logic, or AHP calculations.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from app.engines.mcda_matrix import McdaMatrixBundle, McdaMatrixRow


PROJECTED_REMOVAL_EVIDENCE_COVERAGE = "removal_evidence_coverage"
PROJECTED_REMOVAL_EVIDENCE_SCORE = "removal_evidence_score"
PROJECTED_SITE_SUITABILITY = "site_suitability"
PROJECTED_COST_INDICATOR = "cost_indicator"

SITE_METADATA_FIELDS = [
    "optimal_water_type",
    "climate_suitability",
    "location_suitability",
    "soil_type",
]

SITE_SUITABILITY_NOTE = (
    "Projected site_suitability is provisional metadata completeness only; "
    "it is not expert site validation."
)


class McdaNumericProjectionEngine:
    """Project Step F raw MCDA evidence into numeric criteria for Step G."""

    def project(self, matrix_bundle: McdaMatrixBundle) -> McdaMatrixBundle:
        """Return a copied matrix bundle with safe projected numeric criteria."""

        projected_rows = [_project_row(row) for row in matrix_bundle.rows]
        criteria_names = list(matrix_bundle.criteria_names)
        for row in projected_rows:
            for criterion_name in row.criteria_values:
                _append_once(criteria_names, criterion_name)

        warnings = list(matrix_bundle.warnings)
        if _has_projected_site_suitability(projected_rows):
            _append_once(warnings, SITE_SUITABILITY_NOTE)

        return replace(
            matrix_bundle,
            rows=projected_rows,
            criteria_names=criteria_names,
            warnings=warnings,
        )


def _project_row(row: McdaMatrixRow) -> McdaMatrixRow:
    """Return a copied row with projected numeric criteria added when available."""

    criteria_values = dict(row.criteria_values)
    notes = list(row.notes)

    removal_coverage = _project_removal_evidence_coverage(
        criteria_values.get("removal_evidence")
    )
    if removal_coverage is not None:
        criteria_values[PROJECTED_REMOVAL_EVIDENCE_COVERAGE] = removal_coverage
        notes.append(
            "Projected removal_evidence_coverage from Step F removal_evidence "
            "row counts with numeric efficiency values."
        )

    removal_score = _project_removal_evidence_score(
        criteria_values.get("removal_evidence")
    )
    if removal_score is not None:
        criteria_values[PROJECTED_REMOVAL_EVIDENCE_SCORE] = removal_score
        notes.append(
            "Projected removal_evidence_score from existing Step F removal "
            "efficiency ranges only; no efficiency values were invented."
        )

    site_suitability = _project_site_suitability(
        criteria_values.get("climate_site_suitability")
    )
    if site_suitability is not None:
        criteria_values[PROJECTED_SITE_SUITABILITY] = site_suitability
        notes.append(SITE_SUITABILITY_NOTE)

    cost_indicator = criteria_values.get(PROJECTED_COST_INDICATOR)
    if _as_float(cost_indicator) is not None:
        notes.append(
            "Existing numeric cost_indicator was preserved for Step G; no cost "
            "was inferred from text, footprint, or resource descriptions."
        )

    return replace(row, criteria_values=criteria_values, notes=notes)


def _project_removal_evidence_coverage(raw_value: Any) -> float | None:
    """Project removal evidence coverage from explicit Step F evidence counts."""

    if not isinstance(raw_value, dict):
        return None

    row_count = _as_float(raw_value.get("row_count"))
    rows_with_numeric_efficiency = _as_float(
        raw_value.get("rows_with_numeric_efficiency")
    )
    if row_count and row_count > 0 and rows_with_numeric_efficiency is not None:
        return _clamp_01(rows_with_numeric_efficiency / row_count)

    raw_rows = raw_value.get("raw_rows")
    if not isinstance(raw_rows, list) or not raw_rows:
        return None
    numeric_row_count = sum(
        _row_has_numeric_efficiency(row)
        for row in raw_rows
        if isinstance(row, dict)
    )
    return _clamp_01(numeric_row_count / len(raw_rows))


def _project_removal_evidence_score(raw_value: Any) -> float | None:
    """Project average removal efficiency from explicit Step F raw rows."""

    if not isinstance(raw_value, dict):
        return None

    raw_rows = raw_value.get("raw_rows")
    if not isinstance(raw_rows, list) or not raw_rows:
        return None

    usable_efficiencies = [
        efficiency
        for row in raw_rows
        if isinstance(row, dict)
        for efficiency in [_row_efficiency_value(row)]
        if efficiency is not None
    ]
    if not usable_efficiencies:
        return None

    average_efficiency = sum(usable_efficiencies) / len(usable_efficiencies)
    return _clamp_01(average_efficiency / 100)


def _row_efficiency_value(row: dict[str, Any]) -> float | None:
    """Return one explicit efficiency value from a raw removal row."""

    eff_low = _as_float(row.get("eff_low"))
    eff_high = _as_float(row.get("eff_high"))

    if eff_low is not None and eff_high is not None:
        return (eff_low + eff_high) / 2
    if eff_low is not None:
        return eff_low
    if eff_high is not None:
        return eff_high
    return None


def _project_site_suitability(raw_value: Any) -> float | None:
    """Project metadata completeness only, not expert site suitability."""

    if not isinstance(raw_value, dict):
        return None

    present_count = sum(
        _has_value(raw_value.get(field_name))
        for field_name in SITE_METADATA_FIELDS
    )
    if present_count == 0:
        return None
    return _clamp_01(present_count / len(SITE_METADATA_FIELDS))


def _row_has_numeric_efficiency(row: dict[str, Any]) -> bool:
    """Return whether one raw removal row has numeric efficiency values."""

    return (
        _as_float(row.get("eff_low")) is not None
        or _as_float(row.get("eff_high")) is not None
    )


def _has_projected_site_suitability(rows: list[McdaMatrixRow]) -> bool:
    """Return True when any row received the provisional site proxy."""

    return any(
        PROJECTED_SITE_SUITABILITY in row.criteria_values
        for row in rows
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
    """Return True for existing non-empty metadata values, including zero."""

    return value is not None and value != ""


def _clamp_01(value: float) -> float:
    """Clamp a projected proxy value to the safe 0-1 range."""

    return max(0.0, min(1.0, value))


def _append_once(values: list[str], value: str) -> None:
    """Append a value once while preserving order."""

    if value not in values:
        values.append(value)

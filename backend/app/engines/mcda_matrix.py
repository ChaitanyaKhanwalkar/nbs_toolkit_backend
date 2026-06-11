"""Step F engine for preparing raw MCDA decision matrix inputs.

This module turns Step E candidate eligibility results into raw matrix rows for
future MCDA/TOPSIS work. It only structures existing catalogue, footprint,
implementation, criteria, and removal-evidence fields. It does not normalize,
weight, rank, calculate TOPSIS, calculate match/confidence scores, recommend
plants, classify health risk, or create final recommendations.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.candidate_filtering import (
    DATA_PENDING,
    ELIGIBLE,
    INELIGIBLE,
    CandidateFilterBundle,
    CandidateFilterResult,
    NbsCandidateProvider,
)
from app.engines.input_normalization import normalize_match_key, normalize_text


MATRIX_ELIGIBILITY_STATUSES = {ELIGIBLE, DATA_PENDING}
WEIGHTS_NOT_APPLIED = "not_applied"

# These are raw data buckets, not normalized criteria scores. A row may be
# missing any bucket when the catalogue/provider has no source data for it.
RAW_CRITERIA_NAMES = [
    "removal_evidence",
    "footprint",
    "cost_indicator",
    "maintenance_indicator",
    "implementation_complexity",
    "climate_site_suitability",
    "co_benefit_indicator",
    "catalogue_criteria",
]

SITE_OPTION_FIELDS = [
    "optimal_water_type",
    "location_suitability",
    "climate_suitability",
    "soil_type",
]

RESOURCE_OPTION_FIELDS = ["resource_requirements"]

MAINTENANCE_KEYS = {
    "maintenance",
    "maintenance_requirements",
    "o_m",
    "om",
    "operation",
    "operations",
    "operation_maintenance",
    "operations_maintenance",
}
COMPLEXITY_KEYS = {
    "complexity",
    "implementation",
    "implementation_complexity",
    "construction",
    "resource_requirements",
    "resources",
}
COST_KEYS = {
    "cost",
    "capital_cost",
    "operating_cost",
    "capex",
    "opex",
    "resource",
    "resources",
    "resource_requirements",
}
CO_BENEFIT_KEYS = {
    "co_benefit",
    "co_benefits",
    "cobenefit",
    "cobenefits",
    "biodiversity",
    "ecosystem",
    "ecosystem_services",
    "habitat",
    "amenity",
    "carbon",
}


@dataclass(slots=True)
class McdaMatrixRow:
    """Raw matrix row for one eligible or data-pending NbS candidate."""

    nbs_id: int | None
    nbs_name: str | None
    eligibility_status: str
    supported_treatment_needs: list[str] = field(default_factory=list)
    criteria_values: dict[str, Any] = field(default_factory=dict)
    missing_criteria: list[str] = field(default_factory=list)
    caution_flags: list[str] = field(default_factory=list)
    source_ids: list[int] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class McdaMatrixBundle:
    """Raw Step F matrix bundle for future MCDA/TOPSIS preparation."""

    use_case: str
    treatment_need_groups: list[str] = field(default_factory=list)
    row_count: int = 0
    excluded_ineligible_count: int = 0
    criteria_names: list[str] = field(default_factory=list)
    rows: list[McdaMatrixRow] = field(default_factory=list)
    missing_criteria_summary: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    weights_status: str = WEIGHTS_NOT_APPLIED

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["rows"] = [row.to_dict() for row in self.rows]
        return payload


class McdaMatrixBuilder:
    """Prepare raw MCDA matrix rows from Step E candidate filter output."""

    def __init__(self, nbs_provider: NbsCandidateProvider) -> None:
        self.nbs_provider = nbs_provider

    @classmethod
    def from_session(cls, session: Any) -> "McdaMatrixBuilder":
        """Create the builder using the production NbsCatalogService layer."""

        from app.services.nbs_catalog_service import NbsCatalogService

        return cls(NbsCatalogService(session))

    def build(self, candidate_bundle: CandidateFilterBundle) -> McdaMatrixBundle:
        """Build raw matrix inputs without normalization, weights, or ranking."""

        rows: list[McdaMatrixRow] = []
        warnings = list(candidate_bundle.warnings)
        excluded_ineligible_count = 0

        for candidate in candidate_bundle.results:
            if candidate.eligibility_status == INELIGIBLE:
                excluded_ineligible_count += 1
                continue
            if candidate.eligibility_status not in MATRIX_ELIGIBILITY_STATUSES:
                warnings.append(
                    "Skipped candidate with unsupported eligibility_status: "
                    f"{candidate.eligibility_status}."
                )
                continue
            rows.append(self._build_row(candidate))

        if not rows:
            warnings.append(
                "No eligible or data-pending candidates were available for MCDA matrix preparation."
            )

        return McdaMatrixBundle(
            use_case=candidate_bundle.use_case,
            treatment_need_groups=list(candidate_bundle.treatment_need_groups),
            row_count=len(rows),
            excluded_ineligible_count=excluded_ineligible_count,
            criteria_names=_criteria_names(rows),
            rows=rows,
            missing_criteria_summary=_missing_criteria_summary(rows),
            warnings=warnings,
            weights_status=WEIGHTS_NOT_APPLIED,
        )

    def _build_row(self, candidate: CandidateFilterResult) -> McdaMatrixRow:
        """Build one raw matrix row from candidate and profile data."""

        profile = (
            self.nbs_provider.get_full_nbs_profile(candidate.nbs_id)
            if candidate.nbs_id is not None
            else {}
        )
        option = _as_dict(profile.get("option"))
        removal_rows = _as_dict_list(profile.get("removal_efficiencies"))
        implementation_rows = _as_dict_list(profile.get("implementation"))
        footprint_rows = _as_dict_list(profile.get("footprint"))
        criteria_rows = _as_dict_list(profile.get("criteria"))

        criteria_values = _criteria_values(
            option=option,
            removal_rows=removal_rows,
            implementation_rows=implementation_rows,
            footprint_rows=footprint_rows,
            criteria_rows=criteria_rows,
        )
        missing_criteria = [
            name for name in RAW_CRITERIA_NAMES if name not in criteria_values
        ]
        source_ids = _collect_source_ids(
            candidate.evidence_source_ids,
            candidate.implementation_source_ids,
            [option],
            removal_rows,
            implementation_rows,
            footprint_rows,
            criteria_rows,
        )
        notes = [
            "Step F prepares raw MCDA matrix data only; no normalization, "
            "weights, TOPSIS, ranking, match score, or confidence score was "
            "calculated."
        ]
        missing_sections = [
            normalize_text(section)
            for section in profile.get("missing_sections", [])
            if normalize_text(section)
        ]
        if missing_sections:
            notes.append(
                "Provider reported missing profile sections: "
                + ", ".join(missing_sections)
                + "."
            )

        return McdaMatrixRow(
            nbs_id=candidate.nbs_id,
            nbs_name=candidate.nbs_name or normalize_text(option.get("solution")),
            eligibility_status=candidate.eligibility_status,
            supported_treatment_needs=list(candidate.supported_treatment_needs),
            criteria_values=criteria_values,
            missing_criteria=missing_criteria,
            caution_flags=list(candidate.caution_flags),
            source_ids=source_ids,
            notes=notes,
        )


def _criteria_values(
    *,
    option: dict[str, Any],
    removal_rows: list[dict[str, Any]],
    implementation_rows: list[dict[str, Any]],
    footprint_rows: list[dict[str, Any]],
    criteria_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Collect available raw criteria buckets from provider/profile data."""

    values: dict[str, Any] = {}

    if removal_rows:
        values["removal_evidence"] = {
            "row_count": len(removal_rows),
            "parameters": _unique_text_values(row.get("parameter") for row in removal_rows),
            "rows_with_numeric_efficiency": sum(
                _has_numeric_efficiency(row) for row in removal_rows
            ),
            "raw_rows": removal_rows,
        }

    if footprint_rows:
        values["footprint"] = {
            "row_count": len(footprint_rows),
            "raw_rows": footprint_rows,
        }

    site_values = {
        field_name: option.get(field_name)
        for field_name in SITE_OPTION_FIELDS
        if _has_value(option.get(field_name))
    }
    if site_values:
        values["climate_site_suitability"] = site_values

    cost_values = _option_values(option, RESOURCE_OPTION_FIELDS)
    cost_rows = _matching_criteria_rows(criteria_rows, COST_KEYS)
    if cost_values or cost_rows:
        values["cost_indicator"] = {
            "option_fields": cost_values,
            "criteria_rows": cost_rows,
        }

    maintenance_rows = _matching_criteria_rows(criteria_rows, MAINTENANCE_KEYS)
    maintenance_text = _unique_text_values(
        row.get("maintenance_requirements") for row in implementation_rows
    )
    if maintenance_rows or maintenance_text:
        values["maintenance_indicator"] = {
            "maintenance_requirements": maintenance_text,
            "criteria_rows": maintenance_rows,
        }

    complexity_rows = _matching_criteria_rows(criteria_rows, COMPLEXITY_KEYS)
    implementation_steps = _unique_text_values(
        row.get("implementation_steps") for row in implementation_rows
    )
    if complexity_rows or implementation_steps:
        values["implementation_complexity"] = {
            "implementation_steps_available": bool(implementation_steps),
            "criteria_rows": complexity_rows,
        }

    co_benefit_rows = _matching_criteria_rows(criteria_rows, CO_BENEFIT_KEYS)
    if co_benefit_rows:
        values["co_benefit_indicator"] = {
            "criteria_rows": co_benefit_rows,
        }

    if criteria_rows:
        values["catalogue_criteria"] = {
            "row_count": len(criteria_rows),
            "raw_rows": criteria_rows,
        }

    return values


def _criteria_names(rows: list[McdaMatrixRow]) -> list[str]:
    """Collect raw criteria names present in at least one matrix row."""

    names: list[str] = []
    for row in rows:
        for name in row.criteria_values:
            _append_once(names, name)
    return names


def _missing_criteria_summary(rows: list[McdaMatrixRow]) -> dict[str, int]:
    """Count missing raw criteria buckets across matrix rows."""

    summary: dict[str, int] = {}
    for row in rows:
        for name in row.missing_criteria:
            summary[name] = summary.get(name, 0) + 1
    return summary


def _matching_criteria_rows(
    rows: list[dict[str, Any]],
    target_keys: set[str],
) -> list[dict[str, Any]]:
    """Return criteria rows whose explicit criterion text matches target keys."""

    matches = []
    for row in rows:
        keys = _text_keys(row.get("criterion"))
        if keys.intersection(target_keys):
            matches.append(row)
    return matches


def _text_keys(value: Any) -> set[str]:
    """Return transparent normalized tokens for a simple text field."""

    key = normalize_match_key(value)
    if not key:
        return set()
    return {key, *key.split("_")}


def _option_values(option: dict[str, Any], field_names: list[str]) -> dict[str, Any]:
    """Return non-empty option fields exactly as provided by the catalogue."""

    return {
        field_name: option.get(field_name)
        for field_name in field_names
        if _has_value(option.get(field_name))
    }


def _as_dict(value: Any) -> dict[str, Any]:
    """Return a dictionary or an empty dictionary for missing profile sections."""

    return value if isinstance(value, dict) else {}


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    """Return a list of dictionaries from a provider section."""

    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _collect_source_ids(*groups: Any) -> list[int]:
    """Collect unique source IDs from raw profile sections and Step E output."""

    source_ids: list[int] = []
    for group in groups:
        if group is None:
            continue
        if isinstance(group, list):
            for item in group:
                if isinstance(item, dict):
                    _append_source_id(source_ids, item.get("source_id"))
                else:
                    _append_source_id(source_ids, item)
        elif isinstance(group, dict):
            _append_source_id(source_ids, group.get("source_id"))
        else:
            _append_source_id(source_ids, group)
    return source_ids


def _append_source_id(source_ids: list[int], value: Any) -> None:
    """Append one source ID if it can be read as an integer."""

    if value is None:
        return
    try:
        source_id = int(value)
    except (TypeError, ValueError):
        return
    if source_id not in source_ids:
        source_ids.append(source_id)


def _unique_text_values(values: Any) -> list[str]:
    """Collect unique non-empty text values while preserving source wording."""

    result: list[str] = []
    for value in values:
        text = normalize_text(value)
        if text and text not in result:
            result.append(text)
    return result


def _has_numeric_efficiency(row: dict[str, Any]) -> bool:
    """Return whether a raw removal row has a numeric efficiency range value."""

    return _as_float(row.get("eff_low")) is not None or _as_float(row.get("eff_high")) is not None


def _as_float(value: Any) -> float | None:
    """Convert a value to float without accepting booleans."""

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

"""Step E engine for NbS candidate eligibility filtering.

This module checks whether nature-based solution catalogue options are eligible,
ineligible, or data-pending for treatment need groups from Step D. It is a hard
filter only. It does not create final recommendations, rank candidates,
calculate match/confidence scores, use TOPSIS/AHP, recommend plants, or classify
health risk.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from app.engines.input_normalization import normalize_match_key, normalize_text
from app.engines.treatment_need import TreatmentNeedBundle


ELIGIBLE = "eligible"
INELIGIBLE = "ineligible"
DATA_PENDING = "data_pending"

# Explicit treatment-need to parameter mapping. These are transparent matching
# keys only; the engine does not use fuzzy matching or hidden aliases.
NEED_PARAMETER_KEYS = {
    "organic_load": {"bod", "cod"},
    "solids": {
        "tss",
        "turbidity",
        "suspended_solids",
        "total_suspended_solids",
    },
    "nutrients": {
        "nitrate",
        "phosphate",
        "ammonia",
        "nitrogen",
        "total_nitrogen",
        "phosphorus",
        "total_phosphorus",
    },
    "pathogens": {
        "fecal_coliform",
        "faecal_coliform",
        "total_coliform",
        "e._coli",
        "e_coli",
    },
    "salinity": {"ec", "tds", "chloride", "salinity", "sodium", "sar"},
    "metals": {
        "iron",
        "lead",
        "chromium",
        "cadmium",
        "arsenic",
        "mercury",
        "manganese",
        "heavy_metals",
    },
    "ph_correction": {"ph"},
    "oxygen_deficit": {"do", "dissolved_oxygen"},
    "general_water_quality": {"water_quality_index", "general_water_quality"},
}

PARAMETER_TO_NEED_GROUP = {
    parameter: need_group
    for need_group, parameters in NEED_PARAMETER_KEYS.items()
    for parameter in parameters
}

CATALOGUE_SUPPORT_FIELDS = {
    "supported_treatment_need",
    "supported_treatment_needs",
    "treatment_need",
    "treatment_needs",
}

OPEN_CONTACT_KEYS = {
    "open",
    "pond",
    "lagoon",
    "surface_flow",
    "free_water_surface",
    "open_water",
    "public_contact",
}
FOOD_CHAIN_KEYS = {
    "aquaculture",
    "fish",
    "food_chain",
    "edible",
    "crop",
    "harvest",
}
INFILTRATION_KEYS = {
    "infiltration",
    "soak",
    "recharge",
    "percolation",
    "leach",
}
STEEP_SLOPE_KEYS = {"steep_slope", "steep", "slope_sensitive"}
POOR_SOIL_KEYS = {
    "poor_soil",
    "low_infiltration",
    "clay",
    "impermeable",
    "waterlogging",
}
DRINKING_USE_CASE_KEYS = {
    "drinking",
    "drinking_domestic",
    "domestic",
    "potable",
}


@dataclass(slots=True)
class CandidateFilterResult:
    """Eligibility result for one NbS catalogue candidate."""

    nbs_id: int | None
    nbs_name: str | None
    eligibility_status: str
    supported_treatment_needs: list[str] = field(default_factory=list)
    unsupported_treatment_needs: list[str] = field(default_factory=list)
    data_pending_reasons: list[str] = field(default_factory=list)
    exclusion_reasons: list[str] = field(default_factory=list)
    caution_flags: list[str] = field(default_factory=list)
    evidence_source_ids: list[int] = field(default_factory=list)
    implementation_source_ids: list[int] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class CandidateFilterBundle:
    """Collection of Step E candidate filter results."""

    use_case: str
    selected_source_type: str
    treatment_need_groups: list[str] = field(default_factory=list)
    candidate_count: int = 0
    eligible_count: int = 0
    ineligible_count: int = 0
    data_pending_count: int = 0
    results: list[CandidateFilterResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["results"] = [result.to_dict() for result in self.results]
        return payload


class NbsCandidateProvider(Protocol):
    """Small provider interface needed by the candidate filtering engine."""

    def list_options(self) -> list[dict[str, Any]]:
        """Return raw NbS options."""

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return raw option, evidence, implementation, footprint, and criteria."""


class CandidateFilteringEngine:
    """Evaluate candidate NbS eligibility from treatment need groups only."""

    def __init__(self, nbs_provider: NbsCandidateProvider) -> None:
        self.nbs_provider = nbs_provider

    @classmethod
    def from_session(cls, session: Any) -> "CandidateFilteringEngine":
        """Create the engine using the production NbsCatalogService layer."""

        from app.services import NbsCatalogService

        return cls(NbsCatalogService(session))

    def filter_candidates(
        self,
        treatment_bundle: TreatmentNeedBundle,
    ) -> CandidateFilterBundle:
        """Return eligibility results without ranking or recommendations."""

        treatment_need_groups = _treatment_need_groups(treatment_bundle)
        warnings = list(treatment_bundle.warnings)
        if not treatment_need_groups:
            warnings.append(
                "No classified treatment need groups were available for candidate filtering."
            )

        options = self.nbs_provider.list_options()
        results = [
            self._evaluate_option(option, treatment_bundle, treatment_need_groups)
            for option in options
        ]
        return CandidateFilterBundle(
            use_case=treatment_bundle.use_case,
            selected_source_type=treatment_bundle.selected_source_type,
            treatment_need_groups=treatment_need_groups,
            candidate_count=len(results),
            eligible_count=sum(
                result.eligibility_status == ELIGIBLE for result in results
            ),
            ineligible_count=sum(
                result.eligibility_status == INELIGIBLE for result in results
            ),
            data_pending_count=sum(
                result.eligibility_status == DATA_PENDING for result in results
            ),
            results=results,
            warnings=warnings,
        )

    def _evaluate_option(
        self,
        option: dict[str, Any],
        treatment_bundle: TreatmentNeedBundle,
        treatment_need_groups: list[str],
    ) -> CandidateFilterResult:
        """Evaluate one candidate using raw catalogue/evidence fields."""

        nbs_id = _option_id(option)
        profile = self.nbs_provider.get_full_nbs_profile(nbs_id) if nbs_id else {}
        profile_option = profile.get("option") or option
        removal_rows = list(profile.get("removal_efficiencies") or [])
        implementation_rows = list(profile.get("implementation") or [])
        footprint_rows = list(profile.get("footprint") or [])
        criteria_rows = list(profile.get("criteria") or [])

        evidence_groups, pending_evidence_groups = _need_groups_from_removal(
            removal_rows,
        )
        catalogue_groups = _need_groups_from_catalogue(profile)
        supported = [
            need_group
            for need_group in treatment_need_groups
            if need_group in evidence_groups or need_group in catalogue_groups
        ]
        unsupported = [
            need_group
            for need_group in treatment_need_groups
            if need_group not in supported
        ]

        data_pending_reasons: list[str] = []
        exclusion_reasons: list[str] = []
        caution_flags: list[str] = []
        notes = [
            "Step E checks eligibility only; no ranking or final recommendation "
            "was calculated."
        ]

        missing_sections = list(profile.get("missing_sections") or [])
        if "option" in missing_sections or not profile_option:
            data_pending_reasons.append("Catalogue option details are missing.")
        if not removal_rows and not catalogue_groups:
            data_pending_reasons.append(
                "No removal-efficiency evidence or explicit catalogue support is available."
            )
        if pending_evidence_groups:
            data_pending_reasons.append(
                "Removal-efficiency rows exist without numeric efficiency values for: "
                + ", ".join(pending_evidence_groups)
                + "."
            )
        catalogue_only_groups = [
            need_group
            for need_group in supported
            if need_group in catalogue_groups and need_group not in evidence_groups
        ]
        if catalogue_only_groups:
            data_pending_reasons.append(
                "Catalogue support exists but pollutant-specific removal evidence "
                "is missing for: "
                + ", ".join(catalogue_only_groups)
                + "."
            )
        if "implementation" in missing_sections or not implementation_rows:
            data_pending_reasons.append("Implementation guidance is missing.")

        if not supported and removal_rows:
            exclusion_reasons.append(
                "No explicit support was found for the requested treatment need groups."
            )

        evidence_source_ids = _collect_source_ids(
            [profile_option],
            removal_rows,
            footprint_rows,
            criteria_rows,
        )
        implementation_source_ids = _collect_source_ids(implementation_rows)
        text_keys = _profile_text_keys(
            profile_option,
            implementation_rows,
            footprint_rows,
            criteria_rows,
        )
        _add_caution_flags(
            caution_flags=caution_flags,
            treatment_need_groups=treatment_need_groups,
            use_case=treatment_bundle.use_case,
            text_keys=text_keys,
        )

        return CandidateFilterResult(
            nbs_id=nbs_id,
            nbs_name=normalize_text(profile_option.get("solution") if profile_option else None),
            eligibility_status=_eligibility_status(
                supported,
                exclusion_reasons,
                data_pending_reasons,
            ),
            supported_treatment_needs=supported,
            unsupported_treatment_needs=unsupported,
            data_pending_reasons=data_pending_reasons,
            exclusion_reasons=exclusion_reasons,
            caution_flags=caution_flags,
            evidence_source_ids=evidence_source_ids,
            implementation_source_ids=implementation_source_ids,
            notes=notes,
        )


def _treatment_need_groups(treatment_bundle: TreatmentNeedBundle) -> list[str]:
    """Return unique treatment need group names from Step D output."""

    groups = []
    for treatment_need in treatment_bundle.treatment_needs:
        group = normalize_match_key(treatment_need.need_group)
        if group and group not in groups:
            groups.append(group)
    return groups


def _option_id(option: dict[str, Any]) -> int | None:
    """Return the integer NbS ID from common option fields."""

    for key in ("id", "nbs_id"):
        value = option.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    return None


def _need_groups_from_removal(
    rows: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    """Map removal-efficiency parameter rows to treatment need groups."""

    supported = []
    pending = []
    for row in rows:
        parameter_key = normalize_match_key(row.get("parameter"))
        need_group = PARAMETER_TO_NEED_GROUP.get(parameter_key or "")
        if not need_group:
            continue
        target = supported if _has_numeric_efficiency(row) else pending
        _append_once(target, need_group)
    return supported, pending


def _need_groups_from_catalogue(profile: dict[str, Any]) -> list[str]:
    """Return explicit treatment need support stated by catalogue fields."""

    groups = []
    option = profile.get("option") or {}
    for field_name in CATALOGUE_SUPPORT_FIELDS:
        _extend_need_groups(groups, option.get(field_name))
        _extend_need_groups(groups, profile.get(field_name))
    for row in profile.get("criteria") or []:
        criterion_key = normalize_match_key(row.get("criterion"))
        if criterion_key in CATALOGUE_SUPPORT_FIELDS:
            _extend_need_groups(groups, row.get("value_qual"))
    return groups


def _extend_need_groups(groups: list[str], raw_value: Any) -> None:
    """Parse explicit treatment need values from lists or simple text."""

    if raw_value in (None, ""):
        return
    values = raw_value if isinstance(raw_value, list) else _split_text_values(raw_value)
    for value in values:
        group = normalize_match_key(value)
        if group in NEED_PARAMETER_KEYS and group not in groups:
            groups.append(group)


def _split_text_values(value: Any) -> list[str]:
    """Split simple catalogue support lists without fuzzy matching."""

    text = normalize_text(value)
    if text is None:
        return []
    normalized = text.replace(";", ",").replace("|", ",").replace("/", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def _has_numeric_efficiency(row: dict[str, Any]) -> bool:
    """Return whether a removal row has at least one numeric efficiency value."""

    return _as_float(row.get("eff_low")) is not None or _as_float(row.get("eff_high")) is not None


def _eligibility_status(
    supported: list[str],
    exclusion_reasons: list[str],
    data_pending_reasons: list[str],
) -> str:
    """Choose an eligibility status without scoring or ranking."""

    if exclusion_reasons:
        return INELIGIBLE
    if data_pending_reasons:
        return DATA_PENDING
    if supported:
        return ELIGIBLE
    return DATA_PENDING


def _profile_text_keys(
    option: dict[str, Any],
    implementation_rows: list[dict[str, Any]],
    footprint_rows: list[dict[str, Any]],
    criteria_rows: list[dict[str, Any]],
) -> set[str]:
    """Collect transparent text keys used for hard caution checks."""

    text_parts = []
    for row in [option, *implementation_rows, *footprint_rows, *criteria_rows]:
        for value in row.values():
            if isinstance(value, str):
                text_parts.append(value)
    keys = set()
    for part in text_parts:
        normalized = normalize_match_key(part)
        if normalized:
            keys.update(piece for piece in normalized.split("_") if piece)
            keys.add(normalized)
    return keys


def _add_caution_flags(
    *,
    caution_flags: list[str],
    treatment_need_groups: list[str],
    use_case: str,
    text_keys: set[str],
) -> None:
    """Add transparent hard-filter cautions when source fields support them."""

    if "pathogens" in treatment_need_groups and _has_any(text_keys, OPEN_CONTACT_KEYS):
        _append_once(
            caution_flags,
            "Pathogen treatment need with open-contact/open-water system; "
            "pre-treatment, disinfection, or restricted access may be required.",
        )
    if "metals" in treatment_need_groups and _has_any(text_keys, FOOD_CHAIN_KEYS):
        _append_once(
            caution_flags,
            "Metal treatment need with food-chain or aquaculture pathway; "
            "controlled disposal and expert review may be required.",
        )
    if (
        {"pathogens", "metals"}.intersection(treatment_need_groups)
        and _has_any(text_keys, INFILTRATION_KEYS)
    ):
        _append_once(
            caution_flags,
            "Infiltration system with untreated pathogen or toxic water; "
            "groundwater protection review may be required.",
        )
    if _has_any(text_keys, STEEP_SLOPE_KEYS):
        _append_once(
            caution_flags,
            "Catalogue or implementation fields mention steep-slope sensitivity.",
        )
    if _has_any(text_keys, POOR_SOIL_KEYS):
        _append_once(
            caution_flags,
            "Catalogue or implementation fields mention poor-soil or infiltration limits.",
        )
    if normalize_match_key(use_case) in DRINKING_USE_CASE_KEYS:
        _append_once(
            caution_flags,
            "Drinking/domestic target use case may require engineered treatment, "
            "disinfection, and regulatory validation beyond NbS alone.",
        )


def _has_any(text_keys: set[str], target_keys: set[str]) -> bool:
    """Return whether any explicit normalized caution key is present."""

    return bool(text_keys.intersection(target_keys))


def _collect_source_ids(*groups: list[dict[str, Any]]) -> list[int]:
    """Collect source IDs from raw catalogue and evidence records."""

    source_ids = []
    for group in groups:
        for row in group:
            value = row.get("source_id") if isinstance(row, dict) else None
            if value is None:
                continue
            try:
                source_id = int(value)
            except (TypeError, ValueError):
                continue
            if source_id not in source_ids:
                source_ids.append(source_id)
    return source_ids


def _as_float(value: Any) -> float | None:
    """Convert a value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _append_once(values: list[str], value: str) -> None:
    """Append a value once while preserving order."""

    if value not in values:
        values.append(value)

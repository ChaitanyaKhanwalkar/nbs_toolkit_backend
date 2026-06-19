"""A0 applicability filter driven by canonical database rules.

This engine applies placement and safety rules before MCDA/TOPSIS ranking. The
rules come from `nbs_applicability_rules`; this module only interprets their
target, factor, operator, and action fields. It does not invent scientific
thresholds, final weights, health-risk values, or citations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Protocol

from app.engines.candidate_filtering import (
    ELIGIBLE,
    INELIGIBLE,
    CandidateFilterBundle,
    CandidateFilterResult,
)
from app.engines.input_normalization import InputContext, normalize_match_key, normalize_text


APPLICABILITY_ALLOWED = "allowed"
APPLICABILITY_REJECTED = "rejected"
APPLICABILITY_CONDITIONAL = "conditional"

HARD_RULE_TYPES = {"hard_filter", "hard_safety_filter"}
CONDITIONAL_RULE_TYPES = {"conditional_filter", "conditional_allow"}
MODIFIER_RULE_TYPES = {"scoring_modifier", "confidence_modifier"}

# Global hard-safety rules are usually placement/legal warnings, not a reason
# to remove every option. Keep explicit no-go actions as real rejections.
GLOBAL_ADVISORY_ACTIONS = {
    "do_not_claim_standalone_potable_treatment",
    "require_etp_cetp_pretreatment",
    "treat_before_entry_not_inside_waterbody",
    "direct_user_to_cetp_etp_first",
}
GLOBAL_REJECT_ACTIONS = {"do_not_recommend_simple_nbs_standalone"}


class ApplicabilityRuleProvider(Protocol):
    """Small provider interface for canonical A0 rules."""

    def list_applicability_rules(self, *, active_only: bool = True) -> list[dict[str, Any]]:
        """Return active A0 applicability rules from the canonical database."""


@dataclass(slots=True)
class ApplicabilityRuleHit:
    """One canonical rule that matched a candidate and input context."""

    rule_id: str
    rule_type: str
    severity: str
    action: str
    factor_name: str
    user_message: str
    technical_reason: str
    score_modifier: float | None = None
    confidence_modifier: float | None = None
    target_level: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for schemas, tests, or logs."""

        return asdict(self)


@dataclass(slots=True)
class CandidateApplicabilityResult:
    """A0 applicability outcome for one candidate."""

    nbs_id: int | None
    nbs_name: str | None
    applicability_status: str
    triggered_rules: list[ApplicabilityRuleHit] = field(default_factory=list)
    user_messages: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    technical_reasons: list[str] = field(default_factory=list)
    score_modifier_total: float = 0.0
    confidence_modifier_total: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for schemas, tests, or logs."""

        payload = asdict(self)
        payload["triggered_rules"] = [
            rule_hit.to_dict() for rule_hit in self.triggered_rules
        ]
        return payload


@dataclass(slots=True)
class ApplicabilityFilterBundle:
    """A0 applicability results plus a filtered Step E candidate bundle."""

    use_case: str
    result_count: int = 0
    allowed_count: int = 0
    rejected_count: int = 0
    conditional_count: int = 0
    results: list[CandidateApplicabilityResult] = field(default_factory=list)
    rejected_options: list[CandidateApplicabilityResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary without the filtered candidate object."""

        payload = asdict(self)
        payload["results"] = [result.to_dict() for result in self.results]
        payload["rejected_options"] = [
            result.to_dict() for result in self.rejected_options
        ]
        return payload


class ApplicabilityFilterEngine:
    """Apply active canonical applicability rules before TOPSIS ranking."""

    def __init__(self, rule_provider: ApplicabilityRuleProvider | None = None) -> None:
        """Store the rule provider; tests may pass explicit rules instead."""

        self.rule_provider = rule_provider

    def apply(
        self,
        candidate_bundle: CandidateFilterBundle,
        *,
        input_context: InputContext | None = None,
        site_context: dict[str, Any] | None = None,
        rules: list[dict[str, Any]] | None = None,
    ) -> tuple[ApplicabilityFilterBundle, CandidateFilterBundle]:
        """Return A0 results and a candidate bundle filtered by hard rules."""

        active_rules = list(rules) if rules is not None else self._load_rules()
        context = _rule_context(input_context, site_context, candidate_bundle)
        warnings = list(candidate_bundle.warnings)
        notes = [
            "A0 applicability rules were applied before MCDA/TOPSIS ranking.",
            "Train-targeted rules are kept in the canonical DB but skipped in "
            "this NbS-option workflow until train-level ranking is wired.",
        ]
        if not active_rules:
            warnings.append(
                "No active nbs_applicability_rules were available; A0 filtering was skipped."
            )

        results: list[CandidateApplicabilityResult] = []
        filtered_candidates: list[CandidateFilterResult] = []
        for candidate in candidate_bundle.results:
            result = self._evaluate_candidate(candidate, active_rules, context)
            results.append(result)
            filtered_candidates.append(_filtered_candidate(candidate, result))

        filtered_bundle = replace(
            candidate_bundle,
            results=filtered_candidates,
            eligible_count=sum(
                candidate.eligibility_status == ELIGIBLE
                for candidate in filtered_candidates
            ),
            ineligible_count=sum(
                candidate.eligibility_status == INELIGIBLE
                for candidate in filtered_candidates
            ),
            data_pending_count=sum(
                candidate.eligibility_status not in {ELIGIBLE, INELIGIBLE}
                for candidate in filtered_candidates
            ),
            warnings=warnings,
        )
        rejected_options = [
            result
            for result in results
            if result.applicability_status == APPLICABILITY_REJECTED
        ]
        bundle = ApplicabilityFilterBundle(
            use_case=candidate_bundle.use_case,
            result_count=len(results),
            allowed_count=sum(
                result.applicability_status == APPLICABILITY_ALLOWED
                for result in results
            ),
            rejected_count=len(rejected_options),
            conditional_count=sum(
                result.applicability_status == APPLICABILITY_CONDITIONAL
                for result in results
            ),
            results=results,
            rejected_options=rejected_options,
            warnings=warnings,
            notes=notes,
        )
        return bundle, filtered_bundle

    def _load_rules(self) -> list[dict[str, Any]]:
        """Load active DB rules when a provider was supplied."""

        if self.rule_provider is None:
            return []
        return self.rule_provider.list_applicability_rules(active_only=True)

    def _evaluate_candidate(
        self,
        candidate: CandidateFilterResult,
        rules: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> CandidateApplicabilityResult:
        """Evaluate all rules against one candidate."""

        hits: list[ApplicabilityRuleHit] = []
        for rule in rules:
            if _is_train_rule(rule):
                continue
            if not _target_matches(candidate, rule):
                continue
            if not _factor_matches(rule, context):
                continue
            hit = _rule_hit(rule)
            if _global_rule_should_be_advisory(hit):
                hit = replace(hit, rule_type="conditional_filter")
            hits.append(hit)

        hard_hits = [
            hit for hit in hits if normalize_match_key(hit.rule_type) in HARD_RULE_TYPES
        ]
        conditional_hits = [
            hit
            for hit in hits
            if normalize_match_key(hit.rule_type) in CONDITIONAL_RULE_TYPES
        ]
        modifier_hits = [
            hit for hit in hits if normalize_match_key(hit.rule_type) in MODIFIER_RULE_TYPES
        ]

        if hard_hits:
            status = APPLICABILITY_REJECTED
        elif conditional_hits:
            status = APPLICABILITY_CONDITIONAL
        else:
            status = APPLICABILITY_ALLOWED

        all_visible_hits = [*hard_hits, *conditional_hits, *modifier_hits]
        return CandidateApplicabilityResult(
            nbs_id=candidate.nbs_id,
            nbs_name=candidate.nbs_name,
            applicability_status=status,
            triggered_rules=all_visible_hits,
            user_messages=_unique(hit.user_message for hit in all_visible_hits),
            caveats=_unique(
                hit.user_message
                for hit in [*conditional_hits, *modifier_hits]
            ),
            technical_reasons=_unique(
                hit.technical_reason for hit in all_visible_hits
            ),
            score_modifier_total=sum(
                hit.score_modifier or 0.0 for hit in all_visible_hits
            ),
            confidence_modifier_total=sum(
                hit.confidence_modifier or 0.0 for hit in all_visible_hits
            ),
        )


def _global_rule_should_be_advisory(hit: ApplicabilityRuleHit) -> bool:
    """Return True when a global hard rule should warn, not reject all options."""

    if normalize_match_key(hit.target_level) != "global":
        return False
    rule_type = normalize_match_key(hit.rule_type)
    if rule_type not in HARD_RULE_TYPES:
        return False
    action = normalize_match_key(hit.action)
    if action in GLOBAL_REJECT_ACTIONS:
        return False
    return action in GLOBAL_ADVISORY_ACTIONS or rule_type == "hard_safety_filter"

def _filtered_candidate(
    candidate: CandidateFilterResult,
    result: CandidateApplicabilityResult,
) -> CandidateFilterResult:
    """Return a copied candidate with A0 rejection/caveats applied."""

    exclusion_reasons = list(candidate.exclusion_reasons)
    caution_flags = list(candidate.caution_flags)
    notes = list(candidate.notes)
    for message in result.user_messages:
        _append_once(caution_flags, message)
    for reason in result.technical_reasons:
        _append_once(notes, f"A0 applicability: {reason}")
    status = candidate.eligibility_status
    if result.applicability_status == APPLICABILITY_REJECTED:
        status = INELIGIBLE
        for reason in result.user_messages:
            _append_once(exclusion_reasons, reason)
    return replace(
        candidate,
        eligibility_status=status,
        exclusion_reasons=exclusion_reasons,
        caution_flags=caution_flags,
        notes=notes,
    )


def _rule_context(
    input_context: InputContext | None,
    site_context: dict[str, Any] | None,
    candidate_bundle: CandidateFilterBundle,
) -> dict[str, Any]:
    """Build normalized factor values from request and resolved site context."""

    normalized_input = input_context.normalized_input if input_context else {}
    raw_context = normalized_input.get("context") or {}
    if not isinstance(raw_context, dict):
        raw_context = {}

    context: dict[str, Any] = {}
    context.update(raw_context)
    if site_context:
        context.update(site_context)

    measured_observations = normalized_input.get("measured_observations") or []
    selected_source_type = candidate_bundle.selected_source_type
    if measured_observations or selected_source_type in {"user_measured", "measured"}:
        context.setdefault("input_mode", "measured_water_quality_uploaded")
    elif selected_source_type in {"missing", "location_only"}:
        context.setdefault("input_mode", "location_only_no_water_data")

    if normalized_input.get("use_case"):
        context.setdefault("use_case", normalized_input["use_case"])
    return context


def _target_matches(candidate: CandidateFilterResult, rule: dict[str, Any]) -> bool:
    """Return whether a rule targets this NbS candidate."""

    target_level = normalize_match_key(rule.get("target_level"))
    if target_level == "global":
        return True
    if target_level == "nbs":
        return _ids_match(candidate.nbs_id, rule.get("nbs_id")) or _text_matches(
            candidate.nbs_name,
            rule.get("nbs_solution"),
        )
    if target_level == "family":
        return _text_matches(
            _candidate_family(candidate),
            rule.get("nbs_family"),
        ) or _ids_match(_candidate_family_id(candidate), rule.get("nbs_family_id"))
    return False


def _factor_matches(rule: dict[str, Any], context: dict[str, Any]) -> bool:
    """Return whether the current input/site context triggers a rule."""

    factor_name = normalize_match_key(rule.get("factor_name"))
    if not factor_name:
        return False

    if not _intervention_position_matches(rule, context):
        return False

    factor_value = _factor_value(factor_name, context)
    if factor_value is None:
        return False

    category_value = normalize_match_key(rule.get("category_value"))
    if category_value:
        return normalize_match_key(factor_value) == category_value

    operator = normalize_text(rule.get("operator"))
    value_min = _as_float(rule.get("value_min"))
    value_max = _as_float(rule.get("value_max"))
    numeric_value = _as_float(factor_value)
    if numeric_value is None:
        return False

    if operator == ">=" and value_min is not None:
        return numeric_value >= value_min
    if operator == ">" and value_min is not None:
        return numeric_value > value_min
    if operator == "<=" and value_max is not None:
        return numeric_value <= value_max
    if operator == "<" and value_max is not None:
        return numeric_value < value_max
    if operator in {"=", "=="} and value_min is not None:
        return numeric_value == value_min
    if value_min is not None and value_max is not None:
        return value_min <= numeric_value <= value_max
    return False


def _intervention_position_matches(rule: dict[str, Any], context: dict[str, Any]) -> bool:
    """Return whether a DB rule's intervention position is active."""

    rule_position = normalize_match_key(rule.get("intervention_position"))
    if not rule_position:
        return True
    active_position = normalize_match_key(
        context.get("intervention_position")
        or context.get("placement")
        or context.get("placement_context")
    )
    return active_position == rule_position


def _factor_value(factor_name: str, context: dict[str, Any]) -> Any:
    """Read one factor value from explicit request/site context aliases."""

    aliases = {
        "stream_order": ["stream_order", "stream_order_strahler", "ord_stra"],
        "slope": ["slope", "slope_class", "slope_category"],
        "builtup_lulc": ["builtup_lulc", "builtup_class"],
        "agriculture_lulc": ["agriculture_lulc", "agriculture_class"],
        "forest_lulc": ["forest_lulc", "forest_class"],
        "land_availability": ["land_availability", "land_available"],
        "pollution_source_type": ["pollution_source_type", "source_type"],
        "infrastructure_status": ["infrastructure_status"],
        "input_mode": ["input_mode"],
        "use_case": ["use_case"],
        "waterbody_context": ["waterbody_context"],
        "technology_scope": ["technology_scope"],
        "soil_infiltration": ["soil_infiltration", "infiltration_class"],
        "flood_risk": ["flood_risk"],
        "groundwater_depth": ["groundwater_depth"],
        "climate_seasonality": ["climate_seasonality"],
        "health_risk": ["health_risk"],
    }
    for key in aliases.get(factor_name, [factor_name]):
        value = context.get(key)
        if value not in (None, ""):
            return value
    return None


def _rule_hit(rule: dict[str, Any]) -> ApplicabilityRuleHit:
    """Convert one DB rule row to a visible rule hit."""

    return ApplicabilityRuleHit(
        rule_id=str(rule.get("rule_id") or ""),
        rule_type=str(rule.get("rule_type") or ""),
        severity=str(rule.get("severity") or ""),
        action=str(rule.get("action") or ""),
        factor_name=str(rule.get("factor_name") or ""),
        user_message=str(rule.get("user_message") or ""),
        technical_reason=str(rule.get("technical_reason") or ""),
        score_modifier=_as_float(rule.get("score_modifier")),
        confidence_modifier=_as_float(rule.get("confidence_modifier")),
        target_level=normalize_text(rule.get("target_level")),
    )


def _candidate_family(candidate: CandidateFilterResult) -> Any:
    """Read a family value attached by the candidate/provider when present."""

    return getattr(candidate, "nbs_family", None)


def _candidate_family_id(candidate: CandidateFilterResult) -> Any:
    """Read a family ID attached by the candidate/provider when present."""

    return getattr(candidate, "nbs_family_id", None)


def _is_train_rule(rule: dict[str, Any]) -> bool:
    """Return whether a rule targets train-level rows, not NbS option rows."""

    return normalize_match_key(rule.get("target_level")) == "train"


def _ids_match(left: Any, right: Any) -> bool:
    """Compare IDs after safe integer conversion."""

    left_id = _as_int(left)
    right_id = _as_int(right)
    return left_id is not None and left_id == right_id


def _text_matches(left: Any, right: Any) -> bool:
    """Compare normalized text values."""

    return bool(right) and normalize_match_key(left) == normalize_match_key(right)


def _as_int(value: Any) -> int | None:
    """Convert a value to int without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    """Convert a value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _unique(values: Any) -> list[str]:
    """Return unique non-empty text values while preserving order."""

    unique: list[str] = []
    for value in values:
        text = normalize_text(value)
        if text and text not in unique:
            unique.append(text)
    return unique


def _append_once(values: list[str], value: str) -> None:
    """Append one non-empty string once."""

    if value and value not in values:
        values.append(value)

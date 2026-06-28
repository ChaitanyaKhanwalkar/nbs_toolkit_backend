"""Canonical treatment-train applicability, MCDA, TOPSIS, and confidence.

This engine ranks the eight documented treatment trains. It reads criteria
weights and evidence through ``EngineDataRepository``. Missing evidence stays
unknown: unknown criterion values are median-imputed only for TOPSIS geometry,
are flagged in the response, and reduce confidence rather than becoming zero.
"""

from __future__ import annotations

from math import sqrt
from statistics import median
from typing import Any

from app.engines.applicability_filter import (
    CONDITIONAL_RULE_TYPES,
    HARD_RULE_TYPES,
    _factor_matches,
    _rule_hit,
    _target_matches,
)
from app.engines.candidate_filtering import CandidateFilterResult
from app.engines.input_normalization import normalize_match_key


METHOD_WARNING = (
    "Method: A0 safety/applicability screening -> final v1 AHP-Fuzzy AHP "
    "ensemble weighting -> TOPSIS treatment-train ranking -> confidence and "
    "design-readiness checks."
)
USE_CASES = ("drinking", "irrigation", "discharge_inland")

# These caps are conservative UX safeguards, not scientific certainty or
# expert-derived weights. The four-item panel is used only to describe input
# completeness; it does not claim that other source-specific parameters are
# unimportant.
KEY_SCREENING_PANEL = frozenset({"bod", "cod", "tss", "ph"})
CONFIDENCE_CAP_NO_DATA = 0.0
CONFIDENCE_CAP_ONE_PARAMETER = 0.35
CONFIDENCE_CAP_TWO_TO_THREE = 0.55
CONFIDENCE_CAP_INCOMPLETE_KEY_PANEL = 0.72
CONFIDENCE_CAP_COMPLETE_KEY_PANEL = 0.90
METHOD_CONFIDENCE_CAP = 0.90

# Global safety rules should normally guide the recommendation, not wipe out
# every train. Example: drinking use needs disinfection/advanced treatment;
# industrial wastewater needs ETP/CETP first; mainstem/reservoir sites need
# off-channel/source-control placement. These are advisory constraints unless
# the DB action is an explicit no-go.
GLOBAL_ADVISORY_ACTIONS = {
    "do_not_claim_standalone_potable_treatment",
    "require_etp_cetp_pretreatment",
    "treat_before_entry_not_inside_waterbody",
    "direct_user_to_cetp_etp_first",
}
GLOBAL_REJECT_ACTIONS = {"do_not_recommend_simple_nbs_standalone"}


class TrainRecommendationEngine:
    """Build ranked, explainable train recommendations from canonical data."""

    def __init__(self, repository: Any) -> None:
        self.repository = repository

    def rank(
        self,
        *,
        use_case: str,
        contaminant_gaps: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
        region_id: int | None = None,
        input_source_type: str | None = None,
    ) -> dict[str, Any]:
        """Return ranked and rejected trains for one transparent run."""

        context = dict(context or {})
        site = self.repository.get_site_attributes(region_id)
        context.update(_site_rule_context(site))
        context.setdefault("use_case", use_case)
        context.setdefault("input_mode", _input_mode(input_source_type))

        cards = self.repository.list_train_cards()
        steps = _group(self.repository.list_train_steps(), "train_id")
        performance = _group(self.repository.list_train_performance(), "train_id")
        matrix = _group(self.repository.list_engine_usecase_matrix(), "train_id")
        designs = _group(self.repository.list_train_component_designs(), "train_id")
        footprints = _group(self.repository.list_train_component_footprints(), "train_id")
        plants = _group(self.repository.list_train_plants(), "train_id")
        rules = self.repository.list_applicability_rules(active_only=True)
        weights = self.repository.list_criteria_weights(use_case)

        candidates: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        for card in cards:
            train_id = int(card["train_id"])
            applicability = _train_applicability(
                card,
                steps.get(train_id, []),
                rules,
                context,
            )
            item = {
                **card,
                "applicability_result": applicability,
                "all_use_case_verdicts": _all_use_case_verdicts(
                    matrix.get(train_id, [])
                ),
                "treatment_sequence": _treatment_sequence(steps.get(train_id, [])),
                "nbs_components": _nbs_components(steps.get(train_id, [])),
                "om_intensity": _om_intensity_label(
                    designs.get(train_id, []),
                    steps.get(train_id, []),
                ),
                "suitable_plants": plants.get(train_id, []),
                "selected_use_case": use_case,
                "evidence_source_ids": _evidence_ids(
                    card,
                    designs.get(train_id, []),
                    footprints.get(train_id, []),
                ),
            }
            all_use_cases_unknown = all(
                verdict.get("verdict") == "unknown"
                for verdict in item["all_use_case_verdicts"].values()
            )
            item["all_use_cases_unknown"] = all_use_cases_unknown
            item["use_case_assessment_status"] = (
                "needs_data_for_use_case_assessment"
                if all_use_cases_unknown
                else "partially_or_fully_assessed"
            )
            if applicability["status"] == "rejected":
                rejected.append(
                    {
                        "train_id": train_id,
                        "train_name": card.get("name"),
                        "reasons": applicability["user_messages"],
                        "technical_reasons": applicability["technical_reasons"],
                    }
                )
                continue

            criteria = _criteria(
                contaminant_gaps=contaminant_gaps,
                performance=performance.get(train_id, []),
                usecase_rows=matrix.get(train_id, []),
                use_case=use_case,
                applicability=applicability,
                context=context,
                footprint_rows=footprints.get(train_id, []),
                design_rows=designs.get(train_id, []),
                step_rows=steps.get(train_id, []),
            )
            sensitivity = _context_sensitivity(
                card=card,
                step_rows=steps.get(train_id, []),
                context=context,
                contaminant_gaps=contaminant_gaps,
            )
            criteria = _apply_sensitivity(criteria, sensitivity)
            confidence = _confidence(
                performance.get(train_id, []),
                item["evidence_source_ids"],
                input_source_type,
                site,
                applicability,
                criteria,
                contaminant_gaps,
                context,
            )
            item.update(
                {
                    "criteria_raw": criteria,
                    "confidence_score": confidence["score"],
                    "confidence_label": confidence["label"],
                    "confidence_factors": confidence["factors"],
                    "confidence_explanation": confidence["explanation"],
                    "confidence_cap": confidence["cap"],
                    "pollutant_gap_breakdown": _pollutant_gap_breakdown(
                        contaminant_gaps,
                        performance.get(train_id, []),
                        context,
                    ),
                    "caveats": _unique(
                        [
                            *applicability["caveats"],
                            *sensitivity["caveats"],
                            *confidence["caveats"],
                        ]
                    ),
                    "context_sensitivity": sensitivity,
                }
            )
            candidates.append(item)

        _apply_topsis(candidates, weights)
        candidates.sort(
            key=lambda row: (
                bool(row.get("all_use_cases_unknown")),
                -(row.get("match_score") or 0.0),
                row.get("train_id") or 0,
            )
        )
        for index, candidate in enumerate(candidates, start=1):
            candidate["rank"] = index
            candidate.update(
                _implementation_explanation(
                    candidate,
                    context=context,
                    contaminant_gaps=contaminant_gaps,
                    design_rows=designs.get(int(candidate["train_id"]), []),
                )
            )
            candidate["why_recommended"] = _why_recommended(candidate)

        return {
            "ranked_trains": candidates,
            "rejected_options": rejected,
            "conditional_count": sum(
                row["applicability_result"]["status"] == "conditional"
                for row in candidates
            ),
            "warnings": [METHOD_WARNING],
        }


def _train_applicability(
    card: dict[str, Any],
    steps: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate train-targeted and component-targeted canonical rules."""

    hits = []
    for rule in rules:
        target = normalize_match_key(rule.get("target_level"))
        target_matches = False
        if target == "global":
            target_matches = True
        elif target == "train":
            target_matches = (
                rule.get("train_id") == card.get("train_id")
                or normalize_match_key(rule.get("train_name"))
                == normalize_match_key(card.get("name"))
            )
        elif target in {"nbs", "family"}:
            target_matches = any(
                _target_matches(
                    CandidateFilterResult(
                        nbs_id=step.get("nbs_id"),
                        nbs_name=step.get("nbs_name"),
                        nbs_family=step.get("nbs_family"),
                        eligibility_status="eligible",
                    ),
                    rule,
                )
                for step in steps
                if step.get("nbs_id") is not None
            )
        matched = target_matches and _factor_matches(rule, context)
        industrial_advisory = (
            target_matches
            and rule.get("rule_id") in {"APP_RULE_029", "APP_RULE_030"}
            and normalize_match_key(
                context.get("pollution_source_type") or context.get("source_type")
            )
            == normalize_match_key(rule.get("category_value"))
        )
        if matched or industrial_advisory:
            hit = _rule_hit(rule).to_dict()
            hit["matched_target_level"] = target
            if industrial_advisory and not matched:
                hit["rule_type"] = "conditional_filter"
                hit["placement_advisory"] = True
            if _global_rule_should_be_advisory(hit):
                hit["original_rule_type"] = hit.get("rule_type")
                hit["rule_type"] = "conditional_filter"
                hit["global_safety_advisory"] = True
            hits.append(hit)

    hard = [
        hit
        for hit in hits
        if normalize_match_key(hit["rule_type"]) in HARD_RULE_TYPES
        and hit["matched_target_level"] in {"global", "train"}
    ]
    component_hard = [
        hit
        for hit in hits
        if normalize_match_key(hit["rule_type"]) in HARD_RULE_TYPES
        and hit["matched_target_level"] in {"nbs", "family"}
    ]
    conditional = [
        hit
        for hit in hits
        if normalize_match_key(hit["rule_type"]) in CONDITIONAL_RULE_TYPES
    ]
    status = (
        "rejected"
        if hard
        else "conditional"
        if conditional or component_hard
        else "allowed"
    )
    return {
        "status": status,
        "triggered_rules": hits,
        "user_messages": _unique([hit["user_message"] for hit in hits]),
        "technical_reasons": _unique([hit["technical_reason"] for hit in hits]),
        "caveats": _unique(
            [hit["user_message"] for hit in hits if hit not in hard]
        ),
        "score_modifier_total": sum(hit.get("score_modifier") or 0.0 for hit in hits),
        "confidence_modifier_total": sum(
            hit.get("confidence_modifier") or 0.0 for hit in hits
        ),
    }


def _global_rule_should_be_advisory(hit: dict[str, Any]) -> bool:
    """Return True when a global hard rule should warn, not reject all trains."""

    if normalize_match_key(hit.get("matched_target_level") or hit.get("target_level")) != "global":
        return False
    rule_type = normalize_match_key(hit.get("rule_type"))
    if rule_type not in HARD_RULE_TYPES:
        return False
    action = normalize_match_key(hit.get("action"))
    if action in GLOBAL_REJECT_ACTIONS:
        return False
    return action in GLOBAL_ADVISORY_ACTIONS or rule_type == "hard_safety_filter"

def _criteria(**values: Any) -> dict[str, float | None]:
    """Build C1-C8 raw values; C5 stays reserved with no fabricated value."""

    return {
        "C1": _treatment_fit(values["contaminant_gaps"], values["performance"]),
        "C2": _standard_fit(values["usecase_rows"], values["use_case"]),
        "C3": _site_fit(values["applicability"]),
        "C4": _source_fit(values["context"], values["applicability"]),
        "C5": None,
        "C6": _hydrologic_fit(values["context"], values["applicability"]),
        "C7": _footprint_cost(values["footprint_rows"]),
        "C8": _om_cost(values["design_rows"], values["step_rows"]),
    }


def _context_sensitivity(
    *,
    card: dict[str, Any],
    step_rows: list[dict[str, Any]],
    context: dict[str, Any],
    contaminant_gaps: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return input-sensitive penalties so one generic train cannot always win.

    These are conservative design safeguards, not fabricated treatment values.
    They do not change removal evidence; they only reduce ranking strength when
    the source/chemistry means biological NbS should be polishing or conditional.
    """

    text = normalize_match_key(
        " ".join(
            [
                str(card.get("name") or ""),
                *[str(row.get("nbs_name") or "") for row in step_rows],
                *[str(row.get("nbs_family") or "") for row in step_rows],
            ]
        )
    )
    source = normalize_match_key(
        context.get("pollution_source_type") or context.get("source_type")
    ) or ""
    position = normalize_match_key(context.get("intervention_position")) or ""
    industrial = "industrial" in source
    domestic = "domestic" in source or "sewage" in source
    agricultural = "agriculture" in source or "agricultural" in source
    standalone_primary = "standalone" in position or "primary" in position
    in_channel = position == "in_channel" or "in channel" in position
    stream_order = _float(context.get("stream_order"))
    high_order = stream_order is not None and stream_order >= 5
    extreme_ph = _has_extreme_ph(contaminant_gaps)

    multipliers: dict[str, float] = {}
    caveats: list[str] = []

    is_wetland_or_pond = any(
        token in text
        for token in ("wetland", "vf", "hssf", "pond", "aquaculture")
    )
    is_disposal = any(token in text for token in ("on site", "on-site", "disposal", "soak", "leach"))
    is_reactor_train = any(
        token in text
        for token in ("uasb", "abr", "dewats", "anaerobic_baffled", "anaerobic_filter")
    )
    is_vertical_flow = "vertical_flow" in text or "vf" in text.split("_")

    if domestic and is_disposal:
        caveats.append(
            "On-site disposal is a household-scale pathway, not the primary choice for collected domestic sewage."
        )
        multipliers.update({"C1": 0.45, "C2": 0.55, "C4": 0.30})

    if agricultural and is_disposal:
        caveats.append(
            "Agricultural source control should focus on runoff interception and buffers rather than household disposal."
        )
        multipliers.update({"C2": 0.50, "C4": 0.25})

    if agricultural:
        caveats.append(
            "Diffuse agricultural runoff requires farm-level nutrient, erosion, and sediment source controls before any off-channel polishing unit."
        )
        if is_reactor_train:
            multipliers.update({"C1": 0.55, "C2": 0.55, "C4": 0.35})
        elif is_vertical_flow:
            multipliers.update({"C1": 0.45, "C2": 0.40, "C3": 0.70, "C4": 0.30})
        elif is_wetland_or_pond:
            multipliers.update({"C4": 0.85})

    if industrial:
        caveats.append(
            "Industrial or mixed-industrial wastewater needs ETP/CETP or equivalent pretreatment; NbS should be polishing/buffer only."
        )
        if is_disposal:
            multipliers.update({"C1": 0.15, "C2": 0.20, "C3": 0.20, "C4": 0.10})
        elif is_wetland_or_pond and not is_reactor_train:
            multipliers.update({"C1": 0.20, "C2": 0.30, "C3": 0.25, "C4": 0.15})
        elif is_wetland_or_pond:
            multipliers.update({"C1": 0.55, "C2": 0.60, "C3": 0.55, "C4": 0.45})
        else:
            multipliers.update({"C4": 0.70})

    if standalone_primary and (industrial or is_wetland_or_pond):
        caveats.append(
            "Selected placement is standalone primary treatment; biological NbS trains should be used only after pretreatment or as polishing when influent is strong/industrial."
        )
        multipliers.update({"C1": min(multipliers.get("C1", 1.0), 0.60), "C2": min(multipliers.get("C2", 1.0), 0.60), "C3": min(multipliers.get("C3", 1.0), 0.55)})

    if extreme_ph:
        caveats.append(
            "Extreme pH detected; neutralization/pretreatment is required before biological wetland, pond, or reactor performance can be trusted."
        )
        if is_wetland_or_pond and not is_reactor_train:
            multipliers.update({"C1": min(multipliers.get("C1", 1.0), 0.15), "C2": min(multipliers.get("C2", 1.0), 0.20), "C3": min(multipliers.get("C3", 1.0), 0.15), "C4": min(multipliers.get("C4", 1.0), 0.20)})
        elif is_reactor_train:
            multipliers.update({"C1": min(multipliers.get("C1", 1.0), 0.45), "C2": min(multipliers.get("C2", 1.0), 0.50), "C3": min(multipliers.get("C3", 1.0), 0.45), "C4": min(multipliers.get("C4", 1.0), 0.50)})
        elif is_disposal:
            multipliers.update({"C1": 0.10, "C2": 0.10, "C3": 0.10, "C4": 0.10})

    if high_order and in_channel:
        caveats.append(
            "High-order river context requires off-channel or infrastructure-linked treatment rather than in-channel treatment cells."
        )
        if is_wetland_or_pond and not is_reactor_train:
            multipliers.update({"C3": min(multipliers.get("C3", 1.0), 0.20), "C6": 0.20})
        elif is_reactor_train:
            multipliers.update({"C3": min(multipliers.get("C3", 1.0), 0.65), "C6": 0.70})
        elif is_disposal:
            multipliers.update({"C3": min(multipliers.get("C3", 1.0), 0.25), "C6": 0.25})

    return {"criterion_multipliers": multipliers, "caveats": _unique(caveats)}


def _apply_sensitivity(
    criteria: dict[str, float | None], sensitivity: dict[str, Any]
) -> dict[str, float | None]:
    updated = dict(criteria)
    for code, multiplier in (sensitivity.get("criterion_multipliers") or {}).items():
        if updated.get(code) is not None:
            updated[code] = _clamp(float(updated[code]) * float(multiplier))
    return updated


def _has_extreme_ph(gaps: list[dict[str, Any]]) -> bool:
    for row in gaps:
        if normalize_match_key(row.get("parameter")) != "ph":
            continue
        value = _first_float(
            row,
            ("observed_value", "measured_value", "input_value", "value", "result_value"),
        )
        if value is not None and (value < 6.0 or value > 9.0):
            return True
        severity = normalize_match_key(
            row.get("severity") or row.get("gap_severity") or row.get("status")
        ) or ""
        if "high" in severity or "severe" in severity:
            return True
    return False


def _first_float(row: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = _float(row.get(key))
        if value is not None:
            return value
    return None


def _treatment_fit(gaps: list[dict[str, Any]], rows: list[dict[str, Any]]) -> float | None:
    required = {
        normalize_match_key(row.get("parameter")): _float(row.get("required_removal_percent"))
        for row in gaps
        if row.get("direction") == "reduce"
        and _float(row.get("required_removal_percent")) is not None
        and (_float(row.get("required_removal_percent")) or 0) > 0
    }
    if not required:
        return None
    by_parameter = {normalize_match_key(row.get("parameter")): row for row in rows}
    scores = []
    for parameter, target in required.items():
        row = by_parameter.get(parameter)
        if not row or not row.get("steps_with_data"):
            continue
        low = _float(row.get("cum_removal_low"))
        high = _float(row.get("cum_removal_high"))
        if low is None or high is None or target is None:
            continue
        scores.append(1.0 if target <= low else 0.5 if target <= high else max(0.0, high / target))
    return sum(scores) / len(scores) if scores else None


def _standard_fit(rows: list[dict[str, Any]], use_case: str) -> float | None:
    row = next((r for r in rows if r.get("use_case") == use_case), None)
    if not row:
        return None
    known = sum(int(row.get(key) or 0) for key in ("pass_count", "marginal_count", "fail_count"))
    if not known:
        return None
    return (float(row.get("pass_count") or 0) + 0.5 * float(row.get("marginal_count") or 0)) / known


def _site_fit(applicability: dict[str, Any]) -> float:
    base = 0.5 if applicability["status"] == "conditional" else 1.0
    return _clamp(base + float(applicability["score_modifier_total"]))


def _source_fit(context: dict[str, Any], applicability: dict[str, Any]) -> float | None:
    if not (context.get("pollution_source_type") or context.get("source_type")):
        return None
    source_hits = [
        hit for hit in applicability["triggered_rules"] if hit["factor_name"] == "pollution_source_type"
    ]
    return _clamp(0.5 + sum(float(hit.get("score_modifier") or 0) for hit in source_hits))


def _hydrologic_fit(context: dict[str, Any], applicability: dict[str, Any]) -> float | None:
    if context.get("stream_order") is None:
        return None
    stream_hits = [
        hit for hit in applicability["triggered_rules"] if hit["factor_name"] == "stream_order"
    ]
    if any(normalize_match_key(hit["rule_type"]) in CONDITIONAL_RULE_TYPES for hit in stream_hits):
        return 0.5
    return 1.0


def _footprint_cost(rows: list[dict[str, Any]]) -> float | None:
    known = [_float(row.get("area_per_pe_high")) for row in rows]
    known = [value for value in known if value is not None]
    return sum(known) if known else None


def _om_cost(designs: list[dict[str, Any]], steps: list[dict[str, Any]]) -> float | None:
    values = []
    for row in designs:
        text = normalize_match_key(row.get("skill_om_intensity"))
        if "very low" in text:
            values.append(0.1)
        elif "low moderate" in text or "moderate" in text:
            values.append(0.6)
        elif "low" in text:
            values.append(0.3)
    for row in steps:
        energy = normalize_match_key(row.get("energy_class"))
        if energy == "gravity":
            values.append(0.1)
        elif energy == "low power":
            values.append(0.5)
        elif energy == "power dependent":
            values.append(1.0)
    return sum(values) / len(values) if values else None


def _om_intensity_label(
    designs: list[dict[str, Any]],
    steps: list[dict[str, Any]],
) -> str:
    """Summarize stored O&M/energy descriptors without changing rank."""

    descriptors = [
        normalize_match_key(row.get("skill_om_intensity")) for row in designs
    ]
    energy = [normalize_match_key(row.get("energy_class")) for row in steps]
    if any("high" in value for value in descriptors) or any(
        value == "power dependent" for value in energy
    ):
        return "Higher"
    if any("moderate" in value for value in descriptors) or any(
        value == "low power" for value in energy
    ):
        return "Moderate"
    if descriptors or energy:
        return "Lower"
    return "Not recorded"


def _apply_topsis(candidates: list[dict[str, Any]], weights: list[dict[str, Any]]) -> None:
    """Apply vector-normalized TOPSIS with explicit unknown-value flags."""

    weight_by_code = {row["criterion_code"]: row for row in weights if row["criterion_code"] != "C5"}
    active_codes = [
        code for code in weight_by_code if any(row["criteria_raw"].get(code) is not None for row in candidates)
    ]
    if not candidates or not active_codes:
        for row in candidates:
            row["match_score"] = None
            row["criteria_breakdown"] = []
        return
    normalized_weights = _normalized_weights(weight_by_code, active_codes)
    columns: dict[str, list[float]] = {}
    medians: dict[str, float] = {}
    for code in active_codes:
        known = [float(row["criteria_raw"][code]) for row in candidates if row["criteria_raw"].get(code) is not None]
        medians[code] = median(known)
        columns[code] = [float(row["criteria_raw"].get(code) if row["criteria_raw"].get(code) is not None else medians[code]) for row in candidates]
    normalized: dict[str, list[float]] = {}
    for code, values in columns.items():
        denominator = sqrt(sum(value * value for value in values)) or 1.0
        vector = [value / denominator for value in values]
        if weight_by_code[code]["benefit_or_cost"] == "cost":
            vector = [1.0 - value for value in vector]
        normalized[code] = vector
    weighted = {code: [value * normalized_weights[code] for value in values] for code, values in normalized.items()}
    best = {code: max(values) for code, values in weighted.items()}
    worst = {code: min(values) for code, values in weighted.items()}
    for index, row in enumerate(candidates):
        distance_best = sqrt(sum((weighted[code][index] - best[code]) ** 2 for code in active_codes))
        distance_worst = sqrt(sum((weighted[code][index] - worst[code]) ** 2 for code in active_codes))
        denominator = distance_best + distance_worst
        row["match_score"] = distance_worst / denominator if denominator else 0.5
        row["criteria_breakdown"] = [
            {
                "criterion_code": code,
                "criterion_name": weight_by_code[code]["criterion_name"],
                "raw_value": row["criteria_raw"].get(code),
                "normalized_value": normalized[code][index],
                "weight": normalized_weights[code],
                "weighted_value": weighted[code][index],
                "data_status": "known" if row["criteria_raw"].get(code) is not None else "unknown_median_imputed",
            }
            for code in active_codes
        ]


def _confidence(
    performance: list[dict[str, Any]],
    source_ids: list[int],
    input_type: str | None,
    site: dict[str, Any] | None,
    applicability: dict[str, Any],
    criteria: dict[str, Any],
    contaminant_gaps: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Score result reliability separately from technical TOPSIS match.

    Data-completeness caps deliberately prevent a thin input from appearing
    highly reliable. These constants are transparent rule-based safeguards;
    they are not expert-validated scientific confidence intervals.
    """

    known_perf = sum(bool(row.get("steps_with_data")) for row in performance)
    perf_ratio = known_perf / len(performance) if performance else 0.0
    input_factor = {"user_measured": 1.0, "station_observations": 0.8, "basin_observations": 0.7, "water_type_profile": 0.55}.get(input_type or "", 0.35)
    context_fields = ("pollution_source_type", "intervention_position", "stream_order")
    context_known = sum(context.get(field) not in {None, ""} for field in context_fields)
    site_factor = min(
        1.0,
        (0.55 if site and site.get("source_id") else 0.2) + 0.15 * context_known,
    )
    source_factor = min(len(source_ids) / 4.0, 1.0)
    known_criteria = sum(value is not None for code, value in criteria.items() if code != "C5") / 7.0
    usable_parameters = {
        normalize_match_key(row.get("parameter"))
        for row in contaminant_gaps
        if _first_float(row, ("observed_value", "measured_value", "input_value", "value"))
        is not None
    }
    usable_parameters.discard(None)
    usable_count = len(usable_parameters)
    key_present = sorted(KEY_SCREENING_PANEL.intersection(usable_parameters))
    key_missing = sorted(KEY_SCREENING_PANEL.difference(usable_parameters))
    key_panel_complete = not key_missing
    panel_factor = min(usable_count / len(KEY_SCREENING_PANEL), 1.0)

    csv_summary = context.get("csv_validation_summary")
    csv_summary = csv_summary if isinstance(csv_summary, dict) else {}
    blank_count = _summary_count(csv_summary, "blank_values")
    skipped_count = sum(
        _summary_count(csv_summary, key)
        for key in ("non_numeric_values", "unknown_parameters")
    )
    incomplete_penalty = min(0.15, 0.02 * blank_count + 0.03 * skipped_count)

    score = (
        0.30 * perf_ratio
        + 0.15 * input_factor
        + 0.10 * site_factor
        + 0.15 * source_factor
        + 0.10 * known_criteria
        + 0.20 * panel_factor
    )
    score += float(applicability.get("confidence_modifier_total") or 0.0)
    score = _clamp(score - incomplete_penalty)
    if usable_count == 0:
        data_cap = CONFIDENCE_CAP_NO_DATA
    elif usable_count == 1:
        data_cap = CONFIDENCE_CAP_ONE_PARAMETER
    elif usable_count <= 3:
        data_cap = CONFIDENCE_CAP_TWO_TO_THREE
    elif key_panel_complete:
        data_cap = CONFIDENCE_CAP_COMPLETE_KEY_PANEL
    else:
        data_cap = CONFIDENCE_CAP_INCOMPLETE_KEY_PANEL
    confidence_cap = min(data_cap, METHOD_CONFIDENCE_CAP)
    # Scaling preserves evidence-driven differences between trains while the
    # same cap still bounds every result built from the same thin input.
    score = min(score * confidence_cap, confidence_cap)
    caveats = []
    if perf_ratio < 1:
        caveats.append("Some train performance parameters are unknown data gaps.")
    if usable_count == 0:
        caveats.append("Result confidence is not assessed because no usable water-quality parameters were supplied.")
    elif usable_count == 1:
        caveats.append("Only one usable parameter was supplied. Result confidence has been reduced.")
    elif usable_count <= 3:
        caveats.append("Only two or three usable parameters were supplied, so result confidence is capped.")
    if key_missing:
        caveats.append(
            "The screening completeness panel is missing: "
            + ", ".join(key_missing).upper()
            + "."
        )
    if blank_count:
        caveats.append(f"{blank_count} blank CSV value(s) remain unknown.")
    if skipped_count:
        caveats.append(f"{skipped_count} unsupported or nonnumeric CSV row(s) were skipped.")
    if site_factor < 0.8:
        caveats.append("Site context is incomplete or not source-verified.")
    label = (
        "not_assessed"
        if usable_count == 0
        else "high"
        if score >= 0.75
        else "medium"
        if score >= 0.5
        else "low"
    )
    explanation = [
        f"{usable_count} usable water-quality parameter(s) informed this result.",
        (
            "The BOD, COD, TSS, and pH screening completeness panel is present."
            if key_panel_complete
            else "The screening completeness panel is incomplete."
        ),
        "Confidence also reflects canonical evidence coverage, source type, and site context completeness.",
        f"A documented rule-based data cap of {confidence_cap:.0%} applies to this input.",
        "C5 health-risk integration remains reserved for future expert data.",
    ]
    return {
        "score": score,
        "label": label,
        "cap": confidence_cap,
        "factors": {
            "usable_parameter_count": usable_count,
            "key_parameters_present": key_present,
            "key_parameters_missing": key_missing,
            "blank_unknown_count": blank_count,
            "skipped_row_count": skipped_count,
            "performance_completeness": perf_ratio,
            "input_quality": input_factor,
            "site_context_completeness": site_factor,
            "source_coverage": source_factor,
            "criteria_completeness": known_criteria,
            "method_confidence_cap": METHOD_CONFIDENCE_CAP,
        },
        "explanation": explanation,
        "caveats": caveats,
    }


def _summary_count(summary: dict[str, Any], key: str) -> int:
    """Read either a numeric count or a list-valued CSV validation field."""

    value = summary.get(key)
    if isinstance(value, list):
        return len(value)
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _pollutant_gap_breakdown(
    gaps: list[dict[str, Any]],
    performance: list[dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Explain every supplied parameter against targets and train evidence."""

    addressed = {
        normalize_match_key(row.get("parameter"))
        for row in performance
        if row.get("steps_with_data")
    }
    result = []
    for gap in gaps:
        status = normalize_match_key(gap.get("status"))
        if status == "within_standard":
            gap_status = "below_target"
            severity = "Target is met."
        elif status in {"exceeds_standard", "below_minimum", "outside_range"}:
            gap_status = "exceeds_target"
            parameter_key = normalize_match_key(gap.get("parameter"))
            severity = (
                "pH adjustment or neutralization is required."
                if parameter_key == "ph"
                else "Target is not met; treatment or adjustment is required."
            )
        else:
            gap_status = "not_assessed"
            severity = (
                "No stored target limit is available for this parameter under "
                "the selected use case."
            )
        parameter = normalize_match_key(gap.get("parameter"))
        coverage_category = _coverage_category(
            parameter=parameter,
            gap_status=gap_status,
        )
        result.append(
            {
                "parameter": parameter or gap.get("parameter"),
                "observed_value": gap.get("observed_value"),
                "unit": gap.get("observed_unit") or gap.get("standard_unit"),
                "source": _input_source_label(gap, context),
                "target_threshold": {
                    "limit_low": gap.get("limit_low"),
                    "limit_high": gap.get("limit_high"),
                    "unit": gap.get("standard_unit"),
                },
                "gap_status": gap_status,
                "coverage_category": coverage_category,
                "coverage_label": _coverage_label(coverage_category),
                "severity": severity,
                "train_addresses_parameter": parameter in addressed,
            }
        )
    return result


def _coverage_category(*, parameter: str | None, gap_status: str) -> str:
    """Classify how one recognized observation participates in this run."""

    if gap_status != "not_assessed":
        return "used_in_scoring"
    return "supporting_context"


def _coverage_label(category: str) -> str:
    """Return stable practitioner-facing wording for a coverage category."""

    return {
        "used_in_scoring": "Used in scoring.",
        "supporting_context": "Used as supporting context.",
        "read_not_assessed": "Used as supporting context.",
    }[category]


def _input_source_label(gap: dict[str, Any], context: dict[str, Any]) -> str:
    mode = normalize_match_key(context.get("workflow_mode"))
    if mode == "uploaded_water_quality":
        return "user_csv"
    if mode == "manual_measured_water_quality":
        return "manual"
    source = normalize_match_key(gap.get("source_type"))
    if source in {"station_observations", "basin_observations", "water_type_profile"}:
        return "canonical"
    if source == "user_measured":
        return "manual"
    return "unknown"


def _all_use_case_verdicts(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for use_case in USE_CASES:
        row = next((value for value in rows if value.get("use_case") == use_case), {})
        verdict = "fail" if row.get("fail_count", 0) else "marginal" if row.get("marginal_count", 0) else "unknown" if row.get("unknown_count", 0) else "pass" if row.get("pass_count", 0) else "unknown"
        result[use_case] = {"verdict": verdict, **{key: row.get(key) for key in ("parameters_checked", "pass_count", "marginal_count", "fail_count", "unknown_count", "failing_parameters", "marginal_parameters", "unknown_parameters")}}
    return result


def _why_recommended(row: dict[str, Any]) -> list[str]:
    known = [item for item in row.get("criteria_breakdown", []) if item["data_status"] == "known"]
    known.sort(key=lambda item: item["weighted_value"], reverse=True)
    messages = [f"{item['criterion_name'].replace('_', ' ').title()} was a leading evidence-backed factor in the TOPSIS position." for item in known[:2]]
    selected_use_case = row.get("selected_use_case")
    verdict = (row.get("all_use_case_verdicts") or {}).get(selected_use_case, {})
    if verdict.get("verdict") in {"pass", "marginal"}:
        messages.append(
            f"Canonical performance records indicate a {verdict['verdict']} "
            f"result for {str(selected_use_case).replace('_', ' ')} use."
        )
    if row.get("implementation_role"):
        messages.append(f"Intended role: {row['implementation_role']}.")
    if row["applicability_result"]["status"] == "conditional":
        messages.append("The option remains conditional on the listed site or pretreatment requirements.")
    return messages


def _implementation_explanation(
    row: dict[str, Any],
    *,
    context: dict[str, Any],
    contaminant_gaps: list[dict[str, Any]],
    design_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble implementation facts without inventing missing design evidence."""

    source_type = normalize_match_key(
        context.get("pollution_source_type") or context.get("source_type")
    )
    position = normalize_match_key(context.get("intervention_position"))
    workflow_mode = normalize_match_key(context.get("workflow_mode"))
    steps = row.get("treatment_sequence") or []
    roles = {normalize_match_key(step.get("role")) for step in steps}
    stream_order = _float(context.get("stream_order"))
    high_order_or_in_channel = position == "in_channel" or (
        stream_order is not None and stream_order >= 5
    )
    has_wetland_or_pond = any(
        any(token in normalize_match_key(component.get("family") or component.get("name"))
            for token in ("wetland", "pond", "lagoon"))
        for component in row.get("nbs_components") or []
    )

    if source_type == "industrial_or_mixed_industrial":
        implementation_role = "Polishing or buffer after ETP/CETP pretreatment"
    elif source_type == "high_agriculture_only_no_water_data":
        implementation_role = "Source control and off-channel runoff polishing"
    elif "primary" in roles:
        implementation_role = "Primary-to-polishing treatment train"
    elif "disposal" in roles:
        implementation_role = "On-site disposal following primary treatment"
    else:
        implementation_role = "Secondary treatment and polishing"
    if (
        workflow_mode == "site_context_only"
        and high_order_or_in_channel
        and has_wetland_or_pond
    ):
        implementation_role = "Off-channel treatment or polishing only"

    pretreatment = [
        str(step.get("step_label"))
        for step in steps
        if normalize_match_key(step.get("role")) == "pretreatment"
        and step.get("step_label")
    ]
    pretreatment.extend(
        str(design.get("pretreatment"))
        for design in design_rows
        if design.get("pretreatment")
    )
    if source_type == "industrial_or_mixed_industrial":
        pretreatment.insert(0, "ETP/CETP pretreatment is required before any NbS unit.")
        if any(
            normalize_match_key(gap.get("parameter")) == "ph"
            and gap.get("direction") == "adjust_range"
            for gap in contaminant_gaps
        ):
            pretreatment.insert(1, "Neutralization and pH control are required upstream.")

    data_gaps = [
        f"No train-specific value is available for {item.get('criterion_name', item.get('criterion_code', 'a criterion'))}."
        for item in row.get("criteria_breakdown", [])
        if item.get("data_status") != "known"
    ]
    for use_case, verdict in (row.get("all_use_case_verdicts") or {}).items():
        unknown = verdict.get("unknown_parameters")
        if unknown:
            data_gaps.append(
                f"{str(use_case).replace('_', ' ').title()} evidence is incomplete for: {unknown}."
            )
    if row.get("all_use_cases_unknown"):
        data_gaps.append(
            "Use-case suitability is not assessed because measured water-quality data or canonical performance evidence are incomplete."
        )

    guidance = []
    source_guidance: list[str] = []
    source_text = source_type or ""
    context_only = workflow_mode in {"site_context_only", "pollution_source_screening"}
    if context_only:
        source_guidance.append(
            "This is context guidance; measured water-quality data are required for treatment pass/fail conclusions."
        )
    if source_type == "industrial_or_mixed_industrial" or "industrial" in source_text:
        source_guidance.append(
            "Route industrial or mixed-industrial wastewater through ETP/CETP and source-specific pretreatment before any NbS polishing."
        )
        if _has_extreme_ph(contaminant_gaps):
            source_guidance.append(
                "Neutralize pH upstream before biological wetland, pond, or reactor stages."
            )
        source_guidance.append(
            "Use NbS only as polishing, buffer, or controlled off-channel treatment after compliance checks."
        )
    if source_type == "high_agriculture_only_no_water_data" or "agriculture" in source_text or "agricultural" in source_text:
        source_guidance.append(
            "First reduce nutrient, pesticide, erosion, and sediment generation at source before sizing end-of-pipe treatment units."
        )
        source_guidance.append(
            "Use vegetated buffer/filter strips, grassed waterways, contour bunding, and sediment traps where land, slope, and drainage layout allow."
        )
        source_guidance.append(
            "Source control and edge-of-field measures are first priority. Train ranking applies only to collected runoff or drainage water requiring off-channel polishing."
        )
    if "stormwater" in source_text or "urban" in source_text or "drain" in source_text:
        source_guidance.append(
            "Prioritize litter, oil/grease, and sediment capture at drains, silt traps, and green conveyance before polishing wetlands or ponds."
        )
    if "hospital" in source_text or "biomedical" in source_text or "high_risk" in source_text:
        source_guidance.append(
            "Do not use simple NbS as standalone high-risk wastewater treatment; specialist pretreatment and disinfection are required."
        )

    if source_type == "industrial_or_mixed_industrial":
        guidance.append(
            "Do not use this train as standalone industrial treatment; apply it only after source-specific ETP/CETP treatment and compliance checks."
        )
    if source_type == "high_agriculture_only_no_water_data":
        guidance.append(
            "Prioritize farm-level nutrient and sediment controls; use treatment units only for intercepted, off-channel runoff where site checks support them."
        )
    if high_order_or_in_channel:
        mainstem_message = (
            "Avoid in-channel treatment cells on mainstem/high-order rivers; use off-channel treatment, drain interception, STP/CETP polishing, tributary buffers, or upstream source control."
        )
        guidance.append(mainstem_message)
        source_guidance.append(mainstem_message)
    guidance.extend(
        str(design.get("construction_notes"))
        for design in design_rows
        if design.get("construction_notes")
    )

    plants = row.get("suitable_plants") or []
    if not plants:
        data_gaps.append(
            "No catalogue-backed non-invasive plant mapping is available; planting guidance requires local validation."
        )
    planting_guidance = (
        "Only catalogue-mapped, non-invasive species are shown; confirm local availability and planting design before implementation."
        if plants
        else "Planting guidance requires local validation."
    )
    return {
        "implementation_role": implementation_role,
        "pretreatment_requirements": _unique(pretreatment),
        "data_gaps": _unique(data_gaps),
        "implementation_guidance": _unique(guidance),
        "source_location_guidance": _unique(source_guidance),
        "planting_guidance": planting_guidance,
    }


def _site_rule_context(site: dict[str, Any] | None) -> dict[str, Any]:
    if not site:
        return {}
    return {"stream_order": site.get("stream_order_strahler") or site.get("stream_order"), "slope": site.get("slope_mean"), "builtup_frac": site.get("builtup_frac"), "agri_frac": site.get("agri_frac"), "dom_land_cover": site.get("dom_land_cover")}


def _input_mode(source_type: str | None) -> str:
    return "measured_water_quality_uploaded" if source_type in {"user_measured", "station_observations", "basin_observations"} else "location_only_no_water_data"


def _treatment_sequence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: row.get(key) for key in ("step_order", "step_label", "role", "nbs_id", "nbs_name")} for row in rows]


def _nbs_components(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"nbs_id": row.get("nbs_id"), "name": row.get("nbs_name"), "family": row.get("nbs_family")} for row in rows if row.get("nbs_id") is not None]


def _evidence_ids(card: dict[str, Any], designs: list[dict[str, Any]], footprints: list[dict[str, Any]]) -> list[int]:
    values: list[int] = []
    for raw in [card.get("evidence_source_ids"), *[r.get("source_ids") for r in designs], *[r.get("source_id") for r in footprints]]:
        for item in str(raw or "").split(","):
            try:
                value = int(item.strip())
            except ValueError:
                continue
            if value not in values:
                values.append(value)
    return values


def _normalized_weights(rows: dict[str, dict[str, Any]], codes: list[str]) -> dict[str, float]:
    total = sum(float(rows[code]["weight"]) for code in codes) or 1.0
    return {code: float(rows[code]["weight"]) / total for code in codes}


def _group(rows: list[dict[str, Any]], key: str) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get(key) is not None:
            grouped.setdefault(int(row[key]), []).append(row)
    return grouped


def _float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _unique(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result

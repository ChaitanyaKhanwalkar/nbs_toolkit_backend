"""Screening-level non-monetary cost-benefit ratio interpretation.

This module does not estimate rupee CAPEX/OPEX and does not affect TOPSIS
ranking. It adds a transparent secondary interpretation panel for each ranked
treatment train using existing criterion, confidence, readiness, and safety
signals.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.input_normalization import normalize_match_key


METHOD_KEY = "screening_non_monetary_v1"
METHOD_NAME = "Cost-Benefit Ratio Analysis - Screening Level"
METHOD_DISCLAIMER = (
    "Screening-level non-monetary ratio. Does not estimate rupee CAPEX/OPEX."
)
DENOMINATOR_FLOOR = 0.20
DISPLAY_CAP = 5.0
FORMULA_TEXT = (
    "benefit_score = weighted_average(C1 treatment fit, C2 standard fit, C3 site "
    "fit, C4 source fit, C6 hydrologic fit, confidence score, readiness score, "
    "safety suitability score); cost_burden_score = weighted_average(C7 "
    "footprint burden, C8 O&M burden, energy burden, land constraint burden, "
    "design complexity burden, missing data burden); screening_cbr = "
    "benefit_score / max(cost_burden_score, 0.20)"
)

DEFAULT_WEIGHTS = [
    {
        "component_key": "C1",
        "component_label": "C1 treatment fit",
        "side": "benefit",
        "weight": 0.25,
        "direction": "higher_better",
        "source_field": "criteria_breakdown.C1",
    },
    {
        "component_key": "C2",
        "component_label": "C2 standard fit",
        "side": "benefit",
        "weight": 0.25,
        "direction": "higher_better",
        "source_field": "criteria_breakdown.C2",
    },
    {
        "component_key": "C3",
        "component_label": "C3 site fit",
        "side": "benefit",
        "weight": 0.10,
        "direction": "higher_better",
        "source_field": "criteria_breakdown.C3",
    },
    {
        "component_key": "C4",
        "component_label": "C4 source fit",
        "side": "benefit",
        "weight": 0.10,
        "direction": "higher_better",
        "source_field": "criteria_breakdown.C4",
    },
    {
        "component_key": "C6",
        "component_label": "C6 hydrologic fit",
        "side": "benefit",
        "weight": 0.05,
        "direction": "higher_better",
        "source_field": "criteria_breakdown.C6",
    },
    {
        "component_key": "confidence",
        "component_label": "Confidence score",
        "side": "benefit",
        "weight": 0.10,
        "direction": "higher_better",
        "source_field": "confidence_score",
    },
    {
        "component_key": "readiness",
        "component_label": "Readiness score",
        "side": "benefit",
        "weight": 0.10,
        "direction": "higher_better",
        "source_field": "design_readiness.level",
    },
    {
        "component_key": "safety_suitability",
        "component_label": "Safety suitability score",
        "side": "benefit",
        "weight": 0.05,
        "direction": "higher_better",
        "source_field": "applicability/context warnings",
    },
    {
        "component_key": "C7",
        "component_label": "C7 footprint burden",
        "side": "cost_burden",
        "weight": 0.30,
        "direction": "higher_worse",
        "source_field": "criteria_breakdown.C7",
    },
    {
        "component_key": "C8",
        "component_label": "C8 O&M burden",
        "side": "cost_burden",
        "weight": 0.30,
        "direction": "higher_worse",
        "source_field": "criteria_breakdown.C8",
    },
    {
        "component_key": "energy",
        "component_label": "Energy burden",
        "side": "cost_burden",
        "weight": 0.15,
        "direction": "higher_worse",
        "source_field": "energy_class/om_intensity",
    },
    {
        "component_key": "land_constraint",
        "component_label": "Land constraint burden",
        "side": "cost_burden",
        "weight": 0.10,
        "direction": "higher_worse",
        "source_field": "sizing_estimate.land_fit",
    },
    {
        "component_key": "design_complexity",
        "component_label": "Design complexity burden",
        "side": "cost_burden",
        "weight": 0.10,
        "direction": "higher_worse",
        "source_field": "pretreatment/applicability/design readiness",
    },
    {
        "component_key": "missing_data",
        "component_label": "Missing data burden",
        "side": "cost_burden",
        "weight": 0.05,
        "direction": "higher_worse",
        "source_field": "missing criteria and sizing gaps",
    },
]


@dataclass(slots=True)
class CostBenefitComponent:
    """One input component used in the screening CBR calculation."""

    key: str
    label: str
    value: float | None
    weight: float
    direction: str
    status: str
    explanation: str


@dataclass(slots=True)
class CostBenefitInput:
    """Inputs needed to compute one train's screening CBR panel."""

    train: dict[str, Any]
    design_readiness: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    location_context: dict[str, Any] = field(default_factory=dict)
    method: dict[str, Any] | None = None
    component_weights: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class CostBenefitResult:
    """Serializable output for the recommendation API and report export."""

    screening_cbr: float
    display_cbr: str
    label: str
    benefit_score: float
    cost_burden_score: float
    benefit_components: list[CostBenefitComponent]
    cost_components: list[CostBenefitComponent]
    benefit_drivers: list[str]
    cost_drivers: list[str]
    caveats: list[str]
    is_monetary: bool
    method: str
    method_name: str
    method_disclaimer: str
    formula_text: str
    denominator_floor_used: bool
    official_ranking_unchanged: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a plain API-safe dictionary."""

        result = asdict(self)
        result["is_monetary"] = False
        result["official_ranking_unchanged"] = True
        return result


class CostBenefitAnalysisEngine:
    """Compute screening-only non-monetary CBR panels for ranked trains."""

    def __init__(
        self,
        *,
        method: dict[str, Any] | None = None,
        component_weights: list[dict[str, Any]] | None = None,
    ) -> None:
        self.method = method or _default_method()
        self.component_weights = component_weights or list(DEFAULT_WEIGHTS)

    def analyze(self, item: CostBenefitInput) -> CostBenefitResult:
        """Return one secondary CBR interpretation without changing rank."""

        benefit_components = _benefit_components(item, self.component_weights)
        cost_components = _cost_components(item, self.component_weights)
        benefit_score = weighted_average_available(benefit_components)
        cost_burden_score = weighted_average_available(cost_components)
        denominator = max(cost_burden_score, _method_floor(self.method))
        raw_ratio = benefit_score / denominator if denominator else 0.0
        display_cap = _method_display_cap(self.method)
        caveats = _caveats(item, benefit_components, cost_components, raw_ratio, display_cap)
        label = _label(raw_ratio)
        label, caveats = _apply_safety_caps(item, label, caveats)
        if _insufficient_cost_evidence(cost_components) and label == "Very favourable":
            label = "Favourable"
            caveats = _append_once(
                caveats,
                "Some cost-burden inputs are missing; ratio is indicative.",
            )

        return CostBenefitResult(
            screening_cbr=raw_ratio,
            display_cbr=_display_ratio(raw_ratio, display_cap),
            label=label,
            benefit_score=benefit_score,
            cost_burden_score=cost_burden_score,
            benefit_components=benefit_components,
            cost_components=cost_components,
            benefit_drivers=_drivers(benefit_components, higher_is_good=True),
            cost_drivers=_drivers(cost_components, higher_is_good=False),
            caveats=caveats,
            is_monetary=False,
            method=str(self.method.get("method_key") or METHOD_KEY),
            method_name=str(self.method.get("method_name") or METHOD_NAME),
            method_disclaimer=str(self.method.get("caveat_text") or METHOD_DISCLAIMER),
            formula_text=str(self.method.get("formula_text") or FORMULA_TEXT),
            denominator_floor_used=cost_burden_score < _method_floor(self.method),
            official_ranking_unchanged=True,
        )


def clamp01(value: Any) -> float | None:
    """Return value clamped to 0-1, preserving missing/invalid as None."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, number))


def weighted_average_available(components: list[CostBenefitComponent]) -> float:
    """Average available/derived values using their display weights only."""

    available = [
        component
        for component in components
        if component.value is not None and component.status in {"available", "derived"}
    ]
    weight_sum = sum(component.weight for component in available)
    if not available or weight_sum <= 0:
        return 0.0
    return sum(component.value * component.weight for component in available) / weight_sum


def map_confidence_to_score(value: Any, label: str | None = None) -> float | None:
    """Map existing confidence output to a 0-1 benefit score."""

    numeric = clamp01(value)
    if numeric is not None:
        return numeric
    return {
        "high": 0.85,
        "medium": 0.60,
        "low": 0.35,
        "data_limited": 0.25,
    }.get(normalize_match_key(label), None)


def map_readiness_to_score(readiness: dict[str, Any]) -> float:
    """Map design-readiness level to a conservative benefit score."""

    level = normalize_match_key(readiness.get("level"))
    return {
        "preliminary_design_ready": 0.85,
        "planning_level_result": 0.65,
        "early_screening_only": 0.35,
        "needs_expert_review": 0.25,
    }.get(level, 0.35)


def map_energy_to_burden(train: dict[str, Any]) -> tuple[float | None, str]:
    """Map recorded energy/O&M descriptors to a 0-1 burden."""

    values = " ".join(
        str(value or "")
        for value in [
            train.get("om_intensity"),
            *_sequence_values(train, "energy_class"),
        ]
    )
    key = normalize_match_key(values) or ""
    if not key.strip("_"):
        return None, "No explicit energy class was available."
    if "power_dependent" in key or "higher" in key or "high" in key:
        return 0.85, "Power dependence or high O&M indicates higher energy burden."
    if "low_power" in key or "moderate" in key:
        return 0.50, "Low-power or moderate O&M indicates medium energy burden."
    if "gravity" in key or "lower" in key or "passive" in key or "low" in key:
        return 0.20, "Passive/gravity or lower O&M indicates lower energy burden."
    return 0.45, "Energy class was present but not specific; medium-low burden used."


def map_safety_to_score(
    train: dict[str, Any],
    context: dict[str, Any],
    location_context: dict[str, Any],
) -> float:
    """Map safety/applicability status to a benefit-side suitability score."""

    status = normalize_match_key((train.get("applicability_result") or {}).get("status"))
    flags = location_context.get("context_flags") or {}
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    if status == "rejected":
        return 0.0
    if _industrial_source(source) or flags.get("industrial_pretreatment_required"):
        return 0.25
    if flags.get("mainstem_or_high_order") or flags.get("off_channel_required"):
        return 0.45
    if status == "conditional":
        return 0.50
    return 0.80


def map_missing_data_to_burden(
    train: dict[str, Any],
    cost_components: list[CostBenefitComponent] | None = None,
) -> tuple[float, str]:
    """Convert missing evidence into burden without treating missing as zero."""

    missing = 0
    missing += sum(
        1
        for row in train.get("criteria_breakdown") or []
        if row.get("data_status") == "unknown_median_imputed"
    )
    missing += len(train.get("data_gaps") or [])
    sizing = train.get("sizing_estimate") or {}
    if sizing.get("sizing_confidence") in {None, "", "insufficient_data"}:
        missing += 2
    if sizing.get("land_fit") in {None, "", "insufficient_data"}:
        missing += 1
    for component in cost_components or []:
        if component.status == "missing":
            missing += 1
    if missing == 0:
        return 0.10, "No major missing cost-burden evidence was flagged."
    if missing <= 2:
        return 0.35, "Some supporting cost-burden evidence is incomplete."
    if missing <= 5:
        return 0.65, "Several cost-burden or train evidence gaps are present."
    return 0.90, "Many cost-burden or train evidence gaps are present."


def _benefit_components(
    item: CostBenefitInput,
    weights: list[dict[str, Any]],
) -> list[CostBenefitComponent]:
    train = item.train
    by_code = _criteria_by_code(train)
    components = []
    for row in _side_weights(weights, "benefit"):
        key = row["component_key"]
        if key in {"C1", "C2", "C3", "C4", "C6"}:
            criterion = by_code.get(key)
            value = clamp01((criterion or {}).get("normalized_value"))
            status = _criterion_status(criterion)
            explanation = (
                "Existing criterion-level TOPSIS normalized score; higher is better."
                if value is not None
                else "Criterion was not available for this train."
            )
        elif key == "confidence":
            value = map_confidence_to_score(
                train.get("confidence_score"),
                train.get("confidence_label"),
            )
            status = "available" if value is not None else "missing"
            explanation = "Existing result-confidence score; separate from TOPSIS Ci."
        elif key == "readiness":
            value = map_readiness_to_score(item.design_readiness)
            status = "derived"
            explanation = "Derived from design-readiness level for this run."
        else:
            value = map_safety_to_score(train, item.context, item.location_context)
            status = "derived"
            explanation = "Derived from applicability and source/location safety flags."
        components.append(_component(row, value, status, explanation))
    return components


def _cost_components(
    item: CostBenefitInput,
    weights: list[dict[str, Any]],
) -> list[CostBenefitComponent]:
    train = item.train
    by_code = _criteria_by_code(train)
    components = []
    for row in _side_weights(weights, "cost_burden"):
        key = row["component_key"]
        if key in {"C7", "C8"}:
            criterion = by_code.get(key)
            suitability = clamp01((criterion or {}).get("normalized_value"))
            value = None if suitability is None else 1.0 - suitability
            status = _criterion_status(criterion)
            explanation = (
                "Converted from TOPSIS cost-criterion suitability: burden = 1 - suitability."
                if value is not None
                else "Cost criterion was missing; missing-data burden records this."
            )
        elif key == "energy":
            value, explanation = map_energy_to_burden(train)
            status = "derived" if value is not None else "missing"
        elif key == "land_constraint":
            value, explanation = _land_burden(train.get("sizing_estimate") or {})
            status = "derived" if value is not None else "missing"
        elif key == "design_complexity":
            value, explanation = _design_complexity_burden(train, item.design_readiness)
            status = "derived"
        else:
            value, explanation = map_missing_data_to_burden(train, components)
            status = "derived"
        components.append(_component(row, value, status, explanation))
    return components


def _component(
    row: dict[str, Any],
    value: float | None,
    status: str,
    explanation: str,
) -> CostBenefitComponent:
    return CostBenefitComponent(
        key=str(row["component_key"]),
        label=str(row["component_label"]),
        value=clamp01(value),
        weight=float(row["weight"]),
        direction=str(row["direction"]),
        status=status,
        explanation=explanation,
    )


def _criteria_by_code(train: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("criterion_code")): row
        for row in train.get("criteria_breakdown") or []
        if row.get("criterion_code")
    }


def _criterion_status(row: dict[str, Any] | None) -> str:
    if not row:
        return "missing"
    return "missing" if row.get("data_status") == "unknown_median_imputed" else "available"


def _side_weights(weights: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    return [row for row in weights if row.get("side") == side]


def _sequence_values(train: dict[str, Any], key: str) -> list[Any]:
    return [
        row.get(key)
        for row in [
            *(train.get("treatment_sequence") or []),
            *(train.get("nbs_components") or []),
        ]
        if isinstance(row, dict)
    ]


def _land_burden(sizing: dict[str, Any]) -> tuple[float | None, str]:
    fit = normalize_match_key(sizing.get("land_fit"))
    if fit == "fits":
        return 0.20, "Supplied land appears to fit the screening estimate."
    if fit == "borderline":
        return 0.55, "Supplied land is borderline against the screening estimate."
    if fit == "likely_too_little_land":
        return 0.90, "Supplied land appears below the screening estimate."
    return None, "Land fit is missing or insufficient for this screening estimate."


def _design_complexity_burden(
    train: dict[str, Any],
    readiness: dict[str, Any],
) -> tuple[float, str]:
    requirements = len(train.get("pretreatment_requirements") or [])
    conditional = (
        normalize_match_key((train.get("applicability_result") or {}).get("status"))
        == "conditional"
    )
    needs_expert = normalize_match_key(readiness.get("level")) == "needs_expert_review"
    burden = 0.25 + min(requirements, 4) * 0.10
    if conditional:
        burden += 0.15
    if needs_expert:
        burden += 0.20
    return clamp01(burden) or 0.0, "Derived from pretreatment, conditionality, and readiness."


def _drivers(
    components: list[CostBenefitComponent],
    *,
    higher_is_good: bool,
) -> list[str]:
    available = [
        component
        for component in components
        if component.value is not None and component.status in {"available", "derived"}
    ]
    available.sort(
        key=lambda component: (
            -component.value if higher_is_good else component.value,
            -component.weight,
        )
    )
    return [
        f"{component.label}: {component.value:.2f}"
        for component in available[:3]
    ]


def _caveats(
    item: CostBenefitInput,
    benefit_components: list[CostBenefitComponent],
    cost_components: list[CostBenefitComponent],
    raw_ratio: float,
    display_cap: float,
) -> list[str]:
    caveats = [
        str((item.method or {}).get("caveat_text") or METHOD_DISCLAIMER),
        "Compare within the same scenario/use-case only.",
        "Official recommendation rank remains the TOPSIS train ranking.",
    ]
    if any(component.status == "missing" for component in [*benefit_components, *cost_components]):
        caveats.append("Some cost-burden inputs are missing; ratio is indicative.")
    if raw_ratio > display_cap:
        caveats.append("Display is capped to avoid false precision above 5.00.")
    return _unique(caveats)


def _apply_safety_caps(
    item: CostBenefitInput,
    label: str,
    caveats: list[str],
) -> tuple[str, list[str]]:
    context = item.context
    location_context = item.location_context
    train = item.train
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    use_case = normalize_match_key(context.get("use_case")) or ""
    flags = location_context.get("context_flags") or {}
    status = normalize_match_key((train.get("applicability_result") or {}).get("status"))
    capped = label

    if status == "rejected" or flags.get("industrial_pretreatment_required"):
        capped = "Needs expert review"
    if _industrial_source(source):
        capped = "Needs expert review"
        caveats = _append_once(caveats, "Pretreatment required; NbS polishing only.")
    if use_case in {"drinking", "drinking_strict_use", "potable", "strict_use"}:
        capped = "Needs expert review"
        caveats = _append_once(
            caveats,
            "Expert-review only; not standalone potable treatment.",
        )
    if flags.get("mainstem_or_high_order") or flags.get("off_channel_required"):
        caveats = _append_once(
            caveats,
            "Off-channel/interception treatment required; no in-channel cells.",
        )
    return capped, caveats


def _industrial_source(source: str) -> bool:
    return "industrial" in source or "mixed_industrial" in source


def _insufficient_cost_evidence(components: list[CostBenefitComponent]) -> bool:
    required = {"C7", "C8", "energy", "land_constraint"}
    missing = {
        component.key
        for component in components
        if component.key in required and component.status == "missing"
    }
    return len(missing) >= 2


def _label(ratio: float) -> str:
    if ratio >= 2.0:
        return "Very favourable"
    if ratio >= 1.2:
        return "Favourable"
    if ratio >= 0.8:
        return "Balanced / site-dependent"
    return "Cost-heavy / needs review"


def _display_ratio(ratio: float, display_cap: float) -> str:
    if ratio > display_cap:
        return ">5.00"
    return f"{ratio:.2f}"


def _method_floor(method: dict[str, Any]) -> float:
    return float(method.get("denominator_floor") or DENOMINATOR_FLOOR)


def _method_display_cap(method: dict[str, Any]) -> float:
    return float(method.get("display_cap") or DISPLAY_CAP)


def _default_method() -> dict[str, Any]:
    return {
        "method_key": METHOD_KEY,
        "method_name": METHOD_NAME,
        "version": "v1",
        "is_monetary": 0,
        "formula_text": FORMULA_TEXT,
        "denominator_floor": DENOMINATOR_FLOOR,
        "display_cap": DISPLAY_CAP,
        "caveat_text": METHOD_DISCLAIMER,
    }


def _append_once(values: list[str], value: str) -> list[str]:
    if value not in values:
        return [*values, value]
    return values


def _unique(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result

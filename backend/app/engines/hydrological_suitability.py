"""C4 engine for transparent NbS hydrological-suitability scoring.

This module implements the MCDA criterion **C4 — Hydrological suitability** from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` (section 12.4): score how well
the receiving water's flow/dilution scale at the site matches the flow-handling
capacity of each NbS family.

Per the spec, the criterion:

- uses true ``stream_order`` when available, otherwise falls back to a
  ``drainage_area_km2`` (or ``dilution_proxy``) **dilution proxy**, and
- **must report when it used a proxy** instead of true stream order.

Slope is intentionally NOT scored here — it belongs to C3 (site_suitability) — so
the two criteria stay distinct and are not double-counted.

Like C3, the family flow-capacity rules are **provisional, literature-informed
defaults** (not expert-validated) and every result is flagged
`provisional_not_expert_validated`. No site values, removal efficiencies, AHP
weights, or health-risk scores are invented. Missing flow data yields ``None``
(left unscored) rather than a guessed value.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.site_suitability import classify_family


HYDRO_STATUS_PROVISIONAL = "provisional_not_expert_validated"
HYDRO_STATUS_DATA_PENDING = "data_pending"

PROVISIONAL_NOTE = (
    "C4 hydrological_suitability uses provisional, family-based flow-capacity "
    "rules that are not expert-validated; treat as developmental, not final "
    "scientific validation."
)

# Strahler stream-order thresholds for the site flow scale (transparent defaults).
STREAM_ORDER_HIGH = 5.0
STREAM_ORDER_MODERATE = 3.0

# Drainage-area thresholds (km2) used ONLY as a dilution proxy when true stream
# order is unavailable. Crossing to a proxy is always reported.
DRAINAGE_AREA_HIGH_KM2 = 1000.0
DRAINAGE_AREA_MODERATE_KM2 = 100.0

# --- Provisional per-family flow-handling capacity --------------------------
# "high"     -> large open systems that suit bigger flows (ponds, surface
#               wetlands, riparian buffers along larger watercourses)
# "moderate" -> mid-scale engineered cells
# "low"      -> small, diffuse, low-flow systems (rain gardens, bioretention,
#               small subsurface wetlands)
DEFAULT_FLOW_CAPACITY_BY_FAMILY: dict[str, str] = {
    "surface_water_wetland_pond": "high",
    "vegetated_buffer": "high",
    "subsurface_wetland": "moderate",
    "infiltration_based": "low",
}

# Fit between a family's flow capacity and the site's flow scale. Higher is a
# better match of NbS scale to hydrological scale.
FLOW_FIT_TABLE: dict[str, dict[str, float]] = {
    "high": {"high": 1.0, "moderate": 0.8, "low": 0.6},
    "moderate": {"high": 0.6, "moderate": 0.9, "low": 0.8},
    "low": {"high": 0.3, "moderate": 0.7, "low": 1.0},
}


@dataclass(slots=True)
class HydrologicalSuitabilityResult:
    """C4 hydrological-suitability score plus its transparent breakdown."""

    hydrological_suitability: float | None
    flow_scale: str | None
    flow_capacity: str | None
    flow_metric_used: str | None
    proxy_used: bool
    family_class: str
    status: str
    used_site_fields: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for matrix rows, tests, or future APIs."""

        return asdict(self)


def compute_hydrological_suitability(
    option: dict[str, Any] | None,
    site_context: dict[str, Any] | None,
    flow_capacity_by_family: dict[str, str] | None = None,
) -> HydrologicalSuitabilityResult:
    """Score how well the site's flow/dilution scale fits one NbS family."""

    flow_capacity_by_family = flow_capacity_by_family or DEFAULT_FLOW_CAPACITY_BY_FAMILY
    family_class = classify_family(option)
    site_context = site_context or {}

    notes: list[str] = [PROVISIONAL_NOTE]
    used_site_fields: list[str] = []
    missing_inputs: list[str] = []

    capacity = flow_capacity_by_family.get(family_class)
    if capacity is None:
        notes.append(
            "NbS family was not matched to a provisional flow-capacity profile "
            f"(family_class={family_class}); C4 left unscored."
        )
        return HydrologicalSuitabilityResult(
            hydrological_suitability=None,
            flow_scale=None,
            flow_capacity=None,
            flow_metric_used=None,
            proxy_used=False,
            family_class=family_class,
            status=HYDRO_STATUS_DATA_PENDING,
            used_site_fields=used_site_fields,
            missing_inputs=["nbs_family_profile"],
            notes=notes,
        )

    flow_scale, metric_field, proxy_used = _site_flow_scale(site_context)
    if flow_scale is None:
        missing_inputs.append("flow_scale")
        notes.append(
            "No stream order or drainage-area data was available; C4 "
            "hydrological_suitability left unscored."
        )
        return HydrologicalSuitabilityResult(
            hydrological_suitability=None,
            flow_scale=None,
            flow_capacity=capacity,
            flow_metric_used=None,
            proxy_used=False,
            family_class=family_class,
            status=HYDRO_STATUS_DATA_PENDING,
            used_site_fields=used_site_fields,
            missing_inputs=missing_inputs,
            notes=notes,
        )

    used_site_fields.append(metric_field)
    score = FLOW_FIT_TABLE[capacity][flow_scale]
    if proxy_used:
        notes.append(
            f"C4 used the {metric_field} dilution proxy because true stream order "
            "was unavailable; interpret the flow scale with caution."
        )
    else:
        notes.append("C4 used true stream order for the site flow scale.")
    notes.append(
        f"hydrological_suitability={score}: family flow capacity '{capacity}' vs "
        f"site flow scale '{flow_scale}' from {metric_field}."
    )

    return HydrologicalSuitabilityResult(
        hydrological_suitability=score,
        flow_scale=flow_scale,
        flow_capacity=capacity,
        flow_metric_used=metric_field,
        proxy_used=proxy_used,
        family_class=family_class,
        status=HYDRO_STATUS_PROVISIONAL,
        used_site_fields=used_site_fields,
        missing_inputs=missing_inputs,
        notes=notes,
    )


def _site_flow_scale(site_context: dict[str, Any]) -> tuple[str | None, str, bool]:
    """Return (flow_scale, metric_field, proxy_used) from the best available field.

    Prefers true ``stream_order``; falls back to ``drainage_area_km2`` then
    ``dilution_proxy`` as a dilution proxy, flagging proxy use.
    """

    order = _as_float(site_context.get("stream_order"))
    if order is not None:
        if order >= STREAM_ORDER_HIGH:
            return "high", "stream_order", False
        if order >= STREAM_ORDER_MODERATE:
            return "moderate", "stream_order", False
        return "low", "stream_order", False

    for field_name in ("drainage_area_km2", "dilution_proxy"):
        area = _as_float(site_context.get(field_name))
        if area is None:
            continue
        if area >= DRAINAGE_AREA_HIGH_KM2:
            return "high", field_name, True
        if area >= DRAINAGE_AREA_MODERATE_KM2:
            return "moderate", field_name, True
        return "low", field_name, True

    return None, "", False


def _as_float(value: Any) -> float | None:
    """Convert a scalar value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

"""C5 engine for transparent NbS pollution-source fit scoring.

Implements the MCDA criterion **C5 — Pollution-source fit** from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` (section 12.5): match the
dominant pollution context at the site to the NbS families that the literature
treats as strong for that context.

The pollution context is inferred **transparently** from data already in hand:

- the classified treatment-need groups (metals -> industrial; pathogens ->
  sewage/domestic), then
- the site land-cover mix (built-up dominant -> urban runoff; agriculture
  dominant -> agricultural runoff), else "mixed".

Explicit `pollution_sources` point/non-point integration is a documented future
enhancement; nothing is invented here. The family->context strength map is a
provisional, literature-informed default flagged
`provisional_not_expert_validated`. Missing context leaves C5 unscored.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.site_suitability import classify_family


POLLUTION_FIT_STATUS_PROVISIONAL = "provisional_not_expert_validated"
POLLUTION_FIT_STATUS_DATA_PENDING = "data_pending"

PROVISIONAL_NOTE = (
    "C5 pollution_source_fit uses a provisional, family-based context map that "
    "is not expert-validated; explicit pollution_sources integration is pending."
)

# Provisional map: which family classes are strong for each pollution context
# (engine spec section 12.5 family/context table, mapped to our family taxonomy).
DEFAULT_STRONG_FAMILIES_BY_CONTEXT: dict[str, set[str]] = {
    "agricultural_runoff": {"vegetated_buffer", "surface_water_wetland_pond"},
    "urban_runoff": {"infiltration_based", "surface_water_wetland_pond"},
    "sewage_domestic": {"surface_water_wetland_pond", "subsurface_wetland"},
    "industrial_metals": {"subsurface_wetland"},
    "mixed": set(),  # treatment-train territory; no single strong family
}


@dataclass(slots=True)
class PollutionSourceFitResult:
    """C5 pollution-source fit score plus its transparent breakdown."""

    pollution_source_fit: float | None
    pollution_context: str | None
    context_source: str | None
    family_class: str
    status: str
    cautions: list[str] = field(default_factory=list)
    used_inputs: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for matrix rows, tests, or future APIs."""

        return asdict(self)


def compute_pollution_source_fit(
    option: dict[str, Any] | None,
    site_context: dict[str, Any] | None,
    treatment_need_groups: list[str] | None,
    strong_families_by_context: dict[str, set[str]] | None = None,
) -> PollutionSourceFitResult:
    """Score how well one NbS family fits the site's dominant pollution context."""

    strong_families_by_context = (
        strong_families_by_context or DEFAULT_STRONG_FAMILIES_BY_CONTEXT
    )
    family_class = classify_family(option)
    notes: list[str] = [PROVISIONAL_NOTE]
    cautions: list[str] = []
    used_inputs: list[str] = []
    missing_inputs: list[str] = []

    context, context_source = _determine_context(
        site_context or {}, treatment_need_groups or [], used_inputs
    )
    if context is None:
        missing_inputs.append("pollution_context")
        notes.append("No treatment-need or land-cover signal; C5 left unscored.")
        return PollutionSourceFitResult(
            pollution_source_fit=None,
            pollution_context=None,
            context_source=None,
            family_class=family_class,
            status=POLLUTION_FIT_STATUS_DATA_PENDING,
            cautions=cautions,
            used_inputs=used_inputs,
            missing_inputs=missing_inputs,
            notes=notes,
        )

    if family_class == "unclassified":
        missing_inputs.append("nbs_family_profile")
        notes.append(
            "NbS family was not matched to a family class; C5 left unscored."
        )
        return PollutionSourceFitResult(
            pollution_source_fit=None,
            pollution_context=context,
            context_source=context_source,
            family_class=family_class,
            status=POLLUTION_FIT_STATUS_DATA_PENDING,
            cautions=cautions,
            used_inputs=used_inputs,
            missing_inputs=missing_inputs,
            notes=notes,
        )

    strong_families = strong_families_by_context.get(context, set())
    if context == "mixed":
        score = 0.6
        notes.append(
            "Mixed catchment pressure: no single family is strongly preferred; "
            "consider a treatment-train. C5 scored neutral."
        )
    elif family_class in strong_families:
        score = 1.0
        notes.append(
            f"Family '{family_class}' is a strong fit for context '{context}'."
        )
    else:
        score = 0.4
        notes.append(
            f"Family '{family_class}' is a weak fit for context '{context}'."
        )

    if context == "industrial_metals" and family_class not in strong_families:
        cautions.append(
            "Industrial/metals context: only controlled polishing/phytoremediation "
            "systems are appropriate; expert review and controlled disposal needed."
        )

    return PollutionSourceFitResult(
        pollution_source_fit=score,
        pollution_context=context,
        context_source=context_source,
        family_class=family_class,
        status=POLLUTION_FIT_STATUS_PROVISIONAL,
        cautions=cautions,
        used_inputs=used_inputs,
        missing_inputs=missing_inputs,
        notes=notes,
    )


def _determine_context(
    site_context: dict[str, Any],
    treatment_need_groups: list[str],
    used_inputs: list[str],
) -> tuple[str | None, str | None]:
    """Infer the dominant pollution context from needs, then land cover."""

    needs = {str(group).lower() for group in treatment_need_groups}
    if "metals" in needs:
        used_inputs.append("treatment_need_groups")
        return "industrial_metals", "treatment_need_groups"
    if "pathogens" in needs:
        used_inputs.append("treatment_need_groups")
        return "sewage_domestic", "treatment_need_groups"

    agri = _as_float(site_context.get("agri_frac"))
    builtup = _as_float(site_context.get("builtup_frac"))
    if agri is not None or builtup is not None:
        used_inputs.append("land_cover_fractions")
        agri_value = agri or 0.0
        builtup_value = builtup or 0.0
        if builtup_value >= 0.5 and builtup_value >= agri_value:
            return "urban_runoff", "land_cover_fractions"
        if agri_value >= 0.5 and agri_value > builtup_value:
            return "agricultural_runoff", "land_cover_fractions"
        return "mixed", "land_cover_fractions"

    if needs:
        used_inputs.append("treatment_need_groups")
        return "mixed", "treatment_need_groups"

    return None, None


def _as_float(value: Any) -> float | None:
    """Convert a scalar value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

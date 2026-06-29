"""Safety-aware presentation layer for individual NbS recommendations.

Treatment trains remain the primary wastewater recommendation. This engine
enriches the existing A0-screened component ranking with canonical catalogue,
removal, implementation, plant, and provenance fields. It does not calculate
new removal values or replace the treatment-train TOPSIS result.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.engines.input_normalization import normalize_match_key


SOURCE_CONTROL_TOKENS = {
    "bioretention",
    "rain_garden",
    "bioswale",
    "vegetated_swale",
    "filter_strip",
    "vegetated_buffer",
}
HIGH_RISK_CONTEXT_EXCLUSION_TOKENS = {
    "bioretention",
    "rain_garden",
    "bioswale",
    "vegetated_swale",
    "filter_strip",
    "vegetated_buffer",
    "buffer_strip",
    "green_roof",
    "green_wall",
    "roof",
    "stormwater",
}
STORMWATER_ONLY_TOKENS = {
    "green_roof",
    "green_wall",
    "roof",
    "rain_garden",
    "bioswale",
    "filter_strip",
    "vegetated_buffer",
    "buffer_strip",
}
PRIMARY_PROCESS_TOKENS = {
    "anaerobic_baffled_reactor",
    "dewats",
    "uasb",
    "anaerobic_filter",
}
DISPOSAL_TOKENS = {"soak_pit", "soakaway", "leach_field", "drain_field", "infiltration"}


class NbsProfileProvider(Protocol):
    """Catalogue interface required by the component presentation engine."""

    def list_options(self) -> list[dict[str, Any]]:
        """Return canonical NbS options."""

    def get_full_nbs_profile(self, nbs_id: int) -> dict[str, Any]:
        """Return canonical evidence and implementation rows for one option."""


class PlantProvider(Protocol):
    """Non-invasive plant lookup required by the component engine."""

    def get_plants_for_nbs(
        self,
        nbs_id: int,
        *,
        include_invasive: bool = False,
    ) -> list[dict[str, Any]]:
        """Return explicit plant mappings for one component."""


class IndividualNbsRecommendationEngine:
    """Build a separate component layer without changing train primacy."""

    def __init__(
        self,
        catalogue: NbsProfileProvider,
        plants: PlantProvider,
    ) -> None:
        self.catalogue = catalogue
        self.plants = plants

    def assemble(
        self,
        *,
        assembly_bundle: dict[str, Any] | None,
        candidate_bundle: dict[str, Any] | None,
        applicability_bundle: dict[str, Any] | None,
        context: dict[str, Any],
        contaminant_gaps: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Return recommended and filtered component records.

        Existing measured-data TOPSIS order is preserved. When the scientific
        workflow cannot rank a context-only request, options remain explicitly
        unscored and are ordered by transparent context role, then catalogue ID.
        """

        context = dict(context)
        context["_requires_neutralization"] = _has_extreme_ph(
            contaminant_gaps or []
        )
        ranked = list((assembly_bundle or {}).get("recommendations") or [])
        candidates = {
            row.get("nbs_id"): row
            for row in (candidate_bundle or {}).get("results") or []
            if row.get("nbs_id") is not None
        }
        applicability = {
            row.get("nbs_id"): row
            for row in (applicability_bundle or {}).get("results") or []
            if row.get("nbs_id") is not None
        }
        rejected = {
            row.get("nbs_id"): row
            for row in (applicability_bundle or {}).get("rejected_options") or []
            if row.get("nbs_id") is not None
        }

        if ranked:
            ordered = ranked
            method = "a0_screened_component_topsis"
        else:
            ordered = [
                {
                    "nbs_id": option.get("id"),
                    "nbs_name": option.get("solution"),
                    "rank": None,
                    "match_score": None,
                    "confidence_score": None,
                    "evidence_summary": {},
                }
                for option in self.catalogue.list_options()
                if option.get("id") not in rejected
            ]
            ordered.sort(key=lambda row: _context_sort_key(row, context))
            method = "a0_screened_context_role_order"

        recommendations: list[dict[str, Any]] = []
        context_filtered: list[dict[str, Any]] = []
        for row in ordered:
            nbs_id = row.get("nbs_id")
            if nbs_id is None:
                continue
            identity = self._component_identity(int(nbs_id), row)
            if _excluded_in_high_risk_context(
                identity["name"],
                identity.get("family"),
                context,
            ) or _excluded_non_stormwater_component(
                identity["name"],
                identity.get("family"),
                context,
            ):
                context_filtered.append(
                    {
                        "nbs_id": nbs_id,
                        "name": identity["name"],
                        "status": "not_suitable_for_scenario",
                        "reasons": _high_risk_context_exclusion_reasons(context),
                    }
                )
                continue
            recommendations.append(
                self._component(
                    row,
                    candidate=candidates.get(nbs_id, {}),
                    applicability=applicability.get(nbs_id, {}),
                    context=context,
                    method=method,
                )
            )
        filtered = [
            {
                "nbs_id": nbs_id,
                "name": row.get("nbs_name"),
                "status": "not_suitable_for_context",
                "reasons": _unique(
                    [
                        *(row.get("user_messages") or []),
                        *(row.get("technical_reasons") or []),
                    ]
                ),
            }
            for nbs_id, row in sorted(rejected.items())
        ] + context_filtered
        return {
            "method": method,
            "train_recommendation_remains_primary": True,
            "recommendations": recommendations,
            "filtered_components": filtered,
            "warnings": [
                "Individual components support the primary treatment-train decision.",
                "Context-only component ordering is rule-based and unscored.",
            ],
        }

    def _component_identity(
        self,
        nbs_id: int,
        ranked: dict[str, Any],
    ) -> dict[str, Any]:
        """Return the minimum catalogue identity needed for scenario filtering."""

        profile = self.catalogue.get_full_nbs_profile(nbs_id)
        option = profile.get("option") or {}
        return {
            "name": str(
                option.get("solution")
                or ranked.get("nbs_name")
                or "NbS component"
            ),
            "family": option.get("family"),
        }

    def _component(
        self,
        ranked: dict[str, Any],
        *,
        candidate: dict[str, Any],
        applicability: dict[str, Any],
        context: dict[str, Any],
        method: str,
    ) -> dict[str, Any]:
        nbs_id = int(ranked["nbs_id"])
        profile = self.catalogue.get_full_nbs_profile(nbs_id)
        option = profile.get("option") or {}
        removal_rows = profile.get("removal_efficiencies") or []
        implementation = profile.get("implementation") or []
        plants = [
            plant
            for plant in self.plants.get_plants_for_nbs(
                nbs_id,
                include_invasive=False,
            )
            if plant.get("invasive") in {0, None}
            and "invasive" not in str(plant.get("native_status") or "").lower()
        ]
        name = str(option.get("solution") or ranked.get("nbs_name") or "NbS component")
        family = option.get("family") or candidate.get("nbs_family")
        role = _role(name, family, context)
        standalone, standalone_guidance = _standalone(role, context)
        context_guidance = _context_guidance(name, role, context)
        source_ids = _source_ids(
            ranked,
            candidate,
            option,
            removal_rows,
            implementation,
        )
        constraints = _unique(
            [
                *(candidate.get("caution_flags") or []),
                *(candidate.get("data_pending_reasons") or []),
                *(applicability.get("caveats") or []),
                *context_guidance["constraints"],
            ]
        )
        return {
            "nbs_id": nbs_id,
            "name": name,
            "family": family,
            "component_rank": ranked.get("rank"),
            "suitability_score": ranked.get("match_score"),
            "suitability_basis": (
                "A0-screened component TOPSIS"
                if method == "a0_screened_component_topsis"
                else "A0-screened context role; not numerically scored"
            ),
            "role": role,
            "pollutants_addressed": _pollutants(removal_rows),
            "where_suitable": _unique(
                [
                    str(value)
                    for value in (
                        option.get("optimal_water_type"),
                        option.get("location_suitability"),
                        *context_guidance["suitable"],
                    )
                    if value
                ]
            ),
            "where_not_suitable": context_guidance["not_suitable"],
            "standalone_suitability": standalone,
            "standalone_guidance": standalone_guidance,
            "key_constraints": constraints,
            "implementation_guidance": _implementation_text(implementation),
            "plants": plants,
            "planting_guidance": (
                "Use only explicit non-invasive catalogue mappings and validate locally."
                if plants
                else "Planting guidance requires local validation."
            ),
            "source_ids": source_ids,
            "evidence_status": candidate.get("eligibility_status") or "context_screening",
            "applicability_status": applicability.get("applicability_status") or "not_assessed",
            "train_recommendation_remains_primary": True,
        }


def _role(name: str, family: Any, context: dict[str, Any]) -> str:
    text = normalize_match_key(f"{name} {family or ''}") or ""
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    position = normalize_match_key(context.get("intervention_position")) or ""
    if "industrial" in source:
        return "polishing_or_buffer"
    if _contains(text, SOURCE_CONTROL_TOKENS):
        return "source_control"
    if position == "in_channel" or _number(context.get("stream_order")) >= 5:
        return "off_channel_buffer_or_polishing"
    if _contains(text, DISPOSAL_TOKENS):
        return "disposal"
    if _contains(text, PRIMARY_PROCESS_TOKENS):
        return "primary_train_component"
    return "secondary_or_polishing"


def _standalone(role: str, context: dict[str, Any]) -> tuple[str, str]:
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    if "industrial" in source:
        return (
            "only_as_part_of_train",
            "For industrial wastewater, this component is polishing/buffer only after ETP/CETP or equivalent pretreatment.",
        )
    if role == "source_control" and "agriculture" in source:
        return (
            "can_be_standalone_source_control",
            "This may be implemented as a source-control measure; it is not standalone treatment for collected wastewater.",
        )
    return (
        "only_as_part_of_train",
        "This component supports a treatment train; it is not recommended as standalone treatment for untreated sewage.",
    )


def _context_guidance(
    name: str,
    role: str,
    context: dict[str, Any],
) -> dict[str, list[str]]:
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    position = normalize_match_key(context.get("intervention_position")) or ""
    high_order = position == "in_channel" or _number(context.get("stream_order")) >= 5
    suitable: list[str] = []
    not_suitable: list[str] = []
    constraints: list[str] = []
    if "industrial" in source:
        suitable.append("Polishing or buffering after ETP/CETP and source-specific pretreatment.")
        not_suitable.append("Primary or standalone treatment of untreated industrial wastewater.")
        constraints.append("ETP/CETP pretreatment and compliance verification are required.")
        if context.get("_requires_neutralization"):
            constraints.append(
                "Neutralization and pH control are required before biological or NbS stages."
            )
    if "agriculture" in source:
        if role == "source_control":
            suitable.append("Field-edge or drainage-path source control where local slope and land allow.")
        else:
            suitable.append("Off-channel polishing only after runoff is collected and source controls are applied.")
        not_suitable.append("A substitute for farm-level nutrient, erosion, and sediment source control.")
    if high_order:
        suitable.append("Drain interception, bank-side buffer, or off-channel treatment.")
        not_suitable.append("An in-channel treatment cell in a mainstem or high-order river.")
        constraints.append("Keep treatment infrastructure off-channel and protect river conveyance.")
    if role == "disposal":
        constraints.append("Confirm soil, groundwater, loading, setbacks, and public-health protection.")
    if not suitable:
        suitable.append(f"Use {name} only where its canonical site and design conditions are validated.")
    return {
        "suitable": _unique(suitable),
        "not_suitable": _unique(not_suitable),
        "constraints": _unique(constraints),
    }


def _context_sort_key(row: dict[str, Any], context: dict[str, Any]) -> tuple[int, int]:
    text = normalize_match_key(row.get("nbs_name")) or ""
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    if "agriculture" in source:
        priority = 0 if _contains(text, SOURCE_CONTROL_TOKENS) else 1
    elif "industrial" in source:
        priority = 1
    else:
        priority = 0
    return priority, int(row.get("nbs_id") or 0)


def _excluded_in_high_risk_context(
    name: str,
    family: Any,
    context: dict[str, Any],
) -> bool:
    """Hide stormwater/roof/source-control items from high-risk recommendations."""

    if not _is_high_risk_exclusion_context(context):
        return False
    text = normalize_match_key(f"{name} {family or ''}") or ""
    return _contains(text, HIGH_RISK_CONTEXT_EXCLUSION_TOKENS)


def _excluded_non_stormwater_component(
    name: str,
    family: Any,
    context: dict[str, Any],
) -> bool:
    """Hide stormwater-only components unless the source is runoff/stormwater."""

    if normalize_match_key(context.get("use_case")) == "drinking":
        return False
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    if "stormwater" in source or "runoff" in source or "agriculture" in source:
        return False
    text = normalize_match_key(f"{name} {family or ''}") or ""
    return _contains(text, STORMWATER_ONLY_TOKENS)


def _is_high_risk_exclusion_context(context: dict[str, Any]) -> bool:
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    position = normalize_match_key(context.get("intervention_position")) or ""
    high_order_in_channel = (
        _number(context.get("stream_order")) >= 5
        and position in {"in_channel", "mainstem", "mainstem_high_order"}
    )
    return (
        "industrial" in source
        or context.get("_requires_neutralization") is True
        or high_order_in_channel
    )


def _high_risk_context_exclusion_reasons(context: dict[str, Any]) -> list[str]:
    reasons = [
        "Excluded from current recommendations because this scenario requires treatment-train, pretreatment, or off-channel controls before any polishing/source-control component.",
        "Roof, wall, rain-garden, bioswale, and filter-strip components remain catalogue items for suitable stormwater or urban-runoff contexts only.",
    ]
    source = normalize_match_key(context.get("pollution_source_type")) or ""
    position = normalize_match_key(context.get("intervention_position")) or ""
    if "industrial" in source:
        reasons.append(
            "ETP/CETP pretreatment and compliance verification are required for industrial or mixed-industrial wastewater."
        )
    if context.get("_requires_neutralization"):
        reasons.append(
            "Neutralization and pH control are required before biological or NbS stages."
        )
    if position == "in_channel" or _number(context.get("stream_order")) >= 5:
        reasons.append(
            "High-order or in-channel contexts require off-channel treatment and must protect river conveyance."
        )
    return _unique(reasons)


def _pollutants(rows: list[dict[str, Any]]) -> list[str]:
    return _unique(
        [
            str(row.get("parameter"))
            for row in rows
            if row.get("parameter")
            and (row.get("eff_low") is not None or row.get("eff_high") is not None)
        ]
    )


def _implementation_text(rows: list[dict[str, Any]]) -> list[str]:
    return _unique(
        [
            str(row.get(key))
            for row in rows
            for key in ("implementation_steps", "maintenance_requirements")
            if row.get(key)
        ]
    )


def _source_ids(*groups: Any) -> list[int]:
    values: list[int] = []
    for group in groups:
        rows = group if isinstance(group, list) else [group]
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key in ("source_id", "source_ids", "evidence_source_ids", "implementation_source_ids"):
                raw = row.get(key)
                items = raw if isinstance(raw, list) else [raw]
                for item in items:
                    try:
                        value = int(item)
                    except (TypeError, ValueError):
                        continue
                    if value not in values:
                        values.append(value)
    return values


def _contains(text: str, tokens: set[str]) -> bool:
    return any(token in text for token in tokens)


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _has_extreme_ph(gaps: list[dict[str, Any]]) -> bool:
    for row in gaps:
        if normalize_match_key(row.get("parameter")) != "ph":
            continue
        try:
            value = float(row.get("observed_value"))
        except (TypeError, ValueError):
            continue
        if value < 6.0 or value > 9.0:
            return True
    return False


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        stripped = value.strip()
        if stripped and stripped not in result:
            result.append(stripped)
    return result

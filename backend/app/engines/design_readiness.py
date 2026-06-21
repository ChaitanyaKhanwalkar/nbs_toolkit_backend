"""Apply transparent, conservative design-readiness rules.

This engine does not size infrastructure or infer missing field values. It
classifies how the current evidence can be used and lists what must be supplied
or verified before engineering design.
"""

from typing import Any


class DesignReadinessEngine:
    """Classify one recommendation into a four-level readiness model."""

    def assess(
        self,
        *,
        measured_observations: list[dict[str, Any]],
        context: dict[str, Any],
        location_context: dict[str, Any],
        ranked_trains: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return readiness, checklist statuses, reasons, and next steps."""

        observations = {
            str(row.get("parameter") or "").lower(): row.get("value")
            for row in measured_observations
            if row.get("parameter") and row.get("value") is not None
        }
        flags = location_context.get("context_flags") or {}
        source_type = str(context.get("pollution_source_type") or "").lower()
        industrial = bool(flags.get("industrial_pretreatment_required")) or (
            "industrial" in source_type
        )
        extreme_ph = _extreme_ph(observations.get("ph"))
        high_order = bool(flags.get("mainstem_or_high_order"))
        in_channel = context.get("intervention_position") == "in_channel"
        agricultural = bool(flags.get("agricultural_source_control_first"))
        top_confidence = (
            str(ranked_trains[0].get("confidence_label") or "").lower()
            if ranked_trains
            else ""
        )
        confidence_supports_preliminary = top_confidence in {"medium", "high"}

        checklist = _input_checklist(observations, context, location_context)
        missing_inputs = [
            item["label"]
            for item in checklist
            if item["status"]
            in {
                "not_supplied",
                "mapped_context_verify",
                "needs_field_check",
                "missing_before_engineering_design",
            }
        ]
        parameters = set(observations)
        core_panel = {"bod", "cod", "tss", "ph"}.issubset(parameters)
        nutrient_present = bool(
            parameters & {"ammonia_n", "nitrate_n", "phosphate_p", "total_p"}
        )
        extended_panel = nutrient_present and {"do", "faecal_coliform"}.issubset(
            parameters
        )
        design_context_complete = all(
            _present(context, key)
            for key in (
                "design_flow",
                "peak_flow",
                "available_land",
                "groundwater_depth",
                "flood_risk",
                "inlet_outlet_levels",
                "om_owner_capacity",
            )
        )
        site_verified = all(
            _present(context, key) for key in ("site_slope", "soil_infiltration")
        )

        expert_reasons = []
        if industrial:
            expert_reasons.append("Industrial or mixed-industrial context requires ETP/CETP review.")
        if extreme_ph:
            expert_reasons.append("Extreme pH requires neutralization and expert review.")
        if high_order or in_channel:
            expert_reasons.append(
                "Mainstem/high-order placement requires off-channel treatment and expert review."
            )

        if expert_reasons:
            level = "needs_expert_review"
            short_label = "Expert review needed"
            explanation = (
                "Safety or site-risk conditions require expert review before the option is advanced."
            )
            reasons = expert_reasons
            expert_review_required = True
        elif len(observations) <= 1:
            level = "early_screening_only"
            short_label = "Needs field data"
            explanation = (
                "Use this only to understand possible options. More field and water-quality data are needed."
            )
            reasons = [
                "Only one or no usable water-quality value was supplied.",
                "Engineering design still requires site and flow information.",
            ]
            expert_review_required = False
        elif (
            core_panel
            and extended_panel
            and design_context_complete
            and site_verified
            and confidence_supports_preliminary
            and not flags.get("site_context_incomplete")
        ):
            level = "preliminary_design_ready"
            short_label = "Preliminary design ready"
            explanation = (
                "Enough key inputs are available for preliminary sizing/design review, but expert validation is still needed."
            )
            reasons = [
                "The core, nutrient, DO, and faecal-coliform screening panel is available.",
                "Design flow, land, site, level, flood, groundwater, and O&M context were supplied.",
                "Recommendation confidence supports preliminary review.",
            ]
            expert_review_required = True
        elif core_panel:
            level = "planning_level_result"
            short_label = "Ready for planning"
            explanation = (
                "Suitable for comparing options and planning next studies. Engineering design is still required."
            )
            reasons = [
                "BOD, COD, TSS, and pH are available for screening.",
                "Preliminary-design inputs, field verification, or confidence remain incomplete.",
            ]
            expert_review_required = False
        else:
            level = "early_screening_only"
            short_label = "Needs field data"
            explanation = (
                "Use this only to understand possible options. More field and water-quality data are needed."
            )
            reasons = [
                "The BOD, COD, TSS, and pH screening panel is incomplete.",
                "Upload recent water-quality data to improve confidence.",
            ]
            expert_review_required = False

        next_steps = _next_steps(
            checklist=checklist,
            industrial=industrial,
            extreme_ph=extreme_ph,
            off_channel=bool(flags.get("off_channel_required")),
            agricultural=agricultural,
            has_ranked_train=bool(ranked_trains),
        )
        return {
            "level": level,
            "short_label": short_label,
            "explanation": explanation,
            "reasons": reasons,
            "missing_inputs": missing_inputs,
            "required_next_steps": next_steps,
            "expert_review_required": expert_review_required,
            "input_checklist": checklist,
        }


def _input_checklist(
    observations: dict[str, Any],
    context: dict[str, Any],
    location: dict[str, Any],
) -> list[dict[str, str]]:
    """Return every requested design input with an explicit status."""

    nutrient_keys = {"ammonia_n", "nitrate_n", "phosphate_p", "total_p"}
    items = [
        _context_item(
            "Treatment design flow", context, "design_flow", "not_supplied"
        ),
        _context_item(
            "Peak wastewater flow", context, "peak_flow", "not_supplied"
        ),
        {
            "key": "river_discharge_context",
            "label": "River discharge context",
            "status": (
                "available"
                if location.get("river_discharge_cms") is not None
                else "not_required_for_current_screening"
            ),
        },
        _observation_item("BOD", observations, {"bod"}),
        _observation_item("COD", observations, {"cod"}),
        _observation_item("TSS", observations, {"tss"}),
        _observation_item("pH", observations, {"ph"}),
        _observation_item("Nutrients", observations, nutrient_keys),
        _observation_item("DO", observations, {"do"}),
        _observation_item(
            "Faecal coliform / pathogens", observations, {"faecal_coliform"}
        ),
        _context_item(
            "Available land", context, "available_land", "not_supplied"
        ),
        _verified_site_item("Slope", context, "site_slope", location.get("slope_mean")),
        _verified_site_item(
            "Soil / infiltration",
            context,
            "soil_infiltration",
            location.get("soil_type") or location.get("infiltration_class"),
        ),
        _context_item(
            "Groundwater depth",
            context,
            "groundwater_depth",
            "missing_before_engineering_design",
        ),
        _context_item(
            "Flood risk", context, "flood_risk", "needs_field_check"
        ),
        _context_item(
            "Inlet / outlet levels",
            context,
            "inlet_outlet_levels",
            "missing_before_engineering_design",
        ),
        _context_item(
            "O&M owner / capacity",
            context,
            "om_owner_capacity",
            "needs_field_check",
        ),
    ]
    return items


def _observation_item(
    label: str, observations: dict[str, Any], keys: set[str]
) -> dict[str, str]:
    """Return availability for one measured parameter group."""

    return {
        "key": label.lower().replace(" ", "_").replace("/", "_"),
        "label": label,
        "status": "available" if keys & set(observations) else "not_supplied",
    }


def _context_item(
    label: str,
    context: dict[str, Any],
    key: str,
    missing_status: str = "missing_before_engineering_design",
) -> dict[str, str]:
    """Return availability for one explicitly supplied design context field."""

    return {
        "key": key,
        "label": label,
        "status": "available" if _present(context, key) else missing_status,
    }


def _verified_site_item(
    label: str,
    context: dict[str, Any],
    context_key: str,
    profile_value: Any,
) -> dict[str, str]:
    """Distinguish supplied site data from profile data needing field checks."""

    if _present(context, context_key):
        status = "available"
    elif profile_value is not None:
        status = "mapped_context_verify"
    else:
        status = "needs_field_check"
    return {"key": context_key, "label": label, "status": status}


def _next_steps(
    *,
    checklist: list[dict[str, str]],
    industrial: bool,
    extreme_ph: bool,
    off_channel: bool,
    agricultural: bool,
    has_ranked_train: bool,
) -> list[str]:
    """Return concise next actions tied to observed gaps and safety flags."""

    steps = []
    if any(
        item["status"]
        in {"not_supplied", "missing_before_engineering_design"}
        for item in checklist
    ):
        steps.append("Collect the missing water-quality, flow, land, and site inputs.")
    if any(
        item["status"] in {"mapped_context_verify", "needs_field_check"}
        for item in checklist
    ):
        steps.append("Verify mapped site factors through a field survey.")
    if industrial:
        steps.append("Confirm the ETP/CETP pretreatment pathway with an industrial specialist.")
    if extreme_ph:
        steps.append("Confirm neutralization and pH control before biological or NbS stages.")
    if off_channel:
        steps.append("Develop an off-channel layout; do not place treatment cells in the river.")
    if agricultural:
        steps.append("Confirm field and edge-of-field nutrient and sediment source controls first.")
    if has_ranked_train:
        steps.append("Review the preferred treatment train with a qualified engineer.")
    return steps


def _extreme_ph(value: Any) -> bool:
    """Use the same pH bounds already applied by the recommendation engines."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return numeric < 6.0 or numeric > 9.0


def _present(context: dict[str, Any], key: str) -> bool:
    """Return true for explicitly supplied non-empty context values."""

    aliases = {
        "design_flow": "design_flow_m3_d",
        "available_land": "available_land_m2",
    }
    value = context.get(key)
    if value is None or value == "":
        value = context.get(aliases.get(key, ""))
    return value is not None and value != ""

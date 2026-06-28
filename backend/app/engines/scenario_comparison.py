"""Create concise comparisons from already ranked treatment-train outputs.

The engine does not rerank or create a second scientific scenario. It packages
current alternatives and their stored sizing/O&M evidence for clear comparison.
"""

from typing import Any


class ScenarioComparisonEngine:
    """Compare current ranked alternatives without changing their rank."""

    def compare(
        self,
        *,
        ranked_trains: list[dict[str, Any]],
        component_recommendations: list[dict[str, Any]],
        sizing_estimates: list[dict[str, Any]],
        design_readiness: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Return option rows and plain-language takeaways."""

        sizing_by_train = {
            int(row["train_id"]): row for row in sizing_estimates
        }
        source_type = str(context.get("pollution_source_type") or "").lower()
        selected_use_case = str(context.get("use_case") or "").strip()
        off_channel = context.get("intervention_position") in {
            "off_channel_or_stp_polishing",
            "in_channel",
        } or _is_high_order(context.get("stream_order"))
        options = []
        for train in ranked_trains:
            train_id = int(train["train_id"])
            sizing = sizing_by_train.get(train_id) or {}
            options.append(
                {
                    "train_id": train_id,
                    "name": train.get("name"),
                    "rank": train.get("rank"),
                    "technical_match": train.get("match_score"),
                    "result_confidence": train.get("confidence_score"),
                    "confidence_label": train.get("confidence_label"),
                    "design_readiness": design_readiness.get("short_label"),
                    "land_demand": sizing.get("estimate_label"),
                    "land_fit": sizing.get("land_fit", "insufficient_data"),
                    "om_intensity": train.get("om_intensity", "Not recorded"),
                    "applicability_status": (
                        train.get("applicability_result") or {}
                    ).get("status"),
                    "selected_use_case_verdict": _use_case_verdict(
                        train,
                        selected_use_case,
                    ),
                    "warnings": list(train.get("caveats") or [])[:2],
                    "key_strength": _first_text(train.get("why_recommended")),
                    "key_limitation": _first_text(
                        train.get("caveats")
                        or train.get("pretreatment_requirements")
                    ),
                    "when_to_choose": _when_to_choose(
                        train=train,
                        source_type=source_type,
                        off_channel=off_channel,
                    ),
                }
            )

        takeaways = []
        if options:
            takeaways.append(
                {
                    "label": "Best overall fit",
                    "train_id": options[0]["train_id"],
                    "train_name": options[0]["name"],
                    "explanation": (
                        "This option has the highest current technical match after safety screening."
                    ),
                }
            )
        land_candidates = [
            row
            for row in sizing_estimates
            if row.get("estimated_area_high_m2") is not None
            and row.get("full_component_coverage") is True
        ]
        if land_candidates:
            lower_land = min(
                land_candidates, key=lambda row: row["estimated_area_high_m2"]
            )
            takeaways.append(
                {
                    "label": "Lower land demand",
                    "train_id": lower_land["train_id"],
                    "train_name": lower_land["train_name"],
                    "explanation": (
                        "This option has the smallest complete upper footprint estimate for the supplied inputs."
                    ),
                }
            )
        confidence_candidates = [
            option
            for option in options
            if isinstance(option.get("result_confidence"), (int, float))
        ]
        if confidence_candidates:
            pass_candidates = [
                option
                for option in confidence_candidates
                if option.get("selected_use_case_verdict") == "pass"
            ]
            strongest_pool = pass_candidates or confidence_candidates
            strongest = max(
                strongest_pool,
                key=lambda row: row["result_confidence"],
            )
            if pass_candidates:
                explanation = (
                    "This option has a stored pass verdict for the selected use case and the strongest result-confidence score among those confirmed alternatives."
                )
            else:
                explanation = (
                    "This option has the highest result-confidence score among the current alternatives."
                )
            takeaways.append(
                {
                    "label": "Strongest evidence",
                    "train_id": strongest["train_id"],
                    "train_name": strongest["name"],
                    "explanation": explanation,
                }
            )
        maintenance_order = {"Lower": 0, "Moderate": 1, "Higher": 2}
        maintenance_candidates = [
            option
            for option in options
            if option["om_intensity"] in maintenance_order
        ]
        if maintenance_candidates:
            lower_maintenance = min(
                maintenance_candidates,
                key=lambda row: maintenance_order[row["om_intensity"]],
            )
            takeaways.append(
                {
                    "label": "Lower maintenance",
                    "train_id": lower_maintenance["train_id"],
                    "train_name": lower_maintenance["name"],
                    "explanation": (
                        "Stored O&M and energy descriptors indicate the lowest relative intensity among current alternatives."
                    ),
                }
            )
        if design_readiness.get("expert_review_required"):
            takeaways.append(
                {
                    "label": "Needs expert review",
                    "train_id": options[0]["train_id"] if options else None,
                    "train_name": options[0]["name"] if options else None,
                    "explanation": design_readiness.get("explanation"),
                }
            )
        return {
            "comparison_scope": "current_ranked_alternatives",
            "current_scenario": {
                "workflow_mode": context.get("workflow_mode"),
                "design_flow_m3_d": context.get("design_flow_m3_d"),
                "population_equivalent": context.get("population_equivalent"),
                "available_land_m2": context.get("available_land_m2"),
            },
            "options": options,
            "component_options": [
                {
                    "nbs_id": component.get("nbs_id"),
                    "name": component.get("name"),
                    "role": component.get("role"),
                    "suitability_score": component.get("suitability_score"),
                    "standalone_suitability": component.get(
                        "standalone_suitability"
                    ),
                    "applicability_status": component.get(
                        "applicability_status"
                    ),
                    "key_constraints": list(
                        component.get("key_constraints") or []
                    )[:2],
                }
                for component in component_recommendations[:5]
            ],
            "takeaways": takeaways,
            "limitations": [
                "This comparison uses the current input scenario; changing water quality or site inputs requires a new run.",
                "Unknown footprint or O&M evidence remains unknown and is not scored as zero.",
            ],
        }


def _first_text(values: Any) -> str | None:
    """Return the first existing explanation without creating new evidence."""

    if isinstance(values, list) and values:
        return str(values[0])
    return None


def _use_case_verdict(train: dict[str, Any], use_case: str) -> str:
    """Return the stored verdict for the selected use case, if available."""

    verdicts = train.get("all_use_case_verdicts") or {}
    row = verdicts.get(use_case)
    if isinstance(row, dict):
        return str(row.get("verdict") or "unknown").lower()
    return "unknown"


def _is_high_order(value: Any) -> bool:
    """Return whether a supplied stream order triggers mainstem safeguards."""

    try:
        return float(value) >= 5
    except (TypeError, ValueError):
        return False


def _when_to_choose(
    *, train: dict[str, Any], source_type: str, off_channel: bool
) -> str:
    """Describe selection conditions using existing safety context only."""

    if "industrial" in source_type:
        return "Choose only when effective ETP/CETP pretreatment and required neutralization are already planned."
    if "agricultur" in source_type:
        return "Choose only for collected runoff after field and edge-of-field source controls are in place."
    if off_channel:
        return "Choose only for an off-channel layout with safe interception, access, and monitored return flow."
    role = str(train.get("implementation_role") or "").strip()
    if role:
        return f"Choose when the project needs this option for its stored role: {role}."
    return "Choose after confirming flow, land, site conditions, and pretreatment requirements."

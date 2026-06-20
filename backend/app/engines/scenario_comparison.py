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
                    "warnings": list(train.get("caveats") or [])[:2],
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

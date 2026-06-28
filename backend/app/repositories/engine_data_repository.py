"""Read-only repository for canonical recommendation-engine support data.

The engine-ready canonical database exposes applicability rules, final v1
AHP-Fuzzy AHP criteria weights, and train/use-case summary views. This
repository keeps database access separate from scoring logic so engines can
stay testable.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.core.final_v1_ahp_fuzzy_weights import (
    FINAL_V1_AHP_FUZZY_STATUS,
    final_v1_ahp_fuzzy_weights,
)
from app.repositories.base_repository import BaseRepository


class EngineDataRepository(BaseRepository):
    """Read helpers for A0 rules, MCDA weights, and train summary views."""

    def __init__(self, session: Session) -> None:
        """Store the database session supplied by service or test code."""

        super().__init__(session)

    def canonical_dataset_counts(self) -> dict[str, int | None]:
        """Return review diagnostics for the authoritative engine datasets.

        ``None`` means the relation is unavailable. Keeping this read in the
        repository lets tests verify the configured database without teaching
        the API or scoring engine to query raw tables directly.
        """

        relations = (
            "nbs_options",
            "treatment_train",
            "removal_efficiency",
            "sources",
            "nbs_footprint",
            "plant_solution_map",
            "site_attributes",
        )
        return {
            relation: (
                int(self.fetch_mappings(f"SELECT COUNT(*) AS count FROM {relation}")[0]["count"])
                if self.relation_exists(relation)
                else None
            )
            for relation in relations
        }

    def list_applicability_rules(
        self,
        *,
        active_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Return canonical A0 applicability rules ordered for deterministic use."""

        if not self.relation_exists("nbs_applicability_rules"):
            return []

        active_clause = "WHERE is_active = 1" if active_only else ""
        return self.fetch_mappings(
            f"""
            SELECT
                rule_id,
                is_active,
                target_level,
                nbs_id,
                nbs_solution,
                nbs_family_id,
                nbs_family,
                train_id,
                train_name,
                factor_name,
                factor_source_field,
                intervention_position,
                operator,
                value_min,
                value_max,
                category_value,
                rule_type,
                severity,
                action,
                score_modifier,
                confidence_modifier,
                user_message,
                technical_reason,
                evidence_status,
                provenance_status_id,
                source_id,
                supporting_source_ids,
                review_status,
                notes
            FROM nbs_applicability_rules
            {active_clause}
            ORDER BY
                CASE rule_type
                    WHEN 'hard_safety_filter' THEN 1
                    WHEN 'hard_filter' THEN 2
                    WHEN 'conditional_filter' THEN 3
                    WHEN 'conditional_allow' THEN 4
                    WHEN 'scoring_modifier' THEN 5
                    WHEN 'confidence_modifier' THEN 6
                    WHEN 'pending_rule' THEN 7
                    ELSE 8
                END,
                rule_id
            """
        )

    def list_criteria_weights(
        self,
        use_case: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return criteria weights from the canonical DB, with a named fallback."""

        if not self.relation_exists("criteria_weights"):
            return final_v1_ahp_fuzzy_weights(use_case)

        if use_case:
            rows = self.fetch_mappings(
                """
                SELECT
                    id,
                    use_case_id,
                    use_case,
                    criterion_code,
                    criterion_name,
                    weight,
                    benefit_or_cost,
                    status,
                    derivation_note,
                    source_id,
                    provenance_status_id,
                    created_at
                FROM criteria_weights
                WHERE use_case = :use_case
                ORDER BY criterion_code
                """,
                {"use_case": use_case},
            )
            return _final_rows_or_fallback(rows, use_case)

        rows = self.fetch_mappings(
            """
            SELECT
                id,
                use_case_id,
                use_case,
                criterion_code,
                criterion_name,
                weight,
                benefit_or_cost,
                status,
                derivation_note,
                source_id,
                provenance_status_id,
                created_at
            FROM criteria_weights
            ORDER BY
                CASE use_case
                    WHEN 'drinking' THEN 1
                    WHEN 'irrigation' THEN 2
                    WHEN 'discharge_inland' THEN 3
                    ELSE 4
                END,
                criterion_code
            """
        )
        return _final_rows_or_fallback(rows, use_case)

    def list_engine_usecase_matrix(
        self,
        train_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return all-use-case train verdict summaries for the engine/UI."""

        if not self.relation_exists("v_engine_usecase_matrix"):
            return []

        if train_id is not None:
            return self.fetch_mappings(
                """
                SELECT
                    train_id,
                    train_name,
                    use_case,
                    parameters_checked,
                    pass_count,
                    marginal_count,
                    fail_count,
                    unknown_count,
                    failing_parameters,
                    marginal_parameters,
                    unknown_parameters
                FROM v_engine_usecase_matrix
                WHERE train_id = :train_id
                ORDER BY
                    CASE use_case
                        WHEN 'drinking' THEN 1
                        WHEN 'irrigation' THEN 2
                        WHEN 'discharge_inland' THEN 3
                        ELSE 4
                    END
                """,
                {"train_id": train_id},
            )

        return self.fetch_mappings(
            """
            SELECT
                train_id,
                train_name,
                use_case,
                parameters_checked,
                pass_count,
                marginal_count,
                fail_count,
                unknown_count,
                failing_parameters,
                marginal_parameters,
                unknown_parameters
            FROM v_engine_usecase_matrix
            ORDER BY
                train_id,
                CASE use_case
                    WHEN 'drinking' THEN 1
                    WHEN 'irrigation' THEN 2
                    WHEN 'discharge_inland' THEN 3
                    ELSE 4
                END
            """
        )

    def list_train_cards(self) -> list[dict[str, Any]]:
        """Return frontend-ready treatment train card summaries."""

        if not self.relation_exists("v_app_train_cards"):
            return []

        return self.fetch_mappings(
            """
            SELECT
                train_id,
                name,
                target_use_case,
                scale_context,
                notes,
                treatment_sequence,
                removal_summary,
                usecase_summary,
                evidence_source_ids
            FROM v_app_train_cards
            ORDER BY train_id
            """
        )

    def list_train_usecase_summary(self) -> list[dict[str, Any]]:
        """Return per-train use-case verdict counts including unknown gaps."""

        if not self.relation_exists("v_app_train_usecase_summary"):
            return []

        return self.fetch_mappings(
            """
            SELECT
                train_id,
                use_case,
                parameters_checked,
                pass_count,
                marginal_count,
                fail_count,
                unknown_count,
                failing_parameters,
                marginal_parameters,
                unknown_parameters
            FROM v_app_train_usecase_summary
            ORDER BY
                train_id,
                CASE use_case
                    WHEN 'drinking' THEN 1
                    WHEN 'irrigation' THEN 2
                    WHEN 'discharge_inland' THEN 3
                    ELSE 4
                END
            """
        )

    def list_train_steps(self) -> list[dict[str, Any]]:
        """Return ordered treatment steps with linked NbS metadata."""

        return self.fetch_mappings(
            """
            SELECT
                ts.train_id,
                ts.step_order,
                ts.nbs_id,
                ts.step_label,
                ts.role,
                n.solution AS nbs_name,
                f.name AS nbs_family,
                n.energy_class
            FROM train_step AS ts
            LEFT JOIN nbs_options AS n ON n.id = ts.nbs_id
            LEFT JOIN dim_nbs_family AS f ON f.id = n.family_id
            ORDER BY ts.train_id, ts.step_order
            """
        )

    def list_train_performance(self) -> list[dict[str, Any]]:
        """Return train performance rows while preserving unknown data gaps."""

        return self.fetch_mappings(
            """
            SELECT
                train_id,
                parameter,
                influent_low,
                influent_high,
                cum_removal_low,
                cum_removal_high,
                effluent_low,
                effluent_high,
                steps_with_data,
                note
            FROM train_performance
            ORDER BY train_id, parameter
            """
        )

    def list_train_component_designs(self) -> list[dict[str, Any]]:
        """Return O&M design evidence for NbS components used by trains."""

        return self.fetch_mappings(
            """
            SELECT DISTINCT
                ts.train_id,
                ts.nbs_id,
                d.pretreatment,
                d.planting,
                d.construction_notes,
                d.skill_om_intensity,
                d.om_routine,
                d.om_periodic,
                d.monitoring,
                d.failure_modes,
                d.source_ids
            FROM train_step AS ts
            JOIN nbs_design AS d ON d.nbs_id = ts.nbs_id
            ORDER BY ts.train_id, ts.nbs_id
            """
        )

    def list_train_component_footprints(self) -> list[dict[str, Any]]:
        """Return footprint evidence for NbS components used by trains."""

        return self.fetch_mappings(
            """
            SELECT DISTINCT
                ts.train_id,
                ts.nbs_id,
                n.solution,
                f.area_per_pe_low,
                f.area_per_pe_high,
                f.olr_g_m2_d,
                f.hlr_m3_m2_d,
                f.depth_m,
                f.source_id,
                f.note
            FROM train_step AS ts
            JOIN nbs_footprint AS f ON f.nbs_id = ts.nbs_id
            JOIN nbs_options AS n ON n.id = ts.nbs_id
            ORDER BY ts.train_id, ts.nbs_id
            """
        )

    def list_train_plants(self) -> list[dict[str, Any]]:
        """Return literature-backed plant mappings for train components."""

        return self.fetch_mappings(
            """
            SELECT DISTINCT
                ts.train_id,
                p.id AS mapping_id,
                p.plant_species,
                p.nbs,
                p.basis,
                p.confidence,
                p.source,
                pl.native_status,
                pl.invasive,
                pl.ecological_role,
                pl.evidence_note
            FROM train_step AS ts
            JOIN nbs_options AS n ON n.id = ts.nbs_id
            JOIN v_plant_use AS p ON p.nbs = n.solution
            JOIN plant_solution_map AS pm ON pm.id = p.id
            JOIN plants AS pl ON pl.id = pm.plant_id
            WHERE COALESCE(pl.invasive, 0) = 0
              AND LOWER(COALESCE(pl.native_status, '')) NOT LIKE '%invasive%'
            ORDER BY ts.train_id, p.plant_species
            """
        )

    def get_site_attributes(self, region_id: int | None) -> dict[str, Any] | None:
        """Return canonical site attributes for one resolved region."""

        if region_id is None:
            return None
        rows = self.fetch_mappings(
            """
            SELECT *
            FROM site_attributes
            WHERE region_id = :region_id
            ORDER BY id
            LIMIT 1
            """,
            {"region_id": region_id},
        )
        if not rows:
            return None

        site = dict(rows[0])
        if self.relation_exists("regions"):
            region_rows = self.fetch_mappings(
                """
                SELECT
                    soil_type,
                    hydrologic_soil_group,
                    soil_depth_m,
                    soil_avail_water_mm_m,
                    infiltration_class,
                    rainfall_mm_yr,
                    aridity_P_PET,
                    district,
                    river,
                    lat,
                    lon
                FROM regions
                WHERE id = :region_id
                LIMIT 1
                """,
                {"region_id": region_id},
            )
            if region_rows:
                for key, value in region_rows[0].items():
                    if value is not None:
                        site[key] = value
        return site


def _final_rows_or_fallback(
    rows: list[dict[str, Any]],
    use_case: str | None,
) -> list[dict[str, Any]]:
    """Return current DB weight rows, or the named fallback for stale DBs."""

    accepted_statuses = {
        FINAL_V1_AHP_FUZZY_STATUS,
        "temporary_not_expert_validated",
    }
    if rows and all(row.get("status") in accepted_statuses for row in rows):
        return rows
    return final_v1_ahp_fuzzy_weights(use_case)

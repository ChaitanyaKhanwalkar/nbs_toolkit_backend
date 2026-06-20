"""Read-only learning catalogue assembled from canonical repository records.

The service prepares treatment-train, individual-NbS, and plant learning
packets. It does not rank options, recommend invasive plants, or invent design
values when canonical fields are missing.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.engines.input_normalization import normalize_match_key
from app.repositories import EngineDataRepository, PlantRepository
from app.services.nbs_catalog_service import NbsCatalogService
from app.services.plant_catalog_service import PlantCatalogService


class CatalogueService:
    """Aggregate canonical catalogue records for the learning workspace."""

    def __init__(self, session: Session) -> None:
        self.engine_data = EngineDataRepository(session)
        self.nbs = NbsCatalogService(session)
        self.plants = PlantCatalogService(session)
        self.plant_repository = PlantRepository(session)

    def get_catalogue(self) -> dict[str, Any]:
        """Return all three catalogues with transparent missing-data notes."""

        return {
            "treatment_trains": self._treatment_trains(),
            "nbs_components": self._nbs_components(),
            "plants": self._plant_catalogue(),
            "notes": [
                "Catalogue records are descriptive and do not replace context-specific A0 screening.",
                "Plant catalogue rows marked invasive are learning warnings and must not be recommended for planting.",
                "Missing canonical fields remain unavailable rather than being inferred.",
            ],
        }

    def _treatment_trains(self) -> list[dict[str, Any]]:
        cards = self.engine_data.list_train_cards()
        steps = _group(self.engine_data.list_train_steps(), "train_id")
        matrix = _group(self.engine_data.list_engine_usecase_matrix(), "train_id")
        designs = _group(self.engine_data.list_train_component_designs(), "train_id")
        plants = _group(self.engine_data.list_train_plants(), "train_id")
        result = []
        for card in cards:
            train_id = int(card["train_id"])
            train_steps = steps.get(train_id, [])
            design_rows = designs.get(train_id, [])
            source_ids = _source_ids(
                card,
                train_steps,
                matrix.get(train_id, []),
                design_rows,
                plants.get(train_id, []),
            )
            result.append(
                {
                    **card,
                    "sequence_steps": train_steps,
                    "intended_role": _train_role(train_steps),
                    "use_case_suitability": matrix.get(train_id, []),
                    "strengths": _unique([str(card.get("notes") or "")]),
                    "limitations": _unique(
                        [
                            str(row.get("failure_modes") or "")
                            for row in design_rows
                            if row.get("failure_modes")
                        ]
                    ),
                    "pretreatment_needs": _unique(
                        [
                            str(row.get("pretreatment") or "")
                            for row in design_rows
                            if row.get("pretreatment")
                        ]
                    ),
                    "om_notes": _unique(
                        [
                            str(row.get(key) or "")
                            for row in design_rows
                            for key in ("om_routine", "om_periodic", "monitoring")
                            if row.get(key)
                        ]
                    ),
                    "components": [
                        {
                            "nbs_id": row.get("nbs_id"),
                            "name": row.get("nbs_name"),
                            "family": row.get("nbs_family"),
                            "role": row.get("role"),
                        }
                        for row in train_steps
                        if row.get("nbs_id") is not None
                    ],
                    "plants": plants.get(train_id, []),
                    "source_ids": source_ids,
                }
            )
        return result

    def _nbs_components(self) -> list[dict[str, Any]]:
        result = []
        for option in self.nbs.list_options():
            nbs_id = int(option["id"])
            profile = self.nbs.get_full_nbs_profile(nbs_id)
            removal = profile.get("removal_efficiencies") or []
            implementation = profile.get("implementation") or []
            designs = profile.get("criteria") or []
            mapped_plants = self.plants.get_plants_for_nbs(
                nbs_id,
                include_invasive=False,
            )
            result.append(
                {
                    **option,
                    "catalogue_role": _component_role(option),
                    "pollutants_treated": _unique(
                        [
                            str(row.get("parameter") or "")
                            for row in removal
                            if row.get("parameter")
                            and (
                                row.get("eff_low") is not None
                                or row.get("eff_high") is not None
                            )
                        ]
                    ),
                    "where_suitable": _unique(
                        [
                            str(value)
                            for value in (
                                option.get("optimal_water_type"),
                                option.get("location_suitability"),
                            )
                            if value
                        ]
                    ),
                    "where_not_suitable": _component_boundaries(option),
                    "standalone_suitability": "Context-specific A0 screening required.",
                    "design_notes": _unique(
                        [
                            str(row.get(key) or "")
                            for row in designs
                            for key in (
                                "pretreatment",
                                "construction_notes",
                                "failure_modes",
                            )
                            if row.get(key)
                        ]
                    ),
                    "maintenance_notes": _unique(
                        [
                            str(row.get(key) or "")
                            for row in [*implementation, *designs]
                            for key in (
                                "maintenance_requirements",
                                "om_routine",
                                "om_periodic",
                                "monitoring",
                            )
                            if row.get(key)
                        ]
                    ),
                    "plants": mapped_plants,
                    "source_ids": _source_ids(
                        option,
                        removal,
                        implementation,
                        designs,
                        mapped_plants,
                    ),
                    "missing_sections": profile.get("missing_sections") or [],
                }
            )
        return result

    def _plant_catalogue(self) -> list[dict[str, Any]]:
        grouped: dict[int, dict[str, Any]] = {}
        for row in self.plant_repository.list_catalogue_mappings():
            plant_id = int(row["id"])
            plant = grouped.setdefault(
                plant_id,
                {
                    key: row.get(key)
                    for key in (
                        "id",
                        "plant_species",
                        "locational_availability",
                        "climate_preference",
                        "soil_type",
                        "water_needs",
                        "ecological_role",
                        "plant_type",
                        "native_status",
                        "invasive",
                        "metals_pollutants",
                        "evidence_note",
                        "pollution_tolerance",
                        "optimal_water_type",
                    )
                }
                | {
                    "mapped_components": [],
                    "source_ids": [],
                },
            )
            if row.get("nbs_id") is not None:
                plant["mapped_components"].append(
                    {
                        "nbs_id": row.get("nbs_id"),
                        "name": row.get("nbs_name"),
                        "basis": row.get("basis"),
                    }
                )
            for key in ("plant_source_id", "mapping_source_id"):
                _append_source_id(plant["source_ids"], row.get(key))
            plant["recommendation_status"] = (
                "do_not_recommend_invasive"
                if row.get("invasive") == 1
                or "invasive" in str(row.get("native_status") or "").lower()
                else "eligible_for_local_validation"
            )
        return list(grouped.values())


def _train_role(steps: list[dict[str, Any]]) -> str:
    roles = {normalize_match_key(row.get("role")) for row in steps}
    if "primary" in roles and ("secondary" in roles or "tertiary" in roles):
        return "Primary-to-polishing treatment train"
    if "disposal" in roles:
        return "On-site treatment and disposal train"
    return "Treatment and polishing train"


def _component_role(option: dict[str, Any]) -> str:
    text = normalize_match_key(
        f"{option.get('solution') or ''} {option.get('family') or ''}"
    ) or ""
    if any(token in text for token in ("bioretention", "bioswale", "filter_strip", "buffer")):
        return "Source control / runoff interception"
    if any(token in text for token in ("soak", "leach", "infiltration")):
        return "Infiltration / disposal with site safeguards"
    if any(token in text for token in ("uasb", "baffled", "dewats", "anaerobic_filter")):
        return "Primary treatment-train component"
    return "Secondary treatment / polishing component"


def _component_boundaries(option: dict[str, Any]) -> list[str]:
    text = normalize_match_key(
        f"{option.get('solution') or ''} {option.get('family') or ''}"
    ) or ""
    values = ["Use requires context-specific A0 applicability screening."]
    if any(token in text for token in ("wetland", "pond", "lagoon")):
        values.append("Not an in-channel treatment cell for a mainstem or high-order river.")
    if any(token in text for token in ("soak", "leach", "infiltration")):
        values.append("Not suitable without soil, groundwater, setback, and loading checks.")
    values.append("Not standalone primary treatment for untreated industrial wastewater.")
    return values


def _group(rows: list[dict[str, Any]], key: str) -> dict[int, list[dict[str, Any]]]:
    result: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get(key) is not None:
            result.setdefault(int(row[key]), []).append(row)
    return result


def _source_ids(*groups: Any) -> list[int]:
    result: list[int] = []
    for group in groups:
        rows = group if isinstance(group, list) else [group]
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key in (
                "source_id",
                "source_ids",
                "evidence_source_ids",
                "mapping_source_id",
            ):
                raw = row.get(key)
                if isinstance(raw, str):
                    items = raw.replace(";", ",").split(",")
                elif isinstance(raw, list):
                    items = raw
                else:
                    items = [raw]
                for item in items:
                    _append_source_id(result, item)
    return result


def _append_source_id(values: list[int], value: Any) -> None:
    try:
        source_id = int(value)
    except (TypeError, ValueError):
        return
    if source_id not in values:
        values.append(source_id)


def _unique(values: list[str]) -> list[str]:
    result = []
    for value in values:
        stripped = value.strip()
        if stripped and stripped not in result:
            result.append(stripped)
    return result

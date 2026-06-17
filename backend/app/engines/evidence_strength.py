"""C8 engine for NbS evidence strength (provenance quality).

Implements the MCDA criterion **C8 — Evidence strength** from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` (section 12.8). This is the
project's provenance-first criterion: it scores *how well-supported* a candidate
is, never the science itself, so it invents nothing.

Inputs are all already-known facts:

- water data quality (from the selected water source type),
- whether removal efficiency is sourced with numeric ranges,
- whether site data was resolved, and
- whether implementation guidance is sourced.

These map to the spec's transparent evidence table. It is a benefit criterion
and is kept separate from the Step J confidence score.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EVIDENCE_STATUS_SCORED = "scored"

# Water data quality tiers derived from the selected water source type.
MEASURED_SOURCE_TYPES = {"user_measured", "station_observations"}
REGIONAL_SOURCE_TYPES = {"basin_observations"}


@dataclass(slots=True)
class EvidenceStrengthResult:
    """C8 evidence-strength score (benefit) plus its transparent breakdown."""

    evidence_strength: float
    water_quality_level: str
    removal_sourced: bool
    site_data_present: bool
    implementation_sourced: bool
    status: str
    used_inputs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for matrix rows, tests, or future APIs."""

        return asdict(self)


def compute_evidence_strength(
    *,
    removal_evidence: dict[str, Any] | None,
    source_ids: list[int] | None,
    implementation_sourced: bool,
    site_context: dict[str, Any] | None,
    selected_source_type: str | None,
) -> EvidenceStrengthResult:
    """Score provenance strength from already-known evidence facts."""

    water_quality_level = _water_quality_level(selected_source_type)
    removal_sourced = _removal_is_sourced(removal_evidence)
    has_any_source = bool(source_ids)
    site_data_present = bool(site_context)

    notes: list[str] = []
    used_inputs = ["selected_source_type", "removal_evidence", "source_ids", "site_context"]

    if not removal_sourced:
        score = 0.30 if has_any_source else 0.20
        notes.append(
            "No sourced numeric removal efficiency for this candidate; evidence "
            f"strength capped at {score}."
        )
    else:
        base = {
            "measured": 0.80,
            "regional": 0.70,
            "fallback": 0.55,
        }[water_quality_level]
        if water_quality_level == "measured" and site_data_present and implementation_sourced:
            base = 1.00
        elif water_quality_level == "measured" and (site_data_present or implementation_sourced):
            base = 0.80
        score = base
        notes.append(
            f"evidence_strength={score}: water data '{water_quality_level}', "
            f"removal sourced, site data {'present' if site_data_present else 'absent'}, "
            f"implementation {'sourced' if implementation_sourced else 'unsourced'}."
        )

    return EvidenceStrengthResult(
        evidence_strength=score,
        water_quality_level=water_quality_level,
        removal_sourced=removal_sourced,
        site_data_present=site_data_present,
        implementation_sourced=implementation_sourced,
        status=EVIDENCE_STATUS_SCORED,
        used_inputs=used_inputs,
        notes=notes,
    )


def _water_quality_level(selected_source_type: str | None) -> str:
    """Map the selected water source type to a measured/regional/fallback tier."""

    source_type = (selected_source_type or "").strip().lower()
    if source_type in MEASURED_SOURCE_TYPES:
        return "measured"
    if source_type in REGIONAL_SOURCE_TYPES:
        return "regional"
    return "fallback"


def _removal_is_sourced(removal_evidence: dict[str, Any] | None) -> bool:
    """Return True when the candidate has numeric, sourced removal efficiency."""

    if not isinstance(removal_evidence, dict):
        return False
    numeric_rows = removal_evidence.get("rows_with_numeric_efficiency")
    try:
        return float(numeric_rows) > 0
    except (TypeError, ValueError):
        return False

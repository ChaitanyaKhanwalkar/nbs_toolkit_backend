"""C7 engine for NbS operation & maintenance (O&M) simplicity.

Implements the MCDA criterion **C7 — O&M simplicity** from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` (section 12.7).

It reads the qualitative O&M level from real `nbs_criteria` rows (a criterion
whose name mentions maintenance / O&M / operation) and maps that documented
level word to the spec's transparent score table. Simpler O&M scores higher
(benefit). The text->score table is a documented default; the underlying level
word is real catalogue data, not invented. Missing O&M information leaves the
criterion unscored with a confidence-lowering note.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.input_normalization import normalize_match_key


OM_STATUS_SOURCED = "sourced_catalogue"
OM_STATUS_DATA_PENDING = "data_pending"

OM_CRITERION_KEYS = {
    "maintenance",
    "maintenance_requirements",
    "o_m",
    "om",
    "operation",
    "operations",
    "operation_maintenance",
    "operations_maintenance",
    "o_and_m",
    "om_simplicity",
    "om_level",
}

# Spec section 12.7 score table, keyed by documented O&M level word. Order
# matters: the most extreme/specific words are matched before generic ones so
# "very_high"/"very_complex" map to the expert score, not the complex score.
OM_LEVEL_SCORES: list[tuple[tuple[str, ...], float]] = [
    (("very_simple", "very_low", "minimal"), 1.00),
    (("simple", "low", "easy"), 0.80),
    (("moderate", "medium"), 0.60),
    (("expert", "energy", "intensive", "very_complex", "very_high"), 0.20),
    (("complex", "high", "difficult"), 0.35),
]


@dataclass(slots=True)
class OmSimplicityResult:
    """C7 O&M simplicity score (benefit) plus its transparent breakdown."""

    om_simplicity: float | None
    om_level: str | None
    status: str
    used_inputs: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for matrix rows, tests, or future APIs."""

        return asdict(self)


def compute_om_simplicity(
    criteria_rows: list[dict[str, Any]] | None,
) -> OmSimplicityResult:
    """Score O&M simplicity from the documented O&M level word."""

    notes: list[str] = []
    for row in criteria_rows or []:
        if not isinstance(row, dict):
            continue
        criterion_key = normalize_match_key(row.get("criterion"))
        if not criterion_key:
            continue
        # Drop "&" so "o&m" matches the "om" key, etc.
        criterion_key = criterion_key.replace("&", "")
        tokens = {criterion_key, *criterion_key.split("_")}
        if not tokens & OM_CRITERION_KEYS:
            continue
        level_key = normalize_match_key(row.get("value_qual"))
        if not level_key:
            continue
        score = _score_for_level(level_key)
        if score is None:
            notes.append(
                f"O&M level '{level_key}' not in the documented level table; "
                "C7 left unscored."
            )
            continue
        notes.append(
            f"om_simplicity={score}: documented O&M level '{level_key}'."
        )
        return OmSimplicityResult(
            om_simplicity=score,
            om_level=level_key,
            status=OM_STATUS_SOURCED,
            used_inputs=["nbs_criteria.value_qual"],
            missing_inputs=[],
            notes=notes,
        )

    notes.append(
        "No documented O&M level available; C7 left unscored and confidence lowered."
    )
    return OmSimplicityResult(
        om_simplicity=None,
        om_level=None,
        status=OM_STATUS_DATA_PENDING,
        used_inputs=[],
        missing_inputs=["om_level"],
        notes=notes,
    )


def _score_for_level(level_key: str) -> float | None:
    """Map a normalized O&M level word to the documented score, if known."""

    for level_words, score in OM_LEVEL_SCORES:
        if any(word in level_key for word in level_words):
            return score
    return None

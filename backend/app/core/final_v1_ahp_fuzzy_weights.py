"""Final v1 AHP-Fuzzy AHP ensemble criteria weights for the demo engine.

The values in this module are a code fallback for development databases that
do not yet have the ``criteria_weights`` table. The canonical database remains
the primary source whenever the table exists.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


FINAL_V1_AHP_FUZZY_STATUS = "FINAL_V1_AHP_FUZZY_ENSEMBLE"
FINAL_V1_AHP_FUZZY_SOURCE = "final_v1_ahp_fuzzy_ensemble"
FINAL_V1_AHP_FUZZY_NOTE = (
    "Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. "
    "C5 health-risk integration remains reserved for future expert data."
)


_FINAL_WEIGHTS: dict[str, list[dict[str, Any]]] = {
    "discharge_inland": [
        ("C1", "treatment_fit", "benefit", 0.258313),
        ("C2", "standard_fit", "benefit", 0.258313),
        ("C3", "site_fit", "benefit", 0.099705),
        ("C4", "source_fit", "benefit", 0.113906),
        ("C6", "hydrologic_fit", "benefit", 0.056103),
        ("C7", "footprint", "cost", 0.099755),
        ("C8", "om", "cost", 0.113906),
    ],
    "drinking": [
        ("C1", "treatment_fit", "benefit", 0.266800),
        ("C2", "standard_fit", "benefit", 0.266800),
        ("C3", "site_fit", "benefit", 0.106500),
        ("C4", "source_fit", "benefit", 0.121700),
        ("C6", "hydrologic_fit", "benefit", 0.058250),
        ("C7", "footprint", "cost", 0.058250),
        ("C8", "om", "cost", 0.121700),
    ],
    "irrigation": [
        ("C1", "treatment_fit", "benefit", 0.231600),
        ("C2", "standard_fit", "benefit", 0.231600),
        ("C3", "site_fit", "benefit", 0.095100),
        ("C4", "source_fit", "benefit", 0.116000),
        ("C6", "hydrologic_fit", "benefit", 0.054900),
        ("C7", "footprint", "cost", 0.116000),
        ("C8", "om", "cost", 0.154700),
    ],
}


def final_v1_ahp_fuzzy_weights(use_case: str | None = None) -> list[dict[str, Any]]:
    """Return final v1 weight rows shaped like ``criteria_weights`` records."""

    use_cases = [use_case] if use_case else list(_FINAL_WEIGHTS)
    rows: list[dict[str, Any]] = []
    for raw_use_case in use_cases:
        key = str(raw_use_case or "").strip().lower()
        for code, name, direction, weight in _FINAL_WEIGHTS.get(key, []):
            rows.append(
                {
                    "id": None,
                    "use_case_id": None,
                    "use_case": key,
                    "criterion_code": code,
                    "criterion_name": name,
                    "weight": weight,
                    "benefit_or_cost": direction,
                    "status": FINAL_V1_AHP_FUZZY_STATUS,
                    "derivation_note": FINAL_V1_AHP_FUZZY_NOTE,
                    "source_id": None,
                    "provenance_status_id": None,
                    "created_at": None,
                }
            )
    return deepcopy(rows)

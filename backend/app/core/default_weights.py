"""Provisional default MCDA criteria weights (single swap-in point).

WHY THIS FILE EXISTS
--------------------
The TOPSIS step (Step I) cannot rank candidates without criteria weights. The
final, scientifically authoritative weights must come from the supervisor's AHP
(Analytic Hierarchy Process) pairwise comparisons, which are *not yet available*
(see the provisional ``criteria_weights`` table and `backend/docs/04_PENDING_TABLES.md`).

So the model is *operational now* for the demo, this file holds **transparent,
neutral, literature-informed PROVISIONAL weights**. They are labelled
``temporary_not_expert_validated`` everywhere they surface and must never be
presented as expert/AHP-validated.

HOW TO REPLACE THEM LATER (NO CODE CHANGES NEEDED ELSEWHERE)
-----------------------------------------------------------
1. When the supervisor provides real AHP weights per use case, edit ONLY the
   ``DEFAULT_TEMPORARY_CRITERIA_WEIGHTS`` mapping below (or load them into the
   canonical ``criteria_weights`` table for train-level ranking).
2. When the weights become expert-validated, the caller passes
   ``expert_validated=True`` so the status flips. Nothing else changes.

DESIGN NOTES
------------
- Keys are the criterion names the MCDA normalization step knows a direction for
  (see ``CRITERION_DIRECTION_MAP`` in ``app/engines/mcda_normalization.py``),
  including the C3-C8 criteria. ``select_default_weights`` keeps only the criteria
  actually present in a given run, and the weights handler re-normalizes them, so
  supplying the full set future-proofs the config.
- The numbers are deliberately NEUTRAL: treatment performance (the reason a user
  comes to the tool) gets the largest share, then evidence strength and
  site/hydrological/pollution fit, then operational/footprint feasibility. They
  invent no scientific value and are a defensible starting point pending AHP.
- These are NOT AHP weights, NOT health-risk values, and NOT a final ranking.
"""

from __future__ import annotations

from typing import Mapping


# Stable label used wherever these weights surface. Mirrors
# app.engines.mcda_weights.WEIGHTS_TEMPORARY on purpose.
WEIGHTS_STATUS_TEMPORARY = "temporary_not_expert_validated"

# Source label recorded on the weights bundle so provenance is explicit.
DEFAULT_WEIGHTS_SOURCE = "default_temporary_literature_informed_v1"

# Short rationale surfaced in docs/tests so nothing is hidden.
DEFAULT_WEIGHTS_RATIONALE = (
    "Provisional, transparent, literature-informed neutral weights used only so "
    "the demo can rank candidates before the supervisor's AHP weights exist. "
    "Treatment performance is weighted highest; not expert-validated."
)

# Fallback profile used for any use case without a specific entry. Values sum to
# 1.0 for readability; the weights handler re-normalizes over present criteria.
_DEFAULT_PROFILE: dict[str, float] = {
    # C1 treatment performance (pollutant-gap closure proxy): DOMINANT.
    "removal_evidence_score": 0.26,
    "removal_evidence_coverage": 0.10,
    # C8 evidence strength (provenance): meaningful, matching the project ethos.
    "evidence_strength": 0.12,
    # C3 site suitability.
    "site_suitability": 0.12,
    # C4 hydrological suitability.
    "hydrological_suitability": 0.10,
    # C5 pollution-source fit.
    "pollution_source_fit": 0.10,
    # C6 footprint requirement (cost-direction).
    "footprint_requirement": 0.08,
    # C7 O&M simplicity.
    "om_simplicity": 0.08,
    # Forward-compatible criteria, weighted small until their values are produced.
    "climate_suitability": 0.02,
    "co_benefit_score": 0.02,
}


def _profile(**overrides: float) -> dict[str, float]:
    """Return a copy of the default profile with a few criteria adjusted."""

    profile = dict(_DEFAULT_PROFILE)
    profile.update(overrides)
    return profile


# Per-use-case provisional weights. Keys are matched case-insensitively against
# the request use case (and common aliases). Replace these whole dicts with the
# supervisor's AHP weights when available — the rest of the system is unchanged.
DEFAULT_TEMPORARY_CRITERIA_WEIGHTS: dict[str, dict[str, float]] = {
    # Drinking/domestic: lean on treatment performance and evidence because the
    # target is strict; NbS alone often needs polishing/disinfection.
    "drinking": _profile(
        removal_evidence_score=0.30,
        evidence_strength=0.14,
    ),
    # Bathing/recreation contact: prioritise treatment performance and pollution
    # fit (pathogen context).
    "bathing": _profile(
        removal_evidence_score=0.28,
        pollution_source_fit=0.12,
    ),
    # Irrigation reuse: balance treatment with operational simplicity/footprint.
    "irrigation": _profile(
        removal_evidence_score=0.22,
        om_simplicity=0.10,
        footprint_requirement=0.10,
    ),
    # Inland surface-water discharge (project default demo use case).
    "discharge_inland": _profile(),
    # Generic fallback.
    "_default": _profile(),
}


def _alias(use_case: str | None) -> str:
    """Map a raw use-case string to a known weights profile key."""

    text = (use_case or "").strip().lower()
    if text in DEFAULT_TEMPORARY_CRITERIA_WEIGHTS:
        return text
    aliases = {
        "surface_discharge": "discharge_inland",
        "discharge": "discharge_inland",
        "inland_discharge": "discharge_inland",
        "drinking_domestic": "drinking",
        "domestic": "drinking",
        "potable": "drinking",
        "irrigation_reuse": "irrigation",
        "reuse": "irrigation",
        "landscape_reuse": "irrigation",
        "recreation": "bathing",
    }
    return aliases.get(text, "_default")


def get_default_weights(use_case: str | None) -> dict[str, float]:
    """Return a copy of the provisional weight profile for a use case.

    The returned weights are always provisional. Callers must keep the
    ``temporary_not_expert_validated`` status and never claim expert validation.
    """

    return dict(DEFAULT_TEMPORARY_CRITERIA_WEIGHTS[_alias(use_case)])


def select_default_weights(
    use_case: str | None,
    criteria_names: Mapping[str, object] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Return provisional weights, optionally limited to present criteria.

    When ``criteria_names`` is provided, only weights for criteria that actually
    exist in the current MCDA matrix are returned. This avoids spreading weight
    mass onto criteria that are not in this run. When no criteria match, an empty
    dict is returned so the caller falls back to the normal weights-missing path
    instead of producing an invalid-weights result.
    """

    weights = get_default_weights(use_case)
    if criteria_names is None:
        return weights

    present = {str(name) for name in criteria_names}
    return {name: value for name, value in weights.items() if name in present}

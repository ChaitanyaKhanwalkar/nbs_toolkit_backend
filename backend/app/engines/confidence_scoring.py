"""Step J engine for confidence scoring of TOPSIS-ranked candidates.

Confidence is about trust in the available evidence and workflow inputs. It is
separate from TOPSIS closeness, which is a suitability/ranking calculation.
This module does not change TOPSIS rank, create final recommendations, recommend
plants, classify health risk, or calculate AHP pairwise weights.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.candidate_filtering import (
    DATA_PENDING,
    ELIGIBLE,
    INELIGIBLE,
    CandidateFilterBundle,
    CandidateFilterResult,
)
from app.engines.mcda_normalization import NormalizedMcdaMatrixBundle
from app.engines.mcda_weights import (
    WEIGHTS_EXPERT_VALIDATED,
    WEIGHTS_INVALID,
    WEIGHTS_MISSING,
    WEIGHTS_TEMPORARY,
    McdaWeightsBundle,
)
from app.engines.topsis_ranking import TopsisRankedCandidate, TopsisRankingBundle
from app.engines.water_input_assembly import WaterInputBundle


CONFIDENCE_METHOD = "rule_based_v1"

LABEL_HIGH = "high"
LABEL_MEDIUM = "medium"
LABEL_LOW = "low"

WATER_USER_MEASURED = "user_measured"
WATER_STATION = "station_observations"
WATER_BASIN = "basin_observations"
WATER_MISSING = "missing"

# These weights are deterministic engineering rules for confidence bookkeeping.
# They are not AHP weights, expert criteria weights, or scientific suitability
# weights. The factors sum to 1.0 so confidence_score remains easy to inspect.
CONFIDENCE_FACTOR_WEIGHTS = {
    "water_data_quality": 0.25,
    "candidate_evidence_quality": 0.25,
    "criteria_completeness": 0.20,
    "weights_reliability": 0.20,
    "caution_penalty": 0.10,
}


@dataclass(slots=True)
class ConfidenceFactor:
    """One transparent reason contributing to candidate confidence."""

    factor_name: str
    factor_score: float
    factor_weight: float
    weighted_score: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class CandidateConfidenceResult:
    """Confidence score for one already-ranked TOPSIS candidate."""

    nbs_id: int | None
    nbs_name: str | None
    rank: int
    topsis_closeness: float | None
    confidence_score: float
    confidence_label: str
    factors: list[ConfidenceFactor] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["factors"] = [factor.to_dict() for factor in self.factors]
        return payload


@dataclass(slots=True)
class ConfidenceScoringBundle:
    """Step J confidence outputs for Step I ranked candidates."""

    use_case: str
    ranking_method: str
    weights_status: str
    expert_validated: bool
    confidence_method: str = CONFIDENCE_METHOD
    results: list[CandidateConfidenceResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["results"] = [result.to_dict() for result in self.results]
        return payload


class ConfidenceScoringEngine:
    """Calculate rule-based confidence without changing TOPSIS rank."""

    def score(
        self,
        ranking_bundle: TopsisRankingBundle,
        *,
        water_bundle: WaterInputBundle | None = None,
        candidate_bundle: CandidateFilterBundle | None = None,
        normalized_bundle: NormalizedMcdaMatrixBundle | None = None,
        weights_bundle: McdaWeightsBundle | None = None,
    ) -> ConfidenceScoringBundle:
        """Return candidate confidence scores for a Step I ranking bundle."""

        warnings = _workflow_warnings(
            ranking_bundle=ranking_bundle,
            water_bundle=water_bundle,
            candidate_bundle=candidate_bundle,
            normalized_bundle=normalized_bundle,
            weights_bundle=weights_bundle,
        )
        notes = [
            "Step J calculates confidence only. It does not change TOPSIS rank "
            "and does not create final recommendations.",
            "confidence_score measures reliability/trust, not suitability rank.",
        ]

        if not ranking_bundle.ranked_candidates:
            warnings.append(
                "Confidence scoring returned no candidate results because Step I "
                "ranked_candidates is empty."
            )
            return ConfidenceScoringBundle(
                use_case=ranking_bundle.use_case,
                ranking_method=ranking_bundle.ranking_method,
                weights_status=_weights_status(ranking_bundle, weights_bundle),
                expert_validated=_expert_validated(ranking_bundle, weights_bundle),
                results=[],
                warnings=warnings,
                notes=notes,
            )

        candidate_results = [
            self._score_candidate(
                candidate,
                ranking_bundle=ranking_bundle,
                water_bundle=water_bundle,
                candidate_bundle=candidate_bundle,
                normalized_bundle=normalized_bundle,
                weights_bundle=weights_bundle,
            )
            for candidate in ranking_bundle.ranked_candidates
        ]

        return ConfidenceScoringBundle(
            use_case=ranking_bundle.use_case,
            ranking_method=ranking_bundle.ranking_method,
            weights_status=_weights_status(ranking_bundle, weights_bundle),
            expert_validated=_expert_validated(ranking_bundle, weights_bundle),
            results=candidate_results,
            warnings=warnings,
            notes=notes,
        )

    def _score_candidate(
        self,
        candidate: TopsisRankedCandidate,
        *,
        ranking_bundle: TopsisRankingBundle,
        water_bundle: WaterInputBundle | None,
        candidate_bundle: CandidateFilterBundle | None,
        normalized_bundle: NormalizedMcdaMatrixBundle | None,
        weights_bundle: McdaWeightsBundle | None,
    ) -> CandidateConfidenceResult:
        """Calculate confidence factors for one ranked candidate."""

        matched_candidate = _candidate_filter_result(candidate, candidate_bundle)
        factors = [
            _factor(
                "water_data_quality",
                *_water_data_quality(water_bundle),
            ),
            _factor(
                "candidate_evidence_quality",
                *_candidate_evidence_quality(matched_candidate, candidate_bundle),
            ),
            _factor(
                "criteria_completeness",
                *_criteria_completeness(ranking_bundle, normalized_bundle),
            ),
            _factor(
                "weights_reliability",
                *_weights_reliability(ranking_bundle, weights_bundle),
            ),
            _factor(
                "caution_penalty",
                *_caution_penalty(candidate),
            ),
        ]
        confidence_score = _clamp(
            sum(factor.weighted_score for factor in factors),
            0.0,
            1.0,
        )
        candidate_warnings = [
            note
            for factor in factors
            for note in factor.notes
            if _is_warning_note(note)
        ]

        return CandidateConfidenceResult(
            nbs_id=candidate.nbs_id,
            nbs_name=candidate.nbs_name,
            rank=candidate.rank,
            topsis_closeness=candidate.topsis_closeness,
            confidence_score=confidence_score,
            confidence_label=_confidence_label(confidence_score),
            factors=factors,
            warnings=candidate_warnings,
            notes=[
                "Candidate confidence was calculated separately from TOPSIS "
                "closeness and did not change rank.",
            ],
        )


def _workflow_warnings(
    *,
    ranking_bundle: TopsisRankingBundle,
    water_bundle: WaterInputBundle | None,
    candidate_bundle: CandidateFilterBundle | None,
    normalized_bundle: NormalizedMcdaMatrixBundle | None,
    weights_bundle: McdaWeightsBundle | None,
) -> list[str]:
    """Collect bundle-level warnings without changing any upstream output."""

    warnings = list(ranking_bundle.warnings)
    if water_bundle is None:
        warnings.append("WaterInputBundle was not provided; water data confidence is reduced.")
    else:
        warnings.extend(water_bundle.warnings)
    if candidate_bundle is None:
        warnings.append(
            "CandidateFilterBundle was not provided; candidate evidence confidence is reduced."
        )
    else:
        warnings.extend(candidate_bundle.warnings)
    if normalized_bundle is None:
        warnings.append(
            "NormalizedMcdaMatrixBundle was not provided; criteria completeness confidence "
            "uses only Step I summary fields."
        )
    else:
        warnings.extend(normalized_bundle.warnings)
    if weights_bundle is None:
        warnings.append(
            "McdaWeightsBundle was not provided; weights reliability uses Step I status only."
        )
    else:
        warnings.extend(weights_bundle.warnings)

    status = _weights_status(ranking_bundle, weights_bundle)
    if status == WEIGHTS_TEMPORARY:
        warnings.append(
            "Confidence scoring detected temporary_not_expert_validated weights; "
            "the TOPSIS ranking remains provisional."
        )
    elif status == WEIGHTS_MISSING:
        warnings.append(
            "Confidence scoring detected missing weights; confidence can be reported "
            "only as a safe low-reliability result if ranked candidates exist."
        )
    elif status == WEIGHTS_INVALID:
        warnings.append(
            "Confidence scoring detected invalid weights; confidence can be reported "
            "only as a safe low-reliability result if ranked candidates exist."
        )
    return _unique(warnings)


def _water_data_quality(
    water_bundle: WaterInputBundle | None,
) -> tuple[float, list[str]]:
    """Return a trust score for the water data source used upstream."""

    if water_bundle is None:
        return 0.40, ["Warning: water input bundle is missing."]
    if water_bundle.observation_count <= 0:
        return 0.20, ["Warning: no assembled water observations were available."]

    source_scores = {
        WATER_USER_MEASURED: 1.00,
        WATER_STATION: 0.80,
        WATER_BASIN: 0.60,
        WATER_MISSING: 0.20,
    }
    score = source_scores.get(water_bundle.selected_source_type, 0.45)
    notes = [
        f"Water data source selected by Step B: {water_bundle.selected_source_type}."
    ]
    if water_bundle.selected_source_type == WATER_USER_MEASURED:
        notes.append("User measured data has highest source priority.")
    return score, notes


def _candidate_evidence_quality(
    candidate: CandidateFilterResult | None,
    candidate_bundle: CandidateFilterBundle | None,
) -> tuple[float, list[str]]:
    """Return a trust score for candidate evidence and eligibility support."""

    if candidate_bundle is None:
        return 0.45, ["Warning: candidate filter bundle is missing."]
    if candidate is None:
        return 0.40, ["Warning: ranked candidate was not found in Step E results."]

    notes = [f"Step E eligibility status: {candidate.eligibility_status}."]
    if candidate.eligibility_status == ELIGIBLE:
        score = 0.85
    elif candidate.eligibility_status == DATA_PENDING:
        score = 0.50
        notes.append("Warning: candidate eligibility still has data-pending gaps.")
    elif candidate.eligibility_status == INELIGIBLE:
        score = 0.20
        notes.append("Warning: candidate is marked ineligible upstream.")
    else:
        score = 0.35
        notes.append("Warning: candidate eligibility status is not recognized.")

    if candidate.evidence_source_ids:
        score += 0.08
        notes.append("Removal/catalogue evidence source IDs are present.")
    else:
        score -= 0.10
        notes.append("Warning: evidence source IDs are missing.")
    if candidate.implementation_source_ids:
        score += 0.05
        notes.append("Implementation source IDs are present.")
    elif candidate.data_pending_reasons:
        score -= 0.05
        notes.append("Warning: implementation or evidence gaps remain data-pending.")

    return _clamp(score, 0.0, 1.0), notes


def _criteria_completeness(
    ranking_bundle: TopsisRankingBundle,
    normalized_bundle: NormalizedMcdaMatrixBundle | None,
) -> tuple[float, list[str]]:
    """Return how complete the criteria evidence was for TOPSIS use."""

    used = len(ranking_bundle.criteria_used)
    skipped = len(ranking_bundle.criteria_skipped)
    notes = [
        f"TOPSIS used {used} criteria and skipped {skipped} criteria.",
    ]
    if normalized_bundle is not None:
        normalized = normalized_bundle.normalized_criteria_count
        skipped_normalization = normalized_bundle.skipped_criteria_count
        total = normalized + skipped_normalization
        notes.append(
            f"Step G normalized {normalized} criterion values and skipped "
            f"{skipped_normalization} criterion values."
        )
        if total:
            return _clamp(normalized / total, 0.0, 1.0), notes

    total_summary = used + skipped
    if total_summary:
        if normalized_bundle is None:
            notes.append(
                "Warning: normalized matrix bundle is missing, so criteria completeness "
                "uses Step I criteria summary only."
            )
        return _clamp(used / total_summary, 0.0, 1.0), notes

    notes.append("Warning: no criteria summary was available for confidence scoring.")
    return 0.35, notes


def _weights_reliability(
    ranking_bundle: TopsisRankingBundle,
    weights_bundle: McdaWeightsBundle | None,
) -> tuple[float, list[str]]:
    """Return a trust score for Step H weight provenance/status."""

    status = _weights_status(ranking_bundle, weights_bundle)
    notes = [f"Step H weights_status: {status}."]
    if status == WEIGHTS_EXPERT_VALIDATED and _expert_validated(ranking_bundle, weights_bundle):
        return 1.00, [*notes, "Weights were explicitly marked expert_validated."]
    if status == WEIGHTS_TEMPORARY:
        return 0.55, [
            *notes,
            "Warning: TOPSIS ranking is provisional because weights are temporary "
            "and not expert validated.",
        ]
    if status == WEIGHTS_MISSING:
        return 0.05, [*notes, "Warning: MCDA weights are missing."]
    if status == WEIGHTS_INVALID:
        return 0.05, [*notes, "Warning: MCDA weights are invalid."]
    return 0.35, [*notes, "Warning: weights_status is unrecognized."]


def _caution_penalty(candidate: TopsisRankedCandidate) -> tuple[float, list[str]]:
    """Return a confidence score that decreases as caution flags increase."""

    caution_count = len(candidate.caution_flags)
    if caution_count == 0:
        return 1.00, ["No Step E/Step I caution flags are attached to this candidate."]
    score = max(0.20, 1.00 - (0.25 * caution_count))
    return score, [
        f"Warning: {caution_count} caution flag(s) reduce confidence but do not "
        "remove the candidate.",
    ]


def _factor(
    factor_name: str,
    factor_score: float,
    notes: list[str],
) -> ConfidenceFactor:
    """Create one weighted confidence factor."""

    factor_weight = CONFIDENCE_FACTOR_WEIGHTS[factor_name]
    score = _clamp(factor_score, 0.0, 1.0)
    return ConfidenceFactor(
        factor_name=factor_name,
        factor_score=score,
        factor_weight=factor_weight,
        weighted_score=score * factor_weight,
        notes=notes,
    )


def _candidate_filter_result(
    ranked_candidate: TopsisRankedCandidate,
    candidate_bundle: CandidateFilterBundle | None,
) -> CandidateFilterResult | None:
    """Find the Step E candidate matching one Step I ranked candidate."""

    if candidate_bundle is None:
        return None
    for candidate in candidate_bundle.results:
        if candidate.nbs_id == ranked_candidate.nbs_id:
            return candidate
    return None


def _weights_status(
    ranking_bundle: TopsisRankingBundle,
    weights_bundle: McdaWeightsBundle | None,
) -> str:
    """Prefer Step H status when provided; otherwise use Step I status."""

    return weights_bundle.weights_status if weights_bundle is not None else ranking_bundle.weights_status


def _expert_validated(
    ranking_bundle: TopsisRankingBundle,
    weights_bundle: McdaWeightsBundle | None,
) -> bool:
    """Prefer Step H expert flag when provided; otherwise use Step I flag."""

    return (
        weights_bundle.expert_validated
        if weights_bundle is not None
        else ranking_bundle.expert_validated
    )


def _confidence_label(score: float) -> str:
    """Return the high/medium/low confidence label for a score."""

    if score >= 0.75:
        return LABEL_HIGH
    if score >= 0.50:
        return LABEL_MEDIUM
    return LABEL_LOW


def _is_warning_note(note: str) -> bool:
    """Identify factor notes that should also appear as candidate warnings."""

    return note.lower().startswith("warning:")


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a float into a fixed range."""

    return max(minimum, min(maximum, value))


def _unique(values: list[str]) -> list[str]:
    """Return unique strings while preserving order."""

    unique_values: list[str] = []
    for value in values:
        if value and value not in unique_values:
            unique_values.append(value)
    return unique_values

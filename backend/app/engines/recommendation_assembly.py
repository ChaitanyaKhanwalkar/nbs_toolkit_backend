"""Step L-A engine for internal recommendation assembly objects.

This module combines already-ranked TOPSIS candidates, separate confidence
scores, and optional explicit plant matches into internal recommendation-shaped
objects. It does not create an API route, does not query or mutate data, does
not change rank, and does not invent evidence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.confidence_scoring import ConfidenceScoringBundle
from app.engines.plant_matching import PlantMatch, PlantMatchingBundle
from app.engines.topsis_ranking import TopsisRankedCandidate, TopsisRankingBundle


ASSEMBLY_METHOD = "rank_confidence_plants_v1"


@dataclass(slots=True)
class RecommendationEvidenceSummary:
    """Evidence/provenance summary carried into one assembled recommendation."""

    source_ids: list[int] = field(default_factory=list)
    caution_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class AssembledRecommendation:
    """One internal assembled recommendation object.

    `match_score` is copied directly from Step I `topsis_closeness`.
    `confidence_score` remains separate and is copied from Step J when present.
    """

    nbs_id: int | None
    nbs_name: str | None
    rank: int
    match_score: float | None
    topsis_closeness: float | None
    confidence_score: float | None
    confidence_label: str | None
    weights_status: str
    expert_validated: bool
    ranking_method: str
    confidence_method: str | None
    plant_matches: list[PlantMatch] = field(default_factory=list)
    evidence_summary: RecommendationEvidenceSummary = field(
        default_factory=RecommendationEvidenceSummary
    )
    explanation: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["plant_matches"] = [
            plant_match.to_dict()
            for plant_match in self.plant_matches
        ]
        payload["evidence_summary"] = self.evidence_summary.to_dict()
        return payload


@dataclass(slots=True)
class RecommendationAssemblyBundle:
    """Internal Step L-A bundle of assembled recommendation objects."""

    use_case: str
    assembly_method: str = ASSEMBLY_METHOD
    recommendation_count: int = 0
    recommendations: list[AssembledRecommendation] = field(default_factory=list)
    weights_status: str = "weights_missing"
    expert_validated: bool = False
    ranking_method: str = "topsis"
    confidence_method: str | None = None
    plant_matching_method: str | None = None
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["recommendations"] = [
            recommendation.to_dict()
            for recommendation in self.recommendations
        ]
        return payload


class RecommendationAssemblyEngine:
    """Assemble internal recommendation objects from Steps I, J, and K."""

    def assemble(
        self,
        ranking_bundle: TopsisRankingBundle,
        confidence_bundle: ConfidenceScoringBundle | None = None,
        plant_matching_bundle: PlantMatchingBundle | None = None,
    ) -> RecommendationAssemblyBundle:
        """Return internal assembled recommendations without changing inputs."""

        warnings = list(ranking_bundle.warnings)
        notes = [
            "Step L-A assembles internal recommendation-shaped objects only.",
            "No API route or /recommend endpoint is created by this engine.",
            "match_score is copied directly from topsis_closeness.",
        ]

        confidence_by_nbs_id = _confidence_by_nbs_id(confidence_bundle)
        plant_matches_by_nbs_id = _plant_matches_by_nbs_id(plant_matching_bundle)

        if confidence_bundle is None:
            warnings.append(
                "ConfidenceScoringBundle was not provided; confidence fields are None."
            )
        else:
            warnings.extend(confidence_bundle.warnings)

        if plant_matching_bundle is None:
            warnings.append(
                "PlantMatchingBundle was not provided; plant_matches are empty."
            )
        else:
            warnings.extend(plant_matching_bundle.warnings)

        if ranking_bundle.weights_status == "temporary_not_expert_validated":
            warnings.append(
                "Assembled recommendations use temporary_not_expert_validated weights "
                "and remain provisional."
            )

        recommendations = [
            _assembled_recommendation(
                candidate,
                ranking_bundle=ranking_bundle,
                confidence_bundle=confidence_bundle,
                confidence_by_nbs_id=confidence_by_nbs_id,
                plant_matching_bundle=plant_matching_bundle,
                plant_matches_by_nbs_id=plant_matches_by_nbs_id,
            )
            for candidate in ranking_bundle.ranked_candidates
        ]
        for recommendation in recommendations:
            warnings.extend(recommendation.warnings)

        return RecommendationAssemblyBundle(
            use_case=ranking_bundle.use_case,
            recommendation_count=len(recommendations),
            recommendations=recommendations,
            weights_status=ranking_bundle.weights_status,
            expert_validated=ranking_bundle.expert_validated,
            ranking_method=ranking_bundle.ranking_method,
            confidence_method=(
                confidence_bundle.confidence_method
                if confidence_bundle is not None
                else None
            ),
            plant_matching_method=(
                plant_matching_bundle.plant_matching_method
                if plant_matching_bundle is not None
                else None
            ),
            warnings=_unique(warnings),
            notes=notes,
        )


def _assembled_recommendation(
    candidate: TopsisRankedCandidate,
    *,
    ranking_bundle: TopsisRankingBundle,
    confidence_bundle: ConfidenceScoringBundle | None,
    confidence_by_nbs_id: dict[int, Any],
    plant_matching_bundle: PlantMatchingBundle | None,
    plant_matches_by_nbs_id: dict[int, list[PlantMatch]],
) -> AssembledRecommendation:
    """Build one recommendation object while preserving upstream values."""

    warnings = list(candidate.warnings)
    notes = list(candidate.notes)
    confidence = (
        confidence_by_nbs_id.get(candidate.nbs_id)
        if candidate.nbs_id is not None
        else None
    )
    plant_matches = (
        plant_matches_by_nbs_id.get(candidate.nbs_id, [])
        if candidate.nbs_id is not None
        else []
    )

    if confidence_bundle is None:
        warnings.append(
            "No confidence bundle was supplied for this assembled recommendation."
        )
    elif confidence is None:
        warnings.append(
            f"No Step J confidence result was found for nbs_id {candidate.nbs_id}."
        )
    else:
        warnings.extend(confidence.warnings)
        notes.extend(confidence.notes)

    if plant_matching_bundle is None:
        warnings.append(
            "No plant matching bundle was supplied; plant_matches are empty."
        )
    elif candidate.nbs_id is not None and candidate.nbs_id not in plant_matches_by_nbs_id:
        warnings.append(
            f"No Step K plant matching result was found for nbs_id {candidate.nbs_id}."
        )

    for plant_match in plant_matches:
        warnings.extend(plant_match.warnings)
        notes.extend(plant_match.notes)

    explanation = [
        f"Rank {candidate.rank} is preserved from Step I TOPSIS ranking.",
        "match_score is copied directly from Step I topsis_closeness.",
        "confidence_score is copied from Step J and kept separate from match_score."
        if confidence is not None
        else "confidence_score is None because no matching Step J result was available.",
        "Plant matches are supporting explicit mappings only and do not affect rank.",
    ]

    evidence_summary = RecommendationEvidenceSummary(
        source_ids=_source_ids(candidate, plant_matches),
        caution_flags=list(candidate.caution_flags),
        warnings=_unique(warnings),
        notes=_unique(notes),
    )

    return AssembledRecommendation(
        nbs_id=candidate.nbs_id,
        nbs_name=candidate.nbs_name,
        rank=candidate.rank,
        match_score=candidate.topsis_closeness,
        topsis_closeness=candidate.topsis_closeness,
        confidence_score=(
            confidence.confidence_score
            if confidence is not None
            else None
        ),
        confidence_label=(
            confidence.confidence_label
            if confidence is not None
            else None
        ),
        weights_status=ranking_bundle.weights_status,
        expert_validated=ranking_bundle.expert_validated,
        ranking_method=ranking_bundle.ranking_method,
        confidence_method=(
            confidence_bundle.confidence_method
            if confidence_bundle is not None
            else None
        ),
        plant_matches=list(plant_matches),
        evidence_summary=evidence_summary,
        explanation=explanation,
        warnings=_unique(warnings),
        notes=[
            "Internal assembly only; no API route or endpoint was created.",
            *evidence_summary.notes,
        ],
    )


def _confidence_by_nbs_id(
    confidence_bundle: ConfidenceScoringBundle | None,
) -> dict[int, Any]:
    """Index Step J confidence rows by nbs_id when available."""

    if confidence_bundle is None:
        return {}
    confidence_by_id = {}
    for result in confidence_bundle.results:
        if result.nbs_id is not None:
            confidence_by_id[result.nbs_id] = result
    return confidence_by_id


def _plant_matches_by_nbs_id(
    plant_matching_bundle: PlantMatchingBundle | None,
) -> dict[int, list[PlantMatch]]:
    """Index Step K plant match rows by nbs_id when available."""

    if plant_matching_bundle is None:
        return {}
    matches_by_id = {}
    for candidate_matches in plant_matching_bundle.candidate_matches:
        if candidate_matches.nbs_id is not None:
            matches_by_id[candidate_matches.nbs_id] = list(
                candidate_matches.plant_matches
            )
    return matches_by_id


def _source_ids(
    candidate: TopsisRankedCandidate,
    plant_matches: list[PlantMatch],
) -> list[int]:
    """Collect source IDs from TOPSIS candidate context and plant matches."""

    source_ids: list[int] = []
    for source_id in candidate.source_ids:
        _append_int(source_ids, source_id)
    for plant_match in plant_matches:
        for source_id in plant_match.source_ids:
            _append_int(source_ids, source_id)
    return source_ids


def _append_int(values: list[int], value: Any) -> None:
    """Append one integer ID once when it can be read safely."""

    try:
        int_value = int(value)
    except (TypeError, ValueError):
        return
    if int_value not in values:
        values.append(int_value)


def _unique(values: list[str]) -> list[str]:
    """Return unique strings while preserving order."""

    unique_values: list[str] = []
    for value in values:
        if value and value not in unique_values:
            unique_values.append(value)
    return unique_values

"""Step I engine for TOPSIS ranking of MCDA candidates.

This module applies supplied Step H weights to Step G normalized MCDA criteria
and calculates TOPSIS closeness/rank order. It does not create final
recommendations, confidence scores, AHP pairwise weights, plant selections, or
health-risk classifications.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import sqrt
from typing import Any

from app.engines.mcda_normalization import (
    NORMALIZATION_NORMALIZED,
    NormalizedMcdaMatrixBundle,
    NormalizedMcdaMatrixRow,
)
from app.engines.mcda_weights import (
    WEIGHTS_EXPERT_VALIDATED,
    WEIGHTS_INVALID,
    WEIGHTS_MISSING,
    WEIGHTS_TEMPORARY,
    McdaWeightsBundle,
)


RANKING_METHOD = "topsis"


@dataclass(slots=True)
class TopsisCriterionContribution:
    """Weighted contribution for one normalized TOPSIS criterion."""

    criterion_name: str
    normalized_value: float
    weight: float
    weighted_value: float

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class TopsisRankedCandidate:
    """TOPSIS-ranked candidate from the Step G normalized matrix."""

    nbs_id: int | None
    nbs_name: str | None
    eligibility_status: str
    rank: int
    topsis_closeness: float | None
    distance_to_ideal_best: float | None
    distance_to_ideal_worst: float | None
    criterion_contributions: list[TopsisCriterionContribution] = field(
        default_factory=list
    )
    caution_flags: list[str] = field(default_factory=list)
    source_ids: list[int] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["criterion_contributions"] = [
            contribution.to_dict()
            for contribution in self.criterion_contributions
        ]
        return payload


@dataclass(slots=True)
class TopsisRankingBundle:
    """Step I TOPSIS ranking bundle for eligible/data-pending candidates."""

    use_case: str
    treatment_need_groups: list[str] = field(default_factory=list)
    row_count: int = 0
    ranked_count: int = 0
    criteria_used: list[str] = field(default_factory=list)
    criteria_skipped: list[str] = field(default_factory=list)
    weights_status: str = WEIGHTS_MISSING
    weights_source: str | None = None
    expert_validated: bool = False
    ranking_method: str = RANKING_METHOD
    ranked_candidates: list[TopsisRankedCandidate] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["ranked_candidates"] = [
            candidate.to_dict()
            for candidate in self.ranked_candidates
        ]
        return payload


class TopsisRankingEngine:
    """Calculate TOPSIS closeness using Step G values and Step H weights."""

    def rank(
        self,
        normalized_bundle: NormalizedMcdaMatrixBundle,
        weights_bundle: McdaWeightsBundle,
    ) -> TopsisRankingBundle:
        """Return ranked candidates or a safe no-ranking bundle."""

        warnings = [*normalized_bundle.warnings, *weights_bundle.warnings]
        notes = [
            "Step I calculates TOPSIS rank order only.",
            "This output is not a final recommendation and does not include a "
            "confidence score, plant selection, or AHP pairwise calculation.",
        ]

        if weights_bundle.weights_status == WEIGHTS_MISSING:
            warnings.append(
                "TOPSIS ranking was not calculated because MCDA weights are missing."
            )
            return self._empty_bundle(
                normalized_bundle,
                weights_bundle,
                warnings,
                notes,
            )

        if weights_bundle.weights_status == WEIGHTS_INVALID:
            warnings.append(
                "TOPSIS ranking was not calculated because supplied MCDA weights are invalid."
            )
            return self._empty_bundle(
                normalized_bundle,
                weights_bundle,
                warnings,
                notes,
            )

        if weights_bundle.weights_status == WEIGHTS_TEMPORARY:
            warnings.append(
                "TOPSIS ranking uses temporary_not_expert_validated weights and "
                "must be treated as provisional."
            )
        elif weights_bundle.weights_status != WEIGHTS_EXPERT_VALIDATED:
            warnings.append(
                f"TOPSIS ranking received unrecognized weights_status "
                f"'{weights_bundle.weights_status}'."
            )

        criteria_used, criteria_skipped = _usable_criteria(
            normalized_bundle,
            weights_bundle,
        )
        if not normalized_bundle.rows:
            warnings.append("TOPSIS ranking was not calculated because there are no matrix rows.")
        if not criteria_used:
            warnings.append(
                "TOPSIS ranking was not calculated because no criteria had both "
                "normalized values for every row and supplied weights."
            )
            return TopsisRankingBundle(
                use_case=normalized_bundle.use_case,
                treatment_need_groups=list(normalized_bundle.treatment_need_groups),
                row_count=normalized_bundle.row_count,
                ranked_count=0,
                criteria_used=[],
                criteria_skipped=criteria_skipped,
                weights_status=weights_bundle.weights_status,
                weights_source=weights_bundle.weights_source,
                expert_validated=weights_bundle.expert_validated,
                ranking_method=RANKING_METHOD,
                ranked_candidates=[],
                warnings=warnings,
                notes=notes,
            )

        contributions_by_row = {
            index: _criterion_contributions(row, criteria_used, weights_bundle)
            for index, row in enumerate(normalized_bundle.rows)
        }
        ideal_best = _ideal_values(contributions_by_row, criteria_used, max)
        ideal_worst = _ideal_values(contributions_by_row, criteria_used, min)

        ranked_candidates = [
            _ranked_candidate(
                row,
                contributions_by_row[index],
                ideal_best,
                ideal_worst,
            )
            for index, row in enumerate(normalized_bundle.rows)
        ]
        ranked_candidates.sort(key=_candidate_sort_key)
        for rank, candidate in enumerate(ranked_candidates, start=1):
            candidate.rank = rank

        return TopsisRankingBundle(
            use_case=normalized_bundle.use_case,
            treatment_need_groups=list(normalized_bundle.treatment_need_groups),
            row_count=normalized_bundle.row_count,
            ranked_count=len(ranked_candidates),
            criteria_used=criteria_used,
            criteria_skipped=criteria_skipped,
            weights_status=weights_bundle.weights_status,
            weights_source=weights_bundle.weights_source,
            expert_validated=weights_bundle.expert_validated,
            ranking_method=RANKING_METHOD,
            ranked_candidates=ranked_candidates,
            warnings=warnings,
            notes=notes,
        )

    def _empty_bundle(
        self,
        normalized_bundle: NormalizedMcdaMatrixBundle,
        weights_bundle: McdaWeightsBundle,
        warnings: list[str],
        notes: list[str],
    ) -> TopsisRankingBundle:
        """Return a no-ranking bundle while preserving context."""

        return TopsisRankingBundle(
            use_case=normalized_bundle.use_case,
            treatment_need_groups=list(normalized_bundle.treatment_need_groups),
            row_count=normalized_bundle.row_count,
            ranked_count=0,
            criteria_used=[],
            criteria_skipped=list(normalized_bundle.criteria_names),
            weights_status=weights_bundle.weights_status,
            weights_source=weights_bundle.weights_source,
            expert_validated=weights_bundle.expert_validated,
            ranking_method=RANKING_METHOD,
            ranked_candidates=[],
            warnings=warnings,
            notes=notes,
        )


def _usable_criteria(
    normalized_bundle: NormalizedMcdaMatrixBundle,
    weights_bundle: McdaWeightsBundle,
) -> tuple[list[str], list[str]]:
    """Return criteria usable for TOPSIS and criteria skipped with gaps."""

    criteria_used: list[str] = []
    criteria_skipped: list[str] = []
    criteria_names = _criteria_names(normalized_bundle)
    for criterion_name in criteria_names:
        if criterion_name not in weights_bundle.weights:
            criteria_skipped.append(criterion_name)
            continue
        if all(
            _normalized_criterion(row, criterion_name) is not None
            for row in normalized_bundle.rows
        ):
            criteria_used.append(criterion_name)
        else:
            criteria_skipped.append(criterion_name)
    return criteria_used, criteria_skipped


def _criterion_contributions(
    row: NormalizedMcdaMatrixRow,
    criteria_used: list[str],
    weights_bundle: McdaWeightsBundle,
) -> list[TopsisCriterionContribution]:
    """Build weighted TOPSIS criterion values for one row."""

    contributions = []
    for criterion_name in criteria_used:
        criterion = _normalized_criterion(row, criterion_name)
        if criterion is None or criterion.normalized_value is None:
            continue
        weight = weights_bundle.weights[criterion_name]
        contributions.append(
            TopsisCriterionContribution(
                criterion_name=criterion_name,
                normalized_value=criterion.normalized_value,
                weight=weight,
                weighted_value=criterion.normalized_value * weight,
            )
        )
    return contributions


def _ranked_candidate(
    row: NormalizedMcdaMatrixRow,
    contributions: list[TopsisCriterionContribution],
    ideal_best: dict[str, float],
    ideal_worst: dict[str, float],
) -> TopsisRankedCandidate:
    """Calculate one candidate's TOPSIS distances and closeness."""

    contribution_values = {
        contribution.criterion_name: contribution.weighted_value
        for contribution in contributions
    }
    distance_best = _euclidean_distance(contribution_values, ideal_best)
    distance_worst = _euclidean_distance(contribution_values, ideal_worst)
    denominator = distance_best + distance_worst
    warnings = []
    topsis_closeness = (
        distance_worst / denominator
        if denominator
        else None
    )
    if topsis_closeness is None:
        warnings.append(
            "TOPSIS closeness could not discriminate this candidate because "
            "ideal-best and ideal-worst distances are both zero."
        )

    return TopsisRankedCandidate(
        nbs_id=row.nbs_id,
        nbs_name=row.nbs_name,
        eligibility_status=row.eligibility_status,
        rank=0,
        topsis_closeness=topsis_closeness,
        distance_to_ideal_best=distance_best,
        distance_to_ideal_worst=distance_worst,
        criterion_contributions=contributions,
        caution_flags=list(row.caution_flags),
        source_ids=list(row.source_ids),
        notes=[
            *list(row.notes),
            "Rank is based on TOPSIS closeness only and is not a final recommendation.",
        ],
        warnings=warnings,
    )


def _ideal_values(
    contributions_by_row: dict[int, list[TopsisCriterionContribution]],
    criteria_used: list[str],
    aggregate: Any,
) -> dict[str, float]:
    """Return ideal best or worst weighted values for all used criteria."""

    ideals = {}
    for criterion_name in criteria_used:
        weighted_values = [
            contribution.weighted_value
            for contributions in contributions_by_row.values()
            for contribution in contributions
            if contribution.criterion_name == criterion_name
        ]
        ideals[criterion_name] = aggregate(weighted_values)
    return ideals


def _euclidean_distance(
    contribution_values: dict[str, float],
    ideal_values: dict[str, float],
) -> float:
    """Return Euclidean distance between one candidate and an ideal point."""

    return sqrt(
        sum(
            (contribution_values[criterion_name] - ideal_value) ** 2
            for criterion_name, ideal_value in ideal_values.items()
        )
    )


def _normalized_criterion(row: NormalizedMcdaMatrixRow, criterion_name: str) -> Any:
    """Return a normalized criterion when it is usable for TOPSIS."""

    for criterion in row.normalized_criteria:
        if criterion.criterion_name != criterion_name:
            continue
        if criterion.normalization_status != NORMALIZATION_NORMALIZED:
            return None
        if criterion.normalized_value is None:
            return None
        return criterion
    return None


def _criteria_names(normalized_bundle: NormalizedMcdaMatrixBundle) -> list[str]:
    """Collect criteria names from bundle metadata and row criteria."""

    names: list[str] = []
    for criterion_name in normalized_bundle.criteria_names:
        _append_once(names, criterion_name)
    for row in normalized_bundle.rows:
        for criterion in row.normalized_criteria:
            _append_once(names, criterion.criterion_name)
    return names


def _candidate_sort_key(candidate: TopsisRankedCandidate) -> tuple[Any, ...]:
    """Sort highest closeness first, then deterministically by ID/name."""

    closeness = candidate.topsis_closeness
    return (
        -(closeness if closeness is not None else -1.0),
        candidate.nbs_id is None,
        candidate.nbs_id if candidate.nbs_id is not None else 0,
        candidate.nbs_name or "",
    )


def _append_once(values: list[str], value: str) -> None:
    """Append a value once while preserving order."""

    if value not in values:
        values.append(value)

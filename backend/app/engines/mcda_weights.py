"""Step H engine for MCDA criteria weight handling.

This module prepares optional criteria weights for future TOPSIS work. It only
validates and normalizes supplied weights. It does not calculate AHP pairwise
weights, rank candidates, apply TOPSIS, calculate match/confidence scores,
recommend plants, classify health risk, or create final recommendations.
"""

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.mcda_normalization import NormalizedMcdaMatrixBundle


WEIGHTS_MISSING = "weights_missing"
WEIGHTS_TEMPORARY = "temporary_not_expert_validated"
WEIGHTS_EXPERT_VALIDATED = "expert_validated"
WEIGHTS_INVALID = "invalid_weights"

ALLOWED_WEIGHTS_STATUSES = {
    WEIGHTS_MISSING,
    WEIGHTS_TEMPORARY,
    WEIGHTS_EXPERT_VALIDATED,
    WEIGHTS_INVALID,
}


@dataclass(slots=True)
class McdaWeightsBundle:
    """Validated weight packet for future MCDA/TOPSIS steps."""

    criteria_names: list[str] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)
    weights_status: str = WEIGHTS_MISSING
    weights_source: str | None = None
    expert_validated: bool = False
    missing_weight_criteria: list[str] = field(default_factory=list)
    extra_weight_criteria: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


class McdaWeightsHandler:
    """Validate and normalize supplied MCDA criteria weights."""

    def prepare_weights(
        self,
        criteria_names: Sequence[str],
        supplied_weights: Mapping[str, Any] | None = None,
        *,
        weights_source: str | None = None,
        expert_validated: bool = False,
    ) -> McdaWeightsBundle:
        """Return a weight bundle without ranking or TOPSIS calculations."""

        criteria = _unique_strings(criteria_names)
        notes = [
            "Step H validates and normalizes supplied MCDA criteria weights only.",
            "No AHP pairwise calculation, TOPSIS, ranking, match score, "
            "confidence score, or final recommendation was calculated.",
        ]

        if not supplied_weights:
            return McdaWeightsBundle(
                criteria_names=criteria,
                weights={},
                weights_status=WEIGHTS_MISSING,
                weights_source=weights_source,
                expert_validated=False,
                missing_weight_criteria=list(criteria),
                extra_weight_criteria=[],
                warnings=[
                    "No MCDA criteria weights were supplied. The criteria_weights "
                    "table remains pending expert/AHP workflow."
                ],
                notes=notes,
            )

        supplied_keys = _unique_strings(supplied_weights.keys())
        missing = [criterion for criterion in criteria if criterion not in supplied_weights]
        extra = [criterion for criterion in supplied_keys if criterion not in criteria]

        numeric_weights: dict[str, float] = {}
        warnings: list[str] = []
        invalid_messages: list[str] = []
        for criterion, raw_weight in supplied_weights.items():
            weight = _as_float(raw_weight)
            if weight is None:
                invalid_messages.append(f"Weight for '{criterion}' must be numeric.")
                continue
            if weight < 0:
                invalid_messages.append(f"Weight for '{criterion}' must be non-negative.")
                continue
            if criterion in criteria:
                numeric_weights[criterion] = weight

        if extra:
            warnings.append(
                "Extra supplied weights were ignored because they are not present "
                "in the normalized MCDA criteria: "
                + ", ".join(extra)
                + "."
            )
        if missing:
            warnings.append(
                "Some normalized MCDA criteria do not have supplied weights: "
                + ", ".join(missing)
                + "."
            )

        if invalid_messages:
            return McdaWeightsBundle(
                criteria_names=criteria,
                weights={},
                weights_status=WEIGHTS_INVALID,
                weights_source=weights_source,
                expert_validated=False,
                missing_weight_criteria=missing,
                extra_weight_criteria=extra,
                warnings=[*warnings, *invalid_messages],
                notes=notes,
            )

        total_weight = sum(numeric_weights.values())
        if total_weight <= 0:
            return McdaWeightsBundle(
                criteria_names=criteria,
                weights={},
                weights_status=WEIGHTS_INVALID,
                weights_source=weights_source,
                expert_validated=False,
                missing_weight_criteria=missing,
                extra_weight_criteria=extra,
                warnings=[
                    *warnings,
                    "Supplied weights must have a positive total before they can be normalized.",
                ],
                notes=notes,
            )

        normalized_weights = {
            criterion: weight / total_weight
            for criterion, weight in numeric_weights.items()
        }
        status = (
            WEIGHTS_EXPERT_VALIDATED
            if expert_validated
            else WEIGHTS_TEMPORARY
        )
        source = weights_source or (
            "expert_supplied" if expert_validated else "temporary_supplied"
        )
        if not expert_validated:
            warnings.append(
                "Supplied weights are marked temporary_not_expert_validated. "
                "Do not treat them as final AHP/expert weights."
            )

        return McdaWeightsBundle(
            criteria_names=criteria,
            weights=normalized_weights,
            weights_status=status,
            weights_source=source,
            expert_validated=expert_validated,
            missing_weight_criteria=missing,
            extra_weight_criteria=extra,
            warnings=warnings,
            notes=notes,
        )

    def prepare_from_normalized_bundle(
        self,
        normalized_bundle: NormalizedMcdaMatrixBundle,
        supplied_weights: Mapping[str, Any] | None = None,
        *,
        weights_source: str | None = None,
        expert_validated: bool = False,
    ) -> McdaWeightsBundle:
        """Prepare weights from a Step G normalized MCDA matrix bundle."""

        return self.prepare_weights(
            normalized_bundle.criteria_names,
            supplied_weights,
            weights_source=weights_source,
            expert_validated=expert_validated,
        )


def _unique_strings(values: Any) -> list[str]:
    """Return unique non-empty strings while preserving order."""

    unique: list[str] = []
    for value in values or []:
        text = str(value).strip()
        if text and text not in unique:
            unique.append(text)
    return unique


def _as_float(value: Any) -> float | None:
    """Convert a weight value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

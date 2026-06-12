"""Step K engine for attaching explicitly mapped plants to ranked NbS options.

This module runs after TOPSIS ranking and optional confidence scoring. It only
looks up plants that are already explicitly mapped to an NbS option through the
plant catalogue/provider. It does not change rank, TOPSIS closeness,
confidence scores, or create final recommendations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from inspect import signature
from typing import Any, Protocol

from app.engines.confidence_scoring import ConfidenceScoringBundle
from app.engines.topsis_ranking import TopsisRankedCandidate, TopsisRankingBundle


PLANT_MATCHING_METHOD = "explicit_mapping_v1"


class PlantMappingProvider(Protocol):
    """Provider shape needed by Step K for explicit plant mappings."""

    def get_plants_for_nbs(
        self,
        nbs_id: int,
        *,
        include_invasive: bool = False,
    ) -> list[Any]:
        """Return plants explicitly mapped to one NbS option."""


@dataclass(slots=True)
class PlantMatch:
    """One explicitly mapped plant attached to an already-ranked NbS option."""

    plant_id: int | None
    scientific_name: str | None
    common_name: str | None
    local_name: str | None
    nbs_id: int | None
    nbs_name: str | None
    suitability_notes: list[str] = field(default_factory=list)
    source_ids: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        return asdict(self)


@dataclass(slots=True)
class CandidatePlantMatches:
    """Plant matches for one already-ranked TOPSIS candidate."""

    nbs_id: int | None
    nbs_name: str | None
    rank: int
    topsis_closeness: float | None
    confidence_score: float | None = None
    confidence_label: str | None = None
    plant_matches: list[PlantMatch] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["plant_matches"] = [
            plant_match.to_dict()
            for plant_match in self.plant_matches
        ]
        return payload


@dataclass(slots=True)
class PlantMatchingBundle:
    """Step K plant matching output for ranked NbS candidates."""

    use_case: str
    ranking_method: str
    confidence_method: str | None = None
    plant_matching_method: str = PLANT_MATCHING_METHOD
    candidate_matches: list[CandidatePlantMatches] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for tests, services, or future APIs."""

        payload = asdict(self)
        payload["candidate_matches"] = [
            candidate.to_dict()
            for candidate in self.candidate_matches
        ]
        return payload


class PlantMatchingEngine:
    """Attach explicit plant mappings without changing ranked NbS candidates."""

    def __init__(self, plant_provider: PlantMappingProvider) -> None:
        self.plant_provider = plant_provider

    @classmethod
    def from_session(cls, session: Any) -> "PlantMatchingEngine":
        """Build the engine with the read-only plant catalogue service."""

        from app.services.plant_catalog_service import PlantCatalogService

        return cls(PlantCatalogService(session))

    def match_plants(
        self,
        ranking_bundle: TopsisRankingBundle,
        confidence_bundle: ConfidenceScoringBundle | None = None,
    ) -> PlantMatchingBundle:
        """Return explicit plant matches for each ranked candidate.

        The Step K output copies rank, TOPSIS closeness, and confidence fields
        from upstream bundles. It never recalculates or edits those values.
        """

        warnings = list(ranking_bundle.warnings)
        notes = [
            "Step K attaches only explicitly mapped plants after TOPSIS ranking.",
            "Plant matches do not change rank, TOPSIS closeness, or confidence score.",
        ]

        confidence_by_nbs_id = _confidence_by_nbs_id(confidence_bundle)
        if confidence_bundle is None:
            warnings.append(
                "ConfidenceScoringBundle was not provided; confidence fields are None."
            )
        else:
            warnings.extend(confidence_bundle.warnings)

        if not ranking_bundle.ranked_candidates:
            warnings.append(
                "Plant matching returned no candidate matches because Step I ranked_candidates is empty."
            )

        candidate_matches = [
            self._candidate_matches(candidate, confidence_by_nbs_id)
            for candidate in ranking_bundle.ranked_candidates
        ]
        for candidate in candidate_matches:
            warnings.extend(candidate.warnings)

        return PlantMatchingBundle(
            use_case=ranking_bundle.use_case,
            ranking_method=ranking_bundle.ranking_method,
            confidence_method=(
                confidence_bundle.confidence_method
                if confidence_bundle is not None
                else None
            ),
            candidate_matches=candidate_matches,
            warnings=_unique(warnings),
            notes=notes,
        )

    def match(
        self,
        ranking_bundle: TopsisRankingBundle,
        confidence_bundle: ConfidenceScoringBundle | None = None,
    ) -> PlantMatchingBundle:
        """Alias for callers that prefer a shorter method name."""

        return self.match_plants(ranking_bundle, confidence_bundle)

    def _candidate_matches(
        self,
        candidate: TopsisRankedCandidate,
        confidence_by_nbs_id: dict[int, Any],
    ) -> CandidatePlantMatches:
        """Build plant matches for one ranked candidate."""

        warnings = list(candidate.warnings)
        confidence = (
            confidence_by_nbs_id.get(candidate.nbs_id)
            if candidate.nbs_id is not None
            else None
        )
        if candidate.nbs_id is None:
            warnings.append(
                "Ranked candidate has no nbs_id; explicit plant mappings cannot be looked up."
            )
            mapped_plants: list[Any] = []
        else:
            mapped_plants = self._get_explicit_plants(candidate.nbs_id)

        if confidence_by_nbs_id and confidence is None:
            warnings.append(
                f"No matching Step J confidence result was found for nbs_id {candidate.nbs_id}."
            )

        if not mapped_plants and candidate.nbs_id is not None:
            warnings.append(
                f"No explicit plant mappings were found for nbs_id {candidate.nbs_id}."
            )

        plant_matches = [
            _plant_match_from_row(row, candidate)
            for row in mapped_plants
        ]

        return CandidatePlantMatches(
            nbs_id=candidate.nbs_id,
            nbs_name=candidate.nbs_name,
            rank=candidate.rank,
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
            plant_matches=plant_matches,
            warnings=_unique(warnings),
            notes=[
                "Step K preserved the upstream rank and TOPSIS closeness.",
                "Only provider-returned explicit plant mappings were attached.",
            ],
        )

    def _get_explicit_plants(self, nbs_id: int) -> list[Any]:
        """Return explicit plant mappings while supporting existing providers."""

        get_plants = self.plant_provider.get_plants_for_nbs
        parameters = signature(get_plants).parameters
        if "include_invasive" in parameters:
            return list(get_plants(nbs_id, include_invasive=False))
        return list(get_plants(nbs_id))


def _plant_match_from_row(
    row: Any,
    candidate: TopsisRankedCandidate,
) -> PlantMatch:
    """Convert a provider row/dict/object into a Step K plant match."""

    warnings = _string_list(_value(row, "warnings"))
    if _truthy(_value(row, "invasive")):
        warnings.append(
            "Mapped plant is flagged invasive by source data; review before field use."
        )

    return PlantMatch(
        plant_id=_int_or_none(_first_value(row, "plant_id", "id")),
        scientific_name=_str_or_none(
            _first_value(row, "scientific_name", "plant_species")
        ),
        common_name=_str_or_none(_value(row, "common_name")),
        local_name=_str_or_none(_value(row, "local_name")),
        nbs_id=candidate.nbs_id,
        nbs_name=candidate.nbs_name,
        suitability_notes=_plant_suitability_notes(row),
        source_ids=_source_ids(row),
        warnings=_unique(warnings),
        notes=[
            "Plant was included because the provider returned an explicit NbS mapping.",
        ],
    )


def _plant_suitability_notes(row: Any) -> list[str]:
    """Collect only suitability notes already present in the provider row."""

    notes: list[str] = []
    for key in (
        "suitability_notes",
        "basis",
        "plant_solution_basis",
        "mapping_basis",
        "evidence_note",
        "pollution_tolerance",
        "ecological_role",
    ):
        raw_value = _value(row, key)
        if isinstance(raw_value, list):
            for item in raw_value:
                _append_unique(notes, _str_or_none(item))
        else:
            _append_unique(notes, _str_or_none(raw_value))
    return notes


def _source_ids(row: Any) -> list[int]:
    """Collect source IDs from plant rows and richer mapping rows."""

    source_ids: list[int] = []
    raw_source_ids = _value(row, "source_ids")
    if isinstance(raw_source_ids, list):
        for source_id in raw_source_ids:
            _append_int(source_ids, source_id)
    for key in ("source_id", "plant_source_id", "mapping_source_id"):
        _append_int(source_ids, _value(row, key))
    return source_ids


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


def _first_value(row: Any, *keys: str) -> Any:
    """Return the first available value from a dict/object row."""

    for key in keys:
        value = _value(row, key)
        if value is not None:
            return value
    return None


def _value(row: Any, key: str) -> Any:
    """Return one value from a dict-like or object-like provider row."""

    if isinstance(row, dict):
        return row.get(key)
    return getattr(row, key, None)


def _int_or_none(value: Any) -> int | None:
    """Convert source/catalogue IDs to int when possible."""

    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _append_int(values: list[int], value: Any) -> None:
    """Append one integer ID once when it can be read safely."""

    int_value = _int_or_none(value)
    if int_value is not None and int_value not in values:
        values.append(int_value)


def _str_or_none(value: Any) -> str | None:
    """Return stripped text or None for empty values."""

    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _string_list(value: Any) -> list[str]:
    """Return a list of strings from a provider warning/note value."""

    if value is None:
        return []
    if isinstance(value, list):
        return [
            text
            for item in value
            if (text := _str_or_none(item)) is not None
        ]
    text = _str_or_none(value)
    return [text] if text is not None else []


def _truthy(value: Any) -> bool:
    """Read database-ish truthy values without guessing scientific meaning."""

    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _append_unique(values: list[str], value: str | None) -> None:
    """Append a string once while preserving order."""

    if value and value not in values:
        values.append(value)


def _unique(values: list[str]) -> list[str]:
    """Return unique strings while preserving order."""

    unique_values: list[str] = []
    for value in values:
        _append_unique(unique_values, value)
    return unique_values

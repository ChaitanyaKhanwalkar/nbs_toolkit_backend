"""Run Scientific Engine Steps A-E, A-J, A-K, or A-L as one internal workflow.

This service is a backend-only coordinator. It calls the existing staged
engines in order and returns their intermediate bundles so future code can see
what happened at each step. It does not create final recommendations, API
routes, AHP pairwise weights, plant-driven ranking, or health-risk labels.
Step L only assembles internal recommendation-shaped objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from app.engines import (
    CandidateFilterBundle,
    CandidateFilteringEngine,
    ConfidenceScoringBundle,
    ConfidenceScoringEngine,
    InputContext,
    InputNormalizationEngine,
    McdaMatrixBuilder,
    McdaMatrixBundle,
    McdaNormalizationEngine,
    McdaWeightsBundle,
    McdaWeightsHandler,
    NormalizedMcdaMatrixBundle,
    PlantMatchingBundle,
    PlantMatchingEngine,
    PollutantGapBundle,
    PollutantGapEngine,
    RecommendationAssemblyBundle,
    RecommendationAssemblyEngine,
    TreatmentNeedBundle,
    TreatmentNeedClassifier,
    TopsisRankingBundle,
    TopsisRankingEngine,
    WaterInputAssemblyEngine,
    WaterInputBundle,
)
from app.engines.candidate_filtering import NbsCandidateProvider
from app.engines.plant_matching import PlantMappingProvider
from app.engines.pollutant_gap import StandardsProvider
from app.engines.water_input_assembly import WaterObservationProvider


WORKFLOW_COMPLETED = "completed"
WORKFLOW_VALIDATION_FAILED = "validation_failed"
WORKFLOW_DATA_MISSING = "data_missing"
WORKFLOW_FAILED = "failed"

VALID_WORKFLOW_STEPS = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
}
DEFAULT_WORKFLOW_END_STEP = "E"

MatrixTransform = Callable[[McdaMatrixBundle], McdaMatrixBundle]


def _to_plain_value(value: Any) -> Any:
    """Convert staged engine objects to plain dictionaries when possible."""

    if value is None:
        return None
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _append_unique(items: list[str], value: str | None) -> None:
    """Add a message once while preserving the order messages were found."""

    if value and value not in items:
        items.append(value)


def _extend_unique(items: list[str], values: list[str] | tuple[str, ...] | None) -> None:
    """Add multiple messages once while preserving the order they were found."""

    for value in values or []:
        _append_unique(items, value)


@dataclass(slots=True)
class ScientificWorkflowResult:
    """Staged result returned by the internal Scientific Workflow service."""

    workflow_status: str
    step_completed: str | None = None
    input_context: InputContext | None = None
    water_input_bundle: WaterInputBundle | None = None
    pollutant_gap_bundle: PollutantGapBundle | None = None
    treatment_need_bundle: TreatmentNeedBundle | None = None
    candidate_filter_bundle: CandidateFilterBundle | None = None
    mcda_matrix_bundle: McdaMatrixBundle | None = None
    normalized_mcda_matrix_bundle: NormalizedMcdaMatrixBundle | None = None
    mcda_weights_bundle: McdaWeightsBundle | None = None
    topsis_ranking_bundle: TopsisRankingBundle | None = None
    confidence_scoring_bundle: ConfidenceScoringBundle | None = None
    plant_matching_bundle: PlantMatchingBundle | None = None
    recommendation_assembly_bundle: RecommendationAssemblyBundle | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly view of the staged workflow output."""

        return {
            "workflow_status": self.workflow_status,
            "step_completed": self.step_completed,
            "input_context": _to_plain_value(self.input_context),
            "water_input_bundle": _to_plain_value(self.water_input_bundle),
            "pollutant_gap_bundle": _to_plain_value(self.pollutant_gap_bundle),
            "treatment_need_bundle": _to_plain_value(self.treatment_need_bundle),
            "candidate_filter_bundle": _to_plain_value(self.candidate_filter_bundle),
            "mcda_matrix_bundle": _to_plain_value(self.mcda_matrix_bundle),
            "normalized_mcda_matrix_bundle": _to_plain_value(self.normalized_mcda_matrix_bundle),
            "mcda_weights_bundle": _to_plain_value(self.mcda_weights_bundle),
            "topsis_ranking_bundle": _to_plain_value(self.topsis_ranking_bundle),
            "confidence_scoring_bundle": _to_plain_value(self.confidence_scoring_bundle),
            "plant_matching_bundle": _to_plain_value(self.plant_matching_bundle),
            "recommendation_assembly_bundle": _to_plain_value(
                self.recommendation_assembly_bundle
            ),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


class ScientificWorkflowService:
    """Coordinate staged workflow steps without exposing an endpoint or final decision.

    Pass fake providers in tests or real read-only services in application code.
    The service keeps each step separate so future development can inspect or
    replace one layer without changing the others.
    """

    def __init__(
        self,
        water_service: WaterObservationProvider | None = None,
        standards_service: StandardsProvider | None = None,
        nbs_provider: NbsCandidateProvider | None = None,
        plant_provider: PlantMappingProvider | None = None,
        input_engine: InputNormalizationEngine | None = None,
        treatment_classifier: TreatmentNeedClassifier | None = None,
    ) -> None:
        self.water_service = water_service
        self.standards_service = standards_service
        self.nbs_provider = nbs_provider
        self.plant_provider = plant_provider
        self.input_engine = input_engine or InputNormalizationEngine()
        self.treatment_classifier = treatment_classifier or TreatmentNeedClassifier()

    @classmethod
    def from_session(cls, session: Any) -> "ScientificWorkflowService":
        """Build the workflow with existing read-only services for one session."""

        from app.services.nbs_catalog_service import NbsCatalogService
        from app.services.plant_catalog_service import PlantCatalogService
        from app.services.standards_service import StandardsService
        from app.services.water_data_service import WaterDataService

        return cls(
            water_service=WaterDataService(session),
            standards_service=StandardsService(session),
            nbs_provider=NbsCatalogService(session),
            plant_provider=PlantCatalogService(session),
        )

    def run(
        self,
        raw_input: Mapping[str, Any] | None = None,
        *,
        max_step: str = DEFAULT_WORKFLOW_END_STEP,
        supplied_weights: Mapping[str, Any] | None = None,
        weights_source: str | None = None,
        expert_validated: bool = False,
        matrix_transform: MatrixTransform | None = None,
        **fields: Any,
    ) -> ScientificWorkflowResult:
        """Run staged workflow bundles through the requested step.

        The default `max_step="E"` preserves the original A-E workflow behavior.
        Use `max_step="J"` to run the internal A-J staged workflow. Use
        `max_step="K"` to add explicit plant matching after A-J. Use
        `max_step="L"` to assemble internal recommendation-shaped objects
        after A-K. Supplied weights remain transparent; temporary weights are
        never treated as expert validated unless the explicit flag is true.
        """

        errors: list[str] = []
        warnings: list[str] = []
        step_completed: str | None = None
        input_context: InputContext | None = None
        water_input_bundle: WaterInputBundle | None = None
        pollutant_gap_bundle: PollutantGapBundle | None = None
        treatment_need_bundle: TreatmentNeedBundle | None = None
        candidate_filter_bundle: CandidateFilterBundle | None = None
        mcda_matrix_bundle: McdaMatrixBundle | None = None
        normalized_mcda_matrix_bundle: NormalizedMcdaMatrixBundle | None = None
        mcda_weights_bundle: McdaWeightsBundle | None = None
        topsis_ranking_bundle: TopsisRankingBundle | None = None
        confidence_scoring_bundle: ConfidenceScoringBundle | None = None
        plant_matching_bundle: PlantMatchingBundle | None = None
        recommendation_assembly_bundle: RecommendationAssemblyBundle | None = None

        try:
            max_step = _normalize_max_step(max_step)
            if max_step not in VALID_WORKFLOW_STEPS:
                _append_unique(errors, f"Unsupported max_step '{max_step}'.")
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_FAILED,
                    step_completed=None,
                    errors=errors,
                    warnings=warnings,
                )

            input_context = self.input_engine.normalize(raw_input, **fields)
            step_completed = "A"
            _extend_unique(errors, input_context.errors)
            _extend_unique(warnings, input_context.warnings)

            if input_context.validation_status != "valid":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_VALIDATION_FAILED,
                    step_completed=step_completed,
                    input_context=input_context,
                    errors=errors,
                    warnings=warnings,
                )
            if max_step == "A":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    errors=errors,
                    warnings=warnings,
                )

            water_input_bundle = WaterInputAssemblyEngine(self.water_service).assemble(input_context)
            step_completed = "B"
            _extend_unique(warnings, water_input_bundle.warnings)

            if self._water_data_is_missing(water_input_bundle):
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_DATA_MISSING,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    errors=errors,
                    warnings=warnings,
                )
            if max_step == "B":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            if self.standards_service is None:
                _append_unique(errors, "A standards provider is required before Step C can run.")
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_FAILED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            use_case = input_context.normalized_input.get("use_case")
            pollutant_gap_bundle = PollutantGapEngine(self.standards_service).calculate(
                water_input_bundle,
                use_case=use_case,
            )
            step_completed = "C"
            _extend_unique(warnings, pollutant_gap_bundle.warnings)
            if max_step == "C":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            treatment_need_bundle = self.treatment_classifier.classify(pollutant_gap_bundle)
            step_completed = "D"
            _extend_unique(warnings, treatment_need_bundle.warnings)
            if max_step == "D":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            if self.nbs_provider is None:
                _append_unique(errors, "An NbS provider is required before Step E can run.")
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_FAILED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            candidate_filter_bundle = CandidateFilteringEngine(self.nbs_provider).filter_candidates(
                treatment_need_bundle,
            )
            step_completed = "E"
            _extend_unique(warnings, candidate_filter_bundle.warnings)

            if max_step == "E":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            mcda_matrix_bundle = McdaMatrixBuilder(self.nbs_provider).build(
                candidate_filter_bundle,
            )
            if matrix_transform is not None:
                mcda_matrix_bundle = matrix_transform(mcda_matrix_bundle)
            step_completed = "F"
            _extend_unique(warnings, mcda_matrix_bundle.warnings)
            if max_step == "F":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    mcda_matrix_bundle=mcda_matrix_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            normalized_mcda_matrix_bundle = McdaNormalizationEngine().normalize(
                mcda_matrix_bundle,
            )
            step_completed = "G"
            _extend_unique(warnings, normalized_mcda_matrix_bundle.warnings)
            if max_step == "G":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    mcda_matrix_bundle=mcda_matrix_bundle,
                    normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            mcda_weights_bundle = McdaWeightsHandler().prepare_from_normalized_bundle(
                normalized_mcda_matrix_bundle,
                supplied_weights=supplied_weights,
                weights_source=weights_source,
                expert_validated=expert_validated,
            )
            step_completed = "H"
            _extend_unique(warnings, mcda_weights_bundle.warnings)
            if max_step == "H":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    mcda_matrix_bundle=mcda_matrix_bundle,
                    normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                    mcda_weights_bundle=mcda_weights_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            topsis_ranking_bundle = TopsisRankingEngine().rank(
                normalized_mcda_matrix_bundle,
                mcda_weights_bundle,
            )
            step_completed = "I"
            _extend_unique(warnings, topsis_ranking_bundle.warnings)
            if max_step == "I":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    mcda_matrix_bundle=mcda_matrix_bundle,
                    normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                    mcda_weights_bundle=mcda_weights_bundle,
                    topsis_ranking_bundle=topsis_ranking_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            confidence_scoring_bundle = ConfidenceScoringEngine().score(
                topsis_ranking_bundle,
                water_bundle=water_input_bundle,
                candidate_bundle=candidate_filter_bundle,
                normalized_bundle=normalized_mcda_matrix_bundle,
                weights_bundle=mcda_weights_bundle,
            )
            step_completed = "J"
            _extend_unique(warnings, confidence_scoring_bundle.warnings)

            if max_step == "J":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    mcda_matrix_bundle=mcda_matrix_bundle,
                    normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                    mcda_weights_bundle=mcda_weights_bundle,
                    topsis_ranking_bundle=topsis_ranking_bundle,
                    confidence_scoring_bundle=confidence_scoring_bundle,
                    errors=errors,
                    warnings=warnings,
            )

            if self.plant_provider is None:
                _append_unique(
                    errors,
                    "A plant mapping provider is required before Step K can run.",
                )
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_FAILED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    mcda_matrix_bundle=mcda_matrix_bundle,
                    normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                    mcda_weights_bundle=mcda_weights_bundle,
                    topsis_ranking_bundle=topsis_ranking_bundle,
                    confidence_scoring_bundle=confidence_scoring_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            plant_matching_bundle = PlantMatchingEngine(
                self.plant_provider,
            ).match_plants(topsis_ranking_bundle, confidence_scoring_bundle)
            step_completed = "K"
            _extend_unique(warnings, plant_matching_bundle.warnings)

            if max_step == "K":
                return ScientificWorkflowResult(
                    workflow_status=WORKFLOW_COMPLETED,
                    step_completed=step_completed,
                    input_context=input_context,
                    water_input_bundle=water_input_bundle,
                    pollutant_gap_bundle=pollutant_gap_bundle,
                    treatment_need_bundle=treatment_need_bundle,
                    candidate_filter_bundle=candidate_filter_bundle,
                    mcda_matrix_bundle=mcda_matrix_bundle,
                    normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                    mcda_weights_bundle=mcda_weights_bundle,
                    topsis_ranking_bundle=topsis_ranking_bundle,
                    confidence_scoring_bundle=confidence_scoring_bundle,
                    plant_matching_bundle=plant_matching_bundle,
                    errors=errors,
                    warnings=warnings,
                )

            recommendation_assembly_bundle = RecommendationAssemblyEngine().assemble(
                topsis_ranking_bundle,
                confidence_scoring_bundle,
                plant_matching_bundle,
            )
            step_completed = "L"
            _extend_unique(warnings, recommendation_assembly_bundle.warnings)

            return ScientificWorkflowResult(
                workflow_status=WORKFLOW_COMPLETED,
                step_completed=step_completed,
                input_context=input_context,
                water_input_bundle=water_input_bundle,
                pollutant_gap_bundle=pollutant_gap_bundle,
                treatment_need_bundle=treatment_need_bundle,
                candidate_filter_bundle=candidate_filter_bundle,
                mcda_matrix_bundle=mcda_matrix_bundle,
                normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                mcda_weights_bundle=mcda_weights_bundle,
                topsis_ranking_bundle=topsis_ranking_bundle,
                confidence_scoring_bundle=confidence_scoring_bundle,
                plant_matching_bundle=plant_matching_bundle,
                recommendation_assembly_bundle=recommendation_assembly_bundle,
                errors=errors,
                warnings=warnings,
            )
        except Exception as exc:  # pragma: no cover - defensive workflow boundary
            _append_unique(errors, f"Scientific workflow failed: {exc}")
            return ScientificWorkflowResult(
                workflow_status=WORKFLOW_FAILED,
                step_completed=step_completed,
                input_context=input_context,
                water_input_bundle=water_input_bundle,
                pollutant_gap_bundle=pollutant_gap_bundle,
                treatment_need_bundle=treatment_need_bundle,
                candidate_filter_bundle=candidate_filter_bundle,
                mcda_matrix_bundle=mcda_matrix_bundle,
                normalized_mcda_matrix_bundle=normalized_mcda_matrix_bundle,
                mcda_weights_bundle=mcda_weights_bundle,
                topsis_ranking_bundle=topsis_ranking_bundle,
                confidence_scoring_bundle=confidence_scoring_bundle,
                plant_matching_bundle=plant_matching_bundle,
                recommendation_assembly_bundle=recommendation_assembly_bundle,
                errors=errors,
                warnings=warnings,
            )

    @staticmethod
    def _water_data_is_missing(bundle: WaterInputBundle) -> bool:
        """Return True when Step B found no observations to pass forward."""

        return bundle.selected_source_type == "missing" or bundle.observation_count == 0


def _normalize_max_step(max_step: str) -> str:
    """Normalize the requested workflow end step without guessing behavior."""

    return str(max_step or DEFAULT_WORKFLOW_END_STEP).strip().upper()

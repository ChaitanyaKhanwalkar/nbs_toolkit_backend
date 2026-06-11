"""Run Scientific Engine Steps A-E as one internal workflow.

This service is a backend-only coordinator. It calls the existing staged
engines in order and returns their intermediate bundles so future code can see
what happened at each step. It does not create final recommendations, API
routes, rankings, TOPSIS/AHP scores, plant choices, or health-risk labels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from app.engines import (
    CandidateFilterBundle,
    CandidateFilteringEngine,
    InputContext,
    InputNormalizationEngine,
    PollutantGapBundle,
    PollutantGapEngine,
    TreatmentNeedBundle,
    TreatmentNeedClassifier,
    WaterInputAssemblyEngine,
    WaterInputBundle,
)
from app.engines.candidate_filtering import NbsCandidateProvider
from app.engines.pollutant_gap import StandardsProvider
from app.engines.water_input_assembly import WaterObservationProvider


WORKFLOW_COMPLETED = "completed"
WORKFLOW_VALIDATION_FAILED = "validation_failed"
WORKFLOW_DATA_MISSING = "data_missing"
WORKFLOW_FAILED = "failed"


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
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


class ScientificWorkflowService:
    """Coordinate Steps A-E without exposing an endpoint or final decision.

    Pass fake providers in tests or real read-only services in application code.
    The service keeps each step separate so future development can inspect or
    replace one layer without changing the others.
    """

    def __init__(
        self,
        water_service: WaterObservationProvider | None = None,
        standards_service: StandardsProvider | None = None,
        nbs_provider: NbsCandidateProvider | None = None,
        input_engine: InputNormalizationEngine | None = None,
        treatment_classifier: TreatmentNeedClassifier | None = None,
    ) -> None:
        self.water_service = water_service
        self.standards_service = standards_service
        self.nbs_provider = nbs_provider
        self.input_engine = input_engine or InputNormalizationEngine()
        self.treatment_classifier = treatment_classifier or TreatmentNeedClassifier()

    @classmethod
    def from_session(cls, session: Any) -> "ScientificWorkflowService":
        """Build the workflow with existing read-only services for one session."""

        from app.services.nbs_catalog_service import NbsCatalogService
        from app.services.standards_service import StandardsService
        from app.services.water_data_service import WaterDataService

        return cls(
            water_service=WaterDataService(session),
            standards_service=StandardsService(session),
            nbs_provider=NbsCatalogService(session),
        )

    def run(self, raw_input: Mapping[str, Any] | None = None, **fields: Any) -> ScientificWorkflowResult:
        """Run Steps A-E and return the staged bundles produced along the way."""

        errors: list[str] = []
        warnings: list[str] = []
        step_completed: str | None = None
        input_context: InputContext | None = None
        water_input_bundle: WaterInputBundle | None = None
        pollutant_gap_bundle: PollutantGapBundle | None = None
        treatment_need_bundle: TreatmentNeedBundle | None = None
        candidate_filter_bundle: CandidateFilterBundle | None = None

        try:
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

            treatment_need_bundle = self.treatment_classifier.classify(pollutant_gap_bundle)
            step_completed = "D"
            _extend_unique(warnings, treatment_need_bundle.warnings)

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
                errors=errors,
                warnings=warnings,
            )

    @staticmethod
    def _water_data_is_missing(bundle: WaterInputBundle) -> bool:
        """Return True when Step B found no observations to pass forward."""

        return bundle.selected_source_type == "missing" or bundle.observation_count == 0

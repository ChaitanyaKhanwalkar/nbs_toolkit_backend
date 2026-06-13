"""Step A engine for validating the selected target standards use case.

This module confirms that a user-supplied use case exists in the standards
service. It does not choose defaults, compare observations with standards, or
calculate pollutant gaps.
"""

from dataclasses import replace
from typing import Any, Protocol

from app.engines.input_normalization import InputContext, normalize_match_key


class UseCaseProvider(Protocol):
    """Small service interface needed for target use-case validation."""

    def list_use_cases(self) -> list[str]:
        """Return available target use cases exactly as stored."""


class TargetUseCaseValidator:
    """Validate a normalized use case against stored standards use cases."""

    def __init__(self, standards_service: UseCaseProvider) -> None:
        self.standards_service = standards_service

    @classmethod
    def from_session(cls, session: Any) -> "TargetUseCaseValidator":
        """Create the validator using the production StandardsService layer."""

        from app.services import StandardsService

        return cls(StandardsService(session))

    def validate(self, context: InputContext) -> InputContext:
        """Attach target-use-case validation results to an InputContext."""

        available_use_cases = self.standards_service.list_use_cases()
        available_match_keys = {
            normalize_match_key(use_case): use_case for use_case in available_use_cases
        }

        errors = list(context.errors)
        missing_inputs = list(context.missing_inputs)
        normalized_input = dict(context.normalized_input)
        selected_use_case = normalized_input.get("use_case")

        if not selected_use_case:
            if "use_case" not in missing_inputs:
                missing_inputs.append("use_case")
            if "use_case is required." not in errors:
                errors.append("use_case is required.")
        elif selected_use_case not in available_match_keys:
            errors.append(
                "Unknown use_case. Select one of the available use cases exactly "
                "or with only transparent whitespace/case normalization."
            )
        else:
            normalized_input["use_case"] = available_match_keys[selected_use_case]
            normalized_input["use_case_match_key"] = selected_use_case

        return replace(
            context,
            normalized_input=normalized_input,
            validation_status="valid" if not errors else "invalid",
            errors=errors,
            missing_inputs=missing_inputs,
            available_use_cases=available_use_cases,
        )

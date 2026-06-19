"""Tests for A0 applicability filtering before TOPSIS.

These tests use tiny canonical-shaped rule rows. They confirm that placement
and safety rules can reject or caveat NbS options without hardcoding rule
thresholds inside the recommendation workflow.
"""

from app.engines.applicability_filter import (
    APPLICABILITY_CONDITIONAL,
    APPLICABILITY_REJECTED,
    ApplicabilityFilterEngine,
)
from app.engines.candidate_filtering import (
    ELIGIBLE,
    INELIGIBLE,
    CandidateFilterBundle,
    CandidateFilterResult,
)
from app.engines.input_normalization import InputNormalizationEngine


def _bundle(candidate: CandidateFilterResult) -> CandidateFilterBundle:
    """Return a minimal Step E bundle containing one candidate."""

    return CandidateFilterBundle(
        use_case="drinking",
        selected_source_type="user_measured",
        treatment_need_groups=["pathogens"],
        candidate_count=1,
        eligible_count=1,
        ineligible_count=0,
        data_pending_count=0,
        results=[candidate],
    )


def test_high_stream_order_blocks_in_channel_constructed_wetland() -> None:
    """High-order in-channel wetland rejection must come from DB-like rules."""

    candidate = CandidateFilterResult(
        nbs_id=1,
        nbs_name="Free Water Surface Wetland (FWS)",
        eligibility_status=ELIGIBLE,
        nbs_family="Constructed Wetlands",
        nbs_family_id=3,
    )
    input_context = InputNormalizationEngine().normalize(
        {
            "use_case": "drinking",
            "measured_observations": [
                {"parameter": "BOD", "value": 20, "unit": "mg/L"}
            ],
            "context": {"intervention_position": "in_channel"},
        }
    )
    rules = [
        {
            "rule_id": "APP_RULE_001",
            "target_level": "family",
            "nbs_family": "Constructed Wetlands",
            "factor_name": "stream_order",
            "intervention_position": "in_channel",
            "operator": ">=",
            "value_min": 5,
            "rule_type": "hard_filter",
            "severity": "critical",
            "action": "do_not_recommend_in_channel",
            "user_message": "Not suitable inside a high-order/mainstem river channel.",
            "technical_reason": "High-order rivers are not controllable treatment units.",
        }
    ]

    applicability, filtered = ApplicabilityFilterEngine().apply(
        _bundle(candidate),
        input_context=input_context,
        site_context={"stream_order": 6},
        rules=rules,
    )

    assert applicability.rejected_count == 1
    assert applicability.results[0].applicability_status == APPLICABILITY_REJECTED
    assert filtered.results[0].eligibility_status == INELIGIBLE
    assert "high-order" in filtered.results[0].exclusion_reasons[0]


def test_industrial_source_adds_pretreatment_caveat() -> None:
    """Industrial context should trigger conditional pretreatment messaging."""

    candidate = CandidateFilterResult(
        nbs_id=2,
        nbs_name="Horizontal Subsurface Flow Wetland (HSSF)",
        eligibility_status=ELIGIBLE,
        nbs_family="Constructed Wetlands",
        nbs_family_id=3,
    )
    input_context = InputNormalizationEngine().normalize(
        {
            "use_case": "discharge_inland",
            "measured_observations": [
                {"parameter": "COD", "value": 100, "unit": "mg/L"}
            ],
            "context": {
                "pollution_source_type": "industrial_or_mixed_industrial",
            },
        }
    )
    rules = [
        {
            "rule_id": "APP_RULE_INDUSTRIAL",
            "target_level": "family",
            "nbs_family": "Constructed Wetlands",
            "factor_name": "pollution_source_type",
            "category_value": "industrial_or_mixed_industrial",
            "rule_type": "conditional_allow",
            "severity": "high",
            "action": "allow_only_after_pretreatment",
            "score_modifier": -0.2,
            "confidence_modifier": -0.1,
            "user_message": "Use only after ETP/CETP pretreatment.",
            "technical_reason": "Industrial wastewater requires pretreatment before NbS polishing.",
        }
    ]

    applicability, filtered = ApplicabilityFilterEngine().apply(
        _bundle(candidate),
        input_context=input_context,
        rules=rules,
    )

    assert applicability.conditional_count == 1
    assert applicability.results[0].applicability_status == APPLICABILITY_CONDITIONAL
    assert applicability.results[0].score_modifier_total == -0.2
    assert applicability.results[0].confidence_modifier_total == -0.1
    assert filtered.results[0].eligibility_status == ELIGIBLE
    assert "pretreatment" in filtered.results[0].caution_flags[0].lower()

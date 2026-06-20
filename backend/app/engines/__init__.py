"""Scientific engine modules for staged recommendation workflow work."""

from app.engines.input_normalization import (
    DATA_PRIORITY_NOTE,
    InputContext,
    InputNormalizationEngine,
    normalize_match_key,
    normalize_text,
)
from app.engines.candidate_filtering import (
    CandidateFilterBundle,
    CandidateFilteringEngine,
    CandidateFilterResult,
)
from app.engines.applicability_filter import (
    ApplicabilityFilterBundle,
    ApplicabilityFilterEngine,
    CandidateApplicabilityResult,
    ApplicabilityRuleHit,
)
from app.engines.confidence_scoring import (
    CandidateConfidenceResult,
    ConfidenceFactor,
    ConfidenceScoringBundle,
    ConfidenceScoringEngine,
)
from app.engines.component_recommendation import IndividualNbsRecommendationEngine
from app.engines.design_readiness import DesignReadinessEngine
from app.engines.scenario_comparison import ScenarioComparisonEngine
from app.engines.sizing_estimator import SizingEstimator
from app.engines.mcda_matrix import (
    McdaMatrixBuilder,
    McdaMatrixBundle,
    McdaMatrixRow,
)
from app.engines.mcda_normalization import (
    McdaNormalizationEngine,
    NormalizedMcdaCriterion,
    NormalizedMcdaMatrixBundle,
    NormalizedMcdaMatrixRow,
)
from app.engines.mcda_numeric_projection import McdaNumericProjectionEngine
from app.engines.evidence_strength import (
    EvidenceStrengthResult,
    compute_evidence_strength,
)
from app.engines.footprint_feasibility import (
    FootprintFeasibilityResult,
    compute_footprint_requirement,
)
from app.engines.hydrological_suitability import (
    HydrologicalSuitabilityResult,
    compute_hydrological_suitability,
)
from app.engines.om_simplicity import (
    OmSimplicityResult,
    compute_om_simplicity,
)
from app.engines.pollution_source_fit import (
    PollutionSourceFitResult,
    compute_pollution_source_fit,
)
from app.engines.site_suitability import (
    SiteSuitabilityResult,
    classify_family,
    compute_site_suitability,
)
from app.engines.mcda_weights import (
    McdaWeightsBundle,
    McdaWeightsHandler,
)
from app.engines.plant_matching import (
    CandidatePlantMatches,
    PlantMatch,
    PlantMatchingBundle,
    PlantMatchingEngine,
)
from app.engines.pollutant_gap import (
    ParameterGapResult,
    PollutantGapBundle,
    PollutantGapEngine,
)
from app.engines.recommendation_assembly import (
    AssembledRecommendation,
    RecommendationAssemblyBundle,
    RecommendationAssemblyEngine,
    RecommendationEvidenceSummary,
)
from app.engines.target_validation import TargetUseCaseValidator
from app.engines.treatment_need import (
    TreatmentNeedBundle,
    TreatmentNeedClassifier,
    TreatmentNeedResult,
)
from app.engines.topsis_ranking import (
    TopsisCriterionContribution,
    TopsisRankedCandidate,
    TopsisRankingBundle,
    TopsisRankingEngine,
)
from app.engines.water_input_assembly import (
    SOURCE_PRIORITY,
    WaterInputAssemblyEngine,
    WaterInputBundle,
)

__all__ = [
    "DATA_PRIORITY_NOTE",
    "CandidateFilterBundle",
    "CandidateFilteringEngine",
    "CandidateFilterResult",
    "ApplicabilityFilterBundle",
    "ApplicabilityFilterEngine",
    "CandidateApplicabilityResult",
    "ApplicabilityRuleHit",
    "CandidateConfidenceResult",
    "ConfidenceFactor",
    "ConfidenceScoringBundle",
    "ConfidenceScoringEngine",
    "IndividualNbsRecommendationEngine",
    "DesignReadinessEngine",
    "ScenarioComparisonEngine",
    "SizingEstimator",
    "InputContext",
    "InputNormalizationEngine",
    "McdaMatrixBuilder",
    "McdaMatrixBundle",
    "McdaMatrixRow",
    "McdaNormalizationEngine",
    "McdaNumericProjectionEngine",
    "EvidenceStrengthResult",
    "compute_evidence_strength",
    "FootprintFeasibilityResult",
    "compute_footprint_requirement",
    "HydrologicalSuitabilityResult",
    "compute_hydrological_suitability",
    "OmSimplicityResult",
    "compute_om_simplicity",
    "PollutionSourceFitResult",
    "compute_pollution_source_fit",
    "SiteSuitabilityResult",
    "classify_family",
    "compute_site_suitability",
    "McdaWeightsBundle",
    "McdaWeightsHandler",
    "NormalizedMcdaCriterion",
    "NormalizedMcdaMatrixBundle",
    "NormalizedMcdaMatrixRow",
    "ParameterGapResult",
    "CandidatePlantMatches",
    "PlantMatch",
    "PlantMatchingBundle",
    "PlantMatchingEngine",
    "PollutantGapBundle",
    "PollutantGapEngine",
    "AssembledRecommendation",
    "RecommendationAssemblyBundle",
    "RecommendationAssemblyEngine",
    "RecommendationEvidenceSummary",
    "TargetUseCaseValidator",
    "TreatmentNeedBundle",
    "TreatmentNeedClassifier",
    "TreatmentNeedResult",
    "TopsisCriterionContribution",
    "TopsisRankedCandidate",
    "TopsisRankingBundle",
    "TopsisRankingEngine",
    "SOURCE_PRIORITY",
    "WaterInputAssemblyEngine",
    "WaterInputBundle",
    "normalize_match_key",
    "normalize_text",
]

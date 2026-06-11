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
from app.engines.pollutant_gap import (
    ParameterGapResult,
    PollutantGapBundle,
    PollutantGapEngine,
)
from app.engines.target_validation import TargetUseCaseValidator
from app.engines.treatment_need import (
    TreatmentNeedBundle,
    TreatmentNeedClassifier,
    TreatmentNeedResult,
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
    "InputContext",
    "InputNormalizationEngine",
    "McdaMatrixBuilder",
    "McdaMatrixBundle",
    "McdaMatrixRow",
    "McdaNormalizationEngine",
    "NormalizedMcdaCriterion",
    "NormalizedMcdaMatrixBundle",
    "NormalizedMcdaMatrixRow",
    "ParameterGapResult",
    "PollutantGapBundle",
    "PollutantGapEngine",
    "TargetUseCaseValidator",
    "TreatmentNeedBundle",
    "TreatmentNeedClassifier",
    "TreatmentNeedResult",
    "SOURCE_PRIORITY",
    "WaterInputAssemblyEngine",
    "WaterInputBundle",
    "normalize_match_key",
    "normalize_text",
]

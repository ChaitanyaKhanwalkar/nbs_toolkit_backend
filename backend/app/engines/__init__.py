"""Scientific engine modules for staged recommendation workflow work."""

from app.engines.input_normalization import (
    DATA_PRIORITY_NOTE,
    InputContext,
    InputNormalizationEngine,
    normalize_match_key,
    normalize_text,
)
from app.engines.target_validation import TargetUseCaseValidator
from app.engines.water_input_assembly import (
    SOURCE_PRIORITY,
    WaterInputAssemblyEngine,
    WaterInputBundle,
)

__all__ = [
    "DATA_PRIORITY_NOTE",
    "InputContext",
    "InputNormalizationEngine",
    "TargetUseCaseValidator",
    "SOURCE_PRIORITY",
    "WaterInputAssemblyEngine",
    "WaterInputBundle",
    "normalize_match_key",
    "normalize_text",
]

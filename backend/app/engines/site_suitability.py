"""C3 engine for transparent NbS site-suitability scoring.

This module implements the MCDA criterion **C3 — Site suitability** from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` (section 12.3):

    site_suitability = average(soil_fit, slope_fit, climate_fit, land_cover_fit)

Each sub-score is **rule-based and documented here in code/config**, exactly as
the engine spec requires. The NbS catalogue does not yet carry sourced,
structured per-technology site requirements (the catalogue `soil_type` /
`location_suitability` fields are numeric codes), so the fit rules below are
**provisional, literature-informed defaults grouped by NbS family**. They are
NOT expert-validated. Every result is flagged
`provisional_not_expert_validated` and carries notes explaining the inputs used
and the inputs that were missing. No site values, removal efficiencies, AHP
weights, or health-risk scores are invented here.

The scorer is intentionally pure: it takes a plain NbS `option` dict and a plain
`site_context` dict (the resolved region + site attributes) so it can be tested
without a database. When a sub-score has no usable input it returns `None` and
is simply left out of the average rather than guessed as zero.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.engines.input_normalization import normalize_match_key


SITE_SUITABILITY_STATUS_PROVISIONAL = "provisional_not_expert_validated"
SITE_SUITABILITY_STATUS_DATA_PENDING = "data_pending"

PROVISIONAL_NOTE = (
    "C3 site_suitability uses provisional, family-based fit rules that are not "
    "expert-validated; treat as developmental, not final scientific validation."
)

# --- NbS family classification (transparent keyword tokens only) ------------
# The NbS row is classified by matching normalized tokens from its `family` and
# `solution` text. Subsurface systems are checked before surface systems so a
# "subsurface-flow wetland" is not misread as an open surface wetland.
FAMILY_CLASS_TOKENS: list[tuple[str, set[str]]] = [
    (
        "subsurface_wetland",
        {
            "subsurface",
            "hssf",
            "vssf",
            "hsf",
            "vsf",
            "reedbed",
            "reed",
            "gravel",
        },
    ),
    (
        "infiltration_based",
        {
            "infiltration",
            "soak",
            "soakaway",
            "recharge",
            "bioretention",
            "biofiltration",
            "raingarden",
            "bioswale",
            "percolation",
            "leach",
        },
    ),
    (
        "surface_water_wetland_pond",
        {
            "wetland",
            "pond",
            "lagoon",
            "fws",
            "stabilization",
            "stabilisation",
            "marsh",
            "polishing",
        },
    ),
    (
        "vegetated_buffer",
        {
            "buffer",
            "riparian",
            "strip",
            "vegetated",
            "grassed",
            "swale",
            "bund",
        },
    ),
]
FAMILY_CLASS_UNCLASSIFIED = "unclassified"

# Permeability levels used to compare site soil against family preference.
PERMEABILITY_LEVELS = {"high": 3, "medium": 2, "low": 1}

# --- Provisional per-family requirement profiles ----------------------------
# soil_pref: preferred soil permeability ("high"/"medium"/"low"/"any")
# slope_ideal_max_deg / slope_hard_max_deg: terrain tolerance (degrees)
# water_dependency: how much sustained water the system needs ("high"/"medium"/"low")
# land_cover_pref: preferred dominant land-cover context
DEFAULT_SITE_SUITABILITY_CONFIG: dict[str, dict[str, Any]] = {
    "surface_water_wetland_pond": {
        "soil_pref": "low",
        "slope_ideal_max_deg": 2.0,
        "slope_hard_max_deg": 8.0,
        "water_dependency": "high",
        "land_cover_pref": "any",
    },
    "subsurface_wetland": {
        "soil_pref": "any",
        "slope_ideal_max_deg": 3.0,
        "slope_hard_max_deg": 10.0,
        "water_dependency": "high",
        "land_cover_pref": "any",
    },
    "infiltration_based": {
        "soil_pref": "high",
        "slope_ideal_max_deg": 5.0,
        "slope_hard_max_deg": 15.0,
        "water_dependency": "low",
        "land_cover_pref": "builtup",
    },
    "vegetated_buffer": {
        "soil_pref": "medium",
        "slope_ideal_max_deg": 10.0,
        "slope_hard_max_deg": 25.0,
        "water_dependency": "medium",
        "land_cover_pref": "agriculture",
    },
}


@dataclass(slots=True)
class SiteSuitabilityResult:
    """C3 site-suitability score plus its transparent sub-score breakdown."""

    site_suitability: float | None
    soil_fit: float | None
    slope_fit: float | None
    climate_fit: float | None
    land_cover_fit: float | None
    family_class: str
    status: str
    used_site_fields: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for matrix rows, tests, or future APIs."""

        return asdict(self)


def compute_site_suitability(
    option: dict[str, Any] | None,
    site_context: dict[str, Any] | None,
    config: dict[str, dict[str, Any]] | None = None,
) -> SiteSuitabilityResult:
    """Score how suitable the resolved site is for one NbS option.

    Returns a `SiteSuitabilityResult` whose `site_suitability` is the mean of the
    sub-scores that could be computed from real site data. Missing inputs lower
    coverage but are never replaced with guessed values.
    """

    config = config or DEFAULT_SITE_SUITABILITY_CONFIG
    family_class = classify_family(option)
    site_context = site_context or {}

    notes: list[str] = [PROVISIONAL_NOTE]
    used_site_fields: list[str] = []
    missing_inputs: list[str] = []

    profile = config.get(family_class)
    if profile is None:
        notes.append(
            "NbS family was not matched to a provisional site-suitability "
            f"profile (family_class={family_class}); C3 left unscored."
        )
        return SiteSuitabilityResult(
            site_suitability=None,
            soil_fit=None,
            slope_fit=None,
            climate_fit=None,
            land_cover_fit=None,
            family_class=family_class,
            status=SITE_SUITABILITY_STATUS_DATA_PENDING,
            used_site_fields=used_site_fields,
            missing_inputs=["nbs_family_profile"],
            notes=notes,
        )

    soil_fit = _soil_fit(profile, site_context, used_site_fields, missing_inputs, notes)
    slope_fit = _slope_fit(profile, site_context, used_site_fields, missing_inputs, notes)
    climate_fit = _climate_fit(profile, site_context, used_site_fields, missing_inputs, notes)
    land_cover_fit = _land_cover_fit(
        profile, site_context, used_site_fields, missing_inputs, notes
    )

    available = [
        value
        for value in (soil_fit, slope_fit, climate_fit, land_cover_fit)
        if value is not None
    ]
    if not available:
        notes.append(
            "No site soil/slope/climate/land-cover inputs were available; C3 "
            "site_suitability left unscored."
        )
        status = SITE_SUITABILITY_STATUS_DATA_PENDING
        overall: float | None = None
    else:
        status = SITE_SUITABILITY_STATUS_PROVISIONAL
        overall = _clamp_01(sum(available) / len(available))

    return SiteSuitabilityResult(
        site_suitability=overall,
        soil_fit=soil_fit,
        slope_fit=slope_fit,
        climate_fit=climate_fit,
        land_cover_fit=land_cover_fit,
        family_class=family_class,
        status=status,
        used_site_fields=used_site_fields,
        missing_inputs=missing_inputs,
        notes=notes,
    )


def classify_family(option: dict[str, Any] | None) -> str:
    """Classify an NbS option into a transparent family class by keyword tokens."""

    if not isinstance(option, dict):
        return FAMILY_CLASS_UNCLASSIFIED
    tokens = _text_tokens(option.get("family")) | _text_tokens(option.get("solution"))
    for family_class, class_tokens in FAMILY_CLASS_TOKENS:
        if tokens & class_tokens:
            return family_class
    return FAMILY_CLASS_UNCLASSIFIED


# --- Sub-score rules --------------------------------------------------------


def _soil_fit(
    profile: dict[str, Any],
    site_context: dict[str, Any],
    used_site_fields: list[str],
    missing_inputs: list[str],
    notes: list[str],
) -> float | None:
    """Score site soil permeability against the family preference."""

    preference = profile.get("soil_pref", "any")
    level, source_field = _site_permeability_level(site_context)
    if level is None:
        missing_inputs.append("soil_permeability")
        return None

    used_site_fields.append(source_field)
    if preference == "any":
        notes.append(
            f"soil_fit neutral: family accepts any soil; site permeability "
            f"read as '{level}' from {source_field}."
        )
        return 0.7

    distance = abs(PERMEABILITY_LEVELS[preference] - PERMEABILITY_LEVELS[level])
    score = {0: 1.0, 1: 0.6, 2: 0.2}[distance]
    notes.append(
        f"soil_fit={score}: family prefers '{preference}' permeability; site "
        f"read as '{level}' from {source_field}."
    )
    return score


def _slope_fit(
    profile: dict[str, Any],
    site_context: dict[str, Any],
    used_site_fields: list[str],
    missing_inputs: list[str],
    notes: list[str],
) -> float | None:
    """Score site slope against the family ideal/hard slope thresholds (degrees)."""

    slope = _as_float(site_context.get("slope_mean"))
    if slope is None:
        slope = _as_float(site_context.get("slope_median"))
        if slope is not None:
            used_site_fields.append("slope_median")
    else:
        used_site_fields.append("slope_mean")
    if slope is None:
        missing_inputs.append("slope")
        return None

    ideal_max = float(profile["slope_ideal_max_deg"])
    hard_max = float(profile["slope_hard_max_deg"])
    if slope <= ideal_max:
        score = 1.0
    elif slope >= hard_max:
        score = 0.1
    else:
        score = 1.0 - 0.9 * (slope - ideal_max) / (hard_max - ideal_max)
    score = _clamp_01(score)
    notes.append(
        f"slope_fit={round(score, 3)}: site slope {slope} (deg) vs family "
        f"ideal<= {ideal_max}, hard<= {hard_max}."
    )
    return score


def _climate_fit(
    profile: dict[str, Any],
    site_context: dict[str, Any],
    used_site_fields: list[str],
    missing_inputs: list[str],
    notes: list[str],
) -> float | None:
    """Score site wetness against the family's sustained-water dependency."""

    wetness, source_field = _site_wetness_level(site_context)
    if wetness is None:
        missing_inputs.append("climate_wetness")
        return None

    used_site_fields.append(source_field)
    dependency = profile.get("water_dependency", "medium")
    table = {
        "high": {"wet": 1.0, "moderate": 0.6, "dry": 0.25},
        "medium": {"wet": 0.9, "moderate": 0.8, "dry": 0.5},
        "low": {"wet": 0.8, "moderate": 0.9, "dry": 0.8},
    }
    score = table.get(dependency, table["medium"])[wetness]
    notes.append(
        f"climate_fit={score}: family water-dependency '{dependency}' vs site "
        f"wetness '{wetness}' from {source_field}."
    )
    return score


def _land_cover_fit(
    profile: dict[str, Any],
    site_context: dict[str, Any],
    used_site_fields: list[str],
    missing_inputs: list[str],
    notes: list[str],
) -> float | None:
    """Score site dominant land cover against the family's preferred context."""

    cover, source_field = _site_dominant_cover(site_context)
    if cover is None:
        missing_inputs.append("land_cover")
        return None

    used_site_fields.append(source_field)
    preference = profile.get("land_cover_pref", "any")
    if preference == "any":
        notes.append(
            f"land_cover_fit neutral: family accepts any land cover; site cover "
            f"'{cover}' from {source_field}."
        )
        return 0.8

    score = 1.0 if cover == preference else (0.7 if cover == "mixed" else 0.4)
    notes.append(
        f"land_cover_fit={score}: family prefers '{preference}'; site cover "
        f"'{cover}' from {source_field}."
    )
    return score


# --- Site input readers (defensive, transparent) ----------------------------


def _site_permeability_level(site_context: dict[str, Any]) -> tuple[str | None, str]:
    """Read a high/medium/low permeability level from the best available field."""

    infiltration = normalize_match_key(site_context.get("infiltration_class"))
    if infiltration:
        if any(token in infiltration for token in ("very_low", "low", "impermeable", "poor")):
            return "low", "infiltration_class"
        if any(token in infiltration for token in ("high", "rapid", "well")):
            return "high", "infiltration_class"
        if any(token in infiltration for token in ("moderate", "medium")):
            return "medium", "infiltration_class"

    hsg = normalize_match_key(site_context.get("hydrologic_soil_group"))
    if hsg:
        first = hsg[0]
        if first == "a":
            return "high", "hydrologic_soil_group"
        if first == "b":
            return "medium", "hydrologic_soil_group"
        if first in ("c", "d"):
            return "low", "hydrologic_soil_group"

    soil_text = normalize_match_key(site_context.get("soil_type"))
    if soil_text:
        if any(token in soil_text for token in ("sand", "sandy", "gravel")):
            return "high", "soil_type"
        if any(token in soil_text for token in ("clay", "clayey")):
            return "low", "soil_type"
        if "loam" in soil_text or "silt" in soil_text:
            return "medium", "soil_type"

    sand = _as_float(site_context.get("sand_pct"))
    clay = _as_float(site_context.get("clay_pct"))
    if sand is not None and sand >= 60:
        return "high", "sand_pct"
    if clay is not None and clay >= 40:
        return "low", "clay_pct"
    if sand is not None or clay is not None:
        return "medium", "sand_pct" if sand is not None else "clay_pct"

    return None, ""


def _site_wetness_level(site_context: dict[str, Any]) -> tuple[str | None, str]:
    """Read a wet/moderate/dry wetness level from aridity, then rainfall."""

    aridity = _as_float(site_context.get("aridity_P_PET"))
    if aridity is not None:
        if aridity >= 0.65:
            return "wet", "aridity_P_PET"
        if aridity >= 0.2:
            return "moderate", "aridity_P_PET"
        return "dry", "aridity_P_PET"

    rainfall = _as_float(site_context.get("rainfall_mm_yr"))
    if rainfall is not None:
        if rainfall >= 1000:
            return "wet", "rainfall_mm_yr"
        if rainfall >= 500:
            return "moderate", "rainfall_mm_yr"
        return "dry", "rainfall_mm_yr"

    return None, ""


def _site_dominant_cover(site_context: dict[str, Any]) -> tuple[str | None, str]:
    """Read a dominant land-cover class from text, then from LULC fractions."""

    dom = normalize_match_key(site_context.get("dom_land_cover"))
    if dom:
        if any(token in dom for token in ("crop", "agri", "agriculture", "farm")):
            return "agriculture", "dom_land_cover"
        if any(token in dom for token in ("urban", "built", "builtup", "settlement")):
            return "builtup", "dom_land_cover"
        if any(token in dom for token in ("tree", "forest", "range", "grass", "shrub")):
            return "vegetation", "dom_land_cover"
        return "mixed", "dom_land_cover"

    fractions = {
        "agriculture": _as_float(site_context.get("agri_frac")),
        "builtup": _as_float(site_context.get("builtup_frac")),
        "vegetation": _max_float(
            site_context.get("trees_frac"),
            site_context.get("range_frac"),
        ),
    }
    present = {key: value for key, value in fractions.items() if value is not None}
    if not present:
        return None, ""
    dominant = max(present, key=present.get)
    if present[dominant] < 0.5:
        return "mixed", f"{dominant}_frac"
    return dominant, f"{dominant}_frac"


# --- Small helpers ----------------------------------------------------------


def _text_tokens(value: Any) -> set[str]:
    """Return transparent normalized tokens for an NbS text field."""

    key = normalize_match_key(value)
    if not key:
        return set()
    return {key, *key.split("_")}


def _as_float(value: Any) -> float | None:
    """Convert a scalar value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _max_float(*values: Any) -> float | None:
    """Return the largest float among values, or None when all are missing."""

    floats = [number for value in values for number in [_as_float(value)] if number is not None]
    return max(floats) if floats else None


def _clamp_01(value: float) -> float:
    """Clamp a score to the safe 0-1 range."""

    return max(0.0, min(1.0, value))

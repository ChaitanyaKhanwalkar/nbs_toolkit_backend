"""
Recommendation engine for NbS Toolkit.
Provides plant and NbS matching based on:
- state
- water type
- soil type
- fuzzy soil similarity
- fallback ranking

This is a pure-Python, database-agnostic module.
"""

import pandas as pd
from rapidfuzz.fuzz import ratio as fuzz_ratio


# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------

def _clean_dict(obj):
    """Remove Unnamed columns and sanitize NaN → None for JSON."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if k.lower().startswith("unnamed"):
                continue
            cleaned[k] = _clean_dict(v)
        return cleaned

    if isinstance(obj, list):
        return [_clean_dict(x) for x in obj]

    if isinstance(obj, float) and pd.isna(obj):
        return None

    if pd.isna(obj):
        return None

    return obj


def _lower(s):
    return str(s).strip().lower() if s is not None else ""


# ---------------------------------------------------------
# CORE MATCHING ENGINE
# ---------------------------------------------------------

def _retrieve_soil_type(merged_df, state_name):
    """Get soil type for the given state (fallback = Loamy)."""
    try:
        row = merged_df[merged_df["state_name"].str.lower() == state_name.lower()]
        if not row.empty:
            soil = row.iloc[0].get("soil_type")
            if soil:
                return str(soil)
    except Exception:
        pass
    return "Loamy"  # fallback


def _fuzzy_score(a, b):
    """Case-insensitive fuzzy score for soils."""
    return fuzz_ratio(str(a).lower(), str(b).lower())


def _rank_matches(df, state_name, water_type, soil_type):
    """
    Ranking logic:
    1. Perfect Match = state + water + soil
    2. State + Water
    3. Water only
    4. Fuzzy soil scoring
    5. Any (fallback)
    """

    results = []

    # Pre-normalize columns
    df["_state"] = df["state_name"].apply(_lower)
    df["_water"] = df["optimal_water_type"].apply(_lower)
    df["_soil"] = df.get("soil_type", "").apply(_lower)

    target_state = state_name.lower()
    target_water = water_type.lower()
    target_soil = soil_type.lower()

    # Perfect
    perfect = df[
        (df["_state"] == target_state) &
        (df["_water"] == target_water) &
        (df["_soil"] == target_soil)
    ]
    for _, row in perfect.iterrows():
        results.append((row, "Perfect"))

    # State + Water
    state_water = df[
        (df["_state"] == target_state) &
        (df["_water"] == target_water)
    ]
    for _, row in state_water.iterrows():
        if row not in [r[0] for r in results]:
            results.append((row, "State+Water"))

    # Water only
    water_only = df[df["_water"] == target_water]
    for _, row in water_only.iterrows():
        if row not in [r[0] for r in results]:
            results.append((row, "Water Only"))

    # Fuzzy soil
    fuzzy_candidates = df[~df.index.isin([r[0].name for r in results])]
    fuzzy_candidates["fuzzy_score"] = fuzzy_candidates["_soil"].apply(
        lambda x: _fuzzy_score(x, target_soil)
    )
    fuzzy_sorted = fuzzy_candidates.sort_values("fuzzy_score", ascending=False)

    for _, row in fuzzy_sorted.iterrows():
        results.append((row, "Fuzzy"))

    # Any fallback
    for _, row in df.iterrows():
        if row not in [r[0] for r in results]:
            results.append((row, "Any"))

    # Convert to list of dicts and keep top 5
    final = []
    for row, level in results[:5]:
        d = row.to_dict()
        d["match_level"] = level
        final.append(d)

    return final


# ---------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------

def get_recommendation_data(state_name: str, water_type: str, db):
    """
    Main entry point used by API endpoints.
    Loads DB → pandas → computes recommendations → returns safe JSON dict.
    """

    # --------- Load database tables ----------
    merged_df = pd.read_sql("SELECT * FROM merged_district_data", db.bind)
    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    nbs_df = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    impl_df = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)

    # --------- Soil type for state ----------
    soil_type = _retrieve_soil_type(merged_df, state_name)

    # --------- Match plants ----------
    plant_matches = _rank_matches(plant_df, state_name, water_type, soil_type)

    # --------- Match NBS ----------
    nbs_matches = _rank_matches(nbs_df, state_name, water_type, soil_type)

    # --------- Attach implementation ----------
    impl_dict = {
        int(row["id"]): row.to_dict()
        for _, row in impl_df.iterrows()
    }

    for item in nbs_matches:
        impl = impl_dict.get(item.get("id"))
        item["implementation"] = impl or {}

    # --------- Final structure ----------
    result = {
        "soil_type": soil_type,
        "plants": plant_matches,
        "nbs_options": nbs_matches,
    }

    return _clean_dict(result)

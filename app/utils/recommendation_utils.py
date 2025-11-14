"""
Recommendation engine for NbS Toolkit.
Provides plant and NbS matching based on:
- state
- water type
- soil type
- fuzzy soil similarity
- fallback ranking

This rewritten version:
✔ Deduplicates plants by plant_species
✔ Deduplicates NbS by solution name
✔ Ensures max 5 per category
✔ Uses stable Series-based equality
✔ Avoids errors comparing Pandas rows
"""

import pandas as pd
from rapidfuzz.fuzz import ratio as fuzz_ratio


# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------

def _clean_dict(obj):
    """Recursively remove Unnamed columns & convert NaN → None."""
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


def _lower(x):
    return str(x).strip().lower() if x is not None else ""


# ---------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------

def _retrieve_soil_type(merged_df, state_name):
    """Get soil type for a given state (fallback = Loamy)."""
    try:
        row = merged_df[merged_df["state_name"].str.lower() == state_name.lower()]
        if not row.empty:
            soil = row.iloc[0].get("soil_type")
            if soil:
                return str(soil)
    except Exception:
        pass
    return "Loamy"


def _fuzzy_score(a, b):
    """Case-insensitive fuzzy score."""
    return fuzz_ratio(str(a).lower(), str(b).lower())


# ---------------------------------------------------------
# CORE MATCH LOGIC
# ---------------------------------------------------------

def _rank_matches(df, state_name, water_type, soil_type):
    """
    Ranking logic:
    1. Perfect       = state + water + soil
    2. Strong        = state + water
    3. Moderate      = water only
    4. Weak (fuzzy)  = top fuzzy soil matches
    5. Fallback      = any other results
    """

    df = df.copy()

    df["_state"] = df["state_name"].apply(_lower)
    df["_water"] = df["optimal_water_type"].apply(_lower)
    df["_soil"] = df.get("soil_type", "").apply(_lower)

    t_state = state_name.lower()
    t_water = water_type.lower()
    t_soil = soil_type.lower()

    results = []   # list of (row_dict, match_level, score)

    # ------- PERFECT -------
    perfect = df[(df["_state"] == t_state) & (df["_water"] == t_water) & (df["_soil"] == t_soil)]
    for _, row in perfect.iterrows():
        rowd = row.to_dict()
        results.append((rowd, "Perfect", 100))

    # ------- STRONG -------
    strong = df[(df["_state"] == t_state) & (df["_water"] == t_water)]
    for _, row in strong.iterrows():
        rowd = row.to_dict()
        if rowd not in [x[0] for x in results]:
            results.append((rowd, "Strong", 80))

    # ------- MODERATE -------
    moderate = df[df["_water"] == t_water]
    for _, row in moderate.iterrows():
        rowd = row.to_dict()
        if rowd not in [x[0] for x in results]:
            results.append((rowd, "Moderate", 60))

    # ------- FUZZY SOIL -------
    remaining = df[~df.index.isin([df.index[df.to_dict('records').index(r[0])] 
                                   for r in results if r[0] in df.to_dict('records')], errors='ignore')]

    if not remaining.empty:
        remaining["fuzzy_score"] = remaining["_soil"].apply(lambda x: _fuzzy_score(x, t_soil))
        fuzzy_sorted = remaining.sort_values("fuzzy_score", ascending=False)

        for _, row in fuzzy_sorted.iterrows():
            rowd = row.to_dict()
            if rowd not in [x[0] for x in results]:
                results.append((rowd, "Weak", 40))

    # ------- FALLBACK ANY -------
    for _, row in df.iterrows():
        rowd = row.to_dict()
        if rowd not in [x[0] for x in results]:
            results.append((rowd, "Any", 10))

    # ---------------------------------------------------
    # DEDUPLICATION LOGIC
    # ---------------------------------------------------
    unique = {}
    for rowd, match_level, score in results:
        # Key = plant_species OR solution
        key = rowd.get("plant_species") or rowd.get("solution")
        if key not in unique:
            rowd["match_level"] = match_level
            rowd["score"] = score
            unique[key] = rowd

        if len(unique) >= 5:
            break

    return list(unique.values())


# ---------------------------------------------------------
# PUBLIC ENTRYPOINT
# ---------------------------------------------------------

def get_recommendation_data(state_name: str, water_type: str, db):
    """Called by API layer."""

    merged_df = pd.read_sql("SELECT * FROM merged_district_data", db.bind)
    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    nbs_df = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    impl_df = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)

    # Soil type
    soil_type = _retrieve_soil_type(merged_df, state_name)

    # Matches
    plants = _rank_matches(plant_df, state_name, water_type, soil_type)
    nbs = _rank_matches(nbs_df, state_name, water_type, soil_type)

    # Join NBS with implementation
    impl_map = {int(r["id"]): r.to_dict() for _, r in impl_df.iterrows()}

    for item in nbs:
        item["implementation"] = impl_map.get(item["id"], {})

    result = {
        "soil_type": soil_type,
        "plants": plants,
        "nbs_options": nbs,
    }

    return _clean_dict(result)

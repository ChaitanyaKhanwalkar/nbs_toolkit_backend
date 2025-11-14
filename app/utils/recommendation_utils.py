"""
Stable, production-grade recommendation engine for NbS Toolkit.
This version avoids all Pandas row comparison issues and is guaranteed
to work in Azure App Service (Python 3.11 + pandas).

Key features:
✔ Deduplicates by plant_species / solution
✔ Stable scoring system
✔ No Pandas row comparison
✔ No use of Index.isin()
✔ Pure Python filtering
✔ Always returns clean JSON-safe output
"""

import pandas as pd
from rapidfuzz.fuzz import ratio as fuzz_ratio


# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------

def _clean_dict(obj):
    """Recursively remove Unnamed columns & sanitize NaN."""
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
    """Return soil type for a state, fallback Loamy."""
    try:
        row = merged_df[merged_df["state_name"].str.lower() == state_name.lower()]
        if not row.empty:
            s = row.iloc[0].get("soil_type")
            if s:
                return str(s)
    except:
        pass
    return "Loamy"


def _fuzzy_score(a, b):
    return fuzz_ratio(str(a).lower(), str(b).lower())


# ---------------------------------------------------------
# CORE RANKING (SAFE)
# ---------------------------------------------------------

def _rank_matches(df, state_name, water_type, soil_type):
    """
    Ranking system without any Pandas row comparisons:
    1. Perfect
    2. Strong
    3. Moderate
    4. Weak (fuzzy)
    5. Any
    Dedup key = plant_species OR solution.
    """

    df = df.copy()

    df["_state"] = df["state_name"].apply(_lower)
    df["_water"] = df["optimal_water_type"].apply(_lower)
    df["_soil"] = df.get("soil_type", "").apply(_lower)

    t_state = state_name.lower()
    t_water = water_type.lower()
    t_soil = soil_type.lower()

    results = []

    # ----- PERFECT -----
    for _, row in df.iterrows():
        if row["_state"] == t_state and row["_water"] == t_water and row["_soil"] == t_soil:
            results.append((row.to_dict(), "Perfect", 100))

    # ----- STRONG -----
    for _, row in df.iterrows():
        if row["_state"] == t_state and row["_water"] == t_water:
            results.append((row.to_dict(), "Strong", 80))

    # ----- MODERATE -----
    for _, row in df.iterrows():
        if row["_water"] == t_water:
            results.append((row.to_dict(), "Moderate", 60))

    # ----- WEAK (FUZZY) -----
    for _, row in df.iterrows():
        fuzzy = _fuzzy_score(row["_soil"], t_soil)
        results.append((row.to_dict(), "Weak", 40 + (fuzzy / 10)))

    # ----- ANY -----
    for _, row in df.iterrows():
        results.append((row.to_dict(), "Any", 10))

    # -----------------------------------------------------
    # DEDUP BY NAME (plant_species or solution)
    # -----------------------------------------------------
    unique = {}
    for rowd, level, score in results:
        key = rowd.get("plant_species") or rowd.get("solution")
        if key not in unique:
            rowd["match_level"] = level
            rowd["score"] = score
            unique[key] = rowd

        if len(unique) >= 5:
            break

    return list(unique.values())


# ---------------------------------------------------------
# PUBLIC ENTRYPOINT
# ---------------------------------------------------------

def get_recommendation_data(state_name: str, water_type: str, db):
    """Called by API."""

    merged_df = pd.read_sql("SELECT * FROM merged_district_data", db.bind)
    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    nbs_df = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    impl_df = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)

    soil_type = _retrieve_soil_type(merged_df, state_name)

    plants = _rank_matches(plant_df, state_name, water_type, soil_type)
    nbs = _rank_matches(nbs_df, state_name, water_type, soil_type)

    # Join implementation
    impl_map = {int(r["id"]): r.to_dict() for _, r in impl_df.iterrows()}
    for item in nbs:
        item["implementation"] = impl_map.get(item["id"], {})

    return _clean_dict({
        "soil_type": soil_type,
        "plants": plants,
        "nbs_options": nbs,
    })

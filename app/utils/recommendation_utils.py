"""
Production-grade Recommendation Engine for NbS Toolkit
------------------------------------------------------
Rewritten using deterministic weighted scoring:

Score Weights:
- State match:              +50
- Water type match:         +50
- Soil exact match:         +25
- Soil fuzzy similarity:    +0–20 (RapidFuzz)
- Fallback penalty:         -10

Always returns:
- top 5 plants
- top 5 NbS options
- clean JSON-safe output
"""

import pandas as pd
from rapidfuzz.fuzz import ratio as fuzz_ratio


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _clean(obj):
    """Remove NaN, NaT, unnamed columns, keep JSON-safe values."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if str(k).lower().startswith("unnamed"):
                continue
            cleaned[k] = _clean(v)
        return cleaned

    if isinstance(obj, list):
        return [_clean(v) for v in obj]

    if isinstance(obj, float) and pd.isna(obj):
        return None

    if pd.isna(obj):
        return None

    return obj


def _lower(x):
    return str(x).strip().lower() if x is not None else ""


# ---------------------------------------------------------
# Retrieve Soil Type
# ---------------------------------------------------------

def _get_soil_type(merged_df, state_name):
    """Return soil type for state (fallback = Loamy)."""
    try:
        row = merged_df[merged_df["state_name"].str.lower() == state_name.lower()]
        if not row.empty:
            soil = row.iloc[0].get("soil_type")
            if soil:
                return str(soil)
    except:
        pass
    return "Loamy"


# ---------------------------------------------------------
# Scoring Function
# ---------------------------------------------------------

def _score_row(row, state_name, water_type, soil_type):
    """Compute weighted score for a plant or NbS option."""
    score = 0

    # Normalize values
    r_state = _lower(row.get("state_name"))
    r_water = _lower(row.get("optimal_water_type"))
    r_soil = _lower(row.get("soil_type"))
    t_state = _lower(state_name)
    t_water = _lower(water_type)
    t_soil  = _lower(soil_type)

    # State match
    if r_state == t_state:
        score += 50

    # Water match
    if r_water == t_water:
        score += 50

    # Soil exact match
    if r_soil == t_soil:
        score += 25

    # Fuzzy soil similarity (0–20)
    if r_soil:
        score += int(fuzz_ratio(r_soil, t_soil) * 0.2)

    # Apply fallback penalty for missing fundamentals
    if r_water != t_water and r_state != t_state:
        score -= 10

    return score


# ---------------------------------------------------------
# Generic Matcher
# ---------------------------------------------------------

def _match(df, state_name, water_type, soil_type):
    """Score and return top 5 matches sorted by score desc."""
    df = df.copy()

    scores = []
    for _, row in df.iterrows():
        s = _score_row(row, state_name, water_type, soil_type)
        scores.append(s)

    df["score"] = scores
    df = df.sort_values("score", ascending=False)

    # Keep top 5 only
    top = df.head(5)

    # Convert to list of dicts
    results = []
    for _, row in top.iterrows():
        d = row.to_dict()
        d["match_level"] = _interpret_match_level(d["score"])
        results.append(d)

    return results


def _interpret_match_level(score):
    """Human-friendly match label based on score."""
    if score >= 110:
        return "Perfect"
    if score >= 90:
        return "Strong"
    if score >= 70:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Weak"


# ---------------------------------------------------------
# Main API – Called by FastAPI endpoints
# ---------------------------------------------------------

def get_recommendation_data(state_name: str, water_type: str, db):
    """Main entry point to compute recommendations."""

    # ---- Load DB tables ----
    merged_df = pd.read_sql("SELECT * FROM merged_district_data", db.bind)
    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    nbs_df   = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    impl_df  = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)

    # ---- Resolve soil type ----
    soil_type = _get_soil_type(merged_df, state_name)

    # ---- Compute matches ----
    plants = _match(plant_df, state_name, water_type, soil_type)
    nbs    = _match(nbs_df, state_name, water_type, soil_type)

    # ---- Attach implementation ----
    impl_map = {
        int(r["id"]): r.to_dict()
        for _, r in impl_df.iterrows()
    }

    for item in nbs:
        impl = impl_map.get(item.get("id"))
        item["implementation"] = impl or {}

    # ---- Final Output ----
    result = {
        "soil_type": soil_type,
        "plants": plants,
        "nbs_options": nbs,
    }

    return _clean(result)

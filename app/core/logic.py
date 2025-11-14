# app/core/logic.py

"""
Core logic for water classification used in the NBS Toolkit.
Hosted in this file because classification affects multiple API modules.
"""

import pandas as pd


# ---------------------------------------------------------
# SAFE NUMERIC PARSER
# ---------------------------------------------------------

def _safe_number(val):
    """
    Converts values like:
      - '40-60'
      - '<30'
      - '>50'
      - None / NaN
    into a clean numeric float.
    We always pick the LOWEST value from ranges (“40-60” → 40)
    because classification rules use minimum thresholds.
    """
    if val is None:
        return 0

    try:
        text = str(val).strip().lower().replace("<", "").replace(">", "")
        if "-" in text:
            return float(text.split("-")[0])
        return float(text)
    except Exception:
        return 0


# ---------------------------------------------------------
# WATER TYPE CLASSIFICATION
# ---------------------------------------------------------

def classify_water_type(row: dict) -> str:
    """
    Classifies water quality using BOD, TSS, nitrate, phosphate.
    Based on your custom rules.

    Returns one of:
        - Grey Water
        - Brown Water
        - Black Water
        - Yellow Water
        - Unknown
    """

    bod = _safe_number(row.get("bod"))
    tss = _safe_number(row.get("tss"))
    nitrate = _safe_number(row.get("nitrate"))
    phosphate = _safe_number(row.get("phosphate"))

    # -----------------------------------------------------
    # YOUR CUSTOM CLASSIFICATION RULES
    # -----------------------------------------------------

    # Highly polluted (extreme levels)
    if nitrate > 1000 or phosphate > 100 or bod > 1000:
        return "Yellow Water"

    # Black Water (sewage-like)
    if bod >= 300 and tss >= 250 and nitrate >= 40:
        return "Black Water"

    # Brown Water (mixed organic + sediments)
    if 200 <= bod < 600 and tss >= 200 and 30 <= nitrate < 100:
        return "Brown Water"

    # Lightly polluted household water
    if bod < 300 and tss < 300 and nitrate < 30:
        return "Grey Water"

    return "Unknown"

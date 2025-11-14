"""
Water data upload + classification + recommendation endpoint.
Production-grade, ORM only, stable and safe.
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
import json
from datetime import datetime

from app.db.database import get_db
from app.db import models
from app.core.logic import classify_water_type
from app.utils.recommendation_utils import get_recommendation_data


router = APIRouter()


# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------

def read_uploaded_file(file: UploadFile) -> dict:
    """Reads a CSV or Excel file and returns the first row as a dict."""
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be a valid CSV or Excel file."
        )

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    row = df.iloc[0].to_dict()
    return row



# --------------------------------------------------------
# MAIN ENDPOINT
# --------------------------------------------------------

@router.post("/water-data")
async def upload_water_data(
    file: Optional[UploadFile] = File(None),
    state_name: Optional[str] = Form(None),
    preset_type: Optional[str] = Form(None),
    sample_source: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Processes user-uploaded water data or preset selection."""

    # Require state for recommendations
    if not state_name:
        raise HTTPException(
            status_code=400,
            detail="state_name is required to generate recommendations."
        )

    allowed_types = ["Grey Water", "Black Water", "Brown Water", "Yellow Water"]

    # --------------------------------------------------------
    # A) FILE UPLOAD FLOW
    # --------------------------------------------------------
    if file and file.filename:

        raw_data = read_uploaded_file(file)

        # classify using logic.py
        water_type = classify_water_type(raw_data)

        if water_type == "Unknown":
            raise HTTPException(
                status_code=400,
                detail="Could not classify water type from the uploaded data."
            )

        # Save record
        entry = models.WaterData(
            water_type=water_type,
            colour=raw_data.get("colour"),
            odour=raw_data.get("odour"),
            turbidity=None,   # file upload does not give structured numeric fields
            temperature=None,
            tss=None,
            ph=None,
            bod=None,
            cod=None,
            nitrate=None,
            phosphate=None,
            ammonia=None,
            chloride=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(entry)
        db.commit()

        # Fetch recommendations
        result = get_recommendation_data(state_name, water_type, db)

        # Safe return
        result.setdefault("plants", [])
        result.setdefault("nbs_options", [])
        result.setdefault("nbs_implementation", [])

        return {
            "classified_type": water_type,
            "recommendations": result
        }


    # --------------------------------------------------------
    # B) PRESET SELECTION FLOW
    # --------------------------------------------------------
    if preset_type:

        if preset_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"preset_type must be one of {allowed_types}"
            )

        # Save simple preset entry
        entry = models.WaterData(
            water_type=preset_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            sample_source=sample_source,
            notes=notes,
            raw_data=json.dumps({"preset_type": preset_type})
        )
        db.add(entry)
        db.commit()

        result = get_recommendation_data(state_name, preset_type, db)

        result.setdefault("plants", [])
        result.setdefault("nbs_options", [])
        result.setdefault("nbs_implementation", [])

        return {
            "classified_type": preset_type,
            "recommendations": result
        }


    # --------------------------------------------------------
    # C) NO FILE AND NO PRESET → REJECT
    # --------------------------------------------------------
    raise HTTPException(
        status_code=400,
        detail="Provide either a water data file or a preset_type."
    )

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from typing import Optional
from sqlalchemy.orm import Session
import pandas as pd
from app.db.database import SessionLocal
from app.db import models
from app.core.logic import classify_water_type
from app.utils.recommendation_utils import get_recommendation_data
from fastapi.responses import JSONResponse  # <-- ADD THIS LINE

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/water-data")
async def upload_water_data(
    file: Optional[UploadFile] = File(None),
    state_name: Optional[str] = Form(None),  # <-- Add state_name
    preset_type: Optional[str] = Form(None),
    sample_source: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    import json
    from datetime import datetime

    allowed_types = ["Grey Water", "Black Water", "Brown Water", "Yellow Water"]

    # --- Handle file upload (CSV/Excel) ---
    if file and hasattr(file, "filename") and file.filename:
        try:
            # Accept both .csv and Excel
            if file.filename.endswith(".csv"):
                data = pd.read_csv(file.file)
            else:
                data = pd.read_excel(file.file)
        except Exception:
            raise HTTPException(status_code=400, detail="Failed to read the file. Make sure it's a valid CSV or Excel.")
        if data.empty:
            raise HTTPException(status_code=400, detail="File appears empty.")
        row = data.iloc[0].to_dict()
        classified_type = classify_water_type(row)
        if classified_type == "Unknown":
            raise HTTPException(status_code=400, detail="Could not classify water type from the data.")

        # Save entry
        entry = models.WaterData(
            water_type=classified_type,
            sample_source=sample_source,
            sample_timestamp=datetime.now(),
            raw_data=json.dumps(row),
            notes=notes
        )
        db.add(entry)
        db.commit()

        # You MUST get a state for recommendations! If not provided, pick a default or ask user to add this to the app upload form.
        used_state = state_name or "Madhya Pradesh"
        # Always return safe structure, even if nothing found
        data = get_recommendation_data(used_state, classified_type, db)
        if not data or not isinstance(data, dict):
            return JSONResponse(content={"plants": [], "nbs_options": []})
        # fill empty keys if missing
        data.setdefault("plants", [])
        data.setdefault("nbs_options", [])
        return JSONResponse(content=data)

    # --- Handle preset selection ---
    elif preset_type:
        if preset_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"preset_type must be one of: {allowed_types}"
            )
        entry = models.WaterData(
            water_type=preset_type,
            sample_source=sample_source,
            sample_timestamp=datetime.now(),
            raw_data=json.dumps({"preset_type": preset_type}),
            notes=notes
        )
        db.add(entry)
        db.commit()
        used_state = state_name or "Madhya Pradesh"
        data = get_recommendation_data(used_state, preset_type, db)
        if not data or not isinstance(data, dict):
            return JSONResponse(content={"plants": [], "nbs_options": []})
        data.setdefault("plants", [])
        data.setdefault("nbs_options", [])
        return JSONResponse(content=data)
    else:
        return JSONResponse(content={"plants": [], "nbs_options": []})

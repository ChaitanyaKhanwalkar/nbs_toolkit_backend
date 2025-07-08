from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db import models
from schemas.models import UserLocationSchema
import pandas as pd
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to get the list of valid states for drop-down
@router.get("/states")
def get_states():
    df = pd.read_csv("data/district_data_new.csv")  # Or query from DB if preferred
    states = sorted(df['state_name'].unique())
    return {"states": states}

# Endpoint to record user location selection
@router.post("/location")
def submit_location(
    state_name: str = Form(...),
    state_raw_input: str = Form(None),
    location_source: str = Form("user_selected"),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    # Validate state
    df = pd.read_csv("data/district_data_new.csv")  # Or query DB for production
    valid_states = set(df['state_name'].unique())
    if state_name not in valid_states:
        raise HTTPException(status_code=400, detail="Invalid state selected")

    user_loc = models.UserLocation(
        state_name=state_name,
        state_raw_input=state_raw_input,
        location_source=location_source,
        timestamp=datetime.now(),
        notes=notes
    )
    db.add(user_loc)
    db.commit()
    return {
        "status": "State saved",
        "data": UserLocationSchema(
            state_name=state_name,
            state_raw_input=state_raw_input,
            location_source=location_source,
            notes=notes
        )
    }
# Location endpoint
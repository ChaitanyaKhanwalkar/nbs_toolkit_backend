from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db import models
import pandas as pd

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/recommendations")
def get_recommendations(
    state_name: str = Query(..., description="User's selected state"),
    water_type: str = Query(..., description="User's water type (classified or preset)"),
    db: Session = Depends(get_db)
):
    try:
        data = get_recommendation_data(state_name, water_type, db)
        if not data or not isinstance(data, dict):
            return JSONResponse(content={"plants": [], "nbs_options": []})
        data.setdefault("plants", [])
        data.setdefault("nbs_options", [])
        return JSONResponse(content=data)
    except Exception as e:
        import traceback
        print("ERROR in /recommendations:", e)
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
# Implementation plan endpoint

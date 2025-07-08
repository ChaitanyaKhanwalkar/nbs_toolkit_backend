from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
import pandas as pd
from utils.recommendation_utils import get_recommendation_data
from fastapi.responses import JSONResponse  # <-- ADD THIS LINE

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
    data = get_recommendation_data(state_name, water_type, db)
    # Always return non-null dict with required keys
    if not data or not isinstance(data, dict):
        return JSONResponse(content={"plants": [], "nbs_options": []})
    data.setdefault("plants", [])
    data.setdefault("nbs_options", [])
    return JSONResponse(content=data)

@router.get("/nbs_detail/{nbs_id}")
def get_nbs_detail(nbs_id: int, db: Session = Depends(get_db)):
    nbs_df = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    impl_df = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)
    nbs_row = nbs_df[nbs_df['id'] == nbs_id]
    if nbs_row.empty:
        raise HTTPException(status_code=404, detail="NBS option not found.")
    nbs_data = nbs_row.iloc[0].to_dict()
    impl_row = impl_df[impl_df['solution'] == nbs_data['solution']]
    if not impl_row.empty:
        nbs_data['implementation_steps'] = impl_row.iloc[0]['implementation_steps']
        nbs_data['maintenance_requirements'] = impl_row.iloc[0]['maintenance_requirements']
    else:
        nbs_data['implementation_steps'] = None
        nbs_data['maintenance_requirements'] = None
    return nbs_data

@router.get("/plant_detail/{plant_id}")
def get_plant_detail(plant_id: int, db: Session = Depends(get_db)):
    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    plant_row = plant_df[plant_df['id'] == plant_id]
    if plant_row.empty:
        raise HTTPException(status_code=404, detail="Plant not found.")
    return plant_row.iloc[0].to_dict()

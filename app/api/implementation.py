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

@router.get("/implementation")
def get_implementation(
    solution: str = Query(..., description="Name of the NbS/plant solution"),
    db: Session = Depends(get_db)
):
    # Load the nbs_implementation table (either via pandas or ORM)
    df = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)
    record = df[df['solution'].str.lower() == solution.lower()]

    if record.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No implementation plan found for solution '{solution}'."
        )

    record = record.iloc[0]
    # Split by comma and strip whitespace for clean UX
    steps = [step.strip() for step in str(record['implementation_steps']).split(',')]
    maintenance = [req.strip() for req in str(record['maintenance_requirements']).split(',')]

    return {
        "solution": record['solution'],
        "implementation_steps": steps,
        "maintenance_requirements": maintenance
    }
# Implementation plan endpoint

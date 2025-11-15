"""
Location endpoints for the NbS Toolkit.
Provides:
- List of states
- List of districts in a state
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models

router = APIRouter()


# ----------------------------------------
# GET ALL STATES
# ----------------------------------------

@router.get("/states")
def get_states(db: Session = Depends(get_db)):
    """
    Returns a sorted list of all unique states from the district_data table.
    """

    states = (
        db.query(models.District.state_name)
        .distinct()
        .order_by(models.District.state_name.asc())
        .all()
    )

    state_list = [s[0] for s in states]

    return {"states": state_list}


# ----------------------------------------
# GET DISTRICTS FOR A STATE
# ----------------------------------------

@router.get("/districts")
def get_districts(
    state_name: str = Query(..., description="State name"),
    db: Session = Depends(get_db)
):
    """
    Returns all districts for a given state.
    """

    rows = (
        db.query(models.District.district_name)
        .filter(models.District.state_name.ilike(state_name))
        .distinct()
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No districts found for state '{state_name}'."
        )

    districts = [r[0] for r in rows if r[0] is not None]

    return {
        "state": state_name,
        "districts": districts
    }

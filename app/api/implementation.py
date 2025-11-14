"""
Implementation details endpoint for NbS solutions.
Production-ready, ORM-based, fast.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models

router = APIRouter()


@router.get("/implementation")
def get_implementation(
    solution: str = Query(..., description="Exact name of the NbS solution"),
    db: Session = Depends(get_db)
):
    """
    Fetch implementation steps + maintenance details for a given solution.
    Case-insensitive search.
    """

    record = (
        db.query(models.NbsImplementation)
        .filter(models.NbsImplementation.solution.ilike(solution))
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No implementation plan found for solution '{solution}'."
        )

    # Split comma-separated strings into clean lists
    steps = []
    if record.implementation_steps:
        steps = [step.strip() for step in record.implementation_steps.split(",") if step.strip()]

    maintenance = []
    if record.maintenance_requirements:
        maintenance = [m.strip() for m in record.maintenance_requirements.split(",") if m.strip()]

    return {
        "solution": record.solution,
        "implementation_steps": steps,
        "maintenance_requirements": maintenance
    }

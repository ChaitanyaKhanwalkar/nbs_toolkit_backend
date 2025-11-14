"""
Recommendation endpoints for the NbS Toolkit.
Provides:
- Top recommended plants + NbS options
- Detailed views for specific plants or NbS options
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.utils.recommendation_utils import get_recommendation_data


router = APIRouter()


# ------------------------------------------------------
# MAIN RECOMMENDATION ENDPOINT
# ------------------------------------------------------

@router.get("/recommendations")
def get_recommendations(
    state_name: str = Query(..., description="User-selected state"),
    water_type: str = Query(..., description="Classified water type"),
    db: Session = Depends(get_db)
):
    """
    Returns a list of best-fitting plants and NbS options for the given state/water type.
    Uses the new ORM-based recommendation engine.
    """

    result = get_recommendation_data(state_name, water_type, db)

    # Always return safe empty structure
    if not result or not isinstance(result, dict):
        return {
            "soil_type": None,
            "plant_match_level": "None",
            "nbs_match_level": "None",
            "plants": [],
            "nbs_options": [],
            "nbs_implementation": []
        }

    # Guarantee keys exist
    result.setdefault("plants", [])
    result.setdefault("nbs_options", [])
    result.setdefault("nbs_implementation", [])

    return result



# ------------------------------------------------------
# GET DETAILED VIEW FOR A SINGLE NBS OPTION
# ------------------------------------------------------

@router.get("/nbs/{nbs_id}")
def get_nbs_detail(nbs_id: int, db: Session = Depends(get_db)):
    nbs = db.query(models.NbsOption).filter(models.NbsOption.id == nbs_id).first()

    if not nbs:
        raise HTTPException(status_code=404, detail="NBS option not found.")

    # Join with implementation
    impl = (
        db.query(models.NbsImplementation)
        .filter(models.NbsImplementation.solution == nbs.solution)
        .first()
    )

    return {
        "id": nbs.id,
        "solution": nbs.solution,
        "optimal_water_type": nbs.optimal_water_type,
        "location_suitability": nbs.location_suitability,
        "climate_suitability": nbs.climate_suitability,
        "soil_type": nbs.soil_type,
        "resource_requirements": nbs.resource_requirements,
        "notes": nbs.notes,
        "state_name": nbs.state_name,
        "implementation": {
            "implementation_steps": impl.implementation_steps if impl else None,
            "maintenance_requirements": impl.maintenance_requirements if impl else None
        }
    }




# ------------------------------------------------------
# GET DETAILED VIEW FOR A SINGLE PLANT OPTION
# ------------------------------------------------------

@router.get("/plant/{plant_id}")
def get_plant_detail(plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(models.PlantData).filter(models.PlantData.id == plant_id).first()

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found.")

    return {
        "id": plant.id,
        "plant_species": plant.plant_species,
        "climate_preference": plant.climate_preference,
        "water_needs": plant.water_needs,
        "ecological_role": plant.ecological_role,
        "soil_type": plant.soil_type,
        "locational_availability": plant.locational_availability,
        "pollution_tolerance": plant.pollution_tolerance,
        "state_name": plant.state_name,
        "optimal_water_type": plant.optimal_water_type,
    }

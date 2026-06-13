"""Read-only plant catalogue routes.

These endpoints return stored plants and plant-to-NbS mappings only. They do
not select final plant recommendations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import PlantResponse
from app.services import PlantCatalogService

router = APIRouter(prefix="/plants", tags=["plants"])


@router.get("", response_model=list[PlantResponse])
def list_plants(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all stored plant catalogue rows."""

    return PlantCatalogService(db).list_plants()


@router.get("/nbs/{nbs_id}", response_model=list[PlantResponse])
def get_plants_for_nbs(
    nbs_id: int,
    db: Annotated[Session, Depends(get_db)],
    include_invasive: Annotated[
        bool,
        Query(description="Include invasive plants in this raw catalogue lookup."),
    ] = False,
) -> list[dict[str, object]]:
    """Return plants mapped to one NbS option."""

    return PlantCatalogService(db).get_plants_for_nbs(
        nbs_id,
        include_invasive=include_invasive,
    )


@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant_profile(
    plant_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    """Return one stored plant profile."""

    plant = PlantCatalogService(db).get_plant_profile(plant_id)
    if plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant {plant_id} was not found.",
        )
    return plant

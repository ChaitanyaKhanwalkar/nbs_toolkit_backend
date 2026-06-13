"""Read-only reference data routes.

These endpoints return lookup-style data for future dropdowns and filters.
They do not choose standards, compare water quality, or make recommendations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    BasinResponse,
    ReferenceDataResponse,
    RegionResponse,
    SourceResponse,
    WaterStationResponse,
)
from app.services import ReferenceDataService

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("", response_model=ReferenceDataResponse)
def get_reference_data(db: Annotated[Session, Depends(get_db)]) -> dict[str, object]:
    """Return grouped raw reference data."""

    return ReferenceDataService(db).get_lookup_data()


@router.get("/basins", response_model=list[BasinResponse])
def list_basins(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all stored basin lookup rows."""

    return ReferenceDataService(db).list_basins()


@router.get("/regions", response_model=list[RegionResponse])
def list_regions(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all stored region lookup rows."""

    return ReferenceDataService(db).list_regions()


@router.get("/sources", response_model=list[SourceResponse])
def list_sources(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all stored provenance/source rows."""

    return ReferenceDataService(db).list_sources()


@router.get("/stations", response_model=list[WaterStationResponse])
def list_water_quality_stations(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return regions marked as water-quality stations."""

    return ReferenceDataService(db).list_available_water_quality_stations()


@router.get("/use-cases", response_model=list[str])
def list_standards_use_cases(db: Annotated[Session, Depends(get_db)]) -> list[str]:
    """Return standards use cases exactly as stored."""

    return ReferenceDataService(db).list_standards_use_cases()

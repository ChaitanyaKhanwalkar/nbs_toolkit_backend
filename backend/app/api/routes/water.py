"""Read-only water observation routes.

These endpoints return measured water-quality records and parameter counts.
They never compare observations with standards or calculate exceedance.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import WaterObservationResponse, WaterParameterSummaryResponse
from app.services import WaterDataService

router = APIRouter(prefix="/water", tags=["water"])


@router.get(
    "/stations/{station}/observations",
    response_model=list[WaterObservationResponse],
)
def get_station_observations(
    station: str,
    db: Annotated[Session, Depends(get_db)],
    parameter: Annotated[str | None, Query(description="Optional exact parameter name.")] = None,
) -> list[dict[str, object]]:
    """Return raw observations for one station, optionally for one parameter."""

    service = WaterDataService(db)
    if parameter:
        grouped = service.get_observations_for_parameters(station, [parameter])
        return grouped.get(parameter, [])
    return service.get_observations_by_station(station)


@router.get(
    "/basins/{basin_id}/observations",
    response_model=list[WaterObservationResponse],
)
def get_basin_observations(
    basin_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return raw observations for one basin ID."""

    return WaterDataService(db).get_observations_by_basin(basin_id)


@router.get("/parameters", response_model=list[WaterParameterSummaryResponse])
def list_water_parameters(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return stored water-quality parameter names and raw row counts."""

    return WaterDataService(db).summarize_available_parameters()

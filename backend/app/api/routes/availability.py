"""Read-only data availability routes.

This endpoint reports booleans, counts, inputs, and missing sections only. It
does not decide if a recommendation can or should be produced.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import DataAvailabilityResponse
from app.services import DataAvailabilityService

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get("", response_model=DataAvailabilityResponse)
def get_data_availability(
    db: Annotated[Session, Depends(get_db)],
    region_id: Annotated[int | None, Query()] = None,
    station: Annotated[str | None, Query()] = None,
    use_case: Annotated[str | None, Query()] = None,
    nbs_id: Annotated[int | None, Query()] = None,
) -> dict[str, object]:
    """Return raw availability booleans and counts for selected inputs."""

    return DataAvailabilityService(db).report_availability(
        region_id=region_id,
        station=station,
        use_case=use_case,
        nbs_id=nbs_id,
    )

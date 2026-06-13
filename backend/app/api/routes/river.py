"""Read-only river and stream context routes.

These endpoints return river network and station-stream data only. They do not
calculate hydrological risk or suitability scores.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RiverContextResponse, SiteStreamAttributesResponse
from app.services import RiverContextService

router = APIRouter(prefix="/river", tags=["river"])


@router.get("/stream-order/{stream_order}", response_model=RiverContextResponse)
def get_river_segments_by_stream_order(
    stream_order: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    """Return raw river segments for one stream order."""

    segments = RiverContextService(db).list_river_segments_by_stream_order(stream_order)
    return {
        "river_segments": segments,
        "count": len(segments),
        "missing_sections": [] if segments else ["river_segments"],
    }


@router.get("/sites/{region_id}", response_model=list[SiteStreamAttributesResponse])
def get_site_stream_context(
    region_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return raw stream attributes for one region."""

    return RiverContextService(db).get_stream_attributes(region_id=region_id)

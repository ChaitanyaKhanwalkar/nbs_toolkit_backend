"""Read-only pollution context routes.

These endpoints return raw pollution source records and simple grouped context.
They do not create pollution pressure scores.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import PollutionContextResponse
from app.services import PollutionContextService

router = APIRouter(prefix="/pollution", tags=["pollution"])


@router.get("/regions/{region_id}", response_model=PollutionContextResponse)
def get_pollution_context(
    region_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    """Return raw pollution context for one region."""

    service = PollutionContextService(db)
    sources = service.get_pollution_sources(region_id)
    grouped_context = service.get_grouped_pollution_context(region_id)
    return {
        "region_id": region_id,
        "pollution_sources": sources,
        "grouped_context": grouped_context,
        "missing_sections": [] if sources else ["pollution_sources"],
    }

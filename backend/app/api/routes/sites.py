"""Read-only site profile routes.

These endpoints return raw descriptive site data for a region. They do not
score suitability or hydrological risk.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import SiteProfileResponse
from app.services import SiteProfileService

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("/{region_id}", response_model=SiteProfileResponse)
def get_site_profile(
    region_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    """Return raw site profile data for one region ID."""

    profile = SiteProfileService(db).get_site_profile(region_id)
    if profile["region"] is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region {region_id} was not found.",
        )
    if profile["site_attributes"] is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site attributes for region {region_id} were not found.",
        )
    return profile

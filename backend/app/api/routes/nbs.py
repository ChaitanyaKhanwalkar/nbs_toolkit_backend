"""Read-only nature-based solution catalogue routes.

These endpoints return stored NbS option and profile records only. They do not
rank, filter, or recommend technologies.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import NbsFullProfileResponse, NbsOptionResponse
from app.services import NbsCatalogService

router = APIRouter(prefix="/nbs", tags=["nbs"])


@router.get("/options", response_model=list[NbsOptionResponse])
def list_nbs_options(db: Annotated[Session, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all stored NbS catalogue options."""

    return NbsCatalogService(db).list_options()


@router.get("/{nbs_id}", response_model=NbsFullProfileResponse)
def get_nbs_profile(
    nbs_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    """Return raw catalogue/profile data for one NbS option."""

    profile = NbsCatalogService(db).get_full_nbs_profile(nbs_id)
    if profile["option"] is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NbS option {nbs_id} was not found.",
        )
    return profile

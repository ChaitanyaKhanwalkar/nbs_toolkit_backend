"""Read-only canonical catalogues for the learning workspace."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.catalogue_service import CatalogueService

router = APIRouter(prefix="/catalogue", tags=["catalogue"])


@router.get("")
def get_learning_catalogue(
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    """Return treatment-train, NbS-component, and plant learning records."""

    return CatalogueService(db).get_catalogue()

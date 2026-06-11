"""Read-only standards lookup routes.

These endpoints return stored standards for explicit use cases and parameters.
They do not decide a default use case or evaluate compliance.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import StandardResponse
from app.services import StandardsService

router = APIRouter(prefix="/standards", tags=["standards"])


@router.get("/use-cases", response_model=list[str])
def list_use_cases(db: Annotated[Session, Depends(get_db)]) -> list[str]:
    """Return standards use cases exactly as stored."""

    return StandardsService(db).list_use_cases()


@router.get("/{use_case}", response_model=list[StandardResponse])
def get_standards_for_use_case(
    use_case: str,
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return raw standards rows for one explicit use case."""

    standards = StandardsService(db).get_standards_for_use_case(use_case)
    if not standards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No standards were found for use case '{use_case}'.",
        )
    return standards


@router.get("/{use_case}/{parameter}", response_model=StandardResponse)
def get_standard(
    use_case: str,
    parameter: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, object]:
    """Return one stored standard for a use case and parameter."""

    standard = StandardsService(db).get_standard(use_case, parameter)
    if standard is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No standard was found for '{parameter}' in '{use_case}'.",
        )
    return standard

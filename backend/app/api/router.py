"""Main API router for versioned read-only backend routes.

This file gathers the smaller route modules into one router that `main.py`
mounts under `/api/v1`.
"""

from fastapi import APIRouter

from app.api.routes import (
    availability,
    catalogue,
    nbs,
    plants,
    pollution,
    recommendation,
    reference,
    river,
    sites,
    standards,
    water,
)

api_router = APIRouter()

api_router.include_router(reference.router)
api_router.include_router(sites.router)
api_router.include_router(water.router)
api_router.include_router(standards.router)
api_router.include_router(nbs.router)
api_router.include_router(plants.router)
api_router.include_router(pollution.router)
api_router.include_router(river.router)
api_router.include_router(availability.router)
api_router.include_router(catalogue.router)
api_router.include_router(recommendation.router)

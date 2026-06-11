"""FastAPI application entry point for backend health checks.

This file creates the application and exposes only foundation health routes.
It intentionally does not implement recommendation logic, scoring engines,
or production deployment wiring.
"""

from fastapi import FastAPI, Response, status

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.health import check_database_connection

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a basic application health response."""

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/health/db")
def database_health(response: Response) -> dict[str, str]:
    """Return whether the configured database connection works."""

    result = check_database_connection()
    if result["status"] != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result

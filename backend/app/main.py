"""FastAPI application entry point for backend health checks and API routes.

This file creates the application, exposes foundation health routes, and mounts
versioned API routes under `/api/v1`. Scientific workflow logic lives in
services/engines; this file does not contain scoring logic or production
deployment wiring.
"""

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.health import check_database_connection

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)
# Allow the Flutter web client (random localhost port / Cloudflare tunnel) to
# call the API from the browser. No credentials are used, so "*" is safe here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


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


@app.get("/__version")
def deployment_version() -> dict[str, object]:
    """Diagnostic: prove which backend build/app Azure is actually serving.

    Exposes no secrets: DATABASE_URL is reported only as a boolean. Useful to
    distinguish this app (``Narmada NbS Backend`` v0.1.0, versioned ``/api/v1``
    routes) from any other app object a host might be serving by mistake.
    """

    paths = sorted(app.openapi()["paths"].keys())
    return {
        "app_name": settings.app_name,
        "app_version": app.version,
        "app_env": settings.app_env,
        "database_url_set": bool(settings.database_url),
        "route_count": len(paths),
        "first_20_routes": paths[:20],
    }

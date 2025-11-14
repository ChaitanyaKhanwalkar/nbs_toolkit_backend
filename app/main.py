# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_db
from app.api import (
    recommendations,
    water_data,
    implementation,
    location,
)

# ---------------------------------------------------------
# APPLICATION SETUP
# ---------------------------------------------------------

app = FastAPI(
    title="NBS Toolkit API",
    description="Backend API for the Nature-based Solutions Toolkit",
    version="1.0.0",
)

# ---------------------------------------------------------
# CORS SETTINGS (Front-end compatibility)
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change later to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# STARTUP EVENT — CREATE TABLES
# ---------------------------------------------------------

@app.on_event("startup")
def startup_event():
    """
    Runs once when the server boots.
    Ensures database tables exist.
    """
    print("📌 Initializing database...")
    init_db()
    print("✅ Database ready.")


# ---------------------------------------------------------
# ROUTES REGISTRATION
# ---------------------------------------------------------

app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(water_data.router, prefix="/api", tags=["Water Data"])
app.include_router(implementation.router, prefix="/api", tags=["Implementation"])
app.include_router(location.router, prefix="/api", tags=["Location"])


# ---------------------------------------------------------
# HEALTH CHECK ENDPOINT
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "NBS Toolkit API is running!"}


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to the NBS Toolkit API",
        "docs": "/docs",
        "health": "/api/health",
    }

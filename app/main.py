from fastapi import FastAPI
from app.db import models
from app.db.database import engine
from app.api import location, implementation, water_data, recommendations
import os

# Create FastAPI app
app = FastAPI()

# Include routers cleanly under /api/*
app.include_router(location.router, prefix="/api")
app.include_router(implementation.router, prefix="/api")
app.include_router(water_data.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")

# ---- Startup event ----
@app.on_event("startup")
def startup_event():
    """
    Production-safe startup:
    - Ensures tables exist
    - Does NOT auto-seed on Azure (already seeded manually)
    """
    print("📌 Initializing database (create tables if not exist)...")
    models.Base.metadata.create_all(bind=engine)
    print("✅ Database ready.")


@app.get("/health")
def health():
    """Health check endpoint for Azure."""
    return {"status": "ok"}

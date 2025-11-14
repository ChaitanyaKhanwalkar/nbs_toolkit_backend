from fastapi import FastAPI
from app.db.database import init_db
from app.db import models
from app.api import recommendations, location, water_data, implementation
import os

app = FastAPI(
    title="NBS Toolkit API",
    version="1.0.0",
    description="Production API for Nature-Based Solutions Toolkit"
)

@app.get("/health")
def health():
    return {"status": "ok"}

# Initialize DB ONCE — tables already created, this is safe
@app.on_event("startup")
def startup_event():
    print("🚀 Starting API service...")
    init_db()  # harmless if tables already exist
    print("✅ Database connected")

# Include all routers under /api/*
app.include_router(recommendations.router, prefix="/api/recommendations")
app.include_router(location.router, prefix="/api/location")
app.include_router(water_data.router, prefix="/api/water")
app.include_router(implementation.router, prefix="/api/implementation")

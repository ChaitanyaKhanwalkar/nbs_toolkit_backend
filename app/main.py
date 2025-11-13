from fastapi import FastAPI
<<<<<<< HEAD
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
=======
from db import models, database

import os

try:
    from seed_data import seed_data  # must match function name in seed_data.py
except Exception:
    seed_data = None  # handle missing import gracefully

SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.on_event("startup")
def on_startup():
    print("Startup: tables already created, skipping init_db()")

    # Only seed if the symbol exists AND the flag is on
    if SEED_ON_STARTUP and seed_data:
        try:
            print("📦 Seeding database from CSVs...")
            seed_data(DATABASE_URL)  # pass what your seeder expects
            print("✅ Seeding complete.")
        except Exception as e:
            # Keep the server booting, but log the reason clearly
            print(f"❌ Error seeding database: {e}")


>>>>>>> 97c2960d5dd99bc4f764f12fca88e35ed0149109

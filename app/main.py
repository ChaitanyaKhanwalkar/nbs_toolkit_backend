# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.api import implementation, location, recommendations, water_data

app = FastAPI(
    title="NBS Toolkit API",
    description="Nature-based Solutions Recommendation Backend",
    version="1.0.0"
)

# -----------------------------
# CORS (allow frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Startup: init tables
# -----------------------------
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

    if os.getenv("ENABLE_DB_SEEDING", "false").lower() == "true":
        from app.db.seed_data import seed_database
        seed_database()
# -----------------------------
# Health check
# -----------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "message": "NBS Toolkit API is running!"}

# -----------------------------
# ROUTER REGISTRATION
# -----------------------------
app.include_router(implementation.router, prefix="/api", tags=["Implementation"])
app.include_router(location.router, prefix="/api", tags=["Location"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(water_data.router, prefix="/api", tags=["Water Data"])

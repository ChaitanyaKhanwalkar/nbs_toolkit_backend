# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.db_connection import get_connection

from app.db.database import Base, engine
from app.api import implementation, location, recommendations, water_data

app = FastAPI(
    title="NBS Toolkit API",
    description="Nature-based Solutions Recommendation Backend",
    version="1.0.0"
)

@app.get("/api/test-db")
def test_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return {"status": "success", "timestamp": result}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# -----------------------------
# CORS (allow frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, you should restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Startup: init tables
# -----------------------------
@app.on_event("startup")
def startup_event():
    # This ensures that all tables defined in your SQLAlchemy models are created
    # in the database when the application starts.
    Base.metadata.create_all(bind=engine)

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

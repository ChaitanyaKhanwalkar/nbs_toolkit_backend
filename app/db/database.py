# app/db/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# -------------------------------------------------------
# DATABASE URL
# -------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

# Fix old URLs (Heroku-style)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# -------------------------------------------------------
# ENGINE & SESSION
# -------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # auto-reconnect dead connections
    pool_recycle=1800,      # recycle every 30 min (cloud best practice)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -------------------------------------------------------
# INIT DB
# -------------------------------------------------------

def init_db():
    """Create tables if they don’t exist. Safe to call multiple times."""
    Base.metadata.create_all(bind=engine)

# -------------------------------------------------------
# SESSION DEPENDENCY FOR ROUTES
# -------------------------------------------------------

def get_db():
    """FastAPI dependency to provide DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

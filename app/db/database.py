"""
Database engine + session factory for the NbS Toolkit.
Production-ready: connection pooling, clean dependency injection,
no unnecessary prints, fully modular.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base


# --------------------------------------------
# DATABASE URL (ENV VARIABLE)
# --------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Convert old-style format
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


# --------------------------------------------
# ENGINE
# --------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # Automatically reconnect dropped connections
    pool_recycle=1800,         # Recycle connections every 30 min
    future=True,               # Modern SQLAlchemy API
)


# --------------------------------------------
# SESSION FACTORY
# --------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True
)


# --------------------------------------------
# DB INITIALIZATION
# --------------------------------------------

def init_db():
    """Create all tables safely. Runs only when called."""
    Base.metadata.create_all(bind=engine)


# --------------------------------------------
# SESSION DEPENDENCY FOR FASTAPI
# --------------------------------------------

def get_db():
    """FastAPI dependency: open DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

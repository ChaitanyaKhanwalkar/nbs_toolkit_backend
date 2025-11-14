# app/db/__init__.py
"""
Database package initialization.
Ensures models and database engine are imported cleanly.
"""

from app.db.database import engine, SessionLocal, get_db, init_db
from app.db.models import Base

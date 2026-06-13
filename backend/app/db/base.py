"""Shared SQLAlchemy declarative base.

All ORM model classes inherit from `Base` so SQLAlchemy can collect their table
metadata in one place. This file does not create tables or connect to the
database by itself.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for future SQLAlchemy ORM models."""

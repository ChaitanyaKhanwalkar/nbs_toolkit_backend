"""
SQLAlchemy ORM models for the NbS Toolkit, aligned with the current schema.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Text, DateTime, func
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ============================
#      DISTRICT DATA
# ============================

class District(Base):
    __tablename__ = "district_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state_name = Column(Text)
    soil_type = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ============================
#        PLANT DATA
# ============================

class Plant(Base):
    __tablename__ = "plant_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_species = Column(Text)
    locational_availability = Column(Text)
    climate_preference = Column(Text)
    soil_type = Column(Text)
    water_needs = Column(Text)
    ecological_role = Column(Text)
    pollution_tolerance = Column(Text)
    state_name = Column(Text)
    optimal_water_type = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ============================
#        NBS OPTIONS
# ============================

class NbsOption(Base):
    __tablename__ = "nbs_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution = Column(Text)
    optimal_water_type = Column(Text)
    location_suitability = Column(Text)
    climate_suitability = Column(Text)
    soil_type = Column(Text)
    resource_requirements = Column(Text)
    notes = Column(Text)
    state_name = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ============================
#    NBS IMPLEMENTATION
# ============================

class NbsImplementation(Base):
    __tablename__ = "nbs_implementation"

    id = Column(Integer, primary_key=True)
    solution = Column(Text)
    implementation_steps = Column(Text)
    maintenance_requirements = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ============================
#         WATER DATA
# ============================

class WaterData(Base):
    __tablename__ = "water_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    water_type = Column(Text)
    colour = Column(Text)
    # These fields are TEXT to preserve original ranges (e.g., "30-200").
    turbidity = Column(Text)
    temperature = Column(Text)
    odour = Column(Text)
    tss = Column(Text)
    ph = Column(Text)
    bod = Column(Text)
    cod = Column(Text)
    nitrate = Column(Text)
    phosphate = Column(Text)
    ammonia = Column(Text)
    chloride = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

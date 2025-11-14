"""
SQLAlchemy ORM models for the NbS Toolkit.
Production-grade, consistent naming, typed, optimized for PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Text, Float, DateTime, Index, UniqueConstraint, func
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# ============================
#  MERGED DISTRICT DATA
# ============================

class MergedDistrictData(Base):
    __tablename__ = "merged_district_data"

    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(Text, nullable=False, index=True)
    district_name = Column(Text, nullable=True)
    soil_type = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_state_lower", func.lower(state_name)),
    )


# ============================
#        PLANT DATA
# ============================

class PlantData(Base):
    __tablename__ = "plant_data"

    id = Column(Integer, primary_key=True, index=True)
    plant_species = Column(Text, nullable=False)
    climate_preference = Column(Text)
    water_needs = Column(Text)
    ecological_role = Column(Text)
    soil_type = Column(Text)
    locational_availability = Column(Text)
    pollution_tolerance = Column(Text)

    state_name = Column(Text, nullable=False)
    optimal_water_type = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index(
            "idx_plant_state_water",
            func.lower(state_name),
            func.lower(optimal_water_type)
        ),
        Index("idx_plant_soil", func.lower(soil_type)),
    )


# ============================
#        NBS OPTIONS
# ============================

class NbsOption(Base):
    __tablename__ = "nbs_options"

    id = Column(Integer, primary_key=True, index=True)
    solution = Column(Text, nullable=False)
    optimal_water_type = Column(Text, nullable=False)

    location_suitability = Column(Text)
    climate_suitability = Column(Text)
    soil_type = Column(Text)
    resource_requirements = Column(Text)
    notes = Column(Text)

    state_name = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index(
            "idx_nbs_state_water",
            func.lower(state_name),
            func.lower(optimal_water_type)
        ),
        Index("idx_solution_lower", func.lower(solution)),
    )


# ============================
#    NBS IMPLEMENTATION
# ============================

class NbsImplementation(Base):
    __tablename__ = "nbs_implementation"

    id = Column(Integer, primary_key=True, index=True)
    solution = Column(Text, nullable=False)
    implementation_steps = Column(Text)
    maintenance_requirements = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("solution", name="uq_impl_solution"),
        Index("idx_impl_solution_lower", func.lower(solution)),
    )


# ============================
#         WATER DATA
# ============================

class WaterData(Base):
    __tablename__ = "water_data"

    id = Column(Integer, primary_key=True, index=True)

    water_type = Column(Text, nullable=True)
    colour = Column(Text)
    odour = Column(Text)

    turbidity = Column(Float)
    temperature = Column(Float)
    tss = Column(Float)
    ph = Column(Float)
    bod = Column(Float)
    cod = Column(Float)
    nitrate = Column(Float)
    phosphate = Column(Float)
    ammonia = Column(Float)
    chloride = Column(Float)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_water_type_lower", func.lower(water_type)),
    )

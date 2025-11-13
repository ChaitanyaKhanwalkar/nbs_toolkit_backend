"""
SQLAlchemy ORM models for NbS Toolkit.
Target DB: PostgreSQL 14+
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Text, Float, DateTime, Index, UniqueConstraint, func
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# ---------- Core reference tables ----------

class MergedDistrictData(Base):
    __tablename__ = "merged_district_data"

    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(Text, nullable=False, index=True)
    # Some datasets omit district_name; keep nullable for now.
    district_name = Column(Text, nullable=True)
    soil_type = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_mdd_state_lower", func.lower(state_name)),
    )


class PlantData(Base):
    __tablename__ = "plant_data"

    id = Column(Integer, primary_key=True, index=True)
    plant_species = Column(Text, nullable=False)
    climate_preference = Column(Text, nullable=True)
    water_needs = Column(Text, nullable=True)
    ecological_role = Column(Text, nullable=True)
    soil_type = Column(Text, nullable=True)
    locational_availability = Column(Text, nullable=True)
    pollution_tolerance = Column(Text, nullable=True)

    state_name = Column(Text, nullable=False)
    optimal_water_type = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Fast path for recommendations by (state, water_type)
        Index(
            "idx_plant_state_water",
            func.lower(state_name),
            func.lower(optimal_water_type),
        ),
        Index("idx_plant_soil_lower", func.lower(soil_type)),
    )


class NbsOption(Base):
    __tablename__ = "nbs_options"

    id = Column(Integer, primary_key=True, index=True)
    solution = Column(Text, nullable=False)
    optimal_water_type = Column(Text, nullable=False)

    location_suitability = Column(Text, nullable=True)
    climate_suitability = Column(Text, nullable=True)
    soil_type = Column(Text, nullable=True)
    resource_requirements = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    state_name = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index(
            "idx_nbs_state_water",
            func.lower(state_name),
            func.lower(optimal_water_type),
        ),
        Index("idx_nbs_solution_lower", func.lower(solution)),
    )


class NbsImplementation(Base):
    __tablename__ = "nbs_implementation"

    id = Column(Integer, primary_key=True, index=True)
    solution = Column(Text, nullable=False)  # Should match NbsOption.solution
    implementation_steps = Column(Text, nullable=True)
    maintenance_requirements = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Enforce 1:1 per solution (case-sensitive). If you want true case-insensitive
        # uniqueness in Postgres, prefer a functional unique index:
        # Index("uq_impl_solution_lower", func.lower(solution), unique=True)
        UniqueConstraint("solution", name="uq_impl_solution"),
        Index("idx_impl_solution_lower", func.lower(solution)),
    )


class WaterData(Base):
    """
    Optional table if you choose to persist uploaded/typical water data rows.

    Matches your CSV headers:
      water_type, colour, turbidity, temperature, odour,
      tss, ph, bod, cod, nitrate, phosphate, ammonia, chloride
    """
    __tablename__ = "water_data"

    id = Column(Integer, primary_key=True, index=True)

    water_type = Column(Text, nullable=True)
    colour = Column(Text, nullable=True)
    odour = Column(Text, nullable=True)

    turbidity = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)

    tss = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    bod = Column(Float, nullable=True)
    cod = Column(Float, nullable=True)
    nitrate = Column(Float, nullable=True)
    phosphate = Column(Float, nullable=True)
    ammonia = Column(Float, nullable=True)
    chloride = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_water_type_lower", func.lower(water_type)),
    )


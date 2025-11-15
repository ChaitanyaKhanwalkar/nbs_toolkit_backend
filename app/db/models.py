from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class District(Base):
    __tablename__ = "district_data"
    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(String, index=True)
    district_name = Column(String)
    soil_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Plant(Base):
    __tablename__ = "plant_data"
    id = Column(Integer, primary_key=True, index=True)
    plant_species = Column(String)
    locational_availability = Column(String)
    climate_preference = Column(String)
    soil_type = Column(String)
    water_needs = Column(String)
    ecological_role = Column(String)
    pollution_tolerance = Column(String)
    state_name = Column(String, index=True)
    optimal_water_type = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NBS(Base):
    __tablename__ = "nbs_options"
    id = Column(Integer, primary_key=True, index=True)
    solution = Column(String)
    optimal_water_type = Column(String, index=True)
    location_suitability = Column(String)
    climate_suitability = Column(String)
    soil_type = Column(String)
    resource_requirements = Column(String)
    notes = Column(String)
    state_name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NBSImplementation(Base):
    __tablename__ = "nbs_implementation"
    id = Column(Integer, primary_key=True, index=True)
    solution = Column(String)
    implementation_steps = Column(String)
    maintenance_requirements = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WaterData(Base):
    __tablename__ = "water_data"
    id = Column(Integer, primary_key=True, index=True)
    water_type = Column(String)
    colour = Column(String)
    odour = Column(String)
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
    sample_source = Column(String)
    sample_timestamp = Column(DateTime)
    raw_data = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

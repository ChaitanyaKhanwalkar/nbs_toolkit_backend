from sqlalchemy import Column, Integer, String, Float, Text
from db.database import Base

# 1. Plant Data
class PlantData(Base):
    __tablename__ = "plant_data"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, index=True)
    district = Column(String, index=True, nullable=True)
    plant_name = Column(String, index=True)
    water_type = Column(String, index=True)
    soil_type = Column(String, nullable=True)
    benefit = Column(Text, nullable=True)

# 2. District Data
class DistrictData(Base):
    __tablename__ = "district_data"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    rainfall = Column(Float, nullable=True)
    soil_type = Column(String, nullable=True)

# 3. NBS Options
class NbsOptions(Base):
    __tablename__ = "nbs_options"

    id = Column(Integer, primary_key=True, index=True)
    option_name = Column(String, index=True)
    description = Column(Text, nullable=True)
    water_type = Column(String, index=True, nullable=True)
    state = Column(String, index=True, nullable=True)

# 4. NBS Implementation
class NbsImplementation(Base):
    __tablename__ = "nbs_implementation"

    id = Column(Integer, primary_key=True, index=True)
    option_name = Column(String, index=True)
    step = Column(Text, nullable=True)
    tools_required = Column(Text, nullable=True)
    cost_estimate = Column(String, nullable=True)

# 5. Water Data
class WaterData(Base):
    __tablename__ = "water_data"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    water_type = Column(String, index=True)
    quality_index = Column(Float, nullable=True)
    issue = Column(Text, nullable=True)

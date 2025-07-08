from sqlalchemy import Column, Integer, Text, TIMESTAMP
from app.db.database import Base

class WaterData(Base):
    __tablename__ = "water_data"

    id = Column(Integer, primary_key=True, index=True)
    water_type = Column(Text)
    colour = Column(Text)
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
    sample_source = Column(Text)
    sample_timestamp = Column(TIMESTAMP)
    raw_data = Column(Text)
    notes = Column(Text)

class UserLocation(Base):
    __tablename__ = "user_location"
    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(Text, nullable=False)
    state_raw_input = Column(Text)
    location_source = Column(Text, default='user_selected')
    timestamp = Column(TIMESTAMP)
    notes = Column(Text)
import pandas as pd
from sqlalchemy.orm import Session
from app.db.models import District, Plant, NBS, NBSImplementation, WaterData
from app.db.database import SessionLocal, engine
import os

def load_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    return pd.read_csv(file_path)

def seed_data():
    db: Session = SessionLocal()
    
    # Seed District Data
    if db.query(District).count() == 0:
        df = load_csv("app/data/district_data_new.csv")
        if df is not None:
            df.to_sql('district_data', con=engine, if_exists='append', index=False)
            print("Seeded District data")

    # Seed Plant Data
    if db.query(Plant).count() == 0:
        df = load_csv("app/data/plant_data_new.csv")
        if df is not None:
            df.to_sql('plant_data', con=engine, if_exists='append', index=False)
            print("Seeded Plant data")

    # Seed NBS Options
    if db.query(NBS).count() == 0:
        df = load_csv("app/data/nbs_options_new.csv")
        if df is not None:
            df.to_sql('nbs_options', con=engine, if_exists='append', index=False)
            print("Seeded NBS Options data")

    # Seed NBS Implementation
    if db.query(NBSImplementation).count() == 0:
        df = load_csv("app/data/nbs_implementation_new.csv")
        if df is not None:
            df.to_sql('nbs_implementation', con=engine, if_exists='append', index=False)
            print("Seeded NBS Implementation data")

    # Seed Water Data
    if db.query(WaterData).count() == 0:
        df = load_csv("app/data/water_data_new.csv")
        if df is not None:
            df.to_sql('water_data', con=engine, if_exists='append', index=False)
            print("Seeded Water data")

    db.close()

if __name__ == "__main__":
    seed_data()

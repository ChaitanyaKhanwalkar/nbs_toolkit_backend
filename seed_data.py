import os
import pandas as pd
from sqlalchemy.orm import Session
from db import models, database

# ✅ Base directory (nbs_toolkit_backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def seed_data():
    db: Session = database.SessionLocal()

    try:
        print("📌 Seeding database with CSV data...")

        # 🌱 Load all CSVs
        plant_data = pd.read_csv(os.path.join(BASE_DIR, "plant_data_new.csv"))
        district_data = pd.read_csv(os.path.join(BASE_DIR, "district_data_new.csv"))
        nbs_options = pd.read_csv(os.path.join(BASE_DIR, "nbs_options_new.csv"))
        nbs_implementation = pd.read_csv(os.path.join(BASE_DIR, "nbs_implementation_new.csv"))
        water_data = pd.read_csv(os.path.join(BASE_DIR, "water_data_new.csv"))

        # 🟢 Seed Plant Data
        for _, row in plant_data.iterrows():
            db.add(models.PlantData(**row.to_dict()))

        # 🟢 Seed District Data
        for _, row in district_data.iterrows():
            db.add(models.DistrictData(**row.to_dict()))

        # 🟢 Seed NBS Options
        for _, row in nbs_options.iterrows():
            db.add(models.NBSOption(**row.to_dict()))

        # 🟢 Seed NBS Implementation
        for _, row in nbs_implementation.iterrows():
            db.add(models.NBSImplementation(**row.to_dict()))

        # 🟢 Seed Water Data
        for _, row in water_data.iterrows():
            db.add(models.WaterData(**row.to_dict()))

        db.commit()
        print("✅ Database seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

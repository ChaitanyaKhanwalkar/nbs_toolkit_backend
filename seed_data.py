# seed_data.py
import pandas as pd
from db.database import SessionLocal, engine, Base
from db import models

def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        base_path = "nbs_toolkit_backend/"

        # ---- Seed Plant Data ----
        df = pd.read_csv(base_path + "plant_data_new.csv")
        for _, row in df.iterrows():
            obj = models.PlantData(
                id=row["id"],
                name=row["name"],
                description=row["description"]
            )
            db.merge(obj)

        # ---- Seed District Data ----
        df = pd.read_csv(base_path + "district_data_new.csv")
        for _, row in df.iterrows():
            obj = models.DistrictData(
                id=row["id"],
                state=row["state"],
                district=row["district"]
            )
            db.merge(obj)

        # ---- Seed NBS Options ----
        df = pd.read_csv(base_path + "nbs_options_new.csv")
        for _, row in df.iterrows():
            obj = models.NBSOption(
                id=row["id"],
                name=row["name"],
                category=row["category"]
            )
            db.merge(obj)

        # ---- Seed NBS Implementation ----
        df = pd.read_csv(base_path + "nbs_implementation_new.csv")
        for _, row in df.iterrows():
            obj = models.NBSImplementation(
                id=row["id"],
                nbs_id=row["nbs_id"],
                details=row["details"]
            )
            db.merge(obj)

        # ---- Seed Water Data ----
        df = pd.read_csv(base_path + "water_data_new.csv")
        for _, row in df.iterrows():
            obj = models.WaterData(
                id=row["id"],
                state=row["state"],
                water_type=row["water_type"]
            )
            db.merge(obj)

        # Commit all inserts
        db.commit()
        print("✅ Database seeded successfully!")

    except Exception as e:
        print("❌ Error seeding database:", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

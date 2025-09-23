# seed_data.py
import os
import pandas as pd
from db.database import SessionLocal
from db import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def seed_data():
    db = SessionLocal()
    try:
        # 🌱 Seed PlantData
        plant_csv = os.path.join(BASE_DIR, "plant_data_new.csv")
        if os.path.exists(plant_csv):
            df = pd.read_csv(plant_csv)
            for _, row in df.iterrows():
                plant = models.PlantData(
                    name=row.get("name"),
                    description=row.get("description"),
                    climate=row.get("climate"),
                    soil_type=row.get("soil_type"),
                    water_requirement=row.get("water_requirement"),
                )
                db.add(plant)
            db.commit()
            print("✅ PlantData seeded successfully!")
        else:
            print(f"⚠️ PlantData CSV not found: {plant_csv}")

        # 🌱 Seed NbsImplementation
        nbs_csv = os.path.join(BASE_DIR, "nbs_implementation_new.csv")
        if os.path.exists(nbs_csv):
            df = pd.read_csv(nbs_csv)
            for _, row in df.iterrows():
                nbs = models.NbsImplementation(
                    intervention=row.get("intervention"),
                    description=row.get("description"),
                    benefit=row.get("benefit"),
                    cost=row.get("cost"),
                )
                db.add(nbs)
            db.commit()
            print("✅ NbsImplementation seeded successfully!")
        else:
            print(f"⚠️ NbsImplementation CSV not found: {nbs_csv}")

        # 🌱 Seed WaterData
        water_csv = os.path.join(BASE_DIR, "water_data_new.csv")
        if os.path.exists(water_csv):
            df = pd.read_csv(water_csv)
            for _, row in df.iterrows():
                water = models.WaterData(
                    state=row.get("state"),
                    rainfall=row.get("rainfall"),
                    groundwater_level=row.get("groundwater_level"),
                    quality=row.get("quality"),
                )
                db.add(water)
            db.commit()
            print("✅ WaterData seeded successfully!")
        else:
            print(f"⚠️ WaterData CSV not found: {water_csv}")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

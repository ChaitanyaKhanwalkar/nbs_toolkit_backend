# nbs_toolkit_backend/seed_data.py
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
                    state=row.get("state"),
                    district=row.get("district"),
                    plant_name=row.get("plant_name"),
                    water_type=row.get("water_type"),
                    soil_type=row.get("soil_type"),
                    benefit=row.get("benefit"),
                )
                db.add(plant)
            db.commit()
            print("✅ PlantData seeded")

        # 🌱 Seed DistrictData
        district_csv = os.path.join(BASE_DIR, "district_data_new.csv")
        if os.path.exists(district_csv):
            df = pd.read_csv(district_csv)
            for _, row in df.iterrows():
                district = models.DistrictData(
                    state=row.get("state"),
                    district=row.get("district"),
                    rainfall=row.get("rainfall"),
                    soil_type=row.get("soil_type"),
                )
                db.add(district)
            db.commit()
            print("✅ DistrictData seeded")

        # 🌱 Seed NbsOptions
        nbs_options_csv = os.path.join(BASE_DIR, "nbs_options_new.csv")
        if os.path.exists(nbs_options_csv):
            df = pd.read_csv(nbs_options_csv)
            for _, row in df.iterrows():
                option = models.NbsOptions(
                    option_name=row.get("option_name"),
                    description=row.get("description"),
                    water_type=row.get("water_type"),
                    state=row.get("state"),
                )
                db.add(option)
            db.commit()
            print("✅ NbsOptions seeded")

        # 🌱 Seed NbsImplementation
        nbs_impl_csv = os.path.join(BASE_DIR, "nbs_implementation_new.csv")
        if os.path.exists(nbs_impl_csv):
            df = pd.read_csv(nbs_impl_csv)
            for _, row in df.iterrows():
                impl = models.NbsImplementation(
                    option_name=row.get("option_name"),
                    step=row.get("step"),
                    tools_required=row.get("tools_required"),
                    cost_estimate=row.get("cost_estimate"),
                )
                db.add(impl)
            db.commit()
            print("✅ NbsImplementation seeded")

        # 🌱 Seed WaterData
        water_csv = os.path.join(BASE_DIR, "water_data_new.csv")
        if os.path.exists(water_csv):
            df = pd.read_csv(water_csv)
            for _, row in df.iterrows():
                water = models.WaterData(
                    state=row.get("state"),
                    district=row.get("district"),
                    water_type=row.get("water_type"),
                    quality_index=row.get("quality_index"),
                    issue=row.get("issue"),
                )
                db.add(water)
            db.commit()
            print("✅ WaterData seeded")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

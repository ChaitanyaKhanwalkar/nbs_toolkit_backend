# seed_data.py
import pandas as pd
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db import models

# CSV file paths (these must exist in your deployed app directory)
csv_files = {
    "plant_data": "plant_data_new.csv",
    "district_data": "district_data_new.csv",
    "nbs_options": "nbs_options_new.csv",
    "nbs_implementation": "nbs_implementation_new.csv",
    "water_data": "water_data_new.csv"
}

def seed():
    db: Session = SessionLocal()
    try:
        # 1️⃣ Seed plant_data
        plant_df = pd.read_csv(csv_files["plant_data"])
        for _, row in plant_df.iterrows():
            record = models.PlantData(**row.to_dict())
            db.add(record)

        # 2️⃣ Seed district_data
        district_df = pd.read_csv(csv_files["district_data"])
        for _, row in district_df.iterrows():
            record = models.DistrictData(**row.to_dict())
            db.add(record)

        # 3️⃣ Seed nbs_options
        nbs_options_df = pd.read_csv(csv_files["nbs_options"])
        for _, row in nbs_options_df.iterrows():
            record = models.NbsOption(**row.to_dict())
            db.add(record)

        # 4️⃣ Seed nbs_implementation
        nbs_impl_df = pd.read_csv(csv_files["nbs_implementation"])
        for _, row in nbs_impl_df.iterrows():
            record = models.NbsImplementation(**row.to_dict())
            db.add(record)

        # 5️⃣ Seed water_data
        water_df = pd.read_csv(csv_files["water_data"])
        for _, row in water_df.iterrows():
            record = models.WaterData(**row.to_dict())
            db.add(record)

        # Commit everything
        db.commit()
        print("✅ All data seeded successfully!")

    except Exception as e:
        print("❌ Error seeding data:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()


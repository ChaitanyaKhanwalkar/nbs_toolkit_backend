# seed_data.py
import pandas as pd
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db import models

# CSV paths (adjust if needed)
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
        # Example: Seed plant_data
        plant_df = pd.read_csv(csv_files["plant_data"])
        for _, row in plant_df.iterrows():
            plant = models.PlantData(**row.to_dict())
            db.add(plant)

        # Do the same for other CSVs:
        # district_data, nbs_options, nbs_implementation, water_data

        db.commit()
        print("✅ Data seeded successfully!")
    except Exception as e:
        print("❌ Error seeding data:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()

import os
import pandas as pd
from sqlalchemy.orm import Session
from db.database import engine, SessionLocal
from db import models

# Create tables
print("📌 Creating tables in the database...")
models.Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")

# Open DB session
db: Session = SessionLocal()

def seed_table(df, model, mapping):
    """Generic function to insert CSV rows into a SQLAlchemy model"""
    objects = []
    for _, row in df.iterrows():
        obj_data = {}
        for csv_col, model_attr in mapping.items():
            obj_data[model_attr] = row.get(csv_col, None)
        objects.append(model(**obj_data))
    db.add_all(objects)
    db.commit()
    print(f"🌱 Seeded {len(objects)} rows into {model.__tablename__}")

try:
    print("📌 Seeding database with CSV data...")

    # 1. Plant Data
    plant_df = pd.read_csv("nbs_toolkit_backend/plant_data_new.csv")
    seed_table(plant_df, models.PlantData, {
        "state": "state",
        "district": "district",
        "plant_name": "plant_name",
        "water_type": "water_type",
        "soil_type": "soil_type",
        "benefit": "benefit"
    })

    # 2. District Data
    district_df = pd.read_csv("nbs_toolkit_backend/district_data_new.csv")
    seed_table(district_df, models.DistrictData, {
        "state": "state",
        "district": "district",
        "rainfall": "rainfall",
        "soil_type": "soil_type"
    })

    # 3. NBS Options
    nbs_options_df = pd.read_csv("nbs_toolkit_backend/nbs_options_new.csv")
    seed_table(nbs_options_df, models.NbsOptions, {
        "option_name": "option_name",
        "description": "description",
        "water_type": "water_type",
        "state": "state"
    })

    # 4. NBS Implementation
    nbs_impl_df = pd.read_csv("nbs_toolkit_backend/nbs_implementation_new.csv")
    seed_table(nbs_impl_df, models.NbsImplementation, {
        "option_name": "option_name",
        "step": "step",
        "tools_required": "tools_required",
        "cost_estimate": "cost_estimate"
    })

    # 5. Water Data
    water_df = pd.read_csv("nbs_toolkit_backend/water_data_new.csv")
    seed_table(water_df, models.WaterData, {
        "state": "state",
        "district": "district",
        "water_type": "water_type",
        "quality_index": "quality_index",
        "issue": "issue"
    })

    print("🌱 Database seeded successfully!")

except Exception as e:
    print(f"❌ Error seeding database: {e}")

finally:
    db.close()

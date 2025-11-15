import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import PlantData, NBSOption, NBSImplementation, DistrictMerged


def load_csv(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.fillna(None)  # SQL safe
    return df


def seed_plants(db: Session):
    df = load_csv("app/data/csv/plants.csv")

    for _, row in df.iterrows():
        obj = PlantData(
            plant_species=row.get("plant_species"),
            state_name=row.get("state_name"),
            soil_type=row.get("soil_type"),
            optimal_water_type=row.get("optimal_water_type"),
            description=row.get("description"),
        )
        db.add(obj)

    db.commit()
    print(f"Seeded {len(df)} plant records")


def seed_nbs_options(db: Session):
    df = load_csv("app/data/csv/nbs_options.csv")

    for _, row in df.iterrows():
        obj = NBSOption(
            solution=row.get("solution"),
            state_name=row.get("state_name"),
            soil_type=row.get("soil_type"),
            optimal_water_type=row.get("optimal_water_type"),
            benefits=row.get("benefits"),
        )
        db.add(obj)

    db.commit()
    print(f"Seeded {len(df)} NBS options")


def seed_nbs_implementation(db: Session):
    df = load_csv("app/data/csv/nbs_implementation.csv")

    for _, row in df.iterrows():
        obj = NBSImplementation(
            id=int(row.get("id")),
            steps=row.get("steps"),
            cost=row.get("cost"),
            timeline=row.get("timeline"),
        )
        db.add(obj)

    db.commit()
    print(f"Seeded {len(df)} implementation records")


def seed_merged_data(db: Session):
    df = load_csv("app/data/csv/merged_district_data.csv")

    for _, row in df.iterrows():
        obj = DistrictMerged(
            state_name=row.get("state_name"),
            district=row.get("district"),
            soil_type=row.get("soil_type"),
            population=row.get("population"),
        )
        db.add(obj)

    db.commit()
    print(f"Seeded {len(df)} district merged rows")


def seed_database():
    print("🌱 Seeding Azure PostgreSQL...")

    db = SessionLocal()

    seed_plants(db)
    seed_nbs_options(db)
    seed_nbs_implementation(db)
    seed_merged_data(db)

    db.close()

    print("✅ Seeding completed.")

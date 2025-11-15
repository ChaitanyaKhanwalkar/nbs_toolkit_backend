import pandas as pd
from sqlalchemy import text
from app.db.database import engine

def seed_database():
    print("🌱 Seeding database...")

    conn = engine.connect()

    # Load CSVs
    plant_df = pd.read_csv("data/plant_data_new.csv")
    nbs_df = pd.read_csv("data/nbs_options_new.csv")
    impl_df = pd.read_csv("data/nbs_implementation_new.csv")

    # Clear tables
    conn.execute(text("DELETE FROM plant_data"))
    conn.execute(text("DELETE FROM nbs_options"))
    conn.execute(text("DELETE FROM nbs_implementation"))
    conn.commit()

    # Insert plant data
    plant_df.to_sql("plant_data", conn, if_exists="append", index=False)

    # Insert NBS
    nbs_df.to_sql("nbs_options", conn, if_exists="append", index=False)

    # Insert Implementation
    impl_df.to_sql("nbs_implementation", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    print("✅ Seeding completed successfully!")

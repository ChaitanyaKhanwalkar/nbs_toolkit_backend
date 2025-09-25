from fastapi import FastAPI
from db import models, database

import os

try:
    from seed_data import seed_data  # must match function name in seed_data.py
except Exception:
    seed_data = None  # handle missing import gracefully

SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

@app.on_event("startup")
def on_startup():
    print("📌 Creating tables in the database...")
    init_db()  # make sure this creates tables but is safe to call multiple times
    print("✅ Tables created successfully.")

    # Only seed if the symbol exists AND the flag is on
    if SEED_ON_STARTUP and seed_data:
        try:
            print("📦 Seeding database from CSVs...")
            seed_data(DATABASE_URL)  # pass what your seeder expects
            print("✅ Seeding complete.")
        except Exception as e:
            # Keep the server booting, but log the reason clearly
            print(f"❌ Error seeding database: {e}")



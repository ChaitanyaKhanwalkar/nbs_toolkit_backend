from fastapi import FastAPI
from db import models, database

import os

app = FastAPI()

# ✅ Create tables
print("📌 Creating tables in the database...")
models.Base.metadata.create_all(bind=database.engine)
print("✅ Tables created successfully.")

# ✅ Seed database only once (controlled by ENV variable)
if not os.getenv("DB_ALREADY_SEEDED"):
    try:
        seed_data()
        print("🌱 Database seeded successfully!")
        os.environ["DB_ALREADY_SEEDED"] = "true"  # Prevent reseeding
    except Exception as e:
        print(f"❌ Error seeding database: {e}")

@app.get("/")
def home():
    return {"message": "NBS Toolkit Backend is running 🚀"}



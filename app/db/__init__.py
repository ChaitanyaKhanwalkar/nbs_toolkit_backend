# init_db.py
from db.database import Base, engine
from db import models  # make sure all your models are imported here

print("📌 Creating tables in the database...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")

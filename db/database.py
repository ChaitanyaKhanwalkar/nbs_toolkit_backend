from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

print("DATABASE_URL:", SQLALCHEMY_DATABASE_URL)

SQLALCHEMY_DATABASE_URL = os.environ.get("postgresql://nbs_database_user:olbzqH91si07EtEF7xXhYHxeHxOJM4s2@dpg-d1migujipnbc739lkivg-a/nbs_database")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# db/database.py
import os, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Ensure SSL for managed providers
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("DEBUG DATABASE_URL:", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # validates connections
    pool_recycle=1800,       # avoid stale conns
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def wait_for_db(max_tries=15, delay_sec=2):
    """Retry DB connectivity on startup to survive DNS hiccups."""
    last_err = None
    for i in range(max_tries):
        try:
            with engine.connect() as conn:
                return
        except Exception as e:
            last_err = e
            time.sleep(delay_sec)
    raise last_err

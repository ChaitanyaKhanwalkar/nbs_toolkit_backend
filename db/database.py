# db/database.py
import os, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Ensure SSL for managed providers
if DATABASE_URL and "sslmode=" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

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

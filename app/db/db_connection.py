import os
import psycopg2

def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise RuntimeError("❌ DATABASE_URL missing. Add it in Azure App Settings.")
    
    conn = psycopg2.connect(DATABASE_URL)
    return conn

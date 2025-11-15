import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import io

load_dotenv()

# --- Configuration ---
CSV_FILE = "nbs_implementation_new.csv"
TABLE_NAME = "nbs_implementation"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "data")
# -------------------

def get_db_connection():
    """Establishes a psycopg2 connection to the database."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

def load_specific_data():
    """
    Loads data from a specific CSV file into a database table,
    including the 'id' column from the CSV.
    """
    file_path = os.path.join(DATA_DIR, CSV_FILE)
    if not os.path.exists(file_path):
        print(f"Error: {CSV_FILE} not found in {DATA_DIR}. Aborting.")
        return

    conn = None
    try:
        conn = get_db_connection()
        print(f"Loading data from {CSV_FILE} into {TABLE_NAME}...")
        
        # 1. Read the entire CSV into a pandas DataFrame.
        df = pd.read_csv(file_path)

        # 2. Prepare the data for the COPY command.
        # We are now including the 'id' column, so we use all columns from the DataFrame.
        sql_columns = [col.strip() for col in df.columns]
        sql_columns_str = f"({', '.join(sql_columns)})"

        # Create an in-memory text buffer.
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        with conn.cursor() as cursor:
            # 3. Construct and execute the COPY command.
            # The data is coming from our in-memory buffer which includes the 'id'.
            copy_sql = f"COPY {TABLE_NAME} {sql_columns_str} FROM STDIN WITH (FORMAT CSV, NULL '')"
            
            cursor.copy_expert(copy_sql, buffer)
            conn.commit()
            print(f"Successfully loaded and committed data for {TABLE_NAME}.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"An error occurred: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    load_specific_data()

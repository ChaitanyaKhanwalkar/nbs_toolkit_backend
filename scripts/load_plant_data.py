import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import io

load_dotenv()

# --- Configuration ---
CSV_FILE = "plant_data_new.csv"
TABLE_NAME = "plant_data"
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
    Loads data from a specific CSV file into a database table.
    It handles CSVs with an 'id' column and also removes any unnamed columns
    that pandas might create due to formatting issues (e.g., extra commas).
    """
    file_path = os.path.join(DATA_DIR, CSV_FILE)
    if not os.path.exists(file_path):
        print(f"Error: {CSV_FILE} not found in {DATA_DIR}. Aborting.")
        return

    conn = None
    try:
        conn = get_db_connection()
        print(f"Loading data from {CSV_FILE} into {TABLE_NAME}...")
        
        # 1. Read the CSV into a pandas DataFrame.
        df = pd.read_csv(file_path)

        # 2. Identify and collect any unwanted columns to be dropped.
        cols_to_drop = []
        for col in df.columns:
            col_stripped = col.strip()
            # Find 'id' columns or columns auto-named by pandas.
            if col_stripped.lower() == 'id' or col_stripped.startswith('Unnamed:'):
                cols_to_drop.append(col)
        
        if cols_to_drop:
            print(f"Found and removing ignored columns: {cols_to_drop}")
            df.drop(columns=cols_to_drop, inplace=True)

        # 3. Prepare the cleaned data for the COPY command.
        sql_columns = [col.strip() for col in df.columns]
        sql_columns_str = f"({', '.join(sql_columns)})"

        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        with conn.cursor() as cursor:
            # 4. Construct and execute the COPY command with the cleaned data.
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

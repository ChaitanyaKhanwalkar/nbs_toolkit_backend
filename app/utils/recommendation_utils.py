import pandas as pd
from sqlalchemy.orm import Session
from app.db.models import Plant, NBS, District


def get_recommendations(state: str, water_type: str, db: Session):
    # Load data from database
    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    nbs_df = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    merged_df = pd.read_sql("SELECT * FROM district_data", db.bind)

    # Filter by state and water type
    state_soil_type = merged_df[merged_df['state_name'].str.lower() == state.lower()]['soil_type'].iloc[0]
    
    # Plant recommendations
    plant_reco = plant_df[
        (plant_df['state_name'].str.lower() == state.lower()) &
        (plant_df['optimal_water_type'].str.lower() == water_type.lower()) &
        (plant_df['soil_type'].str.lower() == state_soil_type.lower())
    ]
    
    # NBS recommendations
    nbs_reco = nbs_df[
        (nbs_df['state_name'].str.lower() == state.lower()) &
        (nbs_df['optimal_water_type'].str.lower() == water_type.lower())
    ]
    
    return {
        "plant_recommendations": plant_reco.to_dict(orient="records"),
        "nbs_recommendations": nbs_reco.to_dict(orient="records")
    }

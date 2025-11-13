import pandas as pd
from fuzzywuzzy import fuzz

def remove_unnamed_columns(obj):
    if isinstance(obj, dict):
        return {k: v for k, v in obj.items() if not k.startswith("Unnamed")}
    if isinstance(obj, list):
        return [remove_unnamed_columns(x) for x in obj]
    return obj

def sanitize_for_json(obj):
    """Recursively replaces NaN/NaT/nulls with None in dicts/lists"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    elif pd.isna(obj):
        return None
    else:
        return obj

def get_recommendation_data(state_name, water_type, db):
    # Load all data
    merged_df = pd.read_sql("SELECT * FROM merged_district_data", db.bind)
    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    nbs_df = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    nbs_impl_df = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)

    # Safely get soil type for state
    merged = merged_df[merged_df['state_name'].str.lower() == state_name.lower()]
    soil_type = str(merged.iloc[0]['soil_type']) if not merged.empty and 'soil_type' in merged.columns else "Loamy"

    def get_matches(df, key):
        results = pd.DataFrame()
        match_levels = []

        # 1. Perfect match
        if soil_type:
            perfect = df[
                (df['state_name'].str.lower() == state_name.lower()) &
                (df['optimal_water_type'].str.lower() == water_type.lower()) &
                (df['soil_type'].str.lower() == soil_type.lower())
            ]
            results = pd.concat([results, perfect])
            match_levels.extend(['Perfect'] * len(perfect))

        # 2. State + Water
        if len(results) < 5:
            state_water = df[
                (df['state_name'].str.lower() == state_name.lower()) &
                (df['optimal_water_type'].str.lower() == water_type.lower())
            ]
            new_state_water = state_water[~state_water.index.isin(results.index)]
            results = pd.concat([results, new_state_water])
            match_levels.extend(['State+Water'] * len(new_state_water))

        # 3. Water Only
        if len(results) < 5:
            water = df[df['optimal_water_type'].str.lower() == water_type.lower()]
            new_water = water[~water.index.isin(results.index)]
            results = pd.concat([results, new_water])
            match_levels.extend(['Water Only'] * len(new_water))

        # 4. Fuzzy soil match
        if len(results) < 5 and soil_type:
            df['match_score'] = df.apply(
                lambda row: fuzz.token_set_ratio(str(row.get('soil_type', '')).lower(), soil_type.lower()), axis=1
            )
            fuzzy = df[~df.index.isin(results.index)].sort_values('match_score', ascending=False)
            results = pd.concat([results, fuzzy])
            match_levels.extend(['Fuzzy'] * len(fuzzy))

        # 5. Fallback: Any
        if len(results) < 5:
            others = df[~df.index.isin(results.index)]
            results = pd.concat([results, others])
            match_levels.extend(['Any'] * len(others))

        # Remove any unnamed columns
        results = results.drop(columns=[col for col in results.columns if col.startswith("Unnamed")], errors='ignore')

        # Deduplicate based on plant species or solution name
        dedup_key = 'plant_species' if key == 'plants' else 'solution'
        if dedup_key in results.columns:
            results = results.drop_duplicates(subset=dedup_key).head(5)
        else:
            print(f"[WARNING] '{dedup_key}' column not found in results for {key}. Skipping deduplication.")
            results = results.head(5)

        match_levels = match_levels[:len(results)]

        # Add match_level to each record
        data = results.to_dict(orient='records')
        for i, item in enumerate(data):
            item['match_level'] = match_levels[i] if i < len(match_levels) else 'Any'
        return data, match_levels[0] if match_levels else 'None'

    # Get plant and NbS matches
    plants, plant_level = get_matches(plant_df, 'plants')
    nbs, nbs_level = get_matches(nbs_df, 'nbs_options')

    # Match NbS to implementation
    nbs_impl_list = []
    for nbs_option in nbs:
        impl_row = nbs_impl_df[nbs_impl_df['id'] == nbs_option.get('id')]
        if not impl_row.empty:
            impl_dict = impl_row.iloc[0].to_dict()
            nbs_impl_list.append(impl_dict)
        else:
            nbs_impl_list.append({})

    # Compile result
    result = {
        "plant_match_level": plant_level,
        "nbs_match_level": nbs_level,
        "soil_type": soil_type,
        "plants": plants,
        "nbs_options": nbs,
        "nbs_implementation": nbs_impl_list
    }

    # Clean and return
    result = sanitize_for_json(result)
    return remove_unnamed_columns(result)

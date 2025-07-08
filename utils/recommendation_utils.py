import pandas as pd
from fuzzywuzzy import fuzz

def get_recommendation_data(state_name, water_type, db):
    # Get soil type for state
    merged_df = pd.read_sql("SELECT * FROM merged_district_data", db.bind)
    merged = merged_df[merged_df['state_name'].str.lower() == state_name.lower()]
    soil_type = merged.iloc[0]['soil_type'] if not merged.empty else None

    plant_df = pd.read_sql("SELECT * FROM plant_data", db.bind)
    nbs_df = pd.read_sql("SELECT * FROM nbs_options", db.bind)
    nbs_impl_df = pd.read_sql("SELECT * FROM nbs_implementation", db.bind)  # <-- ADD THIS

    def get_matches(df, key):
        results = pd.DataFrame()
        match_levels = []

        # 1. Perfect match
        if soil_type:
            perfect = df[
                (df['state_name'].str.lower() == state_name.lower()) &
                (df['optimal_water_type'].str.lower() == water_type.lower()) &
                (df['soil_type'].str.lower() == str(soil_type).lower())
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

        # 4. Fuzzy (soil)
        if len(results) < 5:
            if soil_type:
                df['match_score'] = df.apply(
                    lambda row: fuzz.token_set_ratio(str(row.get('soil_type', '')).lower(), str(soil_type).lower()), axis=1
                )
                fuzzy = df[~df.index.isin(results.index)].sort_values('match_score', ascending=False)
                results = pd.concat([results, fuzzy])
                match_levels.extend(['Fuzzy'] * len(fuzzy))
            else:
                others = df[~df.index.isin(results.index)]
                results = pd.concat([results, others])
                match_levels.extend(['Any'] * len(others))

        # Return only the first 5, and keep their match levels
        results = results.head(5)
        match_levels = match_levels[:5]

        # Add match level to each item for transparency
        data = results.to_dict(orient='records')
        for i, item in enumerate(data):
            item['match_level'] = match_levels[i] if i < len(match_levels) else 'Any'
        return data, match_levels[0] if match_levels else 'None'

    plants, plant_level = get_matches(plant_df, 'plants')
    nbs, nbs_level = get_matches(nbs_df, 'nbs_options')

    # ------- ADD THIS SECTION: For each nbs_option, find the matching nbs_implementation by id -------
    nbs_impl_list = []
    for nbs_option in nbs:
        # Match by ID!
        impl_row = nbs_impl_df[nbs_impl_df['id'] == nbs_option['id']]
        if not impl_row.empty:
            impl_dict = impl_row.iloc[0].to_dict()
            nbs_impl_list.append(impl_dict)
        else:
            nbs_impl_list.append({})  # Empty if not found

    return {
        "plant_match_level": plant_level,
        "nbs_match_level": nbs_level,
        "soil_type": soil_type,
        "plants": plants,
        "nbs_options": nbs,
        "nbs_implementation": nbs_impl_list   # <--- THIS KEY
    }

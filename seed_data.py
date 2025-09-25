import os
from pathlib import Path
from typing import Optional, Dict

import pandas as pd
from sqlalchemy import text
from db.database import SessionLocal
from db import models


# ---------------------------
# Paths & CSV helpers
# ---------------------------

HERE = Path(__file__).resolve().parent
SEARCH_DIRS = [
    Path(os.getenv("CSV_DIR", "")).resolve() if os.getenv("CSV_DIR") else None,
    HERE,
    Path.cwd(),
]
SEARCH_DIRS = [p for p in SEARCH_DIRS if p and p.exists()]


def find_csv(filename: str) -> Optional[Path]:
    """Find a CSV in CSV_DIR, alongside this file, or in CWD."""
    for base in SEARCH_DIRS:
        candidate = base / filename
        if candidate.exists():
            return candidate
    return None


def read_csv_clean(path: Path) -> pd.DataFrame:
    """Read CSV, drop 'Unnamed:*' columns, trim headers, keep types loose."""
    df = pd.read_csv(path)
    # Drop stray export columns
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed", na=False)]
    # Normalize headers (lower + strip)
    df.columns = [str(c).strip().lower() for c in df.columns]
    # Trim whitespace in string cells
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    return df


def to_float(series: pd.Series) -> pd.Series:
    """Coerce numeric columns safely."""
    return pd.to_numeric(series, errors="coerce")


# ---------------------------
# Seeder
# ---------------------------

def seed_data():
    """
    Idempotent seeding for the NbS Toolkit database.

    Expects the following CSVs (headers in parentheses):
      - district_data_new.csv
          (state_name, soil_type [, district_name - optional])
      - plant_data_new.csv
          (plant_species, locational_availability, climate_preference, soil_type,
           water_needs, ecological_role, pollution_tolerance, state_name, optimal_water_type)
      - nbs_options_new.csv
          (solution, optimal_water_type, location_suitability, climate_suitability,
           soil_type, resource_requirements, notes, state_name [, id - ignored])
      - nbs_implementation_new.csv
          (solution, implementation_steps, maintenance_requirements [, id - ignored])
      - water_data_new.csv
          (water_type, colour, turbidity, temperature, odour, tss, ph, bod, cod,
           nitrate, phosphate, ammonia, chloride)
    """
    session = SessionLocal()
    try:
        # 1) TRUNCATE tables (safe, repeatable)
        #    Do individual TRUNCATEs so missing optional tables don't explode deploys
        def _truncate(table: str):
            try:
                session.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
                session.commit()
                print(f"🧹 Cleared {table}")
            except Exception as e:
                # If table doesn't exist (e.g., WaterData not created), just log and continue
                session.rollback()
                print(f"ℹ️  Skip TRUNCATE {table}: {e}")

        # Order doesn't really matter (no FKs), but this is tidy
        for table in [
            "nbs_implementation",
            "nbs_options",
            "plant_data",
            "merged_district_data",
            "water_data",
        ]:
            _truncate(table)

        # 2) Seed merged_district_data
        dd_path = find_csv("district_data_new.csv")
        if dd_path:
            df = read_csv_clean(dd_path)
            required = {"state_name"}
            if not required.issubset(set(df.columns)):
                raise ValueError(f"district_data_new.csv missing required columns: {required}")

            rows = []
            for _, r in df.iterrows():
                rows.append(models.MergedDistrictData(
                    state_name=r.get("state_name") or None,
                    # Optional; many rows may not have district_name in this CSV
                    district_name=r.get("district_name") or None,
                    soil_type=r.get("soil_type") or None,
                ))
            session.bulk_save_objects(rows)
            session.commit()
            print(f"✅ MergedDistrictData seeded: {len(rows)} rows")
        else:
            print("⚠️  district_data_new.csv not found — skipping MergedDistrictData")

        # 3) Seed plant_data
        plant_path = find_csv("plant_data_new.csv")
        if plant_path:
            df = read_csv_clean(plant_path)
            required = {"plant_species", "state_name", "optimal_water_type"}
            missing = required - set(df.columns)
            if missing:
                raise ValueError(f"plant_data_new.csv missing required columns: {missing}")

            rows = []
            for _, r in df.iterrows():
                # Skip rows missing hard-required fields
                if not (r.get("plant_species") and r.get("state_name") and r.get("optimal_water_type")):
                    continue
                rows.append(models.PlantData(
                    plant_species=r.get("plant_species"),
                    climate_preference=r.get("climate_preference") or None,
                    water_needs=r.get("water_needs") or None,
                    ecological_role=r.get("ecological_role") or None,
                    soil_type=r.get("soil_type") or None,
                    locational_availability=r.get("locational_availability") or None,
                    pollution_tolerance=r.get("pollution_tolerance") or None,
                    state_name=r.get("state_name"),
                    optimal_water_type=r.get("optimal_water_type"),
                ))
            session.bulk_save_objects(rows)
            session.commit()
            print(f"✅ PlantData seeded: {len(rows)} rows")
        else:
            print("⚠️  plant_data_new.csv not found — skipping PlantData")

        # 4) Seed nbs_options
        nbs_opt_path = find_csv("nbs_options_new.csv")
        if nbs_opt_path:
            df = read_csv_clean(nbs_opt_path)
            # Ignore 'id' if present; DB will set it
            required = {"solution", "optimal_water_type", "state_name"}
            missing = required - set(df.columns)
            if missing:
                raise ValueError(f"nbs_options_new.csv missing required columns: {missing}")

            # Normalize key strings to avoid mismatches
            if "solution" in df.columns:
                df["solution"] = df["solution"].astype(str).str.strip()

            rows = []
            for _, r in df.iterrows():
                if not (r.get("solution") and r.get("optimal_water_type") and r.get("state_name")):
                    continue
                rows.append(models.NbsOption(
                    solution=r.get("solution"),
                    optimal_water_type=r.get("optimal_water_type"),
                    location_suitability=r.get("location_suitability") or None,
                    climate_suitability=r.get("climate_suitability") or None,
                    soil_type=r.get("soil_type") or None,
                    resource_requirements=r.get("resource_requirements") or None,
                    notes=r.get("notes") or None,
                    state_name=r.get("state_name"),
                ))
            session.bulk_save_objects(rows)
            session.commit()
            print(f"✅ NbsOption seeded: {len(rows)} rows")
        else:
            print("⚠️  nbs_options_new.csv not found — skipping NbsOption")

        # 5) Seed nbs_implementation
        nbs_impl_path = find_csv("nbs_implementation_new.csv")
        if nbs_impl_path:
            df = read_csv_clean(nbs_impl_path)
            required = {"solution", "implementation_steps", "maintenance_requirements"}
            missing = required - set(df.columns)
            if missing:
                raise ValueError(f"nbs_implementation_new.csv missing required columns: {missing}")

            if "solution" in df.columns:
                df["solution"] = df["solution"].astype(str).str.strip()

            rows = []
            for _, r in df.iterrows():
                if not r.get("solution"):
                    continue
                rows.append(models.NbsImplementation(
                    solution=r.get("solution"),
                    implementation_steps=r.get("implementation_steps") or None,
                    maintenance_requirements=r.get("maintenance_requirements") or None,
                ))
            session.bulk_save_objects(rows)
            session.commit()
            print(f"✅ NbsImplementation seeded: {len(rows)} rows")
        else:
            print("⚠️  nbs_implementation_new.csv not found — skipping NbsImplementation")

        # 6) Seed water_data (optional persistence)
        water_path = find_csv("water_data_new.csv")
        if water_path:
            df = read_csv_clean(water_path)

            # Make sure expected columns exist; some datasets may use lowercase keys (we normalized)
            expected = {
                "water_type", "colour", "turbidity", "temperature", "odour",
                "tss", "ph", "bod", "cod", "nitrate", "phosphate", "ammonia", "chloride"
            }
            missing = expected - set(df.columns)
            if missing:
                print(f"ℹ️  water_data_new.csv missing some columns (will insert what’s available): {missing}")

            # Coerce numerics safely
            for col in ["turbidity", "temperature", "tss", "ph", "bod", "cod",
                        "nitrate", "phosphate", "ammonia", "chloride"]:
                if col in df.columns:
                    df[col] = to_float(df[col])

            rows = []
            for _, r in df.iterrows():
                rows.append(models.WaterData(
                    water_type=r.get("water_type") or None,
                    colour=r.get("colour") or None,
                    odour=r.get("odour") or None,
                    turbidity=r.get("turbidity"),
                    temperature=r.get("temperature"),
                    tss=r.get("tss"),
                    ph=r.get("ph"),
                    bod=r.get("bod"),
                    cod=r.get("cod"),
                    nitrate=r.get("nitrate"),
                    phosphate=r.get("phosphate"),
                    ammonia=r.get("ammonia"),
                    chloride=r.get("chloride"),
                ))
            session.bulk_save_objects(rows)
            session.commit()
            print(f"✅ WaterData seeded: {len(rows)} rows")
        else:
            print("ℹ️  water_data_new.csv not found — skipping WaterData")

        print("🎉 Seeding complete.")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()

import os
from pathlib import Path
from typing import Optional, Iterable, Set, List

import pandas as pd
from sqlalchemy import text, inspect
from db.database import SessionLocal
from db import models


# ---------------------------
# File discovery & CSV helpers
# ---------------------------

HERE = Path(__file__).resolve().parent
SEARCH_DIRS = [
    Path(os.getenv("CSV_DIR", "")).resolve() if os.getenv("CSV_DIR") else None,
    HERE,
    Path.cwd(),
]
SEARCH_DIRS = [p for p in SEARCH_DIRS if p and p.exists()]

def find_csv(filename: str) -> Optional[Path]:
    for base in SEARCH_DIRS:
        p = base / filename
        if p.exists():
            return p
    return None

def read_csv_clean(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # drop stray "Unnamed:*" export columns
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed", na=False)]
    # normalize headers
    df.columns = [str(c).strip().lower() for c in df.columns]
    # trim strings
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    return df

def to_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def _uniq_preserve(items: List[str]) -> str:
    """Combine values, dropping empties and duplicates while preserving order."""
    seen = set()
    out: List[str] = []
    for val in items:
        v = (val or "").strip()
        if not v:
            continue
        if v not in seen:
            seen.add(v)
            out.append(v)
    return "; ".join(out) if out else None


# ---------------------------
# Schema helpers
# ---------------------------

def _ensure_table(
    session,
    table_obj,                      # SQLAlchemy Table, e.g., models.PlantData.__table__
    required_cols: Iterable[str],   # column names expected on the table
    hard_reset: bool = False
) -> None:
    """
    Ensure the DB table has all required columns.
    - If hard_reset=True: drop & recreate the table unconditionally.
    - Else: inspect live columns; if any required missing -> drop & recreate.
    """
    engine = session.get_bind()
    inspector = inspect(engine)
    table_name = table_obj.name

    recreate = False

    if hard_reset:
        recreate = True
    else:
        # Does table exist?
        if table_name in inspector.get_table_names():
            live_cols: Set[str] = {col["name"] for col in inspector.get_columns(table_name)}
            missing = set(required_cols) - live_cols
            if missing:
                print(f"🧭 Schema drift detected on {table_name}: missing {sorted(missing)} -> will recreate")
                recreate = True
        else:
            print(f"ℹ️  {table_name} does not exist -> will create")
            recreate = True

    if recreate:
        # Drop and recreate only this table
        try:
            print(f"🧨 Dropping {table_name} ...")
            models.Base.metadata.drop_all(bind=engine, tables=[table_obj])
        except Exception as e:
            print(f"   (drop note) {e}")

        print(f"🏗️  Creating {table_name} ...")
        models.Base.metadata.create_all(bind=engine, tables=[table_obj])
        print(f"✅ {table_name} ready.")


# ---------------------------
# Seeder
# ---------------------------

def seed_data():
    """
    Schema-aware, idempotent seeding for NbS Toolkit.

    CSVs expected (headers in parentheses):
      - district_data_new.csv
          state_name, soil_type [, district_name]
      - plant_data_new.csv
          plant_species, locational_availability, climate_preference, soil_type,
          water_needs, ecological_role, pollution_tolerance, state_name, optimal_water_type
      - nbs_options_new.csv
          solution, optimal_water_type, location_suitability, climate_suitability,
          soil_type, resource_requirements, notes, state_name [, id ignored]
      - nbs_implementation_new.csv
          solution, implementation_steps, maintenance_requirements [, id ignored]
          (may contain duplicates -> we dedupe by solution)
      - water_data_new.csv
          water_type, colour, turbidity, temperature, odour, tss, ph, bod, cod,
          nitrate, phosphate, ammonia, chloride
    """
    session = SessionLocal()
    HARD_RESET = os.getenv("DB_HARD_RESET", "false").lower() == "true"

    try:
        # 0) Ensure tables match the ORM schema (self-heal if drift is detected)
        _ensure_table(
            session,
            models.MergedDistrictData.__table__,
            required_cols=["id", "state_name", "district_name", "soil_type", "created_at", "updated_at"],
            hard_reset=HARD_RESET
        )
        _ensure_table(
            session,
            models.PlantData.__table__,
            required_cols=[
                "id", "plant_species", "climate_preference", "water_needs", "ecological_role",
                "soil_type", "locational_availability", "pollution_tolerance",
                "state_name", "optimal_water_type", "created_at", "updated_at"
            ],
            hard_reset=HARD_RESET
        )
        _ensure_table(
            session,
            models.NbsOption.__table__,
            required_cols=[
                "id", "solution", "optimal_water_type", "location_suitability",
                "climate_suitability", "soil_type", "resource_requirements", "notes",
                "state_name", "created_at", "updated_at"
            ],
            hard_reset=HARD_RESET
        )
        _ensure_table(
            session,
            models.NbsImplementation.__table__,
            required_cols=["id", "solution", "implementation_steps", "maintenance_requirements", "created_at", "updated_at"],
            hard_reset=HARD_RESET
        )
        _ensure_table(
            session,
            models.WaterData.__table__,
            required_cols=[
                "id", "water_type", "colour", "odour", "turbidity", "temperature",
                "tss", "ph", "bod", "cod", "nitrate", "phosphate", "ammonia", "chloride",
                "created_at", "updated_at"
            ],
            hard_reset=HARD_RESET
        )

        # 1) TRUNCATE tables before fresh load (idempotent)
        def _truncate(table: str):
            try:
                session.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
                session.commit()
                print(f"🧹 Cleared {table}")
            except Exception as e:
                session.rollback()
                print(f"ℹ️  Skip TRUNCATE {table}: {e}")

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
            rows = []
            for _, r in df.iterrows():
                rows.append(models.MergedDistrictData(
                    state_name=r.get("state_name") or None,
                    district_name=r.get("district_name") or None,  # optional
                    soil_type=r.get("soil_type") or None,
                ))
            if rows:
                session.bulk_save_objects(rows)
                session.commit()
            print(f"✅ MergedDistrictData seeded: {len(rows)} rows")
        else:
            print("⚠️  district_data_new.csv not found — skipping")

        # 3) Seed plant_data
        plant_path = find_csv("plant_data_new.csv")
        if plant_path:
            df = read_csv_clean(plant_path)
            needed = {"plant_species", "state_name", "optimal_water_type"}
            missing = needed - set(df.columns)
            if missing:
                raise ValueError(f"plant_data_new.csv missing columns: {sorted(missing)}")

            rows = []
            for _, r in df.iterrows():
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
            if rows:
                session.bulk_save_objects(rows)
                session.commit()
            print(f"✅ PlantData seeded: {len(rows)} rows")
        else:
            print("⚠️  plant_data_new.csv not found — skipping")

        # 4) Seed nbs_options (optional light dedupe on exact row duplicates)
        nbs_opt_path = find_csv("nbs_options_new.csv")
        if nbs_opt_path:
            df = read_csv_clean(nbs_opt_path)
            if "solution" in df.columns:
                df["solution"] = df["solution"].astype(str).str.strip()

            needed = {"solution", "optimal_water_type", "state_name"}
            missing = needed - set(df.columns)
            if missing:
                raise ValueError(f"nbs_options_new.csv missing columns: {sorted(missing)}")

            # Drop exact duplicate rows to avoid bloat
            df = df.drop_duplicates(
                subset=["solution", "optimal_water_type", "state_name", "soil_type",
                        "location_suitability", "climate_suitability", "resource_requirements", "notes"],
                keep="first"
            )

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
            if rows:
                session.bulk_save_objects(rows)
                session.commit()
            print(f"✅ NbsOption seeded: {len(rows)} rows")
        else:
            print("⚠️  nbs_options_new.csv not found — skipping")

        # 5) Seed nbs_implementation (DEDUP BY SOLUTION to satisfy unique constraint)
        nbs_impl_path = find_csv("nbs_implementation_new.csv")
        if nbs_impl_path:
            df = read_csv_clean(nbs_impl_path)

            needed = {"solution", "implementation_steps", "maintenance_requirements"}
            missing = needed - set(df.columns)
            if missing:
                raise ValueError(f"nbs_implementation_new.csv missing columns: {sorted(missing)}")

            # Normalize solution string and build a case-insensitive key
            df["solution"] = df["solution"].astype(str).str.strip()
            df["solution_key"] = df["solution"].str.casefold()

            # DEDUPE: combine rows with same solution (case-insensitive)
            grouped = (
                df.groupby("solution_key", sort=False)
                  .agg({
                      "solution": "first",  # keep representative casing
                      "implementation_steps": lambda s: _uniq_preserve(list(s)),
                      "maintenance_requirements": lambda s: _uniq_preserve(list(s)),
                  })
                  .reset_index(drop=True)
            )

            # Warn if we collapsed duplicates
            collapsed = len(df) - len(grouped)
            if collapsed > 0:
                print(f"ℹ️  nbs_implementation: collapsed {collapsed} duplicate rows by solution")

            rows = []
            for _, r in grouped.iterrows():
                sol = r.get("solution")
                if not sol:
                    continue
                rows.append(models.NbsImplementation(
                    solution=sol,
                    implementation_steps=r.get("implementation_steps") or None,
                    maintenance_requirements=r.get("maintenance_requirements") or None,
                ))
            if rows:
                session.bulk_save_objects(rows)
                session.commit()
            print(f"✅ NbsImplementation seeded: {len(rows)} rows")
        else:
            print("⚠️  nbs_implementation_new.csv not found — skipping")

        # 6) Seed water_data (optional)
        water_path = find_csv("water_data_new.csv")
        if water_path:
            df = read_csv_clean(water_path)
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
            if rows:
                session.bulk_save_objects(rows)
                session.commit()
            print(f"✅ WaterData seeded: {len(rows)} rows")
        else:
            print("ℹ️  water_data_new.csv not found — skipping")

        print("🎉 Seeding complete.")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()



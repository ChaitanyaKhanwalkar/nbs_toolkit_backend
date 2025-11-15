-- /app/schemas/init.sql
-- This schema is generated based on the CSV files in /app/data.

SET client_min_messages = WARNING;
SET TimeZone = 'UTC';

-- 1) Helper function to auto-update 'updated_at' timestamps
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2) Table Definitions

-- Table for district_data_new.csv
CREATE TABLE IF NOT EXISTS district_data (
  id            SERIAL PRIMARY KEY,
  state_name    TEXT,
  soil_type     TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table for plant_data_new.csv
-- Note: An unnamed column in the CSV header is ignored.
CREATE TABLE IF NOT EXISTS plant_data (
  id                       SERIAL PRIMARY KEY,
  plant_species            TEXT,
  locational_availability  TEXT,
  climate_preference       TEXT,
  soil_type                TEXT,
  water_needs              TEXT,
  ecological_role          TEXT,
  pollution_tolerance      TEXT,
  state_name               TEXT,
  optimal_water_type       TEXT,
  created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table for nbs_options_new.csv
CREATE TABLE IF NOT EXISTS nbs_options (
  id                     SERIAL PRIMARY KEY,
  solution               TEXT,
  optimal_water_type     TEXT,
  location_suitability   TEXT,
  climate_suitability    TEXT,
  soil_type              TEXT,
  resource_requirements  TEXT,
  notes                  TEXT,
  state_name             TEXT,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table for nbs_implementation_new.csv
-- The 'id' is an INTEGER PRIMARY KEY to be provided from the CSV.
CREATE TABLE IF NOT EXISTS nbs_implementation (
  id                         INTEGER PRIMARY KEY,
  solution                   TEXT,
  implementation_steps       TEXT,
  maintenance_requirements   TEXT,
  created_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table for water_data_new.csv
-- Columns with numeric ranges are set to DOUBLE PRECISION.
CREATE TABLE IF NOT EXISTS water_data (
  id           SERIAL PRIMARY KEY,
  water_type   TEXT,
  colour       TEXT,
  turbidity    TEXT, -- Kept as TEXT due to ranges like '30-200'
  temperature  TEXT, -- Kept as TEXT due to ranges like '20-35'
  odour        TEXT,
  tss          TEXT, -- Kept as TEXT due to ranges like '50-300'
  ph           TEXT, -- Kept as TEXT due to ranges like '6.0-9.0'
  bod          TEXT, -- Kept as TEXT due to ranges like '100-300'
  cod          TEXT, -- Kept as TEXT due to ranges like '250-600'
  nitrate      TEXT, -- Kept as TEXT due to ranges like '5-30'
  phosphate    TEXT, -- Kept as TEXT due to ranges like '2-15'
  ammonia      TEXT, -- Kept as TEXT due to ranges like '0-5'
  chloride     TEXT, -- Kept as TEXT due to ranges like '0-10'
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3) Triggers for 'updated_at'

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_district_data_updated_at') THEN
    CREATE TRIGGER trg_district_data_updated_at BEFORE UPDATE ON district_data
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_plant_data_updated_at') THEN
    CREATE TRIGGER trg_plant_data_updated_at BEFORE UPDATE ON plant_data
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_nbs_options_updated_at') THEN
    CREATE TRIGGER trg_nbs_options_updated_at BEFORE UPDATE ON nbs_options
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_nbs_implementation_updated_at') THEN
    CREATE TRIGGER trg_nbs_implementation_updated_at BEFORE UPDATE ON nbs_implementation
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_water_data_updated_at') THEN
    CREATE TRIGGER trg_water_data_updated_at BEFORE UPDATE ON water_data
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;

-- 4) Indexes for faster lookups

CREATE INDEX IF NOT EXISTS idx_district_data_state_name ON district_data (lower(state_name));
CREATE INDEX IF NOT EXISTS idx_plant_data_state_name ON plant_data (lower(state_name));
CREATE INDEX IF NOT EXISTS idx_nbs_options_state_name ON nbs_options (lower(state_name));
CREATE INDEX IF NOT EXISTS idx_nbs_options_solution ON nbs_options (lower(solution));
CREATE INDEX IF NOT EXISTS idx_nbs_implementation_solution ON nbs_implementation (lower(solution));

COMMIT;

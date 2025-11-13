-- schemas/init.sql
SET client_min_messages = WARNING;
SET TimeZone = 'UTC';

-- 1) helper to auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2) tables

-- state/district → soil
CREATE TABLE IF NOT EXISTS merged_district_data (
  id            SERIAL PRIMARY KEY,
  state_name    TEXT NOT NULL,
  district_name TEXT NULL,
  soil_type     TEXT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- plants
CREATE TABLE IF NOT EXISTS plant_data (
  id                       SERIAL PRIMARY KEY,
  plant_species            TEXT NOT NULL,
  locational_availability  TEXT NULL,
  climate_preference       TEXT NULL,
  soil_type                TEXT NULL,
  water_needs              TEXT NULL,
  ecological_role          TEXT NULL,
  pollution_tolerance      TEXT NULL,
  state_name               TEXT NOT NULL,
  optimal_water_type       TEXT NOT NULL,
  created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- NbS options
CREATE TABLE IF NOT EXISTS nbs_options (
  id                     SERIAL PRIMARY KEY,
  solution               TEXT NOT NULL,
  optimal_water_type     TEXT NOT NULL,
  location_suitability   TEXT NULL,
  climate_suitability    TEXT NULL,
  soil_type              TEXT NULL,
  resource_requirements  TEXT NULL,
  notes                  TEXT NULL,
  state_name             TEXT NOT NULL,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Implementation guides (one per solution name)
CREATE TABLE IF NOT EXISTS nbs_implementation (
  id                         SERIAL PRIMARY KEY,
  solution                   TEXT NOT NULL,
  implementation_steps       TEXT NULL,
  maintenance_requirements   TEXT NULL,
  created_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- water data (optional persistence)
CREATE TABLE IF NOT EXISTS water_data (
  id           SERIAL PRIMARY KEY,
  water_type   TEXT NULL,
  colour       TEXT NULL,
  odour        TEXT NULL,
  turbidity    DOUBLE PRECISION NULL,
  temperature  DOUBLE PRECISION NULL,
  tss          DOUBLE PRECISION NULL,
  ph           DOUBLE PRECISION NULL,
  bod          DOUBLE PRECISION NULL,
  cod          DOUBLE PRECISION NULL,
  nitrate      DOUBLE PRECISION NULL,
  phosphate    DOUBLE PRECISION NULL,
  ammonia      DOUBLE PRECISION NULL,
  chloride     DOUBLE PRECISION NULL,
  sample_source TEXT NULL,
  sample_timestamp TIMESTAMPTZ NULL,
  raw_data     TEXT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3) indexes & constraints (idempotent)

-- soil/state lookups
CREATE INDEX IF NOT EXISTS idx_mdd_state_lower
  ON merged_district_data (lower(state_name));

-- plant queries
CREATE INDEX IF NOT EXISTS idx_plant_state_water
  ON plant_data (lower(state_name), lower(optimal_water_type));
CREATE INDEX IF NOT EXISTS idx_plant_soil_lower
  ON plant_data (lower(soil_type));

-- nbs queries
CREATE INDEX IF NOT EXISTS idx_nbs_state_water
  ON nbs_options (lower(state_name), lower(optimal_water_type));
CREATE INDEX IF NOT EXISTS idx_nbs_solution_lower
  ON nbs_options (lower(solution));

-- unique(LOWER(solution)) for implementation to avoid duplicates
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE c.relkind='i' AND c.relname='uq_impl_solution_lower'
  ) THEN
    CREATE UNIQUE INDEX uq_impl_solution_lower
      ON nbs_implementation (lower(solution));
  END IF;
END $$;

-- 4) updated_at triggers
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_mdd_updated_at') THEN
    CREATE TRIGGER trg_mdd_updated_at BEFORE UPDATE ON merged_district_data
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_plant_updated_at') THEN
    CREATE TRIGGER trg_plant_updated_at BEFORE UPDATE ON plant_data
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_nbsopt_updated_at') THEN
    CREATE TRIGGER trg_nbsopt_updated_at BEFORE UPDATE ON nbs_options
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_nbsimpl_updated_at') THEN
    CREATE TRIGGER trg_nbsimpl_updated_at BEFORE UPDATE ON nbs_implementation
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_water_updated_at') THEN
    CREATE TRIGGER trg_water_updated_at BEFORE UPDATE ON water_data
      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;


-- Narmada NbS Toolkit — PostgreSQL schema (Azure). Regenerated from live DB.
-- `sources` is the provenance backbone. Load:  \copy <table> FROM 'db/<table>.csv' CSV HEADER;

CREATE TABLE sources (
  id INTEGER,
  short TEXT,
  citation TEXT,
  type TEXT,
  url TEXT,
  license TEXT
);

CREATE TABLE basins (
  id INTEGER,
  basin TEXT,
  sub_basin TEXT,
  description TEXT,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE regions (
  id INTEGER,
  camels_gauge_id INTEGER,
  station TEXT,
  river TEXT,
  district TEXT,
  cwc_site_type TEXT,
  is_wq_station INTEGER,
  rainfall_mm_yr REAL,
  wet_season TEXT,
  dry_season TEXT,
  tmin_C REAL,
  tmax_C REAL,
  aridity_P_PET REAL,
  pet_mm_yr REAL,
  sand_pct INTEGER,
  silt_pct INTEGER,
  clay_pct INTEGER,
  soil_type TEXT,
  hydrologic_soil_group TEXT,
  soil_depth_m REAL,
  soil_avail_water_mm_m INTEGER,
  basin_id INTEGER REFERENCES basins(id),
  source_climate_soil INTEGER,
  source_district INTEGER,
  infiltration_class TEXT,
  lat REAL,
  lon REAL
);

CREATE TABLE site_attributes (
  id INTEGER,
  region_id INTEGER REFERENCES regions(id),
  gauge_id INTEGER,
  station TEXT,
  elev_mean REAL,
  elev_min INTEGER,
  elev_max INTEGER,
  slope_mean REAL,
  slope_median REAL,
  drainage_area_km2 REAL,
  dpsbar REAL,
  water_frac REAL,
  trees_frac REAL,
  agri_frac REAL,
  builtup_frac REAL,
  bare_frac REAL,
  range_frac REAL,
  dom_land_cover TEXT,
  lai_mean REAL,
  stream_order REAL,
  dilution_proxy REAL,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE pollution_sources (
  id INTEGER,
  region_id INTEGER REFERENCES regions(id),
  gauge_id INTEGER,
  station TEXT,
  source_type TEXT,
  category TEXT,
  indicator TEXT,
  value REAL,
  unit TEXT,
  note TEXT,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE water_observations (
  id INTEGER,
  station TEXT,
  district TEXT,
  state TEXT,
  cwc_code TEXT,
  parameter TEXT,
  unit TEXT,
  value_mean REAL,
  value_min REAL,
  value_max REAL,
  n_samples INTEGER,
  period TEXT,
  basin_id INTEGER REFERENCES basins(id),
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE standards (
  id INTEGER,
  use_case TEXT,
  parameter TEXT,
  limit_low REAL,
  limit_high REAL,
  direction TEXT,
  unit TEXT,
  source_id INTEGER REFERENCES sources(id),
  note TEXT
);

CREATE TABLE plants (
  id INTEGER,
  plant_species TEXT,
  locational_availability TEXT,
  climate_preference TEXT,
  soil_type TEXT,
  water_needs TEXT,
  ecological_role TEXT,
  plant_type TEXT,
  native_status TEXT,
  invasive INTEGER,
  metals_pollutants TEXT,
  evidence_note TEXT,
  pollution_tolerance TEXT,
  optimal_water_type TEXT,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE nbs_options (
  id INTEGER,
  solution TEXT,
  family TEXT,
  description TEXT,
  optimal_water_type TEXT,
  location_suitability REAL,
  climate_suitability TEXT,
  soil_type REAL,
  resource_requirements REAL,
  notes REAL,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE nbs_implementation (
  id INTEGER,
  nbs_id INTEGER REFERENCES nbs_options(id),
  solution TEXT,
  implementation_steps TEXT,
  maintenance_requirements TEXT,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE removal_efficiency (
  id INTEGER,
  nbs TEXT,
  nbs_id INTEGER REFERENCES nbs_options(id),
  parameter TEXT,
  eff_low REAL,
  eff_high REAL,
  confidence TEXT,
  source_id INTEGER REFERENCES sources(id),
  note TEXT
);

CREATE TABLE plant_solution_map (
  id INTEGER,
  plant_id INTEGER REFERENCES plants(id),
  plant_species TEXT,
  nbs_id INTEGER REFERENCES nbs_options(id),
  solution TEXT,
  basis TEXT,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE water_type_profiles (
  id INTEGER,
  water_type TEXT,
  parameter TEXT,
  value_low REAL,
  value_high REAL,
  unit TEXT,
  note TEXT,
  deprecated INTEGER,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE nbs_criteria (
  id INTEGER,
  nbs_id INTEGER REFERENCES nbs_options(id),
  criterion TEXT,
  value_qual TEXT,
  confidence TEXT,
  source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE nbs_footprint (
  id INTEGER,
  nbs_id INTEGER REFERENCES nbs_options(id),
  area_per_pe_low REAL,
  area_per_pe_high REAL,
  olr_g_m2_d REAL,
  olr_basis TEXT,
  hlr_m3_m2_d REAL,
  depth_m REAL,
  source_id INTEGER REFERENCES sources(id),
  note TEXT
);

CREATE INDEX idx_wq_station ON water_observations(station);
CREATE INDEX idx_rem_nbs ON removal_efficiency(nbs_id);
CREATE INDEX idx_sa_region ON site_attributes(region_id);
CREATE INDEX idx_ps_region ON pollution_sources(region_id);
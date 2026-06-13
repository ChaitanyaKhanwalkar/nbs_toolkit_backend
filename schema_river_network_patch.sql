-- Narmada NbS Toolkit — river network patch
-- Adds HydroRIVERS source, river_network table, site_stream_attributes table,
-- and updates site_attributes.stream_order from station nearest-river join.

INSERT INTO sources (id, short, citation, type, url, license)
VALUES (
  56,
  'HydroRIVERS_v10_HydroSHEDS',
  'Lehner, B. and Grill, G. (2013). Global river hydrography and network routing: baseline data and new approaches to study the world''s large river systems. Hydrological Processes 27(15):2171–2186. HydroRIVERS v1.0 / HydroSHEDS.',
  'dataset',
  'https://www.hydrosheds.org/products/hydrorivers',
  'HydroSHEDS license agreement; freely available for scientific, educational and commercial use with attribution'
)
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS river_network (
  id INTEGER PRIMARY KEY,
  hyriv_id INTEGER,
  next_down INTEGER,
  main_riv INTEGER,
  length_km REAL,
  dist_dn_km REAL,
  dist_up_km REAL,
  catch_skm REAL,
  upland_skm REAL,
  endorheic INTEGER,
  dis_av_cms REAL,
  ord_stra INTEGER,
  ord_clas INTEGER,
  ord_flow INTEGER,
  hybas_l12 INTEGER,
  geometry_wkt TEXT,
  source_id INTEGER REFERENCES sources(id)
);

CREATE INDEX IF NOT EXISTS idx_river_network_hyriv ON river_network(hyriv_id);
CREATE INDEX IF NOT EXISTS idx_river_network_stra ON river_network(ord_stra);
CREATE INDEX IF NOT EXISTS idx_river_network_hybas ON river_network(hybas_l12);

CREATE TABLE IF NOT EXISTS site_stream_attributes (
  id INTEGER PRIMARY KEY,
  region_id INTEGER REFERENCES regions(id),
  gauge_id INTEGER,
  station TEXT,
  ghi_stn_id TEXT,
  cwc_river TEXT,
  stream_order INTEGER,
  ord_clas INTEGER,
  ord_flow INTEGER,
  river_discharge_cms REAL,
  upland_skm REAL,
  catch_skm REAL,
  nearest_distance_deg REAL,
  nearest_distance_m REAL,
  station_lon REAL,
  station_lat REAL,
  nearest_lon REAL,
  nearest_lat REAL,
  hybas_l12 INTEGER,
  source_id INTEGER REFERENCES sources(id)
);

CREATE INDEX IF NOT EXISTS idx_site_stream_gauge ON site_stream_attributes(gauge_id);
CREATE INDEX IF NOT EXISTS idx_site_stream_region ON site_stream_attributes(region_id);

-- After loading site_stream_attributes, run:
-- UPDATE site_attributes
-- SET stream_order = (
--   SELECT stream_order FROM site_stream_attributes ssa
--   WHERE ssa.gauge_id = site_attributes.gauge_id
-- )
-- WHERE gauge_id IN (SELECT gauge_id FROM site_stream_attributes);

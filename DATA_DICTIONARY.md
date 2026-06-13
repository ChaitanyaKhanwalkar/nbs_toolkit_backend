# Narmada NbS Toolkit — Database & Data Dictionary

Production data layer for the basin-locked NbS recommendation engine. **15 tables**, all keyed to
`sources` (55 sources). Artifacts: `narmada_nbs.db` (SQLite), `schema.sql` (PostgreSQL DDL),
`db/*.csv`. FK integrity verified clean. Never-invent rule observed — unsourced cells are NULL + logged.

## Tables
| Table | Rows | Source(s) | Notes |
|---|---|---|---|
| sources | 55 | — | provenance registry |
| basins | 4 | NRCD/cNarmada | Narmada + sub-basins |
| regions | 52 | CAMELS-IND; hydrology report | per-site climate+soil+district+**lat/lon**+infiltration_class |
| site_attributes | 52 | CAMELS-IND (topo+land) | **NEW** — elevation, slope, drainage area, %agri, %builtup, land cover |
| pollution_sources | 135 | CAMELS-IND (anth+land) | **NEW** — non-point (diffuse) pressure per catchment; point sources pending |
| water_observations | 625 | CWC NBO Data Book 2023-24 | measured WQ, 33 sites |
| standards | 30 | IS 10500 / CPCB A–E / EP Rules | 4 use_cases |
| plants | 25 | phytoremediation lit + legacy | 18 cited; invasives flagged |
| nbs_options | 28 | Eawag/CPHEEO/lit | expanded taxonomy |
| nbs_implementation | 28 | Eawag/CPHEEO/legacy | steps + maintenance |
| removal_efficiency | 95 | lit | 92 ranges + 3 gaps |
| plant_solution_map | 149 | derived (role-based) | needs supervisor validation |
| water_type_profiles | 48 | lit + legacy | fallback typology |
| nbs_footprint | 9 | lit/manuals | 9/28 techs |
| nbs_criteria | 19 | lit/manuals | MCDA scores, 10/28 techs |

## NBS taxonomy (28 technologies)
- **Constructed Wetlands** (9)
- **Ponds & Lagoons** (5)
- **Stormwater & Green Infrastructure** (5)
- **Infiltration & Soil Systems** (3)
- **Aquaculture & Resource Recovery** (1)
- **Anaerobic & Intensified Decentralized** (5)

## Site-profile / GIS layer (NEW this build)
- **regions.lat/lon** added for all 52 catchments (CAMELS topo, WGS84).
- **site_attributes** (52/52 catchments): elev_mean/min/max, slope_mean, drainage_area_km2,
  agri_frac (crops), builtup_frac (built area), trees/water/bare/range fractions, dom_land_cover, lai_mean,
  dpsbar. `stream_order` is NULL — interim **dilution_proxy = drainage_area_km2**; true Strahler order needs
  HydroRIVERS/India-WRIS river-line network (the uploaded shapefiles were .xml metadata only).
- **pollution_sources** (135 rows, all non-point): per catchment, agricultural-runoff
  (crops_frac), urban-runoff (built_area_frac + pop density), and dam/flow-regulation pressure. Point sources
  (industrial/STP discharges) pending a CPCB/State-PCB/NMCG inventory.
- All from CAMELS-IND = **source 4** (already cited); no new sources needed.

## How it connects to the engine (MCDA)
Measured load (`water_observations`, else `water_type_profiles`) → exceedances vs `standards[use_case]` →
treatment fit via `removal_efficiency` → **site fit via `regions.infiltration_class` + `site_attributes`
(slope/land cover) + `pollution_sources` pressure + dilution proxy** → species via `plant_solution_map`/`plants`
→ steps via `nbs_implementation`. Cost/space/co-benefit criteria from `nbs_footprint` + `nbs_criteria`.
Every output row carries `source_id`.

## PLAN_v3 §4.1 table status
- Built: sources, basins, regions(+coords), site_attributes, pollution_sources(non-point), water_observations,
  standards, plants, nbs_options, nbs_implementation, removal_efficiency, plant_solution_map, nbs_footprint, nbs_criteria.
- **Pending:** `river_network` (need .shp binaries or HydroRIVERS); `health_risk` (supervisor's file, available);
  `criteria_weights` (AHP output — worksheet to be filled with supervisor); point-source `pollution_sources`
  (CPCB inventory); true Strahler `stream_order`.

## Key caveats
- BOD = BOD₃@27°C (matches discharge standard); CWC does not measure COD.
- regions/site_attributes soil & terrain from CAMELS-IND global datasets (HWSD/HiHydroSoil/SRTM/ESRI LULC),
  catchment-averaged — not NBSS&LUP/CartoDEM. Land cover is ESRI 2017–2022.
- gauge_id join: site_attributes/regions joined to CAMELS by gauge_id (all 52 matched).
- plant_solution_map role-based & needs expert validation; nbs_footprint/criteria partial.

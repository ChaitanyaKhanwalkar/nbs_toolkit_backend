# PostgreSQL Migration Verification

This report compares the canonical SQLite mirror with PostgreSQL when a PostgreSQL URL is supplied.

## Expected Canonical Counts

| Table | Expected | SQLite actual | Status |
|---|---:|---:|---|
| sources | 109 | 109 | ok |
| nbs_options | 28 | 28 | ok |
| removal_efficiency | 167 | 167 | ok |
| treatment_train | 8 | 8 | ok |
| ambient_water_quality | 47244 | 47244 | ok |
| river_network | 6339 | 6339 | ok |
| site_attributes | 52 | 52 | ok |
| pollution_sources | 155 | 155 | ok |

## SQLite Table Counts

| Table | Rows |
|---|---:|
| ambient_water_quality | 47244 |
| app_caveats | 7 |
| app_context_rules | 6 |
| app_district_profile_cache | 45 |
| app_input_template | 49 |
| app_layer_metadata | 7 |
| app_parameter_aliases | 15 |
| basins | 4 |
| column_provenance | 324 |
| cost_benefit_component_weights | 14 |
| cost_benefit_method | 1 |
| criteria_weights | 21 |
| dim_confidence | 5 |
| dim_country | 6 |
| dim_nbs_family | 6 |
| dim_parameter | 72 |
| dim_provenance_status | 3 |
| dim_scale | 11 |
| dim_source_type | 10 |
| dim_unit | 10 |
| dim_use_case | 4 |
| engine_data_fix_log | 4 |
| narmada_agriculture_metrics | 13 |
| narmada_groundwater_wells | 143 |
| narmada_hydrology_stations | 30 |
| narmada_infrastructure_assets | 166 |
| narmada_lulc_area | 1032 |
| narmada_map_layers_catalog | 8 |
| narmada_mining_anomalies | 19 |
| narmada_nutrient_sediment_metrics | 52 |
| narmada_topography_metrics | 11 |
| narmada_water_quality_report_stats | 85 |
| nbs_applicability_rules | 46 |
| nbs_design | 17 |
| nbs_footprint | 19 |
| nbs_implementation | 28 |
| nbs_options | 28 |
| plant_solution_map | 118 |
| plants | 25 |
| pollution_sources | 155 |
| regions | 52 |
| removal_efficiency | 167 |
| report_source_catalog | 12 |
| reuse_health_guidance | 21 |
| river_network | 6339 |
| site_attributes | 52 |
| sources | 109 |
| standards | 38 |
| standards_gapfix_review_log | 12 |
| standards_guidance_bands | 15 |
| train_performance | 40 |
| train_step | 23 |
| train_usecase_match | 64 |
| treatment_train | 8 |
| water_observations | 625 |
| water_type_profile_change_log | 3 |
| water_type_profile_source_map | 24 |
| water_type_profiles | 54 |

## PostgreSQL Comparison

| Table | SQLite | PostgreSQL | Status |
|---|---:|---:|---|
| ambient_water_quality | 47244 | 47244 | ok |
| app_caveats | 7 | 7 | ok |
| app_context_rules | 6 | 6 | ok |
| app_district_profile_cache | 45 | 45 | ok |
| app_input_template | 49 | 49 | ok |
| app_layer_metadata | 7 | 7 | ok |
| app_parameter_aliases | 15 | 15 | ok |
| basins | 4 | 4 | ok |
| column_provenance | 324 | 324 | ok |
| cost_benefit_component_weights | 14 | 14 | ok |
| cost_benefit_method | 1 | 1 | ok |
| criteria_weights | 21 | 21 | ok |
| dim_confidence | 5 | 5 | ok |
| dim_country | 6 | 6 | ok |
| dim_nbs_family | 6 | 6 | ok |
| dim_parameter | 72 | 72 | ok |
| dim_provenance_status | 3 | 3 | ok |
| dim_scale | 11 | 11 | ok |
| dim_source_type | 10 | 10 | ok |
| dim_unit | 10 | 10 | ok |
| dim_use_case | 4 | 4 | ok |
| engine_data_fix_log | 4 | 4 | ok |
| narmada_agriculture_metrics | 13 | 13 | ok |
| narmada_groundwater_wells | 143 | 143 | ok |
| narmada_hydrology_stations | 30 | 30 | ok |
| narmada_infrastructure_assets | 166 | 166 | ok |
| narmada_lulc_area | 1032 | 1032 | ok |
| narmada_map_layers_catalog | 8 | 8 | ok |
| narmada_mining_anomalies | 19 | 19 | ok |
| narmada_nutrient_sediment_metrics | 52 | 52 | ok |
| narmada_topography_metrics | 11 | 11 | ok |
| narmada_water_quality_report_stats | 85 | 85 | ok |
| nbs_applicability_rules | 46 | 46 | ok |
| nbs_design | 17 | 17 | ok |
| nbs_footprint | 19 | 19 | ok |
| nbs_implementation | 28 | 28 | ok |
| nbs_options | 28 | 28 | ok |
| plant_solution_map | 118 | 118 | ok |
| plants | 25 | 25 | ok |
| pollution_sources | 155 | 155 | ok |
| regions | 52 | 52 | ok |
| removal_efficiency | 167 | 167 | ok |
| report_source_catalog | 12 | 12 | ok |
| reuse_health_guidance | 21 | 21 | ok |
| river_network | 6339 | 6339 | ok |
| site_attributes | 52 | 52 | ok |
| sources | 109 | 109 | ok |
| standards | 38 | 38 | ok |
| standards_gapfix_review_log | 12 | 12 | ok |
| standards_guidance_bands | 15 | 15 | ok |
| train_performance | 40 | 40 | ok |
| train_step | 23 | 23 | ok |
| train_usecase_match | 64 | 64 | ok |
| treatment_train | 8 | 8 | ok |
| water_observations | 625 | 625 | ok |
| water_type_profile_change_log | 3 | 3 | ok |
| water_type_profile_source_map | 24 | 24 | ok |
| water_type_profiles | 54 | 54 | ok |

## View Check

- SQLite views: 18
- Matching PostgreSQL view names: 18
- Missing/commented/manual-review view names: 0

## Failures

- None.

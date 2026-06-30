# SQLite Schema Audit

Source database: `canonical db\narmada_nbs_canonical.db`

## Summary

- SQLite table count including internal tables: 59
- User table count generated for PostgreSQL: 58
- View count: 18
- Integrity check: `ok`
- SQLite internal objects present: yes
- SQLite internal objects should be skipped during PostgreSQL migration.

## Expected Count Check

All key expected counts match the live canonical DB signature.

## Row Counts

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

## Tables, Columns, Primary Keys, Indexes, Foreign Keys

### `ambient_water_quality`

Rows: `47244`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| station | TEXT | 0 | 0 |  |
| region_id | REAL | 0 | 0 |  |
| season | TEXT | 0 | 0 |  |
| year | TEXT | 0 | 0 |  |
| value | REAL | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| needs_verification | INTEGER | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| parameter_id | INTEGER | 0 | 0 |  |
| unit_id | REAL | 0 | 0 |  |

Indexes:
- `ix_ambient_water_quality_source_id` unique=False origin=c
- `ix_ambient_water_quality_region_id` unique=False origin=c
- `ix_ambient_water_quality_parameter_id` unique=False origin=c

### `app_caveats`

Rows: `7`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| caveat_key | TEXT | 1 | 0 |  |
| severity | TEXT | 1 | 0 |  |
| title | TEXT | 1 | 0 |  |
| plain_language_message | TEXT | 1 | 0 |  |
| technical_note | TEXT | 0 | 0 |  |
| affected_tables | TEXT | 0 | 0 |  |
| status | TEXT | 1 | 0 |  |
| action_needed | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `idx_app_caveats_status_severity` unique=False origin=c
- `sqlite_autoindex_app_caveats_1` unique=True origin=u

### `app_context_rules`

Rows: `6`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| rule_key | TEXT | 1 | 0 |  |
| rule_group | TEXT | 1 | 0 |  |
| plain_language_rule | TEXT | 1 | 0 |  |
| technical_expression | TEXT | 1 | 0 |  |
| app_action | TEXT | 1 | 0 |  |
| caveat | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `sqlite_autoindex_app_context_rules_1` unique=True origin=u

### `app_district_profile_cache`

Rows: `45`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| district | TEXT | 1 | 0 |  |
| state_guess | TEXT | 0 | 0 |  |
| station_count | INTEGER | 0 | 0 |  |
| representative_stations | TEXT | 0 | 0 |  |
| lat_mean | REAL | 0 | 0 |  |
| lon_mean | REAL | 0 | 0 |  |
| rainfall_mm_yr_mean | REAL | 0 | 0 |  |
| tmin_c_mean | REAL | 0 | 0 |  |
| tmax_c_mean | REAL | 0 | 0 |  |
| soil_types | TEXT | 0 | 0 |  |
| infiltration_classes | TEXT | 0 | 0 |  |
| slope_mean | REAL | 0 | 0 |  |
| stream_order_strahler_max | INTEGER | 0 | 0 |  |
| nat_discharge_cms_mean | REAL | 0 | 0 |  |
| site_agri_pct | REAL | 0 | 0 |  |
| site_builtup_pct | REAL | 0 | 0 |  |
| site_trees_pct | REAL | 0 | 0 |  |
| lulc_2024_agriculture_pct | REAL | 0 | 0 |  |
| lulc_2024_builtup_pct | REAL | 0 | 0 |  |
| lulc_2024_forest_pct | REAL | 0 | 0 |  |
| lulc_2024_water_pct | REAL | 0 | 0 |  |
| domestic_sewage_mld | REAL | 0 | 0 |  |
| industrial_wastewater_mld | REAL | 0 | 0 |  |
| stp_capacity_operational_mld | REAL | 0 | 0 |  |
| stp_capacity_under_construction_mld | REAL | 0 | 0 |  |
| stp_count_operational | REAL | 0 | 0 |  |
| stp_count_under_construction | REAL | 0 | 0 |  |
| dominant_pressure_label | TEXT | 0 | 0 |  |
| recommended_pathway_label | TEXT | 0 | 0 |  |
| location_caution | TEXT | 0 | 0 |  |
| data_confidence_label | TEXT | 0 | 0 |  |
| evidence_source_ids | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `idx_app_district_profile_district` unique=False origin=c
- `sqlite_autoindex_app_district_profile_cache_1` unique=True origin=u

### `app_input_template`

Rows: `49`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| use_case | TEXT | 1 | 0 |  |
| canonical_parameter | TEXT | 1 | 0 |  |
| user_label | TEXT | 1 | 0 |  |
| default_unit | TEXT | 0 | 0 |  |
| is_required | INTEGER | 1 | 0 | `0` |
| priority | TEXT | 1 | 0 | `'recommended'` |
| why_needed | TEXT | 0 | 0 |  |
| example_value_note | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `idx_app_input_template_usecase` unique=False origin=c

### `app_layer_metadata`

Rows: `7`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| layer_name | TEXT | 1 | 0 |  |
| layer_type | TEXT | 1 | 0 |  |
| purpose | TEXT | 1 | 0 |  |
| source_tables | TEXT | 1 | 0 |  |
| api_use | TEXT | 0 | 0 |  |
| caveat | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `sqlite_autoindex_app_layer_metadata_1` unique=True origin=u

### `app_parameter_aliases`

Rows: `15`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| canonical_parameter | TEXT | 1 | 0 |  |
| user_label | TEXT | 1 | 0 |  |
| upload_aliases | TEXT | 1 | 0 |  |
| common_units | TEXT | 0 | 0 |  |
| parameter_group | TEXT | 0 | 0 |  |
| recommended_for_upload | INTEGER | 1 | 0 | `1` |
| plain_language_help | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `idx_app_parameter_aliases_param` unique=False origin=c

### `basins`

Rows: `4`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| basin | TEXT | 0 | 0 |  |
| sub_basin | TEXT | 0 | 0 |  |
| description | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |

### `column_provenance`

Rows: `324`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| table_name | TEXT | 0 | 0 |  |
| column | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| source_ids | TEXT | 0 | 0 |  |
| status_id | INTEGER | 0 | 0 |  |

### `cost_benefit_component_weights`

Rows: `14`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| method_key | TEXT | 1 | 0 |  |
| component_key | TEXT | 1 | 0 |  |
| component_label | TEXT | 1 | 0 |  |
| side | TEXT | 1 | 0 |  |
| weight | REAL | 1 | 0 |  |
| direction | TEXT | 1 | 0 |  |
| source_field | TEXT | 0 | 0 |  |
| notes | TEXT | 0 | 0 |  |

Indexes:
- `sqlite_autoindex_cost_benefit_component_weights_1` unique=True origin=u

### `cost_benefit_method`

Rows: `1`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| method_key | TEXT | 1 | 0 |  |
| method_name | TEXT | 1 | 0 |  |
| version | TEXT | 1 | 0 |  |
| is_monetary | INTEGER | 1 | 0 | `0` |
| formula_text | TEXT | 1 | 0 |  |
| denominator_floor | REAL | 1 | 0 | `0.20` |
| display_cap | REAL | 0 | 0 |  |
| caveat_text | TEXT | 1 | 0 |  |
| created_at | TEXT | 0 | 0 | `CURRENT_TIMESTAMP` |

Indexes:
- `sqlite_autoindex_cost_benefit_method_1` unique=True origin=u

### `criteria_weights`

Rows: `21`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| use_case_id | INTEGER | 0 | 0 |  |
| use_case | TEXT | 1 | 0 |  |
| criterion_code | TEXT | 1 | 0 |  |
| criterion_name | TEXT | 1 | 0 |  |
| weight | REAL | 1 | 0 |  |
| benefit_or_cost | TEXT | 1 | 0 |  |
| status | TEXT | 1 | 0 |  |
| derivation_note | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 | `104` |
| provenance_status_id | INTEGER | 0 | 0 | `2` |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `idx_criteria_weights_use_case` unique=False origin=c
- `sqlite_autoindex_criteria_weights_1` unique=True origin=u

### `dim_confidence`

Rows: `5`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_confidence_name` unique=True origin=c

### `dim_country`

Rows: `6`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_country_name` unique=True origin=c

### `dim_nbs_family`

Rows: `6`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_nbs_family_name` unique=True origin=c

### `dim_parameter`

Rows: `72`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_parameter_name` unique=True origin=c

### `dim_provenance_status`

Rows: `3`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_provenance_status_name` unique=True origin=c

### `dim_scale`

Rows: `11`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_scale_name` unique=True origin=c

### `dim_source_type`

Rows: `10`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_source_type_name` unique=True origin=c

### `dim_unit`

Rows: `10`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_unit_name` unique=True origin=c

### `dim_use_case`

Rows: `4`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| name | TEXT | 0 | 0 |  |

Indexes:
- `idx_dim_use_case_name` unique=True origin=c

### `engine_data_fix_log`

Rows: `4`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| fix_key | TEXT | 1 | 0 |  |
| fix_summary | TEXT | 1 | 0 |  |
| created_at | TEXT | 1 | 0 |  |
| source_id | INTEGER | 0 | 0 | `104` |
| provenance_status_id | INTEGER | 0 | 0 | `2` |

### `narmada_agriculture_metrics`

Rows: `13`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| spatial_unit_type | TEXT | 0 | 0 |  |
| spatial_unit_name | TEXT | 0 | 0 |  |
| district | TEXT | 0 | 0 |  |
| year | TEXT | 0 | 0 |  |
| metric | TEXT | 0 | 0 |  |
| value_text | TEXT | 0 | 0 |  |
| value_low | REAL | 0 | 0 |  |
| value_high | REAL | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_groundwater_wells`

Rows: `143`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| well_id | TEXT | 0 | 0 |  |
| district | TEXT | 0 | 0 |  |
| block_name | TEXT | 0 | 0 |  |
| village | TEXT | 0 | 0 |  |
| lat | REAL | 0 | 0 |  |
| lon | REAL | 0 | 0 |  |
| geometry_wkt | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_hydrology_stations`

Rows: `30`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| station_name | TEXT | 0 | 0 |  |
| agency | TEXT | 0 | 0 |  |
| state | TEXT | 0 | 0 |  |
| station_type | TEXT | 0 | 0 |  |
| lat | REAL | 0 | 0 |  |
| lon | REAL | 0 | 0 |  |
| zero_gauge_m | REAL | 0 | 0 |  |
| max_level_m | REAL | 0 | 0 |  |
| min_level_m | REAL | 0 | 0 |  |
| avg_level_m | REAL | 0 | 0 |  |
| max_discharge_cumec | REAL | 0 | 0 |  |
| min_discharge_cumec | REAL | 0 | 0 |  |
| avg_discharge_cumec | REAL | 0 | 0 |  |
| sub_basin | TEXT | 0 | 0 |  |
| geometry_wkt | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_infrastructure_assets`

Rows: `166`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| basin_segment | TEXT | 0 | 0 |  |
| district | TEXT | 0 | 0 |  |
| town_area | TEXT | 0 | 0 |  |
| asset_type | TEXT | 0 | 0 |  |
| asset_name | TEXT | 0 | 0 |  |
| status | TEXT | 0 | 0 |  |
| count_value | REAL | 0 | 0 |  |
| capacity_value | REAL | 0 | 0 |  |
| capacity_unit | TEXT | 0 | 0 |  |
| generated_value | REAL | 0 | 0 |  |
| generated_unit | TEXT | 0 | 0 |  |
| technology | TEXT | 0 | 0 |  |
| reuse_value | REAL | 0 | 0 |  |
| reuse_unit | TEXT | 0 | 0 |  |
| network_length_km | REAL | 0 | 0 |  |
| connections | INTEGER | 0 | 0 |  |
| lat | REAL | 0 | 0 |  |
| lon | REAL | 0 | 0 |  |
| geometry_wkt | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_lulc_area`

Rows: `1032`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| spatial_unit_type | TEXT | 0 | 0 |  |
| spatial_unit_name | TEXT | 0 | 0 |  |
| district | TEXT | 0 | 0 |  |
| state | TEXT | 0 | 0 |  |
| year | INTEGER | 0 | 0 |  |
| lulc_class | TEXT | 0 | 0 |  |
| area_km2 | REAL | 0 | 0 |  |
| percent_area | REAL | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_map_layers_catalog`

Rows: `8`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| layer_name | TEXT | 0 | 0 |  |
| geometry_type | TEXT | 0 | 0 |  |
| source_table | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| map_status | TEXT | 0 | 0 |  |
| join_key | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_mining_anomalies`

Rows: `19`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| severity | TEXT | 0 | 0 |  |
| domain | TEXT | 0 | 0 |  |
| item | TEXT | 0 | 0 |  |
| existing_value | TEXT | 0 | 0 |  |
| existing_source_id | TEXT | 0 | 0 |  |
| report_value | TEXT | 0 | 0 |  |
| report_source_id | TEXT | 0 | 0 |  |
| recommended_action | TEXT | 0 | 0 |  |
| status | TEXT | 0 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_nutrient_sediment_metrics`

Rows: `52`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| degree_sheet | TEXT | 0 | 0 |  |
| basin_zone | TEXT | 0 | 0 |  |
| district_coverage | TEXT | 0 | 0 |  |
| parameter | TEXT | 0 | 0 |  |
| value_min | REAL | 0 | 0 |  |
| value_max | REAL | 0 | 0 |  |
| value_avg | REAL | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| contribution_point | TEXT | 0 | 0 |  |
| contribution_nonpoint | TEXT | 0 | 0 |  |
| key_quantification | TEXT | 0 | 0 |  |
| primary_driver | TEXT | 0 | 0 |  |
| literature_authors | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_topography_metrics`

Rows: `11`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| spatial_unit_name | TEXT | 0 | 0 |  |
| metric_type | TEXT | 0 | 0 |  |
| class_label | TEXT | 0 | 0 |  |
| area_km2 | REAL | 0 | 0 |  |
| percent_area | REAL | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `narmada_water_quality_report_stats`

Rows: `85`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| report_file | TEXT | 0 | 0 |  |
| table_ref | TEXT | 0 | 0 |  |
| page_no | INTEGER | 0 | 0 |  |
| basin_segment | TEXT | 0 | 0 |  |
| district | TEXT | 0 | 0 |  |
| city_town | TEXT | 0 | 0 |  |
| station_name | TEXT | 0 | 0 |  |
| parameter | TEXT | 0 | 0 |  |
| value_mean | REAL | 0 | 0 |  |
| value_min | REAL | 0 | 0 |  |
| value_max | REAL | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| period | TEXT | 0 | 0 |  |
| lat | REAL | 0 | 0 |  |
| lon | REAL | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| provenance_status_id | INTEGER | 1 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `nbs_applicability_rules`

Rows: `46`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| rule_id | TEXT | 0 | 1 |  |
| is_active | INTEGER | 1 | 0 | `1` |
| target_level | TEXT | 1 | 0 |  |
| nbs_id | INTEGER | 0 | 0 |  |
| nbs_solution | TEXT | 0 | 0 |  |
| nbs_family_id | INTEGER | 0 | 0 |  |
| nbs_family | TEXT | 0 | 0 |  |
| train_id | INTEGER | 0 | 0 |  |
| train_name | TEXT | 0 | 0 |  |
| factor_name | TEXT | 1 | 0 |  |
| factor_source_field | TEXT | 0 | 0 |  |
| intervention_position | TEXT | 0 | 0 |  |
| operator | TEXT | 0 | 0 |  |
| value_min | REAL | 0 | 0 |  |
| value_max | REAL | 0 | 0 |  |
| category_value | TEXT | 0 | 0 |  |
| rule_type | TEXT | 1 | 0 |  |
| severity | TEXT | 1 | 0 |  |
| action | TEXT | 1 | 0 |  |
| score_modifier | REAL | 0 | 0 |  |
| confidence_modifier | REAL | 0 | 0 |  |
| user_message | TEXT | 1 | 0 |  |
| technical_reason | TEXT | 1 | 0 |  |
| evidence_status | TEXT | 1 | 0 |  |
| provenance_status_id | INTEGER | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| supporting_source_ids | TEXT | 0 | 0 |  |
| review_status | TEXT | 1 | 0 |  |
| notes | TEXT | 0 | 0 |  |

Indexes:
- `idx_nbs_app_rules_type` unique=False origin=c
- `idx_nbs_app_rules_target` unique=False origin=c
- `idx_nbs_app_rules_factor` unique=False origin=c
- `sqlite_autoindex_nbs_applicability_rules_1` unique=True origin=pk

### `nbs_design`

Rows: `17`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| nbs_id | INTEGER | 0 | 0 |  |
| pretreatment | TEXT | 0 | 0 |  |
| media_substrate | TEXT | 0 | 0 |  |
| hydraulic_config | TEXT | 0 | 0 |  |
| planting | TEXT | 0 | 0 |  |
| construction_notes | TEXT | 0 | 0 |  |
| startup_establishment | TEXT | 0 | 0 |  |
| om_routine | TEXT | 0 | 0 |  |
| om_periodic | TEXT | 0 | 0 |  |
| monitoring | TEXT | 0 | 0 |  |
| failure_modes | TEXT | 0 | 0 |  |
| skill_om_intensity | TEXT | 0 | 0 |  |
| climate_dependence | TEXT | 0 | 0 |  |
| source_ids | TEXT | 0 | 0 |  |

Indexes:
- `ix_nbs_design_nbs_id` unique=False origin=c

### `nbs_footprint`

Rows: `19`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| nbs_id | INTEGER | 0 | 0 |  |
| area_per_pe_low | REAL | 0 | 0 |  |
| area_per_pe_high | REAL | 0 | 0 |  |
| olr_g_m2_d | REAL | 0 | 0 |  |
| olr_basis | TEXT | 0 | 0 |  |
| hlr_m3_m2_d | REAL | 0 | 0 |  |
| depth_m | REAL | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |

Indexes:
- `ix_nbs_footprint_source_id` unique=False origin=c
- `ix_nbs_footprint_nbs_id` unique=False origin=c

### `nbs_implementation`

Rows: `28`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| nbs_id | INTEGER | 0 | 0 |  |
| implementation_steps | TEXT | 0 | 0 |  |
| maintenance_requirements | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |

Indexes:
- `ix_nbs_implementation_source_id` unique=False origin=c
- `ix_nbs_implementation_nbs_id` unique=False origin=c

### `nbs_options`

Rows: `28`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| solution | TEXT | 0 | 0 |  |
| description | TEXT | 0 | 0 |  |
| optimal_water_type | TEXT | 0 | 0 |  |
| location_suitability | TEXT | 0 | 0 |  |
| climate_suitability | TEXT | 0 | 0 |  |
| soil_type | TEXT | 0 | 0 |  |
| resource_requirements | TEXT | 0 | 0 |  |
| notes | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| family_id | INTEGER | 0 | 0 |  |
| energy_class | TEXT | 0 | 0 |  |

Indexes:
- `ix_nbs_options_family_id` unique=False origin=c

### `plant_solution_map`

Rows: `118`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| plant_id | INTEGER | 0 | 0 |  |
| nbs_id | INTEGER | 0 | 0 |  |
| basis | TEXT | 0 | 0 |  |
| confidence_id | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |

Indexes:
- `ix_plant_solution_map_confidence_id` unique=False origin=c
- `ix_plant_solution_map_source_id` unique=False origin=c
- `ix_plant_solution_map_nbs_id` unique=False origin=c
- `ix_plant_solution_map_plant_id` unique=False origin=c

### `plants`

Rows: `25`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| plant_species | TEXT | 0 | 0 |  |
| locational_availability | TEXT | 0 | 0 |  |
| climate_preference | TEXT | 0 | 0 |  |
| soil_type | TEXT | 0 | 0 |  |
| water_needs | TEXT | 0 | 0 |  |
| ecological_role | TEXT | 0 | 0 |  |
| plant_type | TEXT | 0 | 0 |  |
| native_status | TEXT | 0 | 0 |  |
| invasive | INTEGER | 0 | 0 |  |
| metals_pollutants | TEXT | 0 | 0 |  |
| evidence_note | TEXT | 0 | 0 |  |
| pollution_tolerance | TEXT | 0 | 0 |  |
| optimal_water_type | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |

### `pollution_sources`

Rows: `155`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| region_id | REAL | 0 | 0 |  |
| gauge_id | REAL | 0 | 0 |  |
| station | TEXT | 0 | 0 |  |
| source_type | TEXT | 0 | 0 |  |
| category | TEXT | 0 | 0 |  |
| indicator | TEXT | 0 | 0 |  |
| value | REAL | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |

Indexes:
- `ix_pollution_sources_source_id` unique=False origin=c
- `ix_pollution_sources_region_id` unique=False origin=c

### `regions`

Rows: `52`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| camels_gauge_id | INTEGER | 0 | 0 |  |
| station | TEXT | 0 | 0 |  |
| river | TEXT | 0 | 0 |  |
| district | TEXT | 0 | 0 |  |
| cwc_site_type | TEXT | 0 | 0 |  |
| is_wq_station | INTEGER | 0 | 0 |  |
| rainfall_mm_yr | REAL | 0 | 0 |  |
| wet_season | TEXT | 0 | 0 |  |
| dry_season | TEXT | 0 | 0 |  |
| tmin_C | REAL | 0 | 0 |  |
| tmax_C | REAL | 0 | 0 |  |
| aridity_P_PET | REAL | 0 | 0 |  |
| pet_mm_yr | REAL | 0 | 0 |  |
| sand_pct | INTEGER | 0 | 0 |  |
| silt_pct | INTEGER | 0 | 0 |  |
| clay_pct | INTEGER | 0 | 0 |  |
| soil_type | TEXT | 0 | 0 |  |
| hydrologic_soil_group | TEXT | 0 | 0 |  |
| soil_depth_m | REAL | 0 | 0 |  |
| soil_avail_water_mm_m | INTEGER | 0 | 0 |  |
| basin_id | INTEGER | 0 | 0 |  |
| source_climate_soil | INTEGER | 0 | 0 |  |
| source_district | INTEGER | 0 | 0 |  |
| infiltration_class | TEXT | 0 | 0 |  |
| lat | REAL | 0 | 0 |  |
| lon | REAL | 0 | 0 |  |

Indexes:
- `ix_regions_basin_id` unique=False origin=c

### `removal_efficiency`

Rows: `167`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| nbs_id | INTEGER | 0 | 0 |  |
| parameter_id | REAL | 0 | 0 |  |
| eff_low | REAL | 0 | 0 |  |
| eff_high | REAL | 0 | 0 |  |
| confidence_id | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| scale_id | INTEGER | 0 | 0 |  |
| country_id | TEXT | 0 | 0 |  |
| influent_context | TEXT | 0 | 0 |  |
| hrt_loading | TEXT | 0 | 0 |  |
| temp_climate | TEXT | 0 | 0 |  |
| needs_corroboration | INTEGER | 0 | 0 |  |

Indexes:
- `ix_removal_efficiency_confidence_id` unique=False origin=c
- `ix_removal_efficiency_country_id` unique=False origin=c
- `ix_removal_efficiency_scale_id` unique=False origin=c
- `ix_removal_efficiency_source_id` unique=False origin=c
- `ix_removal_efficiency_parameter_id` unique=False origin=c
- `ix_removal_efficiency_nbs_id` unique=False origin=c

### `report_source_catalog`

Rows: `12`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 1 | 0 |  |
| short | TEXT | 1 | 0 |  |
| report_file | TEXT | 1 | 0 |  |
| report_title | TEXT | 0 | 0 |  |
| report_year | TEXT | 0 | 0 |  |
| pages | INTEGER | 0 | 0 |  |
| extracted_text_chars | INTEGER | 0 | 0 |  |
| extraction_status | TEXT | 0 | 0 |  |
| primary_domains | TEXT | 0 | 0 |  |
| mining_note | TEXT | 0 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

### `reuse_health_guidance`

Rows: `21`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 0 | 0 |  |
| source_short | TEXT | 1 | 0 |  |
| source_pdf | TEXT | 0 | 0 |  |
| source_page | TEXT | 0 | 0 |  |
| use_case | TEXT | 1 | 0 |  |
| context | TEXT | 0 | 0 |  |
| parameter_or_measure | TEXT | 1 | 0 |  |
| value | TEXT | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| threshold_basis | TEXT | 0 | 0 |  |
| db_handling | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| created_at | TEXT | 0 | 0 | `CURRENT_DATE` |

Indexes:
- `sqlite_autoindex_reuse_health_guidance_1` unique=True origin=u

### `river_network`

Rows: `6339`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| hyriv_id | INTEGER | 0 | 0 |  |
| next_down | INTEGER | 0 | 0 |  |
| main_riv | INTEGER | 0 | 0 |  |
| length_km | REAL | 0 | 0 |  |
| dist_dn_km | REAL | 0 | 0 |  |
| dist_up_km | REAL | 0 | 0 |  |
| catch_skm | REAL | 0 | 0 |  |
| upland_skm | REAL | 0 | 0 |  |
| dis_av_cms | REAL | 0 | 0 |  |
| ord_stra | INTEGER | 0 | 0 |  |
| ord_clas | INTEGER | 0 | 0 |  |
| ord_flow | INTEGER | 0 | 0 |  |
| hybas_l12 | INTEGER | 0 | 0 |  |
| geometry_wkt | TEXT | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |

### `site_attributes`

Rows: `52`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| region_id | INTEGER | 0 | 0 |  |
| gauge_id | INTEGER | 0 | 0 |  |
| station | TEXT | 0 | 0 |  |
| elev_mean | REAL | 0 | 0 |  |
| elev_min | INTEGER | 0 | 0 |  |
| elev_max | INTEGER | 0 | 0 |  |
| slope_mean | REAL | 0 | 0 |  |
| slope_median | REAL | 0 | 0 |  |
| drainage_area_km2 | REAL | 0 | 0 |  |
| dpsbar | REAL | 0 | 0 |  |
| water_frac | REAL | 0 | 0 |  |
| trees_frac | REAL | 0 | 0 |  |
| agri_frac | REAL | 0 | 0 |  |
| builtup_frac | REAL | 0 | 0 |  |
| bare_frac | REAL | 0 | 0 |  |
| range_frac | REAL | 0 | 0 |  |
| dom_land_cover | TEXT | 0 | 0 |  |
| lai_mean | REAL | 0 | 0 |  |
| stream_order | TEXT | 0 | 0 |  |
| dilution_proxy | REAL | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| stream_order_strahler | INTEGER | 0 | 0 |  |
| nat_discharge_cms | REAL | 0 | 0 |  |
| nearest_hyriv_id | INTEGER | 0 | 0 |  |

Indexes:
- `ix_site_attributes_region_id` unique=False origin=c

### `sources`

Rows: `109`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| short | TEXT | 0 | 0 |  |
| citation | TEXT | 0 | 0 |  |
| url | TEXT | 0 | 0 |  |
| license | TEXT | 0 | 0 |  |
| source_type_id | INTEGER | 0 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

Indexes:
- `ix_sources_source_type_id` unique=False origin=c

### `standards`

Rows: `38`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| use_case_id | INTEGER | 0 | 0 |  |
| parameter_id | INTEGER | 0 | 0 |  |
| limit_low | REAL | 0 | 0 |  |
| limit_high | REAL | 0 | 0 |  |
| direction | TEXT | 0 | 0 |  |
| unit_id | INTEGER | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |

Indexes:
- `ix_standards_source_id` unique=False origin=c
- `ix_standards_use_case_id` unique=False origin=c
- `ix_standards_parameter_id` unique=False origin=c

### `standards_gapfix_review_log`

Rows: `12`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| review_status | TEXT | 0 | 0 |  |
| target_table | TEXT | 0 | 0 |  |
| source_short | TEXT | 0 | 0 |  |
| source_pdf | TEXT | 0 | 0 |  |
| source_page | TEXT | 0 | 0 |  |
| use_case | TEXT | 0 | 0 |  |
| parameter_db_name | TEXT | 0 | 0 |  |
| parameter_label | TEXT | 0 | 0 |  |
| target_low | TEXT | 0 | 0 |  |
| target_high | TEXT | 0 | 0 |  |
| direction | TEXT | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| threshold_basis | TEXT | 0 | 0 |  |
| target_type | TEXT | 0 | 0 |  |
| source_exact_value | TEXT | 0 | 0 |  |
| existing_db_status | TEXT | 0 | 0 |  |
| mapping_note | TEXT | 0 | 0 |  |
| sql_action | TEXT | 0 | 0 |  |
| created_at | TEXT | 0 | 0 | `CURRENT_DATE` |

Indexes:
- `sqlite_autoindex_standards_gapfix_review_log_1` unique=True origin=u

### `standards_guidance_bands`

Rows: `15`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| source_id | INTEGER | 0 | 0 |  |
| source_short | TEXT | 1 | 0 |  |
| source_pdf | TEXT | 0 | 0 |  |
| source_page | TEXT | 0 | 0 |  |
| use_case | TEXT | 1 | 0 |  |
| parameter | TEXT | 1 | 0 |  |
| context | TEXT | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| no_restriction | TEXT | 0 | 0 |  |
| slight_to_moderate | TEXT | 0 | 0 |  |
| severe | TEXT | 0 | 0 |  |
| threshold_basis | TEXT | 0 | 0 |  |
| db_handling | TEXT | 0 | 0 |  |
| created_at | TEXT | 0 | 0 | `CURRENT_DATE` |

Indexes:
- `sqlite_autoindex_standards_guidance_bands_1` unique=True origin=u

### `train_performance`

Rows: `40`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| train_id | INT | 0 | 0 |  |
| parameter | TEXT | 0 | 0 |  |
| influent_low | REAL | 0 | 0 |  |
| influent_high | REAL | 0 | 0 |  |
| cum_removal_low | REAL | 0 | 0 |  |
| cum_removal_high | REAL | 0 | 0 |  |
| effluent_low | REAL | 0 | 0 |  |
| effluent_high | REAL | 0 | 0 |  |
| steps_with_data | INT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |

### `train_step`

Rows: `23`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| train_id | INTEGER | 0 | 0 |  |
| step_order | INTEGER | 0 | 0 |  |
| nbs_id | INTEGER | 0 | 0 |  |
| step_label | TEXT | 0 | 0 |  |
| role | TEXT | 0 | 0 |  |

Indexes:
- `ix_train_step_nbs` unique=False origin=c
- `ix_train_step_train` unique=False origin=c

### `train_usecase_match`

Rows: `64`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| train_id | INT | 0 | 0 |  |
| use_case | TEXT | 0 | 0 |  |
| parameter | TEXT | 0 | 0 |  |
| effluent_low | REAL | 0 | 0 |  |
| effluent_high | REAL | 0 | 0 |  |
| limit_val | REAL | 0 | 0 |  |
| verdict | TEXT | 0 | 0 |  |

### `treatment_train`

Rows: `8`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| name | TEXT | 0 | 0 |  |
| target_use_case | TEXT | 0 | 0 |  |
| scale_context | TEXT | 0 | 0 |  |
| notes | TEXT | 0 | 0 |  |
| source_ids | TEXT | 0 | 0 |  |

### `water_observations`

Rows: `625`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| station | TEXT | 0 | 0 |  |
| district | TEXT | 0 | 0 |  |
| state | TEXT | 0 | 0 |  |
| cwc_code | TEXT | 0 | 0 |  |
| value_mean | REAL | 0 | 0 |  |
| value_min | REAL | 0 | 0 |  |
| value_max | REAL | 0 | 0 |  |
| n_samples | INTEGER | 0 | 0 |  |
| period | TEXT | 0 | 0 |  |
| basin_id | INTEGER | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |
| parameter_id | INTEGER | 0 | 0 |  |
| unit_id | INTEGER | 0 | 0 |  |

Indexes:
- `ix_water_observations_source_id` unique=False origin=c
- `ix_water_observations_basin_id` unique=False origin=c
- `ix_water_observations_parameter_id` unique=False origin=c

### `water_type_profile_change_log`

Rows: `3`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| change_key | TEXT | 1 | 0 |  |
| change_type | TEXT | 1 | 0 |  |
| affected_rows | INTEGER | 1 | 0 |  |
| reason | TEXT | 1 | 0 |  |
| old_value | TEXT | 0 | 0 |  |
| new_value | TEXT | 0 | 0 |  |
| source_ids | TEXT | 0 | 0 |  |
| created_at | TEXT | 1 | 0 |  |

Indexes:
- `sqlite_autoindex_water_type_profile_change_log_1` unique=True origin=u

### `water_type_profile_source_map`

Rows: `24`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 1 |  |
| water_type_profile_id | INTEGER | 1 | 0 |  |
| source_id | INTEGER | 1 | 0 |  |
| source_role | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| created_at | TEXT | 0 | 0 |  |

Indexes:
- `sqlite_autoindex_water_type_profile_source_map_1` unique=True origin=u

### `water_type_profiles`

Rows: `54`

| Column | SQLite type | Not null | Primary key position | Default |
|---|---|---:|---:|---|
| id | INTEGER | 0 | 0 |  |
| water_type | TEXT | 0 | 0 |  |
| parameter | TEXT | 0 | 0 |  |
| value_low | REAL | 0 | 0 |  |
| value_high | REAL | 0 | 0 |  |
| unit | TEXT | 0 | 0 |  |
| note | TEXT | 0 | 0 |  |
| deprecated | INTEGER | 0 | 0 |  |
| source_id | INTEGER | 0 | 0 |  |

## Views

### `v_app_cost_benefit_method`

Status: generated
Dependencies: `cost_benefit_method`, `cost_benefit_component_weights`

```sql
CREATE VIEW v_app_cost_benefit_method AS
SELECT
    m.method_key,
    m.method_name,
    m.version,
    m.is_monetary,
    m.formula_text,
    m.denominator_floor,
    m.display_cap,
    m.caveat_text,
    w.component_key,
    w.component_label,
    w.side,
    w.weight,
    w.direction,
    w.source_field,
    w.notes
FROM cost_benefit_method AS m
JOIN cost_benefit_component_weights AS w
  ON w.method_key = m.method_key
ORDER BY
    CASE w.side WHEN 'benefit' THEN 1 ELSE 2 END,
    w.id
```

### `v_app_district_recommendation_hints`

Status: generated
Dependencies: `app_district_profile_cache`

```sql
CREATE VIEW v_app_district_recommendation_hints AS
    SELECT
        district,
        dominant_pressure_label,
        recommended_pathway_label,
        location_caution,
        data_confidence_label,
        CASE
            WHEN dominant_pressure_label LIKE '%industrial hotspot%' THEN 'industrial_pretreatment_required'
            WHEN dominant_pressure_label LIKE '%domestic sewage gap%' THEN 'decentralized_sewage_priority'
            WHEN dominant_pressure_label LIKE '%agricultural runoff%' THEN 'runoff_and_nutrient_controls_priority'
            WHEN dominant_pressure_label LIKE '%urban/built-up%' THEN 'compact_or_modular_systems_priority'
            ELSE 'use_measured_water_quality_or_standard_train_matching'
        END AS app_recommendation_mode,
        evidence_source_ids
    FROM app_district_profile_cache
```

### `v_app_location_profile`

Status: generated
Dependencies: `app_district_profile_cache`

```sql
CREATE VIEW v_app_location_profile AS
    SELECT
        district,
        state_guess AS state,
        station_count,
        representative_stations,
        ROUND(lat_mean, 5) AS lat,
        ROUND(lon_mean, 5) AS lon,
        ROUND(rainfall_mm_yr_mean, 1) AS rainfall_mm_yr,
        ROUND(tmin_c_mean, 1) AS tmin_c,
        ROUND(tmax_c_mean, 1) AS tmax_c,
        soil_types,
        infiltration_classes,
        ROUND(slope_mean, 2) AS slope_mean,
        stream_order_strahler_max,
        ROUND(nat_discharge_cms_mean, 3) AS nat_discharge_cms,
        ROUND(site_agri_pct, 1) AS site_agri_pct,
        ROUND(site_builtup_pct, 1) AS site_builtup_pct,
        ROUND(site_trees_pct, 1) AS site_trees_pct,
        ROUND(lulc_2024_agriculture_pct, 1) AS lulc_2024_agriculture_pct,
        ROUND(lulc_2024_builtup_pct, 1) AS lulc_2024_builtup_pct,
        ROUND(lulc_2024_forest_pct, 1) AS lulc_2024_forest_pct,
        ROUND(lulc_2024_water_pct, 1) AS lulc_2024_water_pct,
        ROUND(domestic_sewage_mld, 3) AS domestic_sewage_mld,
        ROUND(industrial_wastewater_mld, 3) AS industrial_wastewater_mld,
        ROUND(stp_capacity_operational_mld, 3) AS stp_capacity_operational_mld,
        ROUND(stp_capacity_under_construction_mld, 3) AS stp_capacity_under_construction_mld,
        stp_count_operational,
        stp_count_under_construction,
        dominant_pressure_label,
        recommended_pathway_label,
        location_caution,
        data_confidence_label,
        evidence_source_ids
    FROM app_district_profile_cache
```

### `v_app_map_layers`

Status: generated
Dependencies: `narmada_map_layers_catalog`, `this`

```sql
CREATE VIEW v_app_map_layers AS
    SELECT
        layer_name,
        geometry_type,
        source_table,
        map_status,
        join_key,
        note,
        source_id
    FROM narmada_map_layers_catalog
    UNION ALL
    SELECT
        'district_profile_context',
        'polygon_join',
        'app_district_profile_cache',
        'attribute_ready_no_geometry',
        'district',
        'Frontend can join this app-facing profile to district boundaries and show pressure/pathway cards.',
        104
```

### `v_app_nbs_catalog_cards`

Status: generated
Dependencies: `nbs_footprint`, `nbs_options`, `dim_nbs_family`, `nbs_implementation`, `nf_agg`, `nbs_design`

GROUP_CONCAT usages:
- `GROUP_CONCAT(DISTINCT olr_g_m2_d)`
- `GROUP_CONCAT(DISTINCT hlr_m3_m2_d)`
- `GROUP_CONCAT(DISTINCT depth_m)`
- `GROUP_CONCAT(DISTINCT note)`

```sql
CREATE VIEW v_app_nbs_catalog_cards AS
    WITH nf_agg AS (
        SELECT
            nbs_id,
            MIN(area_per_pe_low) AS area_per_pe_low,
            MAX(area_per_pe_high) AS area_per_pe_high,
            GROUP_CONCAT(DISTINCT olr_g_m2_d) AS olr_g_m2_d,
            GROUP_CONCAT(DISTINCT hlr_m3_m2_d) AS hlr_m3_m2_d,
            GROUP_CONCAT(DISTINCT depth_m) AS depth_m,
            GROUP_CONCAT(DISTINCT note) AS footprint_note
        FROM nbs_footprint
        GROUP BY nbs_id
    )
    SELECT
        n.id AS nbs_id,
        n.solution,
        f.name AS family,
        n.energy_class,
        n.description,
        n.optimal_water_type,
        n.location_suitability,
        n.climate_suitability,
        n.soil_type,
        n.resource_requirements,
        n.notes AS catalogue_notes,
        ni.implementation_steps,
        ni.maintenance_requirements,
        nf.area_per_pe_low,
        nf.area_per_pe_high,
        nf.olr_g_m2_d,
        nf.hlr_m3_m2_d,
        nf.depth_m,
        nf.footprint_note,
        nd.pretreatment,
        nd.media_substrate,
        nd.hydraulic_config,
        nd.planting,
        nd.construction_notes,
        nd.startup_establishment,
        nd.om_routine,
        nd.om_periodic,
        nd.monitoring,
        nd.failure_modes,
        nd.skill_om_intensity,
        nd.climate_dependence,
        n.source_id AS source_id,
        COALESCE(nd.source_ids, CAST(n.source_id AS TEXT)) AS evidence_source_ids
    FROM nbs_options n
    LEFT JOIN dim_nbs_family f ON f.id = n.family_id
    LEFT JOIN nbs_implementation ni ON ni.nbs_id = n.id
    LEFT JOIN nf_agg nf ON nf.nbs_id = n.id
    LEFT JOIN nbs_design nd ON nd.nbs_id = n.id
```

### `v_app_open_caveats`

Status: generated
Dependencies: `app_caveats`

```sql
CREATE VIEW v_app_open_caveats AS
    SELECT severity, title, plain_language_message, technical_note, affected_tables, status, action_needed
    FROM app_caveats
    WHERE status IN ('open','active_guardrail')
    ORDER BY CASE severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, title
```

### `v_app_plant_catalog_cards`

Status: generated
Dependencies: `plants`, `plant_solution_map`, `nbs_options`, `dim_confidence`

GROUP_CONCAT usages:
- `GROUP_CONCAT(DISTINCT n.solution)`
- `GROUP_CONCAT(DISTINCT dc.name)`
- `GROUP_CONCAT(DISTINCT psm.source_id)`

```sql
CREATE VIEW v_app_plant_catalog_cards AS
    SELECT
        p.id AS plant_id,
        p.plant_species,
        p.native_status,
        p.invasive,
        p.plant_type,
        p.locational_availability,
        p.climate_preference,
        p.soil_type,
        p.water_needs,
        p.ecological_role,
        p.pollution_tolerance,
        p.metals_pollutants,
        p.optimal_water_type,
        p.evidence_note,
        COUNT(psm.id) AS mapped_solution_count,
        GROUP_CONCAT(DISTINCT n.solution) AS mapped_solutions,
        GROUP_CONCAT(DISTINCT dc.name) AS mapping_confidence_labels,
        GROUP_CONCAT(DISTINCT psm.source_id) AS evidence_source_ids
    FROM plants p
    LEFT JOIN plant_solution_map psm ON psm.plant_id = p.id
    LEFT JOIN nbs_options n ON n.id = psm.nbs_id
    LEFT JOIN dim_confidence dc ON dc.id = psm.confidence_id
    GROUP BY p.id
```

### `v_app_train_usecase_summary`

Status: generated
Dependencies: `train_usecase_match`

GROUP_CONCAT usages:
- `GROUP_CONCAT(CASE WHEN verdict='fail' THEN parameter END)`
- `GROUP_CONCAT(CASE WHEN verdict='marginal' THEN parameter END)`
- `GROUP_CONCAT(CASE WHEN verdict='unknown' THEN parameter END)`

```sql
CREATE VIEW v_app_train_usecase_summary AS
    SELECT
        train_id,
        use_case,
        COUNT(*) AS parameters_checked,
        SUM(CASE WHEN verdict='pass' THEN 1 ELSE 0 END) AS pass_count,
        SUM(CASE WHEN verdict='marginal' THEN 1 ELSE 0 END) AS marginal_count,
        SUM(CASE WHEN verdict='fail' THEN 1 ELSE 0 END) AS fail_count,
        SUM(CASE WHEN verdict='unknown' THEN 1 ELSE 0 END) AS unknown_count,
        GROUP_CONCAT(CASE WHEN verdict='fail' THEN parameter END) AS failing_parameters,
        GROUP_CONCAT(CASE WHEN verdict='marginal' THEN parameter END) AS marginal_parameters,
        GROUP_CONCAT(CASE WHEN verdict='unknown' THEN parameter END) AS unknown_parameters
    FROM train_usecase_match
    GROUP BY train_id, use_case
```

### `v_app_train_cards`

Status: generated
Dependencies: `train_step`, `train_performance`, `v_app_train_usecase_summary`, `treatment_train`, `ordered_steps`, `perf`, `usecases`

GROUP_CONCAT usages:
- `GROUP_CONCAT(ts.step_order || '. ' || ts.step_label || ' [' || COALESCE(ts.role,'step') || ']', ' → ')`
- `GROUP_CONCAT(
                CASE
                    WHEN steps_with_data = 0 THEN parameter || ': unknown (data gap)'
                    ELSE parameter || ': ' || ROUND(cum_removal_low,1) || '-' || ROUND(cum_removal_high,1) || '%'
                END,
                '; '
            )`
- `GROUP_CONCAT(use_case || ' pass/marginal/fail/unknown=' || pass_count || '/' || marginal_count || '/' || fail_count || '/' || unknown_count, '; ')`

```sql
CREATE VIEW v_app_train_cards AS
    WITH ordered_steps AS (
        SELECT
            ts.train_id,
            GROUP_CONCAT(ts.step_order || '. ' || ts.step_label || ' [' || COALESCE(ts.role,'step') || ']', ' → ') AS treatment_sequence
        FROM (
            SELECT * FROM train_step ORDER BY train_id, step_order
        ) ts
        GROUP BY ts.train_id
    ), perf AS (
        SELECT
            train_id,
            GROUP_CONCAT(
                CASE
                    WHEN steps_with_data = 0 THEN parameter || ': unknown (data gap)'
                    ELSE parameter || ': ' || ROUND(cum_removal_low,1) || '-' || ROUND(cum_removal_high,1) || '%'
                END,
                '; '
            ) AS removal_summary
        FROM train_performance
        GROUP BY train_id
    ), usecases AS (
        SELECT
            train_id,
            GROUP_CONCAT(use_case || ' pass/marginal/fail/unknown=' || pass_count || '/' || marginal_count || '/' || fail_count || '/' || unknown_count, '; ') AS usecase_summary
        FROM v_app_train_usecase_summary
        GROUP BY train_id
    )
    SELECT
        t.id AS train_id,
        t.name,
        t.target_use_case,
        t.scale_context,
        t.notes,
        os.treatment_sequence,
        perf.removal_summary,
        usecases.usecase_summary,
        t.source_ids AS evidence_source_ids
    FROM treatment_train t
    LEFT JOIN ordered_steps os ON os.train_id = t.id
    LEFT JOIN perf ON perf.train_id = t.id
    LEFT JOIN usecases ON usecases.train_id = t.id
```

### `v_app_upload_parameter_template`

Status: generated
Dependencies: `app_input_template`

```sql
CREATE VIEW v_app_upload_parameter_template AS
    SELECT
        use_case,
        canonical_parameter,
        user_label,
        default_unit,
        is_required,
        priority,
        why_needed,
        example_value_note
    FROM app_input_template
    ORDER BY use_case, CASE priority WHEN 'required_if_available' THEN 1 WHEN 'recommended' THEN 2 ELSE 3 END, canonical_parameter
```

### `v_engine_usecase_matrix`

Status: generated
Dependencies: `treatment_train`, `dim_use_case`, `v_app_train_usecase_summary`

```sql
CREATE VIEW v_engine_usecase_matrix AS
    SELECT
        t.id AS train_id,
        t.name AS train_name,
        u.name AS use_case,
        COALESCE(s.parameters_checked, 0) AS parameters_checked,
        COALESCE(s.pass_count, 0) AS pass_count,
        COALESCE(s.marginal_count, 0) AS marginal_count,
        COALESCE(s.fail_count, 0) AS fail_count,
        COALESCE(s.unknown_count, 0) AS unknown_count,
        s.failing_parameters,
        s.marginal_parameters,
        s.unknown_parameters
    FROM treatment_train t
    CROSS JOIN dim_use_case u
    LEFT JOIN v_app_train_usecase_summary s ON s.train_id=t.id AND s.use_case=u.name
    WHERE u.name IN ('drinking','irrigation','discharge_inland')
```

### `v_nbs_profile`

Status: generated
Dependencies: `removal_efficiency`, `nbs_footprint`, `nbs_design`, `nbs_options`, `dim_nbs_family`

```sql
CREATE VIEW v_nbs_profile AS
SELECT o.id AS nbs_id, o.solution, f.name AS family, o.optimal_water_type,
       (SELECT COUNT(*) FROM removal_efficiency r WHERE r.nbs_id=o.id) AS removal_rows,
       (SELECT COUNT(*) FROM removal_efficiency r WHERE r.nbs_id=o.id AND r.needs_corroboration=0) AS removal_corroborated,
       (SELECT COUNT(*) FROM nbs_footprint fp WHERE fp.nbs_id=o.id) AS has_footprint,
       (SELECT COUNT(*) FROM nbs_design dz WHERE dz.nbs_id=o.id) AS has_design
FROM nbs_options o LEFT JOIN dim_nbs_family f ON f.id=o.family_id
```

### `v_plant_use`

Status: generated
Dependencies: `plant_solution_map`, `plants`, `nbs_options`, `dim_confidence`, `sources`

```sql
CREATE VIEW v_plant_use AS
SELECT pm.id, pl.plant_species, o.solution AS nbs, pm.basis, cf.name AS confidence, s.short AS source
FROM plant_solution_map pm
LEFT JOIN plants pl ON pl.id=pm.plant_id
LEFT JOIN nbs_options o ON o.id=pm.nbs_id
LEFT JOIN dim_confidence cf ON cf.id=pm.confidence_id
LEFT JOIN sources s ON s.id=pm.source_id
```

### `v_removal`

Status: generated
Dependencies: `removal_efficiency`, `nbs_options`, `dim_parameter`, `dim_confidence`, `dim_scale`, `dim_country`, `sources`

```sql
CREATE VIEW v_removal AS
SELECT r.id, o.solution AS nbs, p.name AS parameter, r.eff_low, r.eff_high,
       cf.name AS confidence, sc.name AS scale, co.name AS country,
       r.influent_context, r.hrt_loading, r.needs_corroboration, s.short AS source
FROM removal_efficiency r
LEFT JOIN nbs_options o ON o.id=r.nbs_id
LEFT JOIN dim_parameter p ON p.id=r.parameter_id
LEFT JOIN dim_confidence cf ON cf.id=r.confidence_id
LEFT JOIN dim_scale sc ON sc.id=r.scale_id
LEFT JOIN dim_country co ON co.id=r.country_id
LEFT JOIN sources s ON s.id=r.source_id
```

### `v_standards`

Status: generated
Dependencies: `standards`, `dim_use_case`, `dim_parameter`, `dim_unit`, `sources`

```sql
CREATE VIEW v_standards AS
SELECT st.id, uc.name AS use_case, p.name AS parameter, st.limit_low, st.limit_high, st.direction, u.name AS unit, s.short AS source
FROM standards st
LEFT JOIN dim_use_case uc ON uc.id=st.use_case_id
LEFT JOIN dim_parameter p ON p.id=st.parameter_id
LEFT JOIN dim_unit u ON u.id=st.unit_id
LEFT JOIN sources s ON s.id=st.source_id
```

### `v_train`

Status: generated
Dependencies: `treatment_train`, `train_step`, `nbs_options`

```sql
CREATE VIEW v_train AS
SELECT t.id AS train_id, t.name AS train, t.target_use_case, t.scale_context,
       ts.step_order, COALESCE(o.solution, ts.step_label) AS step, ts.role
FROM treatment_train t JOIN train_step ts ON ts.train_id=t.id
LEFT JOIN nbs_options o ON o.id=ts.nbs_id ORDER BY t.id, ts.step_order
```

### `v_train_performance`

Status: generated
Dependencies: `train_performance`, `treatment_train`

```sql
CREATE VIEW v_train_performance AS SELECT t.name AS train, tp.parameter, tp.cum_removal_low, tp.cum_removal_high,
  tp.effluent_low, tp.effluent_high, tp.steps_with_data FROM train_performance tp JOIN treatment_train t ON t.id=tp.train_id
```

### `v_train_usecase`

Status: generated
Dependencies: `train_usecase_match`, `treatment_train`

```sql
CREATE VIEW v_train_usecase AS SELECT t.name AS train, m.use_case, m.parameter, m.effluent_low, m.effluent_high, m.limit_val, m.verdict
  FROM train_usecase_match m JOIN treatment_train t ON t.id=m.train_id
```

## Suspicious Or Review Items

- No zero-row tables found.

SQLite internal objects to skip:
- `index` `sqlite_autoindex_app_caveats_1`
- `index` `sqlite_autoindex_app_context_rules_1`
- `index` `sqlite_autoindex_app_district_profile_cache_1`
- `index` `sqlite_autoindex_app_layer_metadata_1`
- `index` `sqlite_autoindex_cost_benefit_component_weights_1`
- `index` `sqlite_autoindex_cost_benefit_method_1`
- `index` `sqlite_autoindex_criteria_weights_1`
- `index` `sqlite_autoindex_nbs_applicability_rules_1`
- `index` `sqlite_autoindex_reuse_health_guidance_1`
- `index` `sqlite_autoindex_standards_gapfix_review_log_1`
- `index` `sqlite_autoindex_standards_guidance_bands_1`
- `index` `sqlite_autoindex_water_type_profile_change_log_1`
- `index` `sqlite_autoindex_water_type_profile_source_map_1`
- `table` `sqlite_sequence`

Indexes skipped/commented for manual review:
- app_caveats.sqlite_autoindex_app_caveats_1: SQLite autoindex/constraint index
- app_context_rules.sqlite_autoindex_app_context_rules_1: SQLite autoindex/constraint index
- app_district_profile_cache.sqlite_autoindex_app_district_profile_cache_1: SQLite autoindex/constraint index
- app_layer_metadata.sqlite_autoindex_app_layer_metadata_1: SQLite autoindex/constraint index
- cost_benefit_component_weights.sqlite_autoindex_cost_benefit_component_weights_1: SQLite autoindex/constraint index
- cost_benefit_method.sqlite_autoindex_cost_benefit_method_1: SQLite autoindex/constraint index
- criteria_weights.sqlite_autoindex_criteria_weights_1: SQLite autoindex/constraint index
- nbs_applicability_rules.sqlite_autoindex_nbs_applicability_rules_1: SQLite autoindex/constraint index
- reuse_health_guidance.sqlite_autoindex_reuse_health_guidance_1: SQLite autoindex/constraint index
- standards_gapfix_review_log.sqlite_autoindex_standards_gapfix_review_log_1: SQLite autoindex/constraint index
- standards_guidance_bands.sqlite_autoindex_standards_guidance_bands_1: SQLite autoindex/constraint index
- water_type_profile_change_log.sqlite_autoindex_water_type_profile_change_log_1: SQLite autoindex/constraint index
- water_type_profile_source_map.sqlite_autoindex_water_type_profile_source_map_1: SQLite autoindex/constraint index

No SQLite foreign-key declarations found.

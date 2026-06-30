-- Generated PostgreSQL schema draft for the Narmada NbS canonical database.
-- Source: canonical db/narmada_nbs_canonical.db
-- Review before production import. This file changes no scientific values.

BEGIN;

-- Table: ambient_water_quality
DROP TABLE IF EXISTS "ambient_water_quality" CASCADE;
CREATE TABLE "ambient_water_quality" (
    "id" BIGINT,
    "station" TEXT,
    "region_id" DOUBLE PRECISION,
    "season" TEXT,
    "year" TEXT,
    "value" DOUBLE PRECISION,
    "note" TEXT,
    "needs_verification" BIGINT,
    "source_id" BIGINT,
    "parameter_id" BIGINT,
    "unit_id" DOUBLE PRECISION
);

-- Table: app_caveats
DROP TABLE IF EXISTS "app_caveats" CASCADE;
CREATE TABLE "app_caveats" (
    "id" BIGINT NOT NULL,
    "caveat_key" TEXT NOT NULL,
    "severity" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "plain_language_message" TEXT NOT NULL,
    "technical_note" TEXT NOT NULL,
    "affected_tables" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "action_needed" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: app_context_rules
DROP TABLE IF EXISTS "app_context_rules" CASCADE;
CREATE TABLE "app_context_rules" (
    "id" BIGINT NOT NULL,
    "rule_key" TEXT NOT NULL,
    "rule_group" TEXT NOT NULL,
    "plain_language_rule" TEXT NOT NULL,
    "technical_expression" TEXT NOT NULL,
    "app_action" TEXT NOT NULL,
    "caveat" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: app_district_profile_cache
DROP TABLE IF EXISTS "app_district_profile_cache" CASCADE;
CREATE TABLE "app_district_profile_cache" (
    "id" BIGINT NOT NULL,
    "district" TEXT NOT NULL,
    "state_guess" TEXT NOT NULL,
    "station_count" BIGINT NOT NULL,
    "representative_stations" TEXT NOT NULL,
    "lat_mean" DOUBLE PRECISION NOT NULL,
    "lon_mean" DOUBLE PRECISION NOT NULL,
    "rainfall_mm_yr_mean" DOUBLE PRECISION NOT NULL,
    "tmin_c_mean" DOUBLE PRECISION NOT NULL,
    "tmax_c_mean" DOUBLE PRECISION NOT NULL,
    "soil_types" TEXT NOT NULL,
    "infiltration_classes" TEXT NOT NULL,
    "slope_mean" DOUBLE PRECISION NOT NULL,
    "stream_order_strahler_max" BIGINT NOT NULL,
    "nat_discharge_cms_mean" DOUBLE PRECISION NOT NULL,
    "site_agri_pct" DOUBLE PRECISION NOT NULL,
    "site_builtup_pct" DOUBLE PRECISION NOT NULL,
    "site_trees_pct" DOUBLE PRECISION NOT NULL,
    "lulc_2024_agriculture_pct" DOUBLE PRECISION NOT NULL,
    "lulc_2024_builtup_pct" DOUBLE PRECISION NOT NULL,
    "lulc_2024_forest_pct" DOUBLE PRECISION NOT NULL,
    "lulc_2024_water_pct" DOUBLE PRECISION NOT NULL,
    "domestic_sewage_mld" DOUBLE PRECISION NOT NULL,
    "industrial_wastewater_mld" DOUBLE PRECISION NOT NULL,
    "stp_capacity_operational_mld" DOUBLE PRECISION NOT NULL,
    "stp_capacity_under_construction_mld" DOUBLE PRECISION NOT NULL,
    "stp_count_operational" DOUBLE PRECISION NOT NULL,
    "stp_count_under_construction" DOUBLE PRECISION NOT NULL,
    "dominant_pressure_label" TEXT NOT NULL,
    "recommended_pathway_label" TEXT NOT NULL,
    "location_caution" TEXT NOT NULL,
    "data_confidence_label" TEXT NOT NULL,
    "evidence_source_ids" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: app_input_template
DROP TABLE IF EXISTS "app_input_template" CASCADE;
CREATE TABLE "app_input_template" (
    "id" BIGINT NOT NULL,
    "use_case" TEXT NOT NULL,
    "canonical_parameter" TEXT NOT NULL,
    "user_label" TEXT NOT NULL,
    "default_unit" TEXT NOT NULL,
    "is_required" BIGINT NOT NULL,
    "priority" TEXT NOT NULL,
    "why_needed" TEXT NOT NULL,
    "example_value_note" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: app_layer_metadata
DROP TABLE IF EXISTS "app_layer_metadata" CASCADE;
CREATE TABLE "app_layer_metadata" (
    "id" BIGINT NOT NULL,
    "layer_name" TEXT NOT NULL,
    "layer_type" TEXT NOT NULL,
    "purpose" TEXT NOT NULL,
    "source_tables" TEXT NOT NULL,
    "api_use" TEXT NOT NULL,
    "caveat" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: app_parameter_aliases
DROP TABLE IF EXISTS "app_parameter_aliases" CASCADE;
CREATE TABLE "app_parameter_aliases" (
    "id" BIGINT NOT NULL,
    "canonical_parameter" TEXT NOT NULL,
    "user_label" TEXT NOT NULL,
    "upload_aliases" TEXT NOT NULL,
    "common_units" TEXT NOT NULL,
    "parameter_group" TEXT NOT NULL,
    "recommended_for_upload" BIGINT NOT NULL,
    "plain_language_help" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: basins
DROP TABLE IF EXISTS "basins" CASCADE;
CREATE TABLE "basins" (
    "id" BIGINT,
    "basin" TEXT,
    "sub_basin" TEXT,
    "description" TEXT,
    "source_id" BIGINT
);

-- Table: column_provenance
DROP TABLE IF EXISTS "column_provenance" CASCADE;
CREATE TABLE "column_provenance" (
    "id" BIGINT,
    "table_name" TEXT,
    "column" TEXT,
    "note" TEXT,
    "source_ids" TEXT,
    "status_id" BIGINT
);

-- Table: cost_benefit_component_weights
DROP TABLE IF EXISTS "cost_benefit_component_weights" CASCADE;
CREATE TABLE "cost_benefit_component_weights" (
    "id" BIGINT NOT NULL,
    "method_key" TEXT NOT NULL,
    "component_key" TEXT NOT NULL,
    "component_label" TEXT NOT NULL,
    "side" TEXT NOT NULL,
    "weight" DOUBLE PRECISION NOT NULL,
    "direction" TEXT NOT NULL,
    "source_field" TEXT NOT NULL,
    "notes" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: cost_benefit_method
DROP TABLE IF EXISTS "cost_benefit_method" CASCADE;
CREATE TABLE "cost_benefit_method" (
    "id" BIGINT NOT NULL,
    "method_key" TEXT NOT NULL,
    "method_name" TEXT NOT NULL,
    "version" TEXT NOT NULL,
    "is_monetary" BIGINT NOT NULL,
    "formula_text" TEXT NOT NULL,
    "denominator_floor" DOUBLE PRECISION NOT NULL,
    "display_cap" DOUBLE PRECISION NOT NULL,
    "caveat_text" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: criteria_weights
DROP TABLE IF EXISTS "criteria_weights" CASCADE;
CREATE TABLE "criteria_weights" (
    "id" BIGINT NOT NULL,
    "use_case_id" BIGINT NOT NULL,
    "use_case" TEXT NOT NULL,
    "criterion_code" TEXT NOT NULL,
    "criterion_name" TEXT NOT NULL,
    "weight" DOUBLE PRECISION NOT NULL,
    "benefit_or_cost" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "derivation_note" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: dim_confidence
DROP TABLE IF EXISTS "dim_confidence" CASCADE;
CREATE TABLE "dim_confidence" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_country
DROP TABLE IF EXISTS "dim_country" CASCADE;
CREATE TABLE "dim_country" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_nbs_family
DROP TABLE IF EXISTS "dim_nbs_family" CASCADE;
CREATE TABLE "dim_nbs_family" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_parameter
DROP TABLE IF EXISTS "dim_parameter" CASCADE;
CREATE TABLE "dim_parameter" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_provenance_status
DROP TABLE IF EXISTS "dim_provenance_status" CASCADE;
CREATE TABLE "dim_provenance_status" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_scale
DROP TABLE IF EXISTS "dim_scale" CASCADE;
CREATE TABLE "dim_scale" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_source_type
DROP TABLE IF EXISTS "dim_source_type" CASCADE;
CREATE TABLE "dim_source_type" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_unit
DROP TABLE IF EXISTS "dim_unit" CASCADE;
CREATE TABLE "dim_unit" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: dim_use_case
DROP TABLE IF EXISTS "dim_use_case" CASCADE;
CREATE TABLE "dim_use_case" (
    "id" BIGINT,
    "name" TEXT
);

-- Table: engine_data_fix_log
DROP TABLE IF EXISTS "engine_data_fix_log" CASCADE;
CREATE TABLE "engine_data_fix_log" (
    "id" BIGINT NOT NULL,
    "fix_key" TEXT NOT NULL,
    "fix_summary" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_agriculture_metrics
DROP TABLE IF EXISTS "narmada_agriculture_metrics" CASCADE;
CREATE TABLE "narmada_agriculture_metrics" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "spatial_unit_type" TEXT NOT NULL,
    "spatial_unit_name" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "year" TEXT NOT NULL,
    "metric" TEXT NOT NULL,
    "value_text" TEXT NOT NULL,
    "value_low" DOUBLE PRECISION NOT NULL,
    "value_high" DOUBLE PRECISION NOT NULL,
    "unit" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_groundwater_wells
DROP TABLE IF EXISTS "narmada_groundwater_wells" CASCADE;
CREATE TABLE "narmada_groundwater_wells" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "well_id" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "block_name" TEXT NOT NULL,
    "village" TEXT NOT NULL,
    "lat" DOUBLE PRECISION NOT NULL,
    "lon" DOUBLE PRECISION NOT NULL,
    "geometry_wkt" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_hydrology_stations
DROP TABLE IF EXISTS "narmada_hydrology_stations" CASCADE;
CREATE TABLE "narmada_hydrology_stations" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "station_name" TEXT NOT NULL,
    "agency" TEXT NOT NULL,
    "state" TEXT NOT NULL,
    "station_type" TEXT NOT NULL,
    "lat" DOUBLE PRECISION NOT NULL,
    "lon" DOUBLE PRECISION NOT NULL,
    "zero_gauge_m" DOUBLE PRECISION NOT NULL,
    "max_level_m" DOUBLE PRECISION NOT NULL,
    "min_level_m" DOUBLE PRECISION NOT NULL,
    "avg_level_m" DOUBLE PRECISION NOT NULL,
    "max_discharge_cumec" DOUBLE PRECISION NOT NULL,
    "min_discharge_cumec" DOUBLE PRECISION NOT NULL,
    "avg_discharge_cumec" DOUBLE PRECISION NOT NULL,
    "sub_basin" TEXT NOT NULL,
    "geometry_wkt" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_infrastructure_assets
DROP TABLE IF EXISTS "narmada_infrastructure_assets" CASCADE;
CREATE TABLE "narmada_infrastructure_assets" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "basin_segment" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "town_area" TEXT NOT NULL,
    "asset_type" TEXT NOT NULL,
    "asset_name" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "count_value" DOUBLE PRECISION NOT NULL,
    "capacity_value" DOUBLE PRECISION NOT NULL,
    "capacity_unit" TEXT NOT NULL,
    "generated_value" DOUBLE PRECISION NOT NULL,
    "generated_unit" TEXT NOT NULL,
    "technology" TEXT NOT NULL,
    "reuse_value" DOUBLE PRECISION NOT NULL,
    "reuse_unit" TEXT NOT NULL,
    "network_length_km" DOUBLE PRECISION NOT NULL,
    "connections" BIGINT NOT NULL,
    "lat" DOUBLE PRECISION NOT NULL,
    "lon" DOUBLE PRECISION NOT NULL,
    "geometry_wkt" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_lulc_area
DROP TABLE IF EXISTS "narmada_lulc_area" CASCADE;
CREATE TABLE "narmada_lulc_area" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "spatial_unit_type" TEXT NOT NULL,
    "spatial_unit_name" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "state" TEXT NOT NULL,
    "year" BIGINT NOT NULL,
    "lulc_class" TEXT NOT NULL,
    "area_km2" DOUBLE PRECISION NOT NULL,
    "percent_area" DOUBLE PRECISION NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_map_layers_catalog
DROP TABLE IF EXISTS "narmada_map_layers_catalog" CASCADE;
CREATE TABLE "narmada_map_layers_catalog" (
    "id" BIGINT NOT NULL,
    "layer_name" TEXT NOT NULL,
    "geometry_type" TEXT NOT NULL,
    "source_table" TEXT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "map_status" TEXT NOT NULL,
    "join_key" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_mining_anomalies
DROP TABLE IF EXISTS "narmada_mining_anomalies" CASCADE;
CREATE TABLE "narmada_mining_anomalies" (
    "id" BIGINT NOT NULL,
    "severity" TEXT NOT NULL,
    "domain" TEXT NOT NULL,
    "item" TEXT NOT NULL,
    "existing_value" TEXT NOT NULL,
    "existing_source_id" TEXT NOT NULL,
    "report_value" TEXT NOT NULL,
    "report_source_id" TEXT NOT NULL,
    "recommended_action" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_nutrient_sediment_metrics
DROP TABLE IF EXISTS "narmada_nutrient_sediment_metrics" CASCADE;
CREATE TABLE "narmada_nutrient_sediment_metrics" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "degree_sheet" TEXT NOT NULL,
    "basin_zone" TEXT NOT NULL,
    "district_coverage" TEXT NOT NULL,
    "parameter" TEXT NOT NULL,
    "value_min" DOUBLE PRECISION NOT NULL,
    "value_max" DOUBLE PRECISION NOT NULL,
    "value_avg" DOUBLE PRECISION NOT NULL,
    "unit" TEXT NOT NULL,
    "contribution_point" TEXT NOT NULL,
    "contribution_nonpoint" TEXT NOT NULL,
    "key_quantification" TEXT NOT NULL,
    "primary_driver" TEXT NOT NULL,
    "literature_authors" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_topography_metrics
DROP TABLE IF EXISTS "narmada_topography_metrics" CASCADE;
CREATE TABLE "narmada_topography_metrics" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "spatial_unit_name" TEXT NOT NULL,
    "metric_type" TEXT NOT NULL,
    "class_label" TEXT NOT NULL,
    "area_km2" DOUBLE PRECISION NOT NULL,
    "percent_area" DOUBLE PRECISION NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: narmada_water_quality_report_stats
DROP TABLE IF EXISTS "narmada_water_quality_report_stats" CASCADE;
CREATE TABLE "narmada_water_quality_report_stats" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "report_file" TEXT NOT NULL,
    "table_ref" TEXT NOT NULL,
    "page_no" BIGINT NOT NULL,
    "basin_segment" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "city_town" TEXT NOT NULL,
    "station_name" TEXT NOT NULL,
    "parameter" TEXT NOT NULL,
    "value_mean" DOUBLE PRECISION NOT NULL,
    "value_min" DOUBLE PRECISION NOT NULL,
    "value_max" DOUBLE PRECISION NOT NULL,
    "unit" TEXT NOT NULL,
    "period" TEXT NOT NULL,
    "lat" DOUBLE PRECISION NOT NULL,
    "lon" DOUBLE PRECISION NOT NULL,
    "note" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: nbs_applicability_rules
DROP TABLE IF EXISTS "nbs_applicability_rules" CASCADE;
CREATE TABLE "nbs_applicability_rules" (
    "rule_id" TEXT NOT NULL,
    "is_active" BIGINT NOT NULL,
    "target_level" TEXT NOT NULL,
    "nbs_id" BIGINT NOT NULL,
    "nbs_solution" TEXT NOT NULL,
    "nbs_family_id" BIGINT NOT NULL,
    "nbs_family" TEXT NOT NULL,
    "train_id" BIGINT NOT NULL,
    "train_name" TEXT NOT NULL,
    "factor_name" TEXT NOT NULL,
    "factor_source_field" TEXT NOT NULL,
    "intervention_position" TEXT NOT NULL,
    "operator" TEXT NOT NULL,
    "value_min" DOUBLE PRECISION NOT NULL,
    "value_max" DOUBLE PRECISION NOT NULL,
    "category_value" TEXT NOT NULL,
    "rule_type" TEXT NOT NULL,
    "severity" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "score_modifier" DOUBLE PRECISION NOT NULL,
    "confidence_modifier" DOUBLE PRECISION NOT NULL,
    "user_message" TEXT NOT NULL,
    "technical_reason" TEXT NOT NULL,
    "evidence_status" TEXT NOT NULL,
    "provenance_status_id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "supporting_source_ids" TEXT NOT NULL,
    "review_status" TEXT NOT NULL,
    "notes" TEXT NOT NULL,
    PRIMARY KEY ("rule_id")
);

-- Table: nbs_design
DROP TABLE IF EXISTS "nbs_design" CASCADE;
CREATE TABLE "nbs_design" (
    "id" BIGINT,
    "nbs_id" BIGINT,
    "pretreatment" TEXT,
    "media_substrate" TEXT,
    "hydraulic_config" TEXT,
    "planting" TEXT,
    "construction_notes" TEXT,
    "startup_establishment" TEXT,
    "om_routine" TEXT,
    "om_periodic" TEXT,
    "monitoring" TEXT,
    "failure_modes" TEXT,
    "skill_om_intensity" TEXT,
    "climate_dependence" TEXT,
    "source_ids" TEXT
);

-- Table: nbs_footprint
DROP TABLE IF EXISTS "nbs_footprint" CASCADE;
CREATE TABLE "nbs_footprint" (
    "id" BIGINT,
    "nbs_id" BIGINT,
    "area_per_pe_low" DOUBLE PRECISION,
    "area_per_pe_high" DOUBLE PRECISION,
    "olr_g_m2_d" DOUBLE PRECISION,
    "olr_basis" TEXT,
    "hlr_m3_m2_d" DOUBLE PRECISION,
    "depth_m" DOUBLE PRECISION,
    "source_id" BIGINT,
    "note" TEXT
);

-- Table: nbs_implementation
DROP TABLE IF EXISTS "nbs_implementation" CASCADE;
CREATE TABLE "nbs_implementation" (
    "id" BIGINT,
    "nbs_id" BIGINT,
    "implementation_steps" TEXT,
    "maintenance_requirements" TEXT,
    "source_id" BIGINT
);

-- Table: nbs_options
DROP TABLE IF EXISTS "nbs_options" CASCADE;
CREATE TABLE "nbs_options" (
    "id" BIGINT,
    "solution" TEXT,
    "description" TEXT,
    "optimal_water_type" TEXT,
    "location_suitability" TEXT,
    "climate_suitability" TEXT,
    "soil_type" TEXT,
    "resource_requirements" TEXT,
    "notes" TEXT,
    "source_id" BIGINT,
    "family_id" BIGINT,
    "energy_class" TEXT
);

-- Table: plant_solution_map
DROP TABLE IF EXISTS "plant_solution_map" CASCADE;
CREATE TABLE "plant_solution_map" (
    "id" BIGINT,
    "plant_id" BIGINT,
    "nbs_id" BIGINT,
    "basis" TEXT,
    "confidence_id" TEXT,
    "source_id" BIGINT
);

-- Table: plants
DROP TABLE IF EXISTS "plants" CASCADE;
CREATE TABLE "plants" (
    "id" BIGINT,
    "plant_species" TEXT,
    "locational_availability" TEXT,
    "climate_preference" TEXT,
    "soil_type" TEXT,
    "water_needs" TEXT,
    "ecological_role" TEXT,
    "plant_type" TEXT,
    "native_status" TEXT,
    "invasive" BIGINT,
    "metals_pollutants" TEXT,
    "evidence_note" TEXT,
    "pollution_tolerance" TEXT,
    "optimal_water_type" TEXT,
    "source_id" BIGINT
);

-- Table: pollution_sources
DROP TABLE IF EXISTS "pollution_sources" CASCADE;
CREATE TABLE "pollution_sources" (
    "id" BIGINT,
    "region_id" DOUBLE PRECISION,
    "gauge_id" DOUBLE PRECISION,
    "station" TEXT,
    "source_type" TEXT,
    "category" TEXT,
    "indicator" TEXT,
    "value" DOUBLE PRECISION,
    "unit" TEXT,
    "note" TEXT,
    "source_id" BIGINT
);

-- Table: regions
DROP TABLE IF EXISTS "regions" CASCADE;
CREATE TABLE "regions" (
    "id" BIGINT,
    "camels_gauge_id" BIGINT,
    "station" TEXT,
    "river" TEXT,
    "district" TEXT,
    "cwc_site_type" TEXT,
    "is_wq_station" BIGINT,
    "rainfall_mm_yr" DOUBLE PRECISION,
    "wet_season" TEXT,
    "dry_season" TEXT,
    "tmin_C" DOUBLE PRECISION,
    "tmax_C" DOUBLE PRECISION,
    "aridity_P_PET" DOUBLE PRECISION,
    "pet_mm_yr" DOUBLE PRECISION,
    "sand_pct" BIGINT,
    "silt_pct" BIGINT,
    "clay_pct" BIGINT,
    "soil_type" TEXT,
    "hydrologic_soil_group" TEXT,
    "soil_depth_m" DOUBLE PRECISION,
    "soil_avail_water_mm_m" BIGINT,
    "basin_id" BIGINT,
    "source_climate_soil" BIGINT,
    "source_district" BIGINT,
    "infiltration_class" TEXT,
    "lat" DOUBLE PRECISION,
    "lon" DOUBLE PRECISION
);

-- Table: removal_efficiency
DROP TABLE IF EXISTS "removal_efficiency" CASCADE;
CREATE TABLE "removal_efficiency" (
    "id" BIGINT,
    "nbs_id" BIGINT,
    "parameter_id" DOUBLE PRECISION,
    "eff_low" DOUBLE PRECISION,
    "eff_high" DOUBLE PRECISION,
    "confidence_id" TEXT,
    "source_id" BIGINT,
    "note" TEXT,
    "scale_id" BIGINT,
    "country_id" TEXT,
    "influent_context" TEXT,
    "hrt_loading" TEXT,
    "temp_climate" TEXT,
    "needs_corroboration" BIGINT
);

-- Table: report_source_catalog
DROP TABLE IF EXISTS "report_source_catalog" CASCADE;
CREATE TABLE "report_source_catalog" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "short" TEXT NOT NULL,
    "report_file" TEXT NOT NULL,
    "report_title" TEXT NOT NULL,
    "report_year" TEXT NOT NULL,
    "pages" BIGINT NOT NULL,
    "extracted_text_chars" BIGINT NOT NULL,
    "extraction_status" TEXT NOT NULL,
    "primary_domains" TEXT NOT NULL,
    "mining_note" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: reuse_health_guidance
DROP TABLE IF EXISTS "reuse_health_guidance" CASCADE;
CREATE TABLE "reuse_health_guidance" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "source_short" TEXT NOT NULL,
    "source_pdf" TEXT NOT NULL,
    "source_page" TEXT NOT NULL,
    "use_case" TEXT NOT NULL,
    "context" TEXT NOT NULL,
    "parameter_or_measure" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "unit" TEXT NOT NULL,
    "threshold_basis" TEXT NOT NULL,
    "db_handling" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: river_network
DROP TABLE IF EXISTS "river_network" CASCADE;
CREATE TABLE "river_network" (
    "id" BIGINT,
    "hyriv_id" BIGINT,
    "next_down" BIGINT,
    "main_riv" BIGINT,
    "length_km" DOUBLE PRECISION,
    "dist_dn_km" DOUBLE PRECISION,
    "dist_up_km" DOUBLE PRECISION,
    "catch_skm" DOUBLE PRECISION,
    "upland_skm" DOUBLE PRECISION,
    "dis_av_cms" DOUBLE PRECISION,
    "ord_stra" BIGINT,
    "ord_clas" BIGINT,
    "ord_flow" BIGINT,
    "hybas_l12" BIGINT,
    "geometry_wkt" TEXT,
    "source_id" BIGINT
);

-- Table: site_attributes
DROP TABLE IF EXISTS "site_attributes" CASCADE;
CREATE TABLE "site_attributes" (
    "id" BIGINT,
    "region_id" BIGINT,
    "gauge_id" BIGINT,
    "station" TEXT,
    "elev_mean" DOUBLE PRECISION,
    "elev_min" BIGINT,
    "elev_max" BIGINT,
    "slope_mean" DOUBLE PRECISION,
    "slope_median" DOUBLE PRECISION,
    "drainage_area_km2" DOUBLE PRECISION,
    "dpsbar" DOUBLE PRECISION,
    "water_frac" DOUBLE PRECISION,
    "trees_frac" DOUBLE PRECISION,
    "agri_frac" DOUBLE PRECISION,
    "builtup_frac" DOUBLE PRECISION,
    "bare_frac" DOUBLE PRECISION,
    "range_frac" DOUBLE PRECISION,
    "dom_land_cover" TEXT,
    "lai_mean" DOUBLE PRECISION,
    "stream_order" TEXT,
    "dilution_proxy" DOUBLE PRECISION,
    "source_id" BIGINT,
    "stream_order_strahler" BIGINT,
    "nat_discharge_cms" DOUBLE PRECISION,
    "nearest_hyriv_id" BIGINT
);

-- Table: sources
DROP TABLE IF EXISTS "sources" CASCADE;
CREATE TABLE "sources" (
    "id" BIGINT,
    "short" TEXT,
    "citation" TEXT,
    "url" TEXT,
    "license" TEXT,
    "source_type_id" BIGINT,
    "created_at" TEXT
);

-- Table: standards
DROP TABLE IF EXISTS "standards" CASCADE;
CREATE TABLE "standards" (
    "id" BIGINT,
    "use_case_id" BIGINT,
    "parameter_id" BIGINT,
    "limit_low" DOUBLE PRECISION,
    "limit_high" DOUBLE PRECISION,
    "direction" TEXT,
    "unit_id" BIGINT,
    "source_id" BIGINT,
    "note" TEXT
);

-- Table: standards_gapfix_review_log
DROP TABLE IF EXISTS "standards_gapfix_review_log" CASCADE;
CREATE TABLE "standards_gapfix_review_log" (
    "id" BIGINT NOT NULL,
    "review_status" TEXT NOT NULL,
    "target_table" TEXT NOT NULL,
    "source_short" TEXT NOT NULL,
    "source_pdf" TEXT NOT NULL,
    "source_page" TEXT NOT NULL,
    "use_case" TEXT NOT NULL,
    "parameter_db_name" TEXT NOT NULL,
    "parameter_label" TEXT NOT NULL,
    "target_low" TEXT NOT NULL,
    "target_high" TEXT NOT NULL,
    "direction" TEXT NOT NULL,
    "unit" TEXT NOT NULL,
    "threshold_basis" TEXT NOT NULL,
    "target_type" TEXT NOT NULL,
    "source_exact_value" TEXT NOT NULL,
    "existing_db_status" TEXT NOT NULL,
    "mapping_note" TEXT NOT NULL,
    "sql_action" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: standards_guidance_bands
DROP TABLE IF EXISTS "standards_guidance_bands" CASCADE;
CREATE TABLE "standards_guidance_bands" (
    "id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "source_short" TEXT NOT NULL,
    "source_pdf" TEXT NOT NULL,
    "source_page" TEXT NOT NULL,
    "use_case" TEXT NOT NULL,
    "parameter" TEXT NOT NULL,
    "context" TEXT NOT NULL,
    "unit" TEXT NOT NULL,
    "no_restriction" TEXT NOT NULL,
    "slight_to_moderate" TEXT NOT NULL,
    "severe" TEXT NOT NULL,
    "threshold_basis" TEXT NOT NULL,
    "db_handling" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: train_performance
DROP TABLE IF EXISTS "train_performance" CASCADE;
CREATE TABLE "train_performance" (
    "id" BIGINT NOT NULL,
    "train_id" BIGINT NOT NULL,
    "parameter" TEXT NOT NULL,
    "influent_low" DOUBLE PRECISION NOT NULL,
    "influent_high" DOUBLE PRECISION NOT NULL,
    "cum_removal_low" DOUBLE PRECISION NOT NULL,
    "cum_removal_high" DOUBLE PRECISION NOT NULL,
    "effluent_low" DOUBLE PRECISION NOT NULL,
    "effluent_high" DOUBLE PRECISION NOT NULL,
    "steps_with_data" BIGINT NOT NULL,
    "note" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: train_step
DROP TABLE IF EXISTS "train_step" CASCADE;
CREATE TABLE "train_step" (
    "id" BIGINT NOT NULL,
    "train_id" BIGINT NOT NULL,
    "step_order" BIGINT NOT NULL,
    "nbs_id" BIGINT NOT NULL,
    "step_label" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: train_usecase_match
DROP TABLE IF EXISTS "train_usecase_match" CASCADE;
CREATE TABLE "train_usecase_match" (
    "id" BIGINT NOT NULL,
    "train_id" BIGINT NOT NULL,
    "use_case" TEXT NOT NULL,
    "parameter" TEXT NOT NULL,
    "effluent_low" DOUBLE PRECISION NOT NULL,
    "effluent_high" DOUBLE PRECISION NOT NULL,
    "limit_val" DOUBLE PRECISION NOT NULL,
    "verdict" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: treatment_train
DROP TABLE IF EXISTS "treatment_train" CASCADE;
CREATE TABLE "treatment_train" (
    "id" BIGINT NOT NULL,
    "name" TEXT NOT NULL,
    "target_use_case" TEXT NOT NULL,
    "scale_context" TEXT NOT NULL,
    "notes" TEXT NOT NULL,
    "source_ids" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: water_observations
DROP TABLE IF EXISTS "water_observations" CASCADE;
CREATE TABLE "water_observations" (
    "id" BIGINT,
    "station" TEXT,
    "district" TEXT,
    "state" TEXT,
    "cwc_code" TEXT,
    "value_mean" DOUBLE PRECISION,
    "value_min" DOUBLE PRECISION,
    "value_max" DOUBLE PRECISION,
    "n_samples" BIGINT,
    "period" TEXT,
    "basin_id" BIGINT,
    "source_id" BIGINT,
    "parameter_id" BIGINT,
    "unit_id" BIGINT
);

-- Table: water_type_profile_change_log
DROP TABLE IF EXISTS "water_type_profile_change_log" CASCADE;
CREATE TABLE "water_type_profile_change_log" (
    "id" BIGINT NOT NULL,
    "change_key" TEXT NOT NULL,
    "change_type" TEXT NOT NULL,
    "affected_rows" BIGINT NOT NULL,
    "reason" TEXT NOT NULL,
    "old_value" TEXT NOT NULL,
    "new_value" TEXT NOT NULL,
    "source_ids" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: water_type_profile_source_map
DROP TABLE IF EXISTS "water_type_profile_source_map" CASCADE;
CREATE TABLE "water_type_profile_source_map" (
    "id" BIGINT NOT NULL,
    "water_type_profile_id" BIGINT NOT NULL,
    "source_id" BIGINT NOT NULL,
    "source_role" TEXT NOT NULL,
    "note" TEXT NOT NULL,
    "created_at" TEXT NOT NULL,
    PRIMARY KEY ("id")
);

-- Table: water_type_profiles
DROP TABLE IF EXISTS "water_type_profiles" CASCADE;
CREATE TABLE "water_type_profiles" (
    "id" BIGINT,
    "water_type" TEXT,
    "parameter" TEXT,
    "value_low" DOUBLE PRECISION,
    "value_high" DOUBLE PRECISION,
    "unit" TEXT,
    "note" TEXT,
    "deprecated" BIGINT,
    "source_id" BIGINT
);

-- Indexes
CREATE INDEX IF NOT EXISTS "ix_ambient_water_quality_source_id" ON "ambient_water_quality" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_ambient_water_quality_region_id" ON "ambient_water_quality" ("region_id");
CREATE INDEX IF NOT EXISTS "ix_ambient_water_quality_parameter_id" ON "ambient_water_quality" ("parameter_id");
CREATE INDEX IF NOT EXISTS "idx_app_caveats_status_severity" ON "app_caveats" ("status", "severity");
CREATE INDEX IF NOT EXISTS "idx_app_district_profile_district" ON "app_district_profile_cache" ("district");
CREATE INDEX IF NOT EXISTS "idx_app_input_template_usecase" ON "app_input_template" ("use_case");
CREATE INDEX IF NOT EXISTS "idx_app_parameter_aliases_param" ON "app_parameter_aliases" ("canonical_parameter");
CREATE INDEX IF NOT EXISTS "idx_criteria_weights_use_case" ON "criteria_weights" ("use_case");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_confidence_name" ON "dim_confidence" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_country_name" ON "dim_country" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_nbs_family_name" ON "dim_nbs_family" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_parameter_name" ON "dim_parameter" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_provenance_status_name" ON "dim_provenance_status" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_scale_name" ON "dim_scale" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_source_type_name" ON "dim_source_type" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_unit_name" ON "dim_unit" ("name");
CREATE UNIQUE INDEX IF NOT EXISTS "idx_dim_use_case_name" ON "dim_use_case" ("name");
CREATE INDEX IF NOT EXISTS "idx_nbs_app_rules_type" ON "nbs_applicability_rules" ("rule_type", "severity");
CREATE INDEX IF NOT EXISTS "idx_nbs_app_rules_target" ON "nbs_applicability_rules" ("target_level", "nbs_id", "nbs_family_id", "train_id");
CREATE INDEX IF NOT EXISTS "idx_nbs_app_rules_factor" ON "nbs_applicability_rules" ("factor_name");
CREATE INDEX IF NOT EXISTS "ix_nbs_design_nbs_id" ON "nbs_design" ("nbs_id");
CREATE INDEX IF NOT EXISTS "ix_nbs_footprint_source_id" ON "nbs_footprint" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_nbs_footprint_nbs_id" ON "nbs_footprint" ("nbs_id");
CREATE INDEX IF NOT EXISTS "ix_nbs_implementation_source_id" ON "nbs_implementation" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_nbs_implementation_nbs_id" ON "nbs_implementation" ("nbs_id");
CREATE INDEX IF NOT EXISTS "ix_nbs_options_family_id" ON "nbs_options" ("family_id");
CREATE INDEX IF NOT EXISTS "ix_plant_solution_map_confidence_id" ON "plant_solution_map" ("confidence_id");
CREATE INDEX IF NOT EXISTS "ix_plant_solution_map_source_id" ON "plant_solution_map" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_plant_solution_map_nbs_id" ON "plant_solution_map" ("nbs_id");
CREATE INDEX IF NOT EXISTS "ix_plant_solution_map_plant_id" ON "plant_solution_map" ("plant_id");
CREATE INDEX IF NOT EXISTS "ix_pollution_sources_source_id" ON "pollution_sources" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_pollution_sources_region_id" ON "pollution_sources" ("region_id");
CREATE INDEX IF NOT EXISTS "ix_regions_basin_id" ON "regions" ("basin_id");
CREATE INDEX IF NOT EXISTS "ix_removal_efficiency_confidence_id" ON "removal_efficiency" ("confidence_id");
CREATE INDEX IF NOT EXISTS "ix_removal_efficiency_country_id" ON "removal_efficiency" ("country_id");
CREATE INDEX IF NOT EXISTS "ix_removal_efficiency_scale_id" ON "removal_efficiency" ("scale_id");
CREATE INDEX IF NOT EXISTS "ix_removal_efficiency_source_id" ON "removal_efficiency" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_removal_efficiency_parameter_id" ON "removal_efficiency" ("parameter_id");
CREATE INDEX IF NOT EXISTS "ix_removal_efficiency_nbs_id" ON "removal_efficiency" ("nbs_id");
CREATE INDEX IF NOT EXISTS "ix_site_attributes_region_id" ON "site_attributes" ("region_id");
CREATE INDEX IF NOT EXISTS "ix_sources_source_type_id" ON "sources" ("source_type_id");
CREATE INDEX IF NOT EXISTS "ix_standards_source_id" ON "standards" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_standards_use_case_id" ON "standards" ("use_case_id");
CREATE INDEX IF NOT EXISTS "ix_standards_parameter_id" ON "standards" ("parameter_id");
CREATE INDEX IF NOT EXISTS "ix_train_step_nbs" ON "train_step" ("nbs_id");
CREATE INDEX IF NOT EXISTS "ix_train_step_train" ON "train_step" ("train_id");
CREATE INDEX IF NOT EXISTS "ix_water_observations_source_id" ON "water_observations" ("source_id");
CREATE INDEX IF NOT EXISTS "ix_water_observations_basin_id" ON "water_observations" ("basin_id");
CREATE INDEX IF NOT EXISTS "ix_water_observations_parameter_id" ON "water_observations" ("parameter_id");

-- Views
DROP VIEW IF EXISTS "v_app_cost_benefit_method" CASCADE;
CREATE OR REPLACE VIEW "v_app_cost_benefit_method" AS
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
    w.id;

DROP VIEW IF EXISTS "v_app_district_recommendation_hints" CASCADE;
CREATE OR REPLACE VIEW "v_app_district_recommendation_hints" AS
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
    FROM app_district_profile_cache;

DROP VIEW IF EXISTS "v_app_location_profile" CASCADE;
CREATE OR REPLACE VIEW "v_app_location_profile" AS
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
    FROM app_district_profile_cache;

DROP VIEW IF EXISTS "v_app_map_layers" CASCADE;
CREATE OR REPLACE VIEW "v_app_map_layers" AS
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
        104;

DROP VIEW IF EXISTS "v_app_nbs_catalog_cards" CASCADE;
CREATE OR REPLACE VIEW "v_app_nbs_catalog_cards" AS
WITH nf_agg AS (
        SELECT
            nbs_id,
            MIN(area_per_pe_low) AS area_per_pe_low,
            MAX(area_per_pe_high) AS area_per_pe_high,
            STRING_AGG(DISTINCT (olr_g_m2_d)::text, ', ') AS olr_g_m2_d,
            STRING_AGG(DISTINCT (hlr_m3_m2_d)::text, ', ') AS hlr_m3_m2_d,
            STRING_AGG(DISTINCT (depth_m)::text, ', ') AS depth_m,
            STRING_AGG(DISTINCT (note)::text, ', ') AS footprint_note
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
    LEFT JOIN nbs_design nd ON nd.nbs_id = n.id;

DROP VIEW IF EXISTS "v_app_open_caveats" CASCADE;
CREATE OR REPLACE VIEW "v_app_open_caveats" AS
SELECT severity, title, plain_language_message, technical_note, affected_tables, status, action_needed
    FROM app_caveats
    WHERE status IN ('open','active_guardrail')
    ORDER BY CASE severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, title;

DROP VIEW IF EXISTS "v_app_plant_catalog_cards" CASCADE;
CREATE OR REPLACE VIEW "v_app_plant_catalog_cards" AS
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
        STRING_AGG(DISTINCT (n.solution)::text, ', ') AS mapped_solutions,
        STRING_AGG(DISTINCT (dc.name)::text, ', ') AS mapping_confidence_labels,
        STRING_AGG(DISTINCT (psm.source_id)::text, ', ') AS evidence_source_ids
    FROM plants p
    LEFT JOIN plant_solution_map psm ON psm.plant_id = p.id
    LEFT JOIN nbs_options n ON n.id = psm.nbs_id
    LEFT JOIN dim_confidence dc ON dc.id = psm.confidence_id
    GROUP BY p.id;

DROP VIEW IF EXISTS "v_app_train_usecase_summary" CASCADE;
CREATE OR REPLACE VIEW "v_app_train_usecase_summary" AS
SELECT
        train_id,
        use_case,
        COUNT(*) AS parameters_checked,
        SUM(CASE WHEN verdict='pass' THEN 1 ELSE 0 END) AS pass_count,
        SUM(CASE WHEN verdict='marginal' THEN 1 ELSE 0 END) AS marginal_count,
        SUM(CASE WHEN verdict='fail' THEN 1 ELSE 0 END) AS fail_count,
        SUM(CASE WHEN verdict='unknown' THEN 1 ELSE 0 END) AS unknown_count,
        STRING_AGG((CASE WHEN verdict='fail' THEN parameter END)::text, ', ') AS failing_parameters,
        STRING_AGG((CASE WHEN verdict='marginal' THEN parameter END)::text, ', ') AS marginal_parameters,
        STRING_AGG((CASE WHEN verdict='unknown' THEN parameter END)::text, ', ') AS unknown_parameters
    FROM train_usecase_match
    GROUP BY train_id, use_case;

DROP VIEW IF EXISTS "v_app_train_cards" CASCADE;
CREATE OR REPLACE VIEW "v_app_train_cards" AS
WITH ordered_steps AS (
        SELECT
            ts.train_id,
            STRING_AGG((ts.step_order || '. ' || ts.step_label || ' [' || COALESCE(ts.role,'step') || ']')::text, ' → ') AS treatment_sequence
        FROM (
            SELECT * FROM train_step ORDER BY train_id, step_order
        ) ts
        GROUP BY ts.train_id
    ), perf AS (
        SELECT
            train_id,
            STRING_AGG((CASE
                    WHEN steps_with_data = 0 THEN parameter || ': unknown (data gap)'
                    ELSE parameter || ': ' || ROUND(cum_removal_low,1) || '-' || ROUND(cum_removal_high,1) || '%'
                END)::text, '; ') AS removal_summary
        FROM train_performance
        GROUP BY train_id
    ), usecases AS (
        SELECT
            train_id,
            STRING_AGG((use_case || ' pass/marginal/fail/unknown=' || pass_count || '/' || marginal_count || '/' || fail_count || '/' || unknown_count)::text, '; ') AS usecase_summary
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
    LEFT JOIN usecases ON usecases.train_id = t.id;

DROP VIEW IF EXISTS "v_app_upload_parameter_template" CASCADE;
CREATE OR REPLACE VIEW "v_app_upload_parameter_template" AS
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
    ORDER BY use_case, CASE priority WHEN 'required_if_available' THEN 1 WHEN 'recommended' THEN 2 ELSE 3 END, canonical_parameter;

DROP VIEW IF EXISTS "v_engine_usecase_matrix" CASCADE;
CREATE OR REPLACE VIEW "v_engine_usecase_matrix" AS
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
    WHERE u.name IN ('drinking','irrigation','discharge_inland');

DROP VIEW IF EXISTS "v_nbs_profile" CASCADE;
CREATE OR REPLACE VIEW "v_nbs_profile" AS
SELECT o.id AS nbs_id, o.solution, f.name AS family, o.optimal_water_type,
       (SELECT COUNT(*) FROM removal_efficiency r WHERE r.nbs_id=o.id) AS removal_rows,
       (SELECT COUNT(*) FROM removal_efficiency r WHERE r.nbs_id=o.id AND r.needs_corroboration=0) AS removal_corroborated,
       (SELECT COUNT(*) FROM nbs_footprint fp WHERE fp.nbs_id=o.id) AS has_footprint,
       (SELECT COUNT(*) FROM nbs_design dz WHERE dz.nbs_id=o.id) AS has_design
FROM nbs_options o LEFT JOIN dim_nbs_family f ON f.id=o.family_id;

DROP VIEW IF EXISTS "v_plant_use" CASCADE;
CREATE OR REPLACE VIEW "v_plant_use" AS
SELECT pm.id, pl.plant_species, o.solution AS nbs, pm.basis, cf.name AS confidence, s.short AS source
FROM plant_solution_map pm
LEFT JOIN plants pl ON pl.id=pm.plant_id
LEFT JOIN nbs_options o ON o.id=pm.nbs_id
LEFT JOIN dim_confidence cf ON cf.id=pm.confidence_id
LEFT JOIN sources s ON s.id=pm.source_id;

DROP VIEW IF EXISTS "v_removal" CASCADE;
CREATE OR REPLACE VIEW "v_removal" AS
SELECT r.id, o.solution AS nbs, p.name AS parameter, r.eff_low, r.eff_high,
       cf.name AS confidence, sc.name AS scale, co.name AS country,
       r.influent_context, r.hrt_loading, r.needs_corroboration, s.short AS source
FROM removal_efficiency r
LEFT JOIN nbs_options o ON o.id=r.nbs_id
LEFT JOIN dim_parameter p ON p.id=r.parameter_id
LEFT JOIN dim_confidence cf ON cf.id=r.confidence_id
LEFT JOIN dim_scale sc ON sc.id=r.scale_id
LEFT JOIN dim_country co ON co.id=r.country_id
LEFT JOIN sources s ON s.id=r.source_id;

DROP VIEW IF EXISTS "v_standards" CASCADE;
CREATE OR REPLACE VIEW "v_standards" AS
SELECT st.id, uc.name AS use_case, p.name AS parameter, st.limit_low, st.limit_high, st.direction, u.name AS unit, s.short AS source
FROM standards st
LEFT JOIN dim_use_case uc ON uc.id=st.use_case_id
LEFT JOIN dim_parameter p ON p.id=st.parameter_id
LEFT JOIN dim_unit u ON u.id=st.unit_id
LEFT JOIN sources s ON s.id=st.source_id;

DROP VIEW IF EXISTS "v_train" CASCADE;
CREATE OR REPLACE VIEW "v_train" AS
SELECT t.id AS train_id, t.name AS train, t.target_use_case, t.scale_context,
       ts.step_order, COALESCE(o.solution, ts.step_label) AS step, ts.role
FROM treatment_train t JOIN train_step ts ON ts.train_id=t.id
LEFT JOIN nbs_options o ON o.id=ts.nbs_id ORDER BY t.id, ts.step_order;

DROP VIEW IF EXISTS "v_train_performance" CASCADE;
CREATE OR REPLACE VIEW "v_train_performance" AS
SELECT t.name AS train, tp.parameter, tp.cum_removal_low, tp.cum_removal_high,
  tp.effluent_low, tp.effluent_high, tp.steps_with_data FROM train_performance tp JOIN treatment_train t ON t.id=tp.train_id;

DROP VIEW IF EXISTS "v_train_usecase" CASCADE;
CREATE OR REPLACE VIEW "v_train_usecase" AS
SELECT t.name AS train, m.use_case, m.parameter, m.effluent_low, m.effluent_high, m.limit_val, m.verdict
  FROM train_usecase_match m JOIN treatment_train t ON t.id=m.train_id;

COMMIT;

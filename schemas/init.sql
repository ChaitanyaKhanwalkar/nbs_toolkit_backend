create table district_data(
    id int primary key,
    state_name varchar(50) not null,
    soil_type varchar(50) not null
);

create table plant_data(
    id int primary key,
    plant_species varchar(50) not null,
    locational_availability varchar(50) not null,
    climate_preference varchar(50) not null,
    soil_type varchar(50) not null,
    water_needs varchar(50) not null,
    ecological_role varchar(100) not null,
    pollution_tolerance varchar(100) not null,
    state_name varchar(50) not null,
    optimal_water_type varchar(50) not null

);

create table water_data(
    id int primary key,
    water_type varchar(50) not null,
    colour varchar(50) not null,
    turbidity varchar(10) not null,
    temperature varchar(10) not null,
    odour varchar(50) not null,
    tss varchar(50) not null,
    ph varchar(50) not null,
    bod varchar(50) not null,
    cod varchar(50) not null,
    nitrate varchar(50) not null,
    phosphate varchar(50) not null,
    ammonia varchar(50) not null,
    chloride varchar(50) not null,
    sample_source varchar(50),
    sample_timestamp varchar(50) not null,
    raw_data varchar(50)

);

create table nbs_options(
    id int primary key,
    solution varchar(60) not null,
    optimal_water_type varchar(50) not null,
    location_suitability varchar(60) not null,
    climate_suitability varchar(60) not null,
    climate_suitability varchar(60) not null,
    soil_type varchar(60) not null,
    resource_requirements varchar(100) not null,
    notes varchar(100) not null,
    state_name varchar(50) not null
);

create table nbs_implementation(
    id int primary key,
    solution varchar(60) not null,
    implementation_steps varchar(100) not null,
    maintenance_requirements varchar(100) not null
);

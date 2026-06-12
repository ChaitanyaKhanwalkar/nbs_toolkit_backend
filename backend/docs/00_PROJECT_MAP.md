# Project Map

This document explains the backend folder layout in beginner-friendly language.

The backend is organized in layers. Each folder has one main job, so future code is easier to read, test, and review.

## Quick Start For Beginners

Read these files first:

1. `AGENTS.md` - project rules and non-negotiable safety boundaries.
2. `backend/docs/01_EXISTING_BACKEND_AUDIT.md` - explains old MVP logic versus the future research logic.
3. `backend/docs/02_TARGET_BACKEND_STRUCTURE.md` - explains the target layered backend.
4. `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` - defines the future scientific recommendation logic.
5. `backend/docs/03_DEVELOPMENT_WORKFLOW.md` - explains how to work safely without touching production.

## backend/

The root folder for the production backend skeleton.

It contains application code, tests, documentation, and database migration scaffolding.

## backend/app/

The Python application package.

Most backend code will eventually live here, split into smaller folders by responsibility.

## backend/app/main.py

The future entry point for the API server.

At this stage it is only a placeholder. It does not create production routes, connect to Azure, or implement recommendation logic.

## backend/app/core/

Shared application setup belongs here.

Use this folder later for:

- environment-based settings
- logging setup
- app startup and shutdown helpers
- safe configuration loading

Do not put secrets, hard-coded Azure settings, scientific scores, or recommendation formulas here.

## backend/app/db/

Database connection code belongs here.

Change database connection/session code in this folder later.

Use this folder for:

- local database connection setup
- session helpers
- transaction helpers
- migration integration

Do not write recommendation logic here. This folder should explain how the app connects to the database, not how scientific decisions are made.

## backend/app/models/

Database table models belong here.

Change database model definitions in this folder later.

Models should match the approved schema files:

- `schema.sql`
- `schema_river_network_patch.sql`

Models describe table shape and relationships. They should not query the database directly and should not rank NbS options.

The current model files are grouped one table per file, such as `source.py`,
`water_observation.py`, and `river_network.py`. Pending tables that are not in
the schema yet, such as `criteria_weights` and `health_risk`, are documented in
`backend/docs/04_PENDING_TABLES.md` instead of being created as active models.

## backend/app/schemas/

API request and response schemas belong here.

Use this folder to define:

- what inputs an endpoint accepts
- what outputs an endpoint returns
- validation-friendly response shapes

The current schema files describe raw read-only response shapes for reference
data, site profiles, water observations, standards, NbS catalogue records,
plants, pollution context, river context, and data availability checks. They
match the service layer where possible and keep fields optional because some
research data may be incomplete.

`backend/app/schemas/engine.py` describes safe JSON shapes for existing
internal scientific engine bundles from Steps A-E. It is for future
serialization and testing only; it does not create workflow routes or final
recommendation responses.

Schemas are especially important for future recommendation responses because every output should include explanations, cautions, confidence, and provenance.

Do not add recommendation response fields, TOPSIS rankings, AHP weights,
exceedance labels, or health-risk classifications until the scientific engine
readiness gate is satisfied.

## backend/app/repositories/

Database query code belongs here.

Change database query behavior in this folder later.

Repositories should be the only backend layer that directly queries tables. For example:

- `water_repository` can fetch water observations.
- `standards_repository` can fetch standards for a use case.
- `sources_repository` can fetch citations and provenance.

API routes should not query raw tables directly.

The current repository files are read-only. They return ORM objects, lists,
simple dictionaries, `None`, or empty lists. They do not write to the database
and do not contain recommendation scoring, ranking, or exceedance calculations.

## backend/app/services/

Scientific workflow orchestration belongs here.

Services connect steps together. A future recommendation service may:

- resolve a site
- load measured water-quality data
- select the correct standard
- call engine modules in the approved order
- attach implementation guidance and provenance

Services should call repositories for data and engines for calculations.

The current service files prepare raw data packets only. They combine
repository outputs into dictionaries and lists for future API schemas. They do
not calculate exceedance, health risk, AHP weights, TOPSIS rankings, or
recommendations.

`scientific_workflow_service.py` is an internal coordinator for Scientific
Engine Steps A-E. It runs the staged engines in order and returns their
intermediate bundles only; it does not expose an endpoint or create final
recommendations.

## backend/app/engines/

Future scientific logic and recommendation calculations will live here.

Change scientific logic in this folder later, but only after the repository, service, engine, and schema layers are ready.

The current engine files implement Step A, Step B, Step C, Step D, Step E, Step F, Step G, Step H, Step I, and Step J
only. Step A handles input normalization and target use-case validation. Step B
assembles raw water observations by priority: user measured data, then station
observations, then basin observations, then a safe missing-data bundle. Step C
calculates pollutant gaps against explicit standards for a selected use case.
Step D classifies broad treatment-need groups from those gap results using
explicit parameter mappings. Step E checks which NbS catalogue candidates are
eligible, ineligible, or data-pending for those treatment needs. Step F prepares
raw MCDA matrix rows for eligible and data-pending candidates without
normalizing, weighting, or ranking them. Step G normalizes numeric MCDA criteria
with explicit min-max rules only and still does not apply weights, TOPSIS, or
ranking. Step H validates optional supplied MCDA criteria weights, reports
missing or extra weights, and clearly marks temporary weights as not expert
validated. Step I applies the Step H weights to Step G normalized criteria and
calculates TOPSIS closeness/rank order for eligible and data-pending candidates.
Step J calculates rule-based confidence scores separately from TOPSIS closeness,
preserves rank, and labels confidence as high, medium, or low. These steps
prepare, rank, and confidence-label candidate technologies, but do not create
final recommendations, classify health risk, or recommend plants.

Later engine modules may handle:

- plant selection after technology ranking and confidence scoring
- final recommendation assembly after plant and confidence layers are ready

Do not implement recommendation code yet. The rules are defined in `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

## backend/app/api/

API route definitions belong here.

Change API routes in this folder later.

Routes should be thin. Their job is to:

- receive requests
- validate input through schemas
- call services
- return responses

Routes should not directly query database tables and should not contain scientific ranking logic.

The current API routes are read-only raw data endpoints mounted under
`/api/v1`. They expose reference data, site profiles, water observations,
standards, NbS catalogue records, plants, pollution context, river context, and
data availability checks.

There is intentionally no `/recommend` endpoint yet. Do not add recommendation
routes until the approved scientific engine work begins.

## backend/app/data_ingestion/

Controlled data import helpers belong here.

Use this folder later for scripts or modules that load approved datasets, check file formats, or prepare migration inputs.

Because this project is provenance-first, ingestion code must preserve source IDs and must not silently change scientific values.

## backend/app/validators/

Validation helpers belong here.

Use this folder later for checks such as:

- whether a region ID exists
- whether a requested use case is valid
- whether required provenance fields are present
- whether uploaded data has the needed columns

Validators should report problems clearly instead of hiding missing data.

## backend/app/utils/

Small shared helper functions belong here.

Only use this folder for simple reusable helpers that do not fit a clearer domain folder. Do not use it as a dumping ground for database access or recommendation logic.

## backend/tests/

Automated tests belong here.

Future tests should cover repositories, services, validators, and engines. Tests should also verify that recommendations do not contain invented or unsourced values.

## backend/docs/

Backend documentation belongs here.

Use this folder for architecture notes, development workflow, scientific rules, audits, and beginner-friendly guides.

## backend/alembic/

Database migration scaffolding belongs here.

Alembic is commonly used to track database schema changes over time. Future migration files should describe structural schema changes only. They should not invent or silently alter scientific data.

## Where To Change Things Later

Change database connection code in `backend/app/db/`.

Change database table models in `backend/app/models/`.

Change database queries in `backend/app/repositories/`.

Change API routes in `backend/app/api/`.

Change request and response shapes in `backend/app/schemas/`.

Change scientific workflow orchestration in `backend/app/services/`.

Change scientific calculations and recommendation logic in `backend/app/engines/`, but only after the readiness gate in `backend/docs/02_TARGET_BACKEND_STRUCTURE.md` is satisfied.

## Conflict Note

This scaffold does not move or delete older backend folders such as `nbs_toolkit_backend-main` or `nbs_toolkit_backend-reborn`.

No old code was found inside `backend/app/` during this documentation pass. If old code is later copied into `backend/app/`, document the conflict before rewriting or moving it.

## Data Context Read For This Scaffold

This scaffold and documentation were aligned after reading:

- `AGENTS.md`
- `backend/docs/01_EXISTING_BACKEND_AUDIT.md`
- `backend/docs/02_TARGET_BACKEND_STRUCTURE.md`
- `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`
- `research/main_v2/files/DATA_DICTIONARY.md`
- `research/main_v2/files/schema.sql`
- `research/gpt given stuff/schema_river_network_patch.sql`

No scientific data files were changed.

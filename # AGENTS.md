# AGENTS.md — NBS APP Backend Build Rules

## Project Goal

Build a production-quality, research-grade backend for the Narmada NbS decision-support toolkit.

The backend must be:
- modular
- beginner-readable
- well documented
- testable
- future-extensible
- provenance-first
- suitable for scientific review

## Non-Negotiable Rules

1. Do not delete data files unless explicitly asked.
2. Do not invent scientific values, weights, health-risk scores, citations, or sources.
3. Health-risk data and AHP criteria weights are pending expert consultation.
4. Keep placeholder structures for future health-risk and criteria-weight integration.
5. Build incrementally.
6. Make small, reviewable commits/changes.
7. Every important file must include a short top-level docstring explaining its purpose.
8. Every service must have a clear single responsibility.
9. The API layer must not directly query raw database tables.
10. Use repositories for database access.
11. Use services for scientific/business logic.
12. Use engines for scoring/recommendation logic.
13. All configuration must come from environment variables or config files, not hard-coded secrets.
14. Add tests for important logic.
15. Update docs whenever folder structure or behavior changes.

## Data Truth

The current authoritative data assets are:
- canonical db/narmada_nbs_canonical.db
- canonical db/DATA_DICTIONARY_canonical.md
- canonical db/DATA_SOURCING_LOG.md
- HANDOFF (1).md
- canonical db/narmada_nbs_canonical_csvs.zip
- canonical db/narmada_nbs_canonical_csvs/

Older database/schema assets such as narmada_nbs_with_river_network.db,
schema.sql, schema_river_network_patch.sql, and the older simple CSVs are
legacy/reference only unless the handoff explicitly says otherwise.

## Target Backend Structure

backend/
  app/
    main.py
    core/
    db/
    models/
    schemas/
    repositories/
    services/
    engines/
    api/
    data_ingestion/
    validators/
    utils/
  tests/
  docs/
  alembic/

## Build Philosophy

This project should be understandable by a starting-level student.
Prefer clear code over clever code.
Use comments and docstrings to explain why something exists.

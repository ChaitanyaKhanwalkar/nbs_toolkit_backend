# PostgreSQL Migration Package

This package prepares a reviewed, reproducible path from the canonical SQLite
mirror to PostgreSQL, including Azure PostgreSQL Flexible Server later.

## What This Does

- Audits the live SQLite schema in `canonical db/narmada_nbs_canonical.db`.
- Generates a PostgreSQL schema draft in `deployment/postgres/generated/schema_pg.sql`.
- Provides a migration script that imports table data in batches.
- Provides a verification script that compares row counts against the canonical
  SQLite mirror.

## What This Does Not Do

- It does not deploy to Azure.
- It does not change recommendation or scientific logic.
- It does not edit canonical SQLite data.
- It does not invent scientific values, weights, sources, standards, or
  citations.
- It does not hardcode credentials.

Warning: no scientific values are changed by this migration. The migration only
moves the canonical DB into PostgreSQL format.

## Required Environment Variables

For migration or PostgreSQL verification:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require"
```

Do not commit real credentials. Use Azure App Service / GitHub secrets / local
shell environment variables.

## Generate Schema And Audit

```powershell
python backend/scripts/generate_postgres_schema_from_sqlite.py `
  --sqlite "canonical db/narmada_nbs_canonical.db" `
  --schema "deployment/postgres/generated/schema_pg.sql" `
  --report "deployment/postgres/generated/schema_generation_report.md" `
  --audit "deployment/postgres/sqlite_schema_audit.md"
```

## Local PostgreSQL Dry Run

Run this only against an empty throwaway database:

```powershell
python backend/scripts/migrate_sqlite_to_postgres.py `
  --sqlite "canonical db/narmada_nbs_canonical.db" `
  --postgres-url "$env:DATABASE_URL" `
  --schema "deployment/postgres/generated/schema_pg.sql"

python backend/scripts/verify_postgres_migration.py `
  --sqlite "canonical db/narmada_nbs_canonical.db" `
  --postgres-url "$env:DATABASE_URL"
```

## Azure PostgreSQL Command Shape

After Azure PostgreSQL Flexible Server exists and firewall/network access is
configured, set `DATABASE_URL` to the Azure PostgreSQL connection string and run
the same migration command from a secure machine or CI job with access.

```powershell
$env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@SERVER.postgres.database.azure.com:5432/DB?sslmode=require"
python backend/scripts/migrate_sqlite_to_postgres.py --postgres-url "$env:DATABASE_URL"
python backend/scripts/verify_postgres_migration.py --postgres-url "$env:DATABASE_URL"
```

## Rollback And Safety Notes

- Import into an empty database first.
- Keep `canonical db/narmada_nbs_canonical.db` as the working mirror until the
  PostgreSQL import is reviewed and verified.
- If import fails, drop the throwaway PostgreSQL database/schema and rerun after
  fixing the generated DDL or migration script.
- Do not modify canonical SQLite as part of deployment migration.

## Review Requirement

Generated files must be reviewed before production. SQLite and PostgreSQL differ
in type affinity, default expressions, index support, and view functions. Views
that use SQLite-specific syntax are commented/skipped for manual conversion
instead of guessed.

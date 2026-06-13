# Pending Tables

This document records tables that are referenced by the scientific plan but are
not present in the current approved schema files.

Do not create active SQLAlchemy models for these tables until the schema is
approved and added to `schema.sql` or a reviewed migration.

## criteria_weights

Status: pending expert/AHP workflow.

Why it matters:

- Future recommendation ranking may use AHP-derived weights.
- The current schema files do not define this table.
- Fake or default expert weights must not be invented.

Next safe step:

- Wait for supervisor-approved AHP outputs and an approved schema/migration.

## health_risk

Status: pending supervisor data integration.

Why it matters:

- Future recommendation confidence may use health-risk information.
- The current schema files do not define this table.
- HQ, HI, cancer-risk values, or other health-risk scores must not be invented.

Next safe step:

- Wait for the approved health-risk dataset and an approved schema/migration.

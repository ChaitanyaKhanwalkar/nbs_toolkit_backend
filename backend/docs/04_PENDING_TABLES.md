# Pending Tables

This document records tables that are referenced by the scientific plan but are
not present in the current approved schema files.

Do not create active SQLAlchemy models for these tables until the schema is
approved and added to `schema.sql` or a reviewed migration.

## criteria_weights

Status: implemented with 21 `UNVERIFIED_PROVISIONAL` rows.

Why it matters:

- Interim train ranking uses the canonical DB rows for C1-C4 and C6-C8.
- C5 health risk remains reserved and unweighted.
- The weights are not expert-final and must stay visibly provisional.

Next safe step:

- Replace the provisional rows after supervisor-approved pairwise AHP outputs.

## health_risk

Status: pending supervisor data integration.

Why it matters:

- Future recommendation confidence may use health-risk information.
- The current schema files do not define this table.
- HQ, HI, cancer-risk values, or other health-risk scores must not be invented.

Next safe step:

- Wait for the approved health-risk dataset and an approved schema/migration.

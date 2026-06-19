# Models

Put database table models here.

Models should match the approved schema from `schema.sql` and `schema_river_network_patch.sql`.

Models describe data shape. They should not contain recommendation logic or scientific scoring.

The active models use each table's `id` column as the SQLAlchemy ORM identity
key. The current base schema lists most `id` columns as plain `INTEGER`, but
the ORM needs a primary key to map rows.

Pending tables such as `health_risk` are documented in
`backend/docs/04_PENDING_TABLES.md` until their schemas are approved.

Import smoke test from the `backend/` folder after installing requirements:

```powershell
python -c "from app.models import Source, Region, RiverNetwork; print('models import ok')"
```

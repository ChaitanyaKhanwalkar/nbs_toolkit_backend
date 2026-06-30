# Azure Backend Deployment Readiness

This folder documents the Azure App Service deployment path for the FastAPI
backend only.

It does not deploy the Flutter frontend, create Azure PostgreSQL, create DNS
records, or import the database. Keep those as separate reviewed steps.

## Required Azure Resources

- Azure App Service for the backend API.
- Azure PostgreSQL Flexible Server with the migrated canonical schema/data.
- A deployed frontend origin later, so production CORS can be restricted to the
  real frontend URL.

## Required App Service Settings

Set these in Azure App Service configuration. Do not commit real values to git.

```text
APP_ENV=production
DATABASE_URL=<Azure PostgreSQL SQLAlchemy URL>
CORS_ALLOW_ORIGINS=<frontend URL or comma-separated frontend URLs>
```

Use a SQLAlchemy PostgreSQL URL accepted by the backend, for example the shape:

```text
postgresql+psycopg://USER:PASSWORD@SERVER.postgres.database.azure.com:5432/DB?sslmode=require
```

The backend also accepts `postgresql://...` and normalizes it to the installed
`psycopg` driver.

## Startup Command

Preferred Azure Linux App Service startup command:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind=0.0.0.0:${PORT:-8000}
```

The same command is saved in `deployment/azure/backend/startup-command.txt`.
The deployment package is zipped from `backend/`, so `app.main:app` is available
at the package root.

## Proven Dry-Run State

The local SQLite to PostgreSQL dry-run has already passed:

- PostgreSQL objects: 58 tables and 18 views.
- Imported rows: 57,521.
- Key canonical counts verified.
- Backend tests against PostgreSQL: 106 passed.
- FastAPI smoke test against PostgreSQL: passed.

## Health Checks

After deployment and before connecting production traffic, check:

```text
/health
/health/db
/api/v1/reference
/api/v1/sites/options
```

You can run:

```powershell
python backend/scripts/smoke_test_backend.py --base-url https://YOUR-APP.azurewebsites.net
```

## CORS

For production, avoid `*` unless the API is intentionally public. Set
`CORS_ALLOW_ORIGINS` to the deployed frontend origin, or a comma-separated list
of approved origins.

## Rollback Notes

- Keep the previous App Service deployment slot/version available until the new
  backend passes health checks.
- Verify PostgreSQL import counts before pointing production backend settings to
  the Azure database.
- If health checks fail, roll App Service back to the previous known-good
  version and keep the database unchanged until the failure is reviewed.

# API

This folder contains FastAPI route definitions for the production backend.

Routes are thin wrappers. They should:

- receive HTTP GET requests
- use `app.db.session.get_db` for a database session
- call service classes in `backend/app/services/`
- return Pydantic response shapes from `backend/app/schemas/`

Routes should not query database tables directly. Repositories handle database
queries, and services prepare raw data packets.

Current routes are read-only raw data access routes under `/api/v1`.

Do not add POST, PUT, PATCH, or DELETE routes unless a future task explicitly
asks for them.

Do not add `/recommend` here yet. Recommendation logic must follow
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` and should only be built
after the repository, service, engine, and schema layers are ready.

## Local Route Smoke Test

Run this from the `backend/` folder after installing requirements:

```powershell
set PYTHONPATH=%CD%
python tests\api_smoke_test.py
```

In PowerShell, the equivalent environment command is:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python tests\api_smoke_test.py
```

The smoke test uses FastAPI `TestClient` and an in-memory SQLite database. It
does not connect to Azure, does not need production data, and does not mutate
database records.

The test checks:

- `/health`
- `/health/db`
- raw `/api/v1` reference, water, standards, NbS, plant, and availability routes
- route-order safety for literal routes such as `/nbs/options`
- missing-resource 404 behavior
- OpenAPI output
- that current `/api/v1` routes expose only `GET`
- that `/api/v1/recommend` does not exist

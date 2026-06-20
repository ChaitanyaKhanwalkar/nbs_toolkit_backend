# API

This folder contains FastAPI route definitions for the production backend.

Routes are thin wrappers. They should:

- receive HTTP GET requests for raw data routes
- receive the local POST `/recommend` request for the staged recommendation workflow
- use `app.db.session.get_db` for a database session
- call service classes in `backend/app/services/`
- return Pydantic response shapes from `backend/app/schemas/`

Routes should not query database tables directly. Repositories handle database
queries, and services prepare raw data packets.

Current routes include read-only raw data access routes under `/api/v1` plus a
local `/api/v1/recommend` workflow wrapper.

Do not add POST, PUT, PATCH, or DELETE routes unless a future task explicitly
asks for them.

Do not add more recommendation endpoints here without an explicit future task.
The local `/recommend` route must call `ScientificWorkflowService.run(...)`
with `max_step="L"`, keep temporary weights visibly provisional, and follow
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

The recommendation response also attaches two non-ranking decision-support
objects:

- `location_context` contains verified site fields, request context, placement
  flags, and explicit missing-site information. Coordinates are null unless
  both values exist in stored site records.
- `design_readiness` applies transparent conservative rules after ranking. It
  does not change TOPSIS rank or confidence and does not perform engineering
  sizing.

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
- local `/api/v1/recommend` route wiring is covered by the recommendation API tests
- route-order safety for literal routes such as `/nbs/options`
- missing-resource 404 behavior
- OpenAPI output
- that raw-data `/api/v1` routes remain `GET`
- that `/api/v1/recommend` is the only current versioned `POST` route

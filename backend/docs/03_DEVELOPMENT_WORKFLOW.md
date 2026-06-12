# Development Workflow

This document explains how to work on the backend safely.

The short version: work locally, make small changes, do not touch production Azure settings, and update `DEVLOG.md` after each session.

## 1. Work Safely On A Branch

Before making code changes, use a branch that clearly describes the task.

Example branch names:

```text
backend-scaffold-docs
backend-model-alignment
backend-repository-layer
```

Recommended habit:

1. Read `AGENTS.md`.
2. Read the relevant files in `backend/docs/`.
3. Check what files already exist.
4. Make the smallest useful change.
5. Run local checks if the project has them.
6. Update `DEVLOG.md`.
7. Summarize changed files and any risks.

Do not combine unrelated work in one branch. For example, do not mix documentation, Azure deployment settings, and recommendation algorithms in one change.

## 2. Avoid Touching Azure Production

Do not change production Azure settings during normal backend development.

Avoid editing files that control deployment, production secrets, or production connection strings unless a future task explicitly asks for it.

Do not modify:

- production deployment configuration
- production secrets
- `.env` files
- Azure connection strings
- production startup commands
- live endpoint routing for old endpoints

Do not connect this branch to production deployment.

If local development needs configuration, use a local-only example file or documented environment variables. Never commit real secrets.

## 3. Run The Backend Locally

The backend now has a small FastAPI app with health checks only. It does not implement recommendation logic.

Use these PowerShell commands from the workspace root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env` and set `DATABASE_URL`.

For local SQLite development, keep the example value:

```text
DATABASE_URL="sqlite:///./narmada_nbs_local.db"
```

For local or development PostgreSQL, use a non-production connection string:

```text
DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/narmada_nbs_dev"
```

Do not put production Azure credentials in `.env`.

Start the local server:

```powershell
python -m uvicorn app.main:app --reload
```

Test the health endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/health/db
```

The `/health` endpoint checks that the app is running. The `/health/db` endpoint checks whether the configured database can run a simple `SELECT 1`.

Do not point local development at production Azure resources. Use local or approved development data.

Run the read-only API route smoke test:

```powershell
set PYTHONPATH=%CD%
python tests\api_smoke_test.py
```

If you are already inside PowerShell, use:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python tests\api_smoke_test.py
```

This test uses an in-memory SQLite database for route checks. It does not need
Azure and does not write scientific records.

## Scientific Workflow Test Commands

Run these commands from `backend/` when checking the staged scientific workflow
and schema serialization layers:

```cmd
set PYTHONPATH=%CD%
python tests\input_normalization_test.py
python tests\water_input_assembly_test.py
python tests\pollutant_gap_test.py
python tests\treatment_need_test.py
python tests\candidate_filtering_test.py
python tests\scientific_engine_ad_integration_test.py
python tests\scientific_engine_ae_integration_test.py
python tests\scientific_engine_af_integration_test.py
python tests\scientific_engine_ag_integration_test.py
python tests\scientific_engine_ah_integration_test.py
python tests\scientific_engine_ai_integration_test.py
python tests\scientific_engine_aj_integration_test.py
python tests\scientific_engine_ak_integration_test.py
python tests\engine_schema_smoke_test.py
python tests\engine_schema_conversion_test.py
python tests\mcda_matrix_schema_test.py
python tests\mcda_matrix_schema_conversion_test.py
python tests\mcda_normalization_schema_test.py
python tests\mcda_normalization_schema_conversion_test.py
python tests\mcda_weights_test.py
python tests\mcda_weights_schema_test.py
python tests\mcda_weights_schema_conversion_test.py
python tests\topsis_ranking_test.py
python tests\topsis_ranking_schema_test.py
python tests\topsis_ranking_schema_conversion_test.py
python tests\confidence_scoring_test.py
python tests\confidence_scoring_schema_test.py
python tests\confidence_scoring_schema_conversion_test.py
python tests\plant_matching_test.py
python tests\plant_matching_schema_test.py
python tests\plant_matching_schema_conversion_test.py
python tests\scientific_workflow_service_test.py
python tests\workflow_schema_test.py
python tests\workflow_schema_conversion_test.py
python tests\scientific_workflow_service_aj_test.py
python tests\workflow_aj_schema_test.py
python tests\workflow_aj_schema_conversion_test.py
python tests\scientific_workflow_service_ak_test.py
python tests\workflow_ak_schema_test.py
python tests\workflow_ak_schema_conversion_test.py
python tests\scientific_workflow_service_al_test.py
python tests\workflow_al_schema_test.py
python tests\workflow_al_schema_conversion_test.py
```

These tests validate staged scientific workflow behavior only. Some tests now
exercise Step I TOPSIS ranking, Step J confidence scoring, and Step K explicit
plant matching. Step L workflow tests exercise internal recommendation assembly
only. They do not expose `/recommend`, run AHP, or change deployment settings.

## Internal Workflow Service Note

`ScientificWorkflowService.run(...)` defaults to the safe A-E path. That means
it stops after input normalization, water input assembly, pollutant gaps,
treatment need classification, and candidate filtering unless a later step is
explicitly requested.

Use `max_step="J"` only when you intentionally want the staged A-J internal
workflow. The A-J path adds MCDA matrix preparation, MCDA normalization, criteria
weights handling, TOPSIS ranking, and confidence scoring. It still does not
create final recommendations and does not create or expose `/recommend`.

Use `max_step="K"` only when you intentionally want the staged A-K internal
workflow. The A-K path runs A-J first, then attaches explicitly mapped plants
through Step K. Plant matching preserves rank, TOPSIS closeness,
`confidence_score`, and `confidence_label`; missing plant mappings produce empty
plant match lists with warnings instead of guessed plant records.

Use `max_step="L"` only when you intentionally want the staged A-L internal
workflow. The A-L path runs A-K first, then assembles internal recommendation
objects through Step L. Step L sets `match_score` equal to `topsis_closeness`,
keeps `confidence_score` separate, preserves rank and `weights_status`, and
still does not create a `/recommend` endpoint.

Keep TOPSIS closeness separate from `confidence_score`. Temporary weights must
remain visibly marked as `temporary_not_expert_validated`; do not present them
as expert-validated weights.

## 4. Add Future Modules Step By Step

Build the backend in layers.

Recommended order:

1. Add settings/configuration in `backend/app/core/`.
2. Add database session setup in `backend/app/db/`.
3. Add models in `backend/app/models/` that match the approved schema.
4. Add repositories in `backend/app/repositories/` for database access.
5. Add schemas in `backend/app/schemas/` for API inputs and outputs.
6. Add validators in `backend/app/validators/` for input and data-quality checks.
7. Add services in `backend/app/services/` to orchestrate workflows.
8. Add engines in `backend/app/engines/` only when the recommendation readiness gate is met.
9. Add API routes in `backend/app/api/` that call services.
10. Add tests in `backend/tests/`.

Recommendation logic must not be implemented until the repository, service, engine, and schema layers are ready.

When recommendation work begins later, follow `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

## 5. Keep Old Endpoints Safe

Old MVP endpoints and older backend folders should not be deleted during the transition.

If old MVP logic conflicts with the new architecture, document the conflict first. Do not force a rewrite as part of scaffolding or documentation work.

The old MVP logic is state/water-type/fuzzy matching. The future research logic is pollutant-first, standard-based, site-constrained, evidence-ranked, confidence-labelled, and provenance-linked.

## 6. Update DEVLOG After Each Session

After each development session, update `DEVLOG.md` at the workspace root.

Keep entries short and useful. Include:

- date
- files changed
- what changed
- what was intentionally not changed
- tests or checks run
- next recommended step

Example entry:

```text
## 2026-06-11

- Added backend folder READMEs and development workflow docs.
- Did not implement recommendation logic.
- Did not change Azure deployment settings or secrets.
- Check run: verified backend folder tree.
- Next: add local dependency/config plan before implementing db sessions.
```

If no tests exist yet, write that clearly instead of pretending tests ran.

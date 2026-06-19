# DEVLOG — NbS Toolkit

Append a dated entry at the end of every work session. This is not busywork: it is the
Methods / reproducibility trail for the internship report and the paper. Capture the *why*,
not just the *what*. Newest entries at the top.

## 2026-06-19 - Canonical train recommendation flow

- Added DB-driven A0 applicability filtering before TOPSIS, including high-order
  in-channel relocation rules and industrial ETP/CETP pretreatment caveats.
- Added treatment-train C1-C8 criterion assembly; C5 remains reserved with no
  invented health-risk value.
- Added provisional DB-weighted TOPSIS, separate dynamic confidence, all-three
  use-case verdicts, train sequences, components, plants, caveats, and evidence.
- Added non-persistent CSV upload analysis and canonical station options routes.
- Connected Flutter site, pollution screening, and CSV upload workflows and
  replaced option cards with expandable treatment-train results.
- Verification: 13 pytest checks passed; legacy script suite rerun separately.

Template:

## YYYY-MM-DD — <short title>
**Done:** what changed (files, schema, data).
**Why:** the reasoning / the decision made and the alternative rejected.
**Sources added:** any datasets/papers/standards wired in (with citation).
**Gaps / NULLs logged:** values left empty for lack of a source.
**Blockers / next:** what's stuck, what's next.

---

## 2026-06-18 - Stabilize backend on canonical database
**Done:** Re-pointed local backend configuration to `canonical db/narmada_nbs_canonical.db`; added canonical-aware repository read paths for normalized water observations, standards, sources, NbS options/removal/implementation/O&M design, and folded site-stream attributes; kept old-schema fallbacks for in-memory tests and legacy snapshots. Added `httpx2>=0.28` for current FastAPI/Starlette TestClient support. Updated AGENTS and backend docs to make the canonical DB and handoff the current source of truth.
**Why:** `HANDOFF (1).md` showed the engine was still running on the stale 95-removal/56-source pre-regrounding DB. The fix was to evolve the data-access layer onto the canonical 167-removal/104-source DB, not rebuild the engine.
**Sources added:** none. Existing canonical database/source package only.
**Gaps / NULLs logged:** No scientific values, AHP weights, health-risk data, or removal efficiencies were invented. C2 health risk remains blocked; AHP weights remain `temporary_not_expert_validated`; extension `narmada_*` tables remain staging until join keys are verified. C1 still needs the planned severity-weighted pollutant-gap closure rebuild.
**Blockers / next:** Decide how to commit/package `canonical db/` and `HANDOFF (1).md`; regenerate PostgreSQL schema before Azure; then build C1 and hard-safety/applicability filters in the handoff order. Verification: all backend test scripts passed with `.venv_canonical`; real-data `/api/v1/recommend` returned 24 ranked Step L recommendations against canonical DB.

---

## 2026-06-17 - Add CORS so the Flutter web client can reach the API
**Done:** Added `CORSMiddleware` to `app/main.py`, configurable via a new `CORS_ALLOW_ORIGINS` setting (comma-separated; default `*`, parsed by `Settings.cors_origins_list`). `allow_credentials=False`, all methods/headers allowed. Added `tests/cors_test.py` (origin-parsing, a simple request gets `access-control-allow-origin`, and a `/api/v1/recommend` preflight is permitted).
**Why:** The backend had no CORS at all, so the Flutter **web** app (Chrome, random localhost port, calling the API over the Cloudflare tunnel) would be blocked by the browser's same-origin policy — the app could not actually work in the browser regardless of the API_BASE_URL. No credentials/cookies are used, so `*` is safe for dev; set an explicit origin list for production.
**Sources added:** none.
**Gaps / NULLs logged:** Default `*` is dev-appropriate; tighten `CORS_ALLOW_ORIGINS` for production. No DB mutation, no secrets/.env committed, no Azure deployment change.
**Blockers / next:** Real-data validation pass; sensitivity analysis. With CORS + matching response shapes, the full stack now works in the browser: uvicorn + Cloudflare tunnel ↔ Flutter web. All 65 local test scripts pass in isolation.

---

## 2026-06-17 - Align frontend with live /recommend (criteria_breakdown shape + citations)
**Done:** Connected the restored Flutter app to the current backend response. (1) Backend: changed `AssembledRecommendation.criteria_breakdown` from a `dict[str,float]` to a **list of TOPSIS contributions** (`criterion_name, normalized_value, weight, weighted_value`) to match the frontend's pre-existing `CriterionBreakdown` model (richer: includes weight + weighted value); updated the schema (`list[TopsisCriterionContributionResponse]`) and the assembly test. (2) Frontend: added a `Citation` model + `citations` parsing (and `citationsById`) to `RecommendationResponse`, threaded `citations` from `main.dart` into `DetailScreen`, and rendered a new "Citations" block (id, label, type/license, url) under section E next to the raw source-ID chips. Removed a dead `max_step` field from the Dart request body (the route hardcodes it; the request model ignores extras anyway). `flutter analyze` clean; backend 64/64.
**Why:** My earlier `criteria_breakdown` dict silently broke the frontend breakdown view (it expects a list of contributions), and the new `citations` were unused by the UI. Aligning both makes the app render per-criterion bars and real citations end to end. The frontend reads the backend base URL from the `API_BASE_URL` dart-define (default `http://127.0.0.1:8000`); for the Cloudflare tunnel run it with `flutter run -d chrome --dart-define=API_BASE_URL=https://<tunnel-host>`.
**Sources added:** none.
**Gaps / NULLs logged:** Top-level `data_quality_level`, `exceedances`, `global_gaps` and per-item `why_recommended`/`cautions`/`data_gaps`/`implementation_summary` exist in the Dart model but are not yet populated by the backend response (they degrade gracefully to empty); wiring those is future work. No DB mutation, no Azure/secrets/.env change.
**Blockers / next:** Real-data validation pass (known Narmada scenarios); sensitivity analysis. The app now runs end to end: backend (uvicorn + Cloudflare tunnel) ↔ Flutter web (Chrome).

---

## 2026-06-17 - Resolve source_ids into citations in /recommend response
**Done:** `/api/v1/recommend` now returns a top-level `citations` list resolving every `source_id` referenced by the recommendations into real `sources` rows (id, short, citation, type, url, license) — the project's provenance "defining feature". Added `ReferenceDataService.get_citations_for_ids` (read-only, dedups, skips unknown/non-integer IDs via the existing `SourceRepository.get_many_by_ids`), a `CitationResponse` schema + `citations` field on `RecommendationResponse`, and a `get_reference_data_service` dependency on the route. The route collects source IDs from each recommendation's `evidence_summary.source_ids`, resolves them best-effort (failures degrade to `[]`, never crash the response). Tests: hermetic API test overrides the new dependency with an echo double and asserts citation IDs == referenced IDs; real-data smoke test asserts citations resolve from the live DB and each recommendation carries a `criteria_breakdown`.
**Why:** Recommendations exposed raw `source_ids` but no human-readable citations, so provenance wasn't actually usable by a reader/frontend. Resolving them server-side keeps the engines pure (no DB) while making every recommendation traceable to a cited source.
**Sources added:** none (reads existing `sources` table only).
**Gaps / NULLs logged:** Citation resolution is best-effort and read-only; unknown IDs are skipped, not invented. No DB mutation, no Azure/secrets/.env change. Per-criterion `caution_flags` already surface in `evidence_summary`; mapping individual values to their specific source rows (value-level provenance) remains future work.
**Blockers / next:** Point the Flutter frontend at the live `/recommend` shape (now includes citations + criteria_breakdown); real-data validation pass; sensitivity analysis. All 64 local test scripts pass in isolation.

---

## 2026-06-17 - Wire provisional default AHP weights into /recommend
**Done:** Recreated `app/core/default_weights.py` (the single AHP swap-in point) for the current criteria set — neutral, transparent, literature-informed provisional weights per use case, with `removal_evidence_score` (C1) dominant and the new C3-C8 criteria included; helpers `get_default_weights` / `select_default_weights` filter to criteria actually present and label everything `temporary_not_expert_validated` (source `default_temporary_literature_informed_v1`). `ScientificWorkflowService.run` gained `use_default_weights` (default True): when no weights are supplied and not expert-validated, it applies the filtered default profile at Step H. `RecommendationRequest` gained `use_default_weights` (default True) and the route threads it. Added `tests/default_weights_test.py`, a positive API test (`assert_default_weights_produce_provisional_ranking`), and updated the missing-weights test to opt out explicitly.
**Why:** `default_weights.py` was missing on this branch (it lives on `main`, commit 443ab6a, alongside the frontend) and the route only used client-supplied `temporary_weights`, so `/api/v1/recommend` produced no ranking out-of-the-box. This makes the endpoint usable for the demo while keeping the "no weights" safety contract available via `use_default_weights=False`. User-supplied weights still override; expert validation is never implied.
**Sources added:** none. Default weights are provisional placeholders pending the supervisor's AHP pairwise comparisons.
**Gaps / NULLs logged:** No AHP math, no health-risk, no DB mutation, no Azure/secrets/.env change. Weights remain `temporary_not_expert_validated`; swap real AHP values into `default_weights.py` (or the `criteria_weights` table) with no other code changes.
**Blockers / next:** Real AHP weights + use-case lock from supervisor. Next buildable: resolve `source_ids` into citations in the response (provenance), and point the Flutter frontend at the live `/recommend` shape. All 64 local test scripts pass in isolation.

---

## 2026-06-17 - Surface per-criterion breakdown in recommendations + restore frontend
**Done:** (1) Added `criteria_breakdown` (criterion_name -> normalized 0-1 value) to `AssembledRecommendation` (Step L-A) and its `AssembledRecommendationResponse` schema, populated straight from the Step I TOPSIS `criterion_contributions`, so `/api/v1/recommend` now explains which criteria (C1, C3-C8) drove each rank (engine spec §8/§18). Added an assembly test assertion. (2) Restored the Flutter frontend source into the working tree from `main` (`git restore --source=main -- frontend/`): on `backend-revamp-foundation` the `frontend/` folder only had generated `build/`+`.dart_tool/`, so Flutter reported "no pubspec.yaml". The source lives on `main` (commit 443ab6a); it is restored to the worktree but left untracked on this branch.
**Why:** The new MCDA criteria were influencing TOPSIS but invisible in the output; surfacing the breakdown makes recommendations self-explaining without changing rank/score. The frontend was never committed on the backend branch, only its build artifacts remained locally.
**Sources added:** none.
**Gaps / NULLs logged:** `criteria_breakdown` exposes existing normalized values only (no new scores, no AHP, no health-risk). No DB mutation, no Azure/secrets/.env change. Frontend restore is worktree-only (untracked on this branch); decide separately whether to commit/merge the frontend here.
**Blockers / next:** Frontend `recommendation_api.dart` should be checked against the current `/recommend` response shape before a UI demo. All 63 local test scripts pass in isolation.

---

## 2026-06-17 - C5-C8 MCDA criteria (pollution fit, footprint, O&M, evidence)
**Done:** Implemented the remaining minimum-viable MCDA criteria (engine spec §12.5-12.8) as four new pure engines, each injected by Step F (`mcda_matrix.py`) in the same site-context-gated enrichment as C3/C4:
- **C5 pollution_source_fit** (`pollution_source_fit.py`, benefit) — infers the site pollution context transparently (metals→industrial, pathogens→sewage, else land-cover built-up/agri→urban/agricultural, else mixed) and scores each NbS family against the spec's strong-family map; provisional, with an industrial/metals caution for weak families.
- **C6 footprint_requirement** (`footprint_feasibility.py`, cost) — mean `area_per_pe` from real `nbs_footprint` rows; a sourced (non-heuristic) cost criterion already in the normalization map.
- **C7 om_simplicity** (`om_simplicity.py`, benefit) — maps the documented O&M level word from `nbs_criteria` to the spec's score table.
- **C8 evidence_strength** (`evidence_strength.py`, benefit) — provenance score from water-data tier (selected source type), sourced numeric removal, resolved site data, and sourced implementation. Kept separate from the Step J confidence score.

`mcda_normalization.py` registers C5/C7/C8 as benefit (C6 cost was already mapped). `_build_row` now threads `candidate_bundle` so C5/C8 can read treatment-need groups and the selected water source type. Added four test files. **All 63 local test scripts pass in isolation.**
**Why:** Completes the spec's minimum-viable criteria set (§12.2: C1, C3, C4, C5, C6, C7, C8). Gating all of C3-C8 behind a resolved `site_context` keeps every staged/unit engine test (which passes no site context) unchanged while the location-first recommend path gets the full criteria set. C6/C7/C8 use real catalogue/provenance data (no invented science); C5's family→context map is provisional like C3/C4. Family-relative scoring keeps these from collapsing into constant TOPSIS columns.
**Sources added:** none. C5 context map and the C7 level→score table are provisional/transparent defaults; C6/C8 read sourced data only.
**Gaps / NULLs logged:** No invented values, no AHP weights, no health-risk logic, no DB mutation, no Azure/secrets/.env change. C5 explicit `pollution_sources` point/non-point integration is still pending (context inferred from needs + land cover). Missing footprint/O&M data leaves C6/C7 unscored with confidence-lowering notes. All site-aware criteria require a `region_id` that resolves site data.
**Blockers / next:** Validate the full C1+C3-C8 matrix on real Narmada rows via `/api/v1/recommend`; supervisor to review provisional maps; wire real AHP weights (C2 health-risk still blocked on supervisor data). Consider surfacing the per-criterion breakdowns in the API response.

---

## 2026-06-17 - C4 hydrological-suitability criterion
**Done:** Implemented the MCDA criterion **C4 — Hydrological suitability** (engine spec §12.4). New `backend/app/engines/hydrological_suitability.py` scores how well the site's flow/dilution scale matches each NbS family's flow-handling capacity. It uses true `stream_order` when available and falls back to a `drainage_area_km2` (then `dilution_proxy`) dilution proxy, **reporting whenever a proxy was used** as the spec requires. Step F (`mcda_matrix.py`) now injects `hydrological_suitability` + a structured `hydrological_suitability_breakdown` alongside C3 when a `site_context` is present; `mcda_normalization.py` maps the criterion as a benefit; the workflow `site_context` now carries `stream_order`/`drainage_area_km2`/`dilution_proxy`. Added `tests/hydrological_suitability_test.py`.
**Why:** C4 is the next criterion in the spec's own minimum-viable set (§12.2: C1, C3, C4, ...), and the C3 work already built the site-context plumbing. Slope is deliberately left to C3 so the two criteria stay distinct (no double-counting). Family→flow-capacity rules are **provisional, family-based defaults** flagged `provisional_not_expert_validated`, mirroring C3; they make C4 discriminate (a high-order site favours large open systems like ponds/buffers over small rain gardens) instead of being a constant TOPSIS column.
**Sources added:** none. Stream-order/drainage-area thresholds and family flow-capacity tables are provisional, not cited; they await supervisor validation.
**Gaps / NULLs logged:** No invented site values, removal efficiencies, AHP weights, or health-risk scores. No DB mutation, no Azure/secrets/.env change. C4 only scores when a `region_id` resolves stream-order or drainage-area data; otherwise it is left missing. When only a drainage-area proxy exists, `proxy_used=True` is recorded and reported in notes.
**Blockers / next:** Validate C4 on real Narmada `site_attributes` rows (confirm `stream_order` coverage vs proxy reliance); supervisor to review the provisional flow-capacity rules. Likely next criterion: C5 — pollution-source fit. All 59 local test scripts pass in isolation.

---

## 2026-06-17 - C3 site-suitability criterion (full specced)
**Done:** Implemented the MCDA criterion **C3 — Site suitability** end to end. New `backend/app/engines/site_suitability.py` computes `site_suitability = average(soil_fit, slope_fit, climate_fit, land_cover_fit)` per the engine spec §12.3, from the resolved site (region + site_attributes) compared to each NbS family. Step F (`mcda_matrix.py`) now accepts an optional `site_context` and injects the numeric `site_suitability` plus a structured `site_suitability_breakdown`; `McdaMatrixBundle` gained a `site_context_applied` flag. The Step M.1 numeric projection now skips its metadata-completeness `site_suitability` proxy whenever real C3 was applied, so the two definitions never mix in one matrix. `ScientificWorkflowService` resolves the site profile via `SiteProfileService` (wired in `from_session`) and threads `site_context` into the matrix build. Added `tests/site_suitability_test.py`.
**Why:** Supervisor/user chose the full specced C3 over a plumbing-only or partial increment. The NbS catalogue has no sourced per-technology site requirements (its `soil_type`/`location_suitability` are numeric codes), so — exactly as the spec authorises ("each sub-score must be rule-based and documented in code/config") — fit rules are **transparent, configurable, family-based heuristic defaults**, flagged `provisional_not_expert_validated` like the temporary AHP weights. Missing site inputs yield `None` sub-scores (averaged out, never guessed as zero); an unmatched NbS family or empty site context leaves C3 unscored (`data_pending`). Because rules are per-family, C3 actually discriminates between candidates rather than being a constant TOPSIS column.
**Sources added:** none. The fit thresholds are provisional literature-informed defaults, not cited values; they await supervisor validation.
**Gaps / NULLs logged:** No invented site values, removal efficiencies, AHP weights, or health-risk scores. No DB mutation, no Azure/secrets/.env change. C3 only scores when a `region_id` resolves usable site attributes; otherwise a warning is logged and C3 is left missing. Slope rules assume `slope_mean` is in degrees (documented assumption). Sub-score fit tables are not expert-validated.
**Blockers / next:** Validate `/api/v1/recommend` C3 output on real Narmada region rows; have the supervisor review/replace the provisional family fit rules; consider surfacing the structured `site_suitability_breakdown` in the recommendation API response. All 58 local test scripts pass in isolation.

---

## 2026-06-13 - Step N.5 Azure startup dependency readiness
**Done:** Added `gunicorn>=22.0` to the revamped backend runtime dependencies for Azure FastAPI startup.
**Why:** The current direct Uvicorn startup command may work, but Gunicorn with Uvicorn workers is preferred for production App Service. Recommended Azure Startup Command: `gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app`.
**Sources added:** none.
**Gaps / NULLs logged:** No secrets changed, no DB files changed, no app/scientific logic changed, and no deployment was performed.
**Blockers / next:** Set or verify the Azure Startup Command only during the controlled deployment step.

---

## 2026-06-13 - Step N.4 backend-only Azure workflow packaging
**Done:** Updated the GitHub Actions workflow packaging path for the revamped backend.
**Why:** Azure needs the backend package root to contain `app/` and `requirements.txt`, not the old root app or the whole repository. The workflow now installs `backend/requirements.txt` and packages the contents of `backend/`.
**Sources added:** none.
**Gaps / NULLs logged:** The package excludes local `.env`, `.venv/`, `.venv_broken/`, `data/*.db`, Python caches, compiled files, and tests. The `main` trigger remains unchanged, no deployment was performed from this branch, no secrets changed, and no app/scientific logic changed.
**Blockers / next:** Review the workflow run artifact listing on `main` before treating Azure as production-ready.

---

## 2026-06-13 - Step M.2 real-data recommendation API smoke test
**Done:** Added a local FastAPI TestClient smoke test for `POST /api/v1/recommend` using live standards vocabulary and the Step M.1 projected `removal_evidence_score`.
**Why:** The recommendation endpoint needed a repeatable real-data check that proves the staged Step L path can produce ranked recommendations without requiring a live Uvicorn server or Azure services.
**Sources added:** none.
**Gaps / NULLs logged:** The smoke test confirms `match_score` mirrors `topsis_closeness`, `confidence_score` remains separate, temporary weights remain `temporary_not_expert_validated`, and ranked Step L recommendations are returned. No DB mutation, no Azure/deployment change, no AHP expert weights, and no health-risk logic were added.
**Blockers / next:** Keep this as a local readiness test before any deployment work; production deployment still needs a separate database and Azure review.

---

## 2026-06-13 - Step M.1 production numeric MCDA projection
**Done:** Added a conservative numeric projection layer between raw MCDA matrix preparation and normalization.
**Why:** Live Step F produces rich raw MCDA criteria objects, while Step G only normalizes numeric values with explicit direction rules. The projection layer derives numeric proxy criteria only from already-present Step F raw data so TOPSIS can receive normalizable criteria without weakening Step G safety.
**Sources added:** none.
**Gaps / NULLs logged:** Projection uses already-present Step F raw data only. No DB mutation, no Azure deployment, no secrets or `.env` changes, no AHP expert weights, and no health-risk logic were added. Temporary weights remain `temporary_not_expert_validated`.
**Blockers / next:** Continued Step M.1 by adding variable `removal_evidence_score`, derived only from existing removal efficiency ranges in Step F raw rows. Still no DB mutation, no Azure deployment, no secrets or `.env` changes, no AHP expert weights, and no health-risk logic. Validate live `/api/v1/recommend` output to confirm projected criteria produce ranked candidates with production data, then review whether more explicit numeric source fields are needed in the schema.

---

## 2026-06-13 - Step M local recommendation API endpoint
**Done:** Step M local recommendation API endpoint was added. `POST /api/v1/recommend` wraps `ScientificWorkflowService.run(..., max_step="L")` and returns the internal `recommendation_assembly_bundle`.
**Why:** The backend needed a local API readiness wrapper around the staged A-L workflow without changing deployment, Azure settings, secrets, `.env`, old folders, or database records.
**Sources added:** none.
**Gaps / NULLs logged:** `match_score` is copied from `topsis_closeness`. `confidence_score` remains separate from `match_score`. `weights_status` and `expert_validated` remain visible. Temporary weights remain provisional and must not be presented as expert validated. Health risk and AHP remain pending/not implemented. No Azure deployment was done, no secrets or `.env` changes were made, and no DB mutation was added.
**Blockers / next:** Local API tests passed for the recommendation route. `/health/db` returned `503` during `api_smoke_test.py` while other raw DB-backed routes passed; DB health should be checked before deployment.

---

## 2026-06-13 - Step L-B workflow service support
**Done:** Step L-B workflow-service support was added. `ScientificWorkflowService.run(...)` still defaults to the safe A-E path. `max_step="J"` still runs A-J only. `max_step="K"` still runs A-K only. `max_step="L"` now runs A-K plus internal recommendation assembly.
**Why:** The workflow needed an explicit opt-in path for internal recommendation assembly while keeping earlier staged paths unchanged and avoiding endpoint work.
**Sources added:** none.
**Gaps / NULLs logged:** `recommendation_assembly_bundle` is internal workflow output only. `match_score` is copied from `topsis_closeness`. `confidence_score`, rank, `weights_status`, and `expert_validated` remain separate and preserved. Plant matches remain supporting options and do not affect rank. Still no `/recommend` endpoint, still no API route, still no Azure/secrets/env changes, and still no DB mutation.
**Blockers / next:** Keep Step L internal until a future task explicitly approves any endpoint or production-facing API design.

---

## 2026-06-12 - A-K workflow service support
**Done:** A-K workflow-service support was added. `ScientificWorkflowService.run(...)` still defaults to the safe A-E path. `max_step="J"` still runs A-J without plant matching. `max_step="K"` now runs A-J plus Step K plant matching.
**Why:** The internal workflow needed an explicit opt-in path for plant matching after ranked NbS options while preserving the safe default and the A-J behavior.
**Sources added:** none.
**Gaps / NULLs logged:** Step K attaches plants after ranked NbS options, but plant matching does not change rank, `topsis_closeness`, or `confidence_score`. Missing plant mappings return empty plant lists plus warnings, not guessed plants. Still no final recommendation, still no `match_score`, and still no `/recommend` endpoint.
**Blockers / next:** Keep Step K internal and read-only until a future task explicitly approves final recommendation assembly and any endpoint work.

---

## 2026-06-12 - Internal workflow service documentation alignment
**Done:** Internal workflow service documentation was aligned. `ScientificWorkflowService.run(...)` defaults to the safe A-E path. `max_step="J"` explicitly runs the staged A-J path.
**Why:** The workflow guide needed to make the safe default and explicit extended path clear for future developers before any endpoint or final recommendation work begins.
**Sources added:** none.
**Gaps / NULLs logged:** A-J includes MCDA matrix preparation, normalization, weights handling, TOPSIS ranking, and confidence scoring, but still does not create final recommendations or expose `/recommend`. TOPSIS closeness remains separate from `confidence_score`. Temporary weights remain marked as `temporary_not_expert_validated`.
**Blockers / next:** Do not add final recommendation logic, plant matching, or `/recommend` until those steps are explicitly approved and documented.

---

## 2026-06-03 — Project kickoff & data audit
**Done:** Set up CLAUDE.md + PLAN.md. Audited the five CSVs.
**Why:** Establish provenance-first conventions and a verified picture of current data before
touching features.
**Sources added:** none yet (provenance scaffolding only).
**Gaps / NULLs logged:** district_data is state-level with invented soil buckets; plant/NbS
data duplicated across states (15 species / 10 solutions); soil vocab mismatch; dirty
optimal_water_type values; junk Unnamed:7 column. All flagged in PLAN.md section 2.
**Blockers / next:** confirm Claude Code API connectivity; then Phase 0 data hygiene
(PLAN.md section 10).
Scientific workflow staged tests were run locally from backend/. Steps A-E, workflow service, engine schemas, and workflow schema conversion checks passed. No /recommend endpoint, TOPSIS/AHP ranking, match_score, confidence_score, plant recommendation, or health-risk logic has been introduced yet.

Scientific workflow staged tests were run locally from backend/. Steps A-F, engine schemas, workflow service, and workflow schema conversion checks passed. The workflow still does not expose /recommend, does not create final recommendations, does not run TOPSIS/AHP, does not calculate match_score/confidence_score, does not recommend plants, and does not classify health risk.

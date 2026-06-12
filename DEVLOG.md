# DEVLOG — NbS Toolkit

Append a dated entry at the end of every work session. This is not busywork: it is the
Methods / reproducibility trail for the internship report and the paper. Capture the *why*,
not just the *what*. Newest entries at the top.

Template:

## YYYY-MM-DD — <short title>
**Done:** what changed (files, schema, data).
**Why:** the reasoning / the decision made and the alternative rejected.
**Sources added:** any datasets/papers/standards wired in (with citation).
**Gaps / NULLs logged:** values left empty for lack of a source.
**Blockers / next:** what's stuck, what's next.

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

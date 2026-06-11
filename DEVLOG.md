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
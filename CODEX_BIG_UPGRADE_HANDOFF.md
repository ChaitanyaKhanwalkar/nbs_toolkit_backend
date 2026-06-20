# Codex Big Upgrade Final Handoff

## Modules completed

1. Trustworthy scoring and confidence - `62da2da`
2. Treatment trains plus individual NbS - `a6bd780`
3. Responsive UI and user-facing language - `dae779f`
4. Catalogue and learning workspace - included in the current checkpoint

## Module 4 files changed

- `backend/app/api/router.py`
- `backend/app/api/routes/catalogue.py`
- `backend/app/repositories/nbs_repository.py`
- `backend/app/repositories/plant_repository.py`
- `backend/app/services/catalogue_service.py`
- `backend/app/services/__init__.py`
- `backend/docs/00_PROJECT_MAP.md`
- `backend/tests/catalogue_service_test.py`
- `frontend/lib/main.dart`
- `frontend/lib/screens/nbs_screens.dart`
- `frontend/lib/services/recommendation_api.dart`
- `frontend/test/catalogue_screen_test.dart`
- `frontend/test/home_responsive_test.dart`
- `CODEX_BIG_UPGRADE_HANDOFF.md`
- `NEXT_CODEX_PROMPT.md`

## Final verification

- Backend: 43 passed.
- Flutter analyze: no issues found.
- Flutter tests: 10 passed.
- `git diff --check`: clean.

## Current backend status

- FastAPI remains repository/service/engine separated.
- Canonical database counts are guarded by tests.
- Confidence is separate from technical match and capped for thin data.
- Every train exposes supplied pollutant gaps and train evidence coverage.
- Treatment trains remain the primary recommendation.
- Individual components are A0-screened and context constrained.
- `GET /api/v1/catalogue` returns all 8 train records, 28 NbS profiles,
  canonical plant mappings, O&M/design notes, and source IDs.
- Invasive plant catalogue rows are explicitly marked do-not-recommend.

## Current frontend status

- Four workflows remain distinct.
- Phone/tablet/desktop setup layouts are tested.
- Results use professional Technical match / Result confidence language.
- Summary keeps the primary train above supporting components.
- NbS Components shows role, standalone boundary, pollutant evidence, plants,
  context limitations, filtered reasons, and source IDs.
- Catalogue & Learning provides searchable Treatment Train, NbS Component, and
  Plant views with sequence, design, monitoring, O&M, mappings, and provenance.

## Scientific safeguards preserved

- A0 applicability precedes ranking.
- Missing data stays unknown, never zero.
- No scientific value, threshold, weight, citation, or health-risk score was
  invented.
- Industrial ETP/CETP and pH-neutralization requirements remain explicit.
- High-order/mainstem output is off-channel only.
- Agricultural output prioritizes source control.
- Invasive plants are never recommended.
- The canonical database was read only.

## Known limitations

- Confidence caps and context-only component ordering are transparent rule-based
  research safeguards, not expert-validated scientific certainty.
- Component TOPSIS still needs expert calibration and may technically score
  unusual options highly; context and standalone safeguards limit interpretation.
- Catalogue source IDs are displayed, but a richer citation-detail browser and
  PDF/CSV export are future work.
- Widget tests catch layout exceptions but do not replace device/browser visual
  QA.
- Local prompt/safety/checkpoint artifacts remain untracked and outside commits.

## Commit status

Module 4 is included in the scoped checkpoint commit:
`Module 4: Add catalogue and learning workspace upgrades`.

## Recommended next step

Do not start another automatic patch. Review the complete app interactively
against the four representative workflows, then choose among the future work
listed in `NEXT_CODEX_PROMPT.md`.

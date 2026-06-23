# Codex Big Upgrade Handoff

## Completed

- Integrated final v1 AHP-Fuzzy AHP ensemble weights for `drinking`, `irrigation`, and `discharge_inland`.
- Added a named final-weight fallback in code for stale or missing local `criteria_weights` tables.
- Updated the local canonical DB rows during this run and added a reviewable SQL seed patch.
- Updated method wording to: `A0 safety/applicability screening -> AHP-Fuzzy AHP ensemble weighting -> TOPSIS treatment-train ranking -> confidence and design-readiness checks`.
- Kept C5 health-risk reserved/future and kept design/field-validation limitations.
- Replaced references placeholder with citation-backed grouped references.
- Replaced offline grey map canvas with a verified-location context card when tiles are unavailable.
- Improved sizing, compare-card, component comparison, report, CSV, and print/PDF wording.
- Added a clean print-only HTML export path and Excel-friendly CSV BOM.
- Added Mandleshwar industrial acidic high-order safety regression.
- Updated affected visual goldens.

## Files Changed

- `backend/app/core/final_v1_ahp_fuzzy_weights.py`
- `backend/app/repositories/engine_data_repository.py`
- `backend/app/services/scientific_workflow_service.py`
- `backend/app/engines/train_recommendation.py`
- `backend/app/api/routes/recommendation.py`
- `backend/tests/engine_data_repository_test.py`
- `backend/tests/train_recommendation_test.py`
- `backend/criteria_weights_ahp_fuzzy_ensemble.sql`
- `frontend/lib/screens/nbs_screens.dart`
- `frontend/lib/services/recommendation_report.dart`
- `frontend/lib/services/report_platform_stub.dart`
- `frontend/lib/services/report_platform_web.dart`
- `frontend/lib/widgets/location_context_diagram.dart`
- `frontend/test/location_context_diagram_test.dart`
- `frontend/test/recommendation_report_test.dart`
- `frontend/test/visual_qa_goldens/desktop1440__workspace_report_preview.png`
- `frontend/test/visual_qa_goldens/mobile390__edge_weak_summary.png`

## Verification

- Backend: `backend/.venv_canonical/Scripts/python.exe -m pytest -q` -> `67 passed`
- Flutter dependencies: `flutter pub get` -> completed
- Flutter analyze: `flutter analyze` -> no issues
- Flutter tests: `flutter test` -> `25 passed`
- Diff hygiene: `git diff --check` -> clean, line-ending warnings only

## Important Caveats

- The canonical DB file is not tracked by Git in this workspace. The local DB was updated, and the repository now falls back to final v1 weights if a stale DB still contains old provisional rows.
- C5 health-risk remains inactive.
- Sizing is still screening-level only.
- Field validation, hydraulic design, O&M ownership, regulatory review, and local planting validation remain required before implementation.

## Exact Next Step

Review the scoped commit diff, run the app manually for the demo flows, then continue with any post-demo cleanup or documentation pass.

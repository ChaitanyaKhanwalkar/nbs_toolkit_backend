# Final Demo Hardening Handoff

## Current state

Base commit: `69ca847 Guide UX and add sizing comparison tools`.

The final hardening source patch is implemented but intentionally uncommitted. Backend tests pass and the diff is whitespace-clean. Flutter dependency resolution, analysis, and tests are blocked because `latlong2` is not present in the local Pub cache and network approval was rejected when the Codex tool account reached its usage limit.

## Files changed

- Backend response, engines, and schema:
  - `backend/app/api/routes/recommendation.py`
  - `backend/app/engines/design_readiness.py`
  - `backend/app/engines/sizing_estimator.py`
  - `backend/app/engines/train_recommendation.py`
  - `backend/app/schemas/recommendation.py`
- Backend tests:
  - `backend/tests/design_readiness_test.py`
  - `backend/tests/sizing_comparison_test.py`
  - `backend/tests/train_recommendation_test.py`
- Flutter implementation:
  - `frontend/lib/models/recommendation_models.dart`
  - `frontend/lib/screens/nbs_screens.dart`
  - `frontend/lib/services/recommendation_report.dart`
  - `frontend/lib/widgets/location_context_diagram.dart`
  - `frontend/lib/widgets/nbs_diagrams.dart`
  - `frontend/pubspec.yaml`
- Flutter tests:
  - `frontend/test/home_responsive_test.dart`
  - `frontend/test/location_context_diagram_test.dart`
  - `frontend/test/nbs_diagram_test.dart`
  - `frontend/test/recommendation_report_test.dart`
  - `frontend/test/workflow_responsive_test.dart`
- New SVG assets:
  - `frontend/assets/diagrams/vf_wetland.svg`
  - `frontend/assets/diagrams/hssf_wetland.svg`
  - `frontend/assets/diagrams/wsp_series.svg`
  - `frontend/assets/diagrams/dewats_flow.svg`
  - `frontend/assets/diagrams/buffer_strip.svg`
  - `frontend/assets/diagrams/off_channel_safety.svg`
  - `frontend/assets/diagrams/vermifilter.svg`
  - `frontend/assets/diagrams/bioswale.svg`

## Packages added

- `flutter_svg: ^2.0.17`
- `flutter_map: ^8.1.1`
- `latlong2: ^0.9.1`

`flutter pub get` has not completed because network access was unavailable and `latlong2` was not cached. `pubspec.lock` therefore has not been updated.

## Verification

- Backend interpreter actually used: `backend/.venv_canonical/Scripts/python.exe`.
- Backend tests: **65 passed in 8.66s** on the final run.
- SVG XML validation: **8/8 passed**.
- Dart formatter parsed all 10 changed Dart source/test files successfully.
- `git diff --check`: **clean** (line-ending notices only).
- Flutter analyze: **not run after this patch** because dependency resolution is blocked.
- Flutter tests: **not run after this patch** for the same reason.
- Commit: **not done**, correctly following the rule that all Flutter gates must pass first.

## Parameter coverage fix

The API now returns a top-level `parameter_coverage` list and pollutant-gap rows include `coverage_category` and `coverage_label`. Categories are `used_in_scoring`, `supporting_context`, `read_not_assessed`, and `skipped`. Recognized values stay visible, skipped CSV rows remain explicit, and missing values are never converted to zero. UI and reports explain the distinction.

## Site and design status fix

Readiness now distinguishes `available`, `not_supplied`, `mapped_context_verify`, `needs_field_check`, `missing_before_engineering_design`, and `not_required_for_current_screening`. Treatment design flow, peak wastewater flow, and available land are user-supplied design inputs. River discharge is exposed separately as receiving-water context and never satisfies treatment design flow. Stored slope/soil are labelled as mapped context requiring field verification.

## Footprint and sizing correction

Sizing bases are separated. Hydraulic-loading evidence requires explicit design flow. Per-person evidence requires explicit population/PE. No flow-to-PE conversion or hidden default is used. Incompatible or incomplete evidence produces no absolute area. Land fit runs only for a complete absolute estimate plus supplied land. Assumptions and excluded engineering factors are explicit.

## Home revamp

Home is now headed `Narmada NbS Planner`, uses the four guided workflow names and descriptions from the prompt, includes a four-step `How it works` strip, and uses calmer system-status wording.

## Component and catalogue alignment

Component and catalogue expansion content is left-aligned. Raw/internal empty-state wording was replaced with practitioner language. Visible semicolon lists are normalized. Plant catalogue grouping continues to put invasive plants under `Not recommended`, with the required warning.

## SVG diagrams

The old diagram `CustomPainter` was replaced with `flutter_svg` assets. Eight original engineering-style diagrams are registered and mapped to train/component names. Cards retain `What it shows`, `When to use`, `Watch out for`, and `Design notes` disclosures.

## Map upgrade

Verified coordinates render through `flutter_map` on an offline-safe coordinate canvas with a stored-location marker. Optional OpenStreetMap tiles are supported only when explicitly enabled, and visible attribution is then shown. Missing coordinates retain the schematic-only state; missing context retains the no-map state. Tests are designed to use the offline state.

## Export and report updates

Summary, JSON, CSV, and preview data now include parameter coverage, map status, river-discharge context separate from design flow, grouped readiness statuses, sizing basis, flow status, and population status.

## Known limitations / failures

1. The prompt listed an invalid Python path (`backend.venv_canonical`); the valid path is `backend/.venv_canonical`.
2. `flutter pub get` inside the sandbox stalled because its normal analytics/config directory was not writable.
3. A direct offline Pub run with a workspace-local tool home failed exactly with: `Because nbs_toolkit_frontend depends on latlong2 any which doesn't exist (could not find package latlong2 in cache), version solving failed.`
4. Escalated network access was rejected because the Codex tool usage limit was reached. No workaround was attempted.
5. OSM tiles are disabled by default so the demo and tests do not depend on internet. The verified-coordinate map still uses a real geographic coordinate canvas and marker.
6. `frontend/analysis_options.yaml` can appear modified because the sandbox denied Git index refresh after formatting. Its working-tree and index blob hashes are identical (`0d2902135caece481a035652d88970c80e29cc7e`), and `git diff` is empty for that file; do not stage it.

## Exact next step

When network/tool access is available:

1. Run `flutter pub get` from `frontend`.
2. Run `flutter analyze` and fix any package-API or lint errors.
3. Run `flutter test` and fix any assertions or overflow failures.
4. Run backend pytest again and `git diff --check`.
5. Stage only the scoped files listed above plus this handoff and `NEXT_CODEX_PROMPT.md`; do not stage unrelated untracked artifacts.
6. Commit with `Final demo hardening for maps diagrams and trust` only after every gate passes.

## Final demo manual QA checklist

- Home at 390x844, 768x1024, and desktop: all four workflows and `How it works` fit.
- Upload BOD/COD/TSS/pH plus DO, EC, TDS, turbidity, and PO4-P: every recognized value appears with a coverage category.
- Unknown and nonnumeric CSV rows remain visible as skipped warnings.
- Station case with stored coordinates shows a verified marker; station without coordinates says schematic only; blank context says no verified map.
- River discharge appears only as river context, never treatment design flow.
- Mapped slope/soil say field verification is required.
- Design-flow-only case never creates a per-person estimate.
- Population/PE-only case uses only per-person evidence.
- Industrial acidic case retains ETP/CETP and neutralization safeguards.
- High-order/mainstem case retains off-channel-only guidance.
- Agricultural case retains field/edge-of-field source control priority.
- Diagram, catalogue, report preview, JSON, and CSV export render without overflow or raw internal wording.

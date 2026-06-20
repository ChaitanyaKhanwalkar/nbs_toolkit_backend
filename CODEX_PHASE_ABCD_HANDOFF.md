# Phase A+B+C+D v1 Handoff

## Status

All four requested modules are complete. The canonical database and scientific
engine architecture were not replaced or bypassed.

Final automated gate:

- Backend: `44 passed in 7.72s`
- Flutter analyze: `No issues found`
- Flutter tests: `15 passed`
- `git diff --check`: clean (line-ending notices only)
- Flutter web server compiled and served successfully at `127.0.0.1:8765`

## Module A - Professional polish

- Replaced raw CSV/database wording with practitioner-facing labels.
- Added readable parameter and unit labels, including BOD, COD, TSS, pH,
  NH4-N, NO3-N, PO4-P, mg/L, NTU, MPN/100 mL, and microS/cm display.
- Added ten common phosphorus aliases, mapped to the existing canonical
  `phosphate_p` key. No new scientific parameter was invented.
- Improved data-limited confidence wording without changing score semantics.
- Shortened implementation guidance and collapsed long input-value lists.
- Reordered train/component catalogue sections around practical questions.
- Grouped plants as recommended, conditional, and invasive/not recommended.

## Module B - Original NbS diagrams

Added six lightweight Flutter `CustomPainter` schematics:

1. Vertical-flow wetland cross-section
2. Horizontal subsurface-flow wetland cross-section
3. Waste-stabilization pond series
4. DEWATS modular flow
5. Buffer/riparian strip
6. Drain interception, off-channel treatment, and mainstem safety

Diagrams are mapped into the learning workspace, train catalogue, component
catalogue, result component cards, and high-order implementation guidance.
They are original screening/learning visuals, not engineering drawings.

## Module C - Evidence and references

- Catalogue API now returns resolved evidence records from the existing source
  repository.
- Train and component evidence is grouped into performance, design, and
  planting evidence where the stored links support that grouping.
- Result, train, component, plant, catalogue, and Evidence & Method views use
  expandable evidence disclosures.
- Readable stored citation labels are preferred. Missing labels fall back to
  `Evidence record N`; no citation, author, URL, or source was invented.
- Evidence panels state that sources support screening and comparison, not
  final engineering design.

## Module D - Export/report v1

- Added a report preview panel.
- Added copyable practitioner summary.
- Added structured JSON export.
- Added row-oriented CSV export.
- Web builds download JSON/CSV through a conditional browser adapter.
- Non-web builds/tests copy prepared export content to the clipboard.
- Added browser print/save-as-PDF guidance without a PDF dependency.
- Report content covers inputs, top train, technical match, confidence,
  water-quality values, pollutant gaps, supporting components, use-case
  suitability, limitations, data gaps, evidence, and disclaimer.

Disclaimer used:

> This is a planning-level decision-support output. It is not a final
> engineering design. Confirm flow, pollutant loads, land availability,
> hydraulics, and site constraints before implementation.

## Files changed

Backend:

- `backend/app/api/routes/water.py`
- `backend/app/services/catalogue_service.py`
- `backend/tests/catalogue_service_test.py`
- `backend/tests/train_recommendation_test.py`

Frontend:

- `frontend/lib/models/recommendation_models.dart`
- `frontend/lib/screens/nbs_screens.dart`
- `frontend/lib/services/recommendation_report.dart`
- `frontend/lib/services/report_platform.dart`
- `frontend/lib/services/report_platform_stub.dart`
- `frontend/lib/services/report_platform_web.dart`
- `frontend/lib/widgets/nbs_diagrams.dart`
- `frontend/test/catalogue_screen_test.dart`
- `frontend/test/nbs_diagram_test.dart`
- `frontend/test/recommendation_report_test.dart`
- `frontend/test/workflow_responsive_test.dart`

Documentation:

- `CODEX_PHASE_ABCD_HANDOFF.md`
- `NEXT_CODEX_PROMPT.md`

## Tests added or expanded

- Ten phosphorus spelling/alias cases.
- Catalogue evidence records and grouped provenance.
- Readable citation disclosure in catalogue UI.
- Six diagram kinds and 390x844 diagram rendering.
- JSON report structure and CSV row structure.
- Report controls and preview at 390x844.
- Existing upload, workflow, catalogue, component, tablet, desktop, and mobile
  tests remain green.

## Manual QA checklist

- [x] Complete uploaded-file path covered by widget/API tests.
- [x] Partial uploaded-file and blank-is-unknown behavior retained.
- [x] Site/context-only confidence display covered by existing logic/tests.
- [x] NbS Components result workspace rendered at 390x844.
- [x] Train, component, and plant catalogue interactions covered by tests.
- [x] Mobile 390x844, tablet 768x1024, and desktop widths covered by tests.
- [x] Flutter web compiled and served locally.
- [ ] Interactive browser screenshots were not completed: the in-app browser
  process was denied by the Windows sandbox before it opened the local page.

## Known limitations and intentional deferrals

- Browser print uses the browser's print/save-as-PDF path; it is not a polished
  generated PDF layout.
- Full DPR-grade reports, curated video references, and external reference
  expansion are deferred.
- The evidence layer exposes only records already stored in the canonical data.
- Diagrams are conceptual learning schematics, not dimensioned design details.
- Research-stage criteria weights and health-risk structures still require
  expert consultation; no expert values were invented in this patch.
- A dedicated simple/expert toggle remains optional future work; progressive
  disclosure is the current implementation.

## Exact next step

Run a human browser QA session on the committed web build, focusing on report
downloads and print layout. Then scope the next phase around publication-grade
report generation and expert-reviewed evidence/weight calibration without
changing canonical data unless reviewed source material is supplied.

## Commit status

Completed as a scoped checkpoint with commit message:
`Professional trust polish diagrams references and export v1`.

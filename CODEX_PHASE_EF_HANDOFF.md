# Phase E+F Handoff - Location Intelligence and Design Readiness

## Status

Phase E+F is complete and verified. The canonical database was not modified,
and no coordinates, station values, pollution records, flow values, design
standards, citations, weights, or health-risk values were invented.

Final verification:

- Backend: `54 passed in 7.52s`
- Flutter analyze: `No issues found`
- Flutter tests: `17 passed`
- `git diff --check`: clean (line-ending notices only)
- Flutter web: compiled and served successfully at `127.0.0.1:8765`

## Files changed

Backend:

- `backend/app/api/README.md`
- `backend/app/api/routes/recommendation.py`
- `backend/app/engines/README.md`
- `backend/app/engines/__init__.py`
- `backend/app/engines/design_readiness.py`
- `backend/app/schemas/recommendation.py`
- `backend/app/services/README.md`
- `backend/app/services/__init__.py`
- `backend/app/services/location_context_service.py`
- `backend/tests/design_readiness_test.py`

Frontend:

- `frontend/lib/models/recommendation_models.dart`
- `frontend/lib/screens/nbs_screens.dart`
- `frontend/lib/services/recommendation_report.dart`
- `frontend/lib/widgets/location_context_diagram.dart`
- `frontend/test/location_context_diagram_test.dart`
- `frontend/test/recommendation_report_test.dart`
- `frontend/test/workflow_responsive_test.dart`

Documentation:

- `CODEX_PHASE_EF_HANDOFF.md`
- `NEXT_CODEX_PROMPT.md`

## Location intelligence

The recommendation response now includes `location_context`, assembled by a
read-only service through the existing site-profile repository/service layer.

Verified fields exposed where available:

- region ID and selected station
- river, district, basin, and sub-basin
- stream order and readable river context
- intervention position and pollution-source type
- linked pollution-source record count already fetched by the site workflow
- stored river-discharge context and drainage area
- mapped slope, soil type, and infiltration class
- stored latitude/longitude only when both coordinates exist
- missing-site-information list and concise context notes

Safety flags:

- `mainstem_or_high_order`
- `off_channel_required`
- `industrial_pretreatment_required`
- `agricultural_source_control_first`
- `site_context_incomplete`

The previous `_location_profile` missing-return defect was also fixed.

## Context visualization

- A new Location workspace presents site factors, safety/source context, and
  missing site information.
- A compact Site context card appears in Summary.
- When verified stored coordinates exist, the UI shows a local site schematic
  and prints the stored coordinate pair.
- Without coordinates, it explicitly shows a basin-context schematic and says
  that it is not a geographic map.
- Mainstem/high-order cases show drain interception, off-channel treatment,
  safe return flow, and the do-not-build-in-channel warning.
- No online tiles, API keys, external maps, or fake points are used.

## Design-readiness rules

The response now includes `design_readiness` with:

- level and short label
- concise explanation and reasons
- missing inputs
- required next steps
- expert-review boolean
- per-input checklist with available, missing, and field-verification statuses

Levels:

1. `early_screening_only` / Needs field data
2. `planning_level_result` / Ready for planning
3. `preliminary_design_ready` / Preliminary design ready
4. `needs_expert_review` / Expert review needed

Conservative rules:

- zero/one usable water-quality value remains early screening
- incomplete BOD/COD/TSS/pH remains early screening
- a complete BOD/COD/TSS/pH panel supports planning-level comparison
- industrial/mixed-industrial, pH outside the existing 6-9 engine bounds, or
  mainstem/high-order/in-channel context requires expert review
- preliminary readiness requires the core panel, nutrients, DO, faecal
  coliform, explicit design and peak flow, land, groundwater, flood, levels,
  O&M, field-verified slope/soil context, non-low existing confidence, and
  complete site context
- mapped slope/soil context is marked `needs_field_verification`; it is not
  silently treated as a completed field survey
- stored river discharge is context only and is not substituted for design flow

The readiness engine is post-ranking and does not alter TOPSIS rank, technical
match, or confidence.

## Missing-input checklist

The Design readiness workspace covers:

- design flow and peak flow
- BOD, COD, TSS, pH, nutrients, DO, and faecal coliform/pathogens
- available land
- slope and soil/infiltration
- groundwater depth and flood risk
- inlet/outlet levels
- O&M owner/capacity

Each row is labelled Available, Missing, Needs field verification, or (when
future rules use it) Not required for current screening.

## Export and report updates

Location context and design readiness are included in:

- report preview
- copied practitioner summary
- structured JSON export
- row-oriented CSV export

The report preview includes the readiness reason, checklist statuses, missing
inputs, and next steps alongside site context.

## Tests added or expanded

Backend coverage includes:

- complete core panel -> planning level
- one parameter -> early screening
- industrial acidic case -> ETP/CETP, neutralization, expert review
- high-order/mainstem -> off-channel expert review
- no user data/site context -> early screening
- explicit complete design/site inputs -> preliminary readiness
- low confidence blocks preliminary readiness
- absent coordinates remain null and unavailable
- verified stored coordinates and safety flags are preserved
- public recommendation API returns both new objects

Frontend coverage includes:

- Location and Design readiness workspaces at 390x844
- missing-input checklist and field-verification label
- report preview contains readiness information
- JSON, CSV, and copied summary carry both new sections
- coordinate and no-coordinate diagrams render without overflow
- all existing catalogue, diagram, export, upload, workflow, tablet, desktop,
  and mobile tests remain green

## Known limitations

- The current UI does not yet collect the full design-flow, land, groundwater,
  flood, level, and O&M input set. The checklist exposes these gaps; preliminary
  readiness is available to API/future workflows only when values are supplied.
- The local drawing is a context schematic, not a GIS basemap or survey plan.
- Stored coordinates and catchment attributes still require normal field/design
  verification before implementation.
- Interactive in-app browser screenshots could not be captured because Windows
  denied the browser sandbox process before page startup. Web compilation and
  responsive widget rendering passed.
- Engineering sizing, final design, regulatory review, expert weight
  calibration, and health-risk assessment remain out of scope.

## Manual QA checklist

- [x] Backend API contract and all four readiness levels covered by tests
- [x] Location workspace rendered at mobile width
- [x] Design-readiness checklist rendered at mobile width
- [x] Coordinate-present schematic covered
- [x] Coordinate-absent schematic covered
- [x] Mainstem/off-channel warning covered
- [x] Report preview and JSON/CSV structures covered
- [x] Flutter web compiled and served locally
- [ ] Interactive browser screenshot review blocked by Windows browser sandbox

## Commit status

Completed as a single scoped commit with message:
`Add location intelligence and design readiness`.

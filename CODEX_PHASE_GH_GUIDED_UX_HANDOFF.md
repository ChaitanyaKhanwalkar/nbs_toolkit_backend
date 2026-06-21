# Guided UX, Maps, Diagrams, Sizing, and Comparison Handoff

## Files changed

Backend:

- `backend/app/engines/design_readiness.py`
- `backend/app/engines/scenario_comparison.py`
- `backend/app/engines/sizing_estimator.py`
- `backend/app/engines/README.md`
- `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`
- `backend/tests/design_readiness_test.py`
- `backend/tests/sizing_comparison_test.py`

Frontend:

- `frontend/lib/models/recommendation_models.dart`
- `frontend/lib/screens/nbs_screens.dart`
- `frontend/lib/services/recommendation_report.dart`
- `frontend/lib/widgets/location_context_diagram.dart`
- `frontend/lib/widgets/nbs_diagrams.dart`
- `frontend/test/location_context_diagram_test.dart`
- `frontend/test/nbs_diagram_test.dart`
- `frontend/test/recommendation_report_test.dart`
- `frontend/test/workflow_responsive_test.dart`

Project continuity:

- `NEXT_CODEX_PROMPT.md`
- `CODEX_PHASE_GH_GUIDED_UX_HANDOFF.md`

## Packages added

No package was added. The existing offline CustomPainter diagrams and local
Inter font remain in use. No online map tile or API-key dependency was added.

## Tests run

- Backend: `60 passed in 7.39s`.
- Flutter analyze: no issues found.
- Flutter tests and visual goldens: `25 passed`.
- `git diff --check`: clean.

## Summary UX changes

Summary is now a calmer decision page with a recommended-option sentence,
technical match, confidence, readiness, a two-sentence interpretation, one
major warning when triggered, three numbered actions, and direct navigation to
why, checks, sizing, comparison, diagrams, and export. Detailed science remains
outside Summary.

## Language simplification

Missing-data, land-fit, map-state, and readiness copy now uses short complete
sentences. The pollution workflow explicitly says when no site was selected.
Normal-user views avoid raw backend field names; TOPSIS and evidence detail stay
behind `Show technical details`.

## Design-readiness simplification

The active checklist is grouped into:

1. Needed to improve this result
2. Needed before engineering design
3. Field checks

Each group has one guidance sentence and calm status labels. Unit-explicit
frontend keys (`design_flow_m3_d`, `available_land_m2`) now count as supplied
inputs in the readiness engine.

## Diagram upgrades

The six existing engineering-style diagrams keep their offline vector drawing
and now show one `What it shows` sentence plus collapsed `When to use`, `Watch
out for`, and `Design notes` sections. They remain in Learn, component, train,
and catalogue detail contexts rather than Summary.

## Map and location behavior

The location card has three explicit states:

- Verified stored location: shows the verified coordinate marker and coordinate
  badge while stating that surrounding lines are schematic.
- Schematic context view: shows river/drain, site, interception, off-channel
  treatment, safe return, and safety labels without claiming surveyed geometry.
- No verified location: shows a clear no-map message and directs the user to the
  site checklist.

No coordinates, geometry, or external basemap tiles were invented.

## Pollution-source location fix

Pollution-source screening uses the shared site/station selector. Region and
station values are preserved in the request when selected. When omitted, the
screen states: `No site was selected. The result uses only the selected
pollution-source context.`

## Sizing estimator behavior

Absolute area bands now require supplied design flow and matching canonical
hydraulic-loading evidence. Population-only cases may display a stored
per-person footprint band but cannot claim an absolute area or land fit. The
response includes flow status, screening confidence, assumptions, missing
inputs, evidence coverage, source IDs, and a not-final-design caution.

## Scenario comparison behavior

The comparison keeps scientific rank unchanged and shows the top three options
by default. Additional options are collapsed. Each option can show technical
match, confidence/readiness, land, O&M, a stored strength, limitation, and a
context-safe `when to choose` sentence. Takeaways include best overall, lower
land demand when defensible, strongest evidence, lower maintenance, and expert
review when triggered.

## Export and report updates

JSON and CSV exports now include grouped readiness, location display status,
sizing flow status/confidence/assumptions, and comparison decision guidance.
The report preview uses the grouped checklist and natural zero-data wording.

## Known limitations

- The location view is deliberately schematic because no reviewed local river
  geometry layer is available for this patch.
- Sizing is screening-level only and does not add peak-flow, setback, access,
  freeboard, or ancillary-area allowances.
- Scenario history remains in-memory for the current app session.
- AHP expert weights and health-risk data remain pending expert consultation.
- Dependency resolution reports newer incompatible package versions; current
  pinned versions analyze and test cleanly.
- The local untracked visual-QA test and 50 regenerated PNG baselines passed but
  remain outside the commit to avoid adding a large generated review bundle.

## Manual QA checklist

1. Run measured-water input with and without design flow and available land.
2. Confirm no absolute area or land-fit claim appears without design flow.
3. Run pollution screening with a selected station and with no station.
4. Verify industrial acidic input shows pretreatment/neutralization warning.
5. Verify mainstem/high-order input remains off-channel only.
6. Open each Summary navigation action at desktop and 390 x 844.
7. Expand expert details and confirm method/evidence stay collapsed by default.
8. Review all three location-card states.
9. Expand all three diagram disclosure sections.
10. Open report preview and inspect grouped readiness, location status, sizing,
    and comparison.

## Commit status

Yes. This handoff belongs to the final scoped checkpoint commit named
`Guide UX and add sizing comparison tools`. See the latest `git log` entry for
the commit hash.

# Codex Big Upgrade Handoff

## Module completed

Module 3 - User-facing language and responsive polish.

Previous checkpoints:

- Module 1: `62da2da`
- Module 2: `a6bd780`

## Files changed

- `frontend/lib/screens/nbs_screens.dart`
- `frontend/test/home_responsive_test.dart`
- `frontend/test/workflow_responsive_test.dart`
- `CODEX_BIG_UPGRADE_HANDOFF.md`
- `NEXT_CODEX_PROMPT.md`

## Tests run

- Backend: 39 passed.
- Flutter analyze: no issues found.
- Flutter tests: 8 passed.
- `git diff --check`: clean.

## What changed

- Pollution source and intervention-position dropdowns now stack below 680px
  and use expanded dropdown content.
- Added setup-screen coverage at 390x844, 768x1024, and 1280x900.
- Added a narrow Results/NbS Components workspace check.
- Added desktop Home coverage.
- Replaced ambiguous visible wording with Technical match, Result confidence,
  Water-quality input, What this means, Important limitation, and Planning-level
  result.
- Upload help now explicitly explains unknown blanks, skipped unsupported or
  nonnumeric rows, and their confidence impact.
- Match versus confidence and treatment train versus component boundaries
  remain visible and concise.

## Intentionally not changed

- No backend scoring, schema, canonical data, or scientific values changed.
- No home-screen feature list or marketing content was added.
- Method caveats remain available in Method/technical details.

## Scientific safeguards preserved

- Missing values remain unknown, never zero.
- Treatment trains remain primary.
- Component standalone boundaries remain visible.
- Industrial, pH, mainstem, agricultural, and invasive-plant safeguards are
  unchanged.

## Known limitations

- Widget tests verify layout exceptions, not visual pixel perfection on every
  browser/font combination.
- Very long future translated labels may need an additional localization pass.
- Known local prompt/safety artifacts remain untracked and outside commits.

## Commit status

This module is included in the scoped checkpoint commit:
`Module 3: Polish responsive UI and user-facing language`.

## Exact next step

Start Module 4 from `NEXT_CODEX_PROMPT.md`. Build catalogue data through
repository/service boundaries, then add concise treatment train, individual
NbS, plant, and learning workspace views using only canonical fields and source
IDs.

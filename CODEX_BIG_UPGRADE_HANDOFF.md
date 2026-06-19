# Codex Big Upgrade Handoff

## Module completed

Module 1 - Trustworthy scoring and confidence.

## Files changed

- `backend/app/engines/README.md`
- `backend/app/engines/train_recommendation.py`
- `backend/app/repositories/engine_data_repository.py`
- `backend/tests/train_recommendation_test.py`
- `frontend/lib/models/recommendation_models.dart`
- `frontend/lib/screens/nbs_screens.dart`
- `CODEX_BIG_UPGRADE_HANDOFF.md`
- `NEXT_CODEX_PROMPT.md`

## Tests run

- Backend: 34 passed.
- Flutter analyze: no issues found.
- Flutter tests: 2 passed at 390x844 and 768x1024.
- `git diff --check`: clean.

## What changed

- Verified the configured canonical database through the repository boundary:
  28 NbS options, 8 treatment trains, 167 removal rows, 104 sources,
  19 footprint rows, 118 plant mappings, and 52 site attributes.
- Added per-train pollutant-gap explanations for every supplied parameter,
  including observed value/unit, source, target, target status, severity text,
  and whether canonical train evidence addresses the parameter.
- Added explicit use-case labels for drinking, irrigation, and inland discharge.
- Kept TOPSIS technical match separate from result confidence.
- Added documented, rule-based confidence caps for zero, one, two-to-three,
  and complete/incomplete key-panel inputs.
- Blank values remain unknown. Skipped or nonnumeric CSV rows reduce confidence.
- Added clear match-versus-confidence wording in Summary and Ranking.
- Reduced an accidental full-file Dart formatting diff back to semantic edits.

## What still needs work

- Module 2: add a separate individual-NbS recommendation layer while keeping
  treatment trains primary.
- Module 3: broader responsive and user-language pass.
- Module 4: treatment train, individual NbS, plant, and learning catalogues.

## Scientific safeguards preserved

- A0 applicability remains before TOPSIS.
- No scientific values, standards, removal efficiencies, citations, or expert
  weights were invented.
- Confidence caps are labelled as transparent UX safeguards, not scientific
  confidence intervals.
- Industrial pretreatment, pH neutralization, mainstem placement, agricultural
  source-control, and invasive-plant safeguards remain active.
- The canonical database was read only and was not replaced or modified.

## Known limitations

- The BOD/COD/TSS/pH panel is only a screening-completeness rule; source-specific
  parameters may still be essential.
- Confidence is research-stage and still requires expert calibration.
- A train can technically match a limited input while correctly showing low
  result confidence.
- Known untracked local prompt/safety artifacts remain outside commits.

## Commit status

BLOCKED before commit. The scoped checkpoint command was rejected before
execution because the Codex approval system reported that its usage limit had
been reached. No workaround was attempted. The verified Module 1 changes remain
unstaged and uncommitted. When tool access resumes, stage only the eight files
listed above and commit with:
`Module 1: Research-grade scoring and confidence`.

## Exact next step

First create the pending Module 1 checkpoint commit. Then start Module 2 from
`NEXT_CODEX_PROMPT.md`. Inspect canonical NbS, design,
performance, applicability, plant mapping, and provenance fields; then add
individual component recommendations as a separate response/UI layer without
altering treatment-train primacy.

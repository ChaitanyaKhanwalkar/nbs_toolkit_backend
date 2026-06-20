# Codex Big Upgrade Handoff

## Module completed

Module 2 - Dual recommendation system: treatment trains plus individual NbS.

Module 1 was committed successfully as `62da2da` despite the earlier approval
response reporting a limit error after the commit completed.

## Files changed

- `backend/app/api/routes/recommendation.py`
- `backend/app/engines/component_recommendation.py`
- `backend/app/engines/README.md`
- `backend/app/engines/__init__.py`
- `backend/app/schemas/recommendation.py`
- `backend/tests/train_recommendation_test.py`
- `frontend/lib/models/recommendation_models.dart`
- `frontend/lib/screens/nbs_screens.dart`
- `frontend/test/component_recommendation_test.dart`
- `CODEX_BIG_UPGRADE_HANDOFF.md`
- `NEXT_CODEX_PROMPT.md`

## Tests run

- Backend: 39 passed.
- Flutter analyze: no issues found.
- Flutter tests: 3 passed.
- `git diff --check`: clean.

## What changed

- Treatment trains remain the primary wastewater recommendation.
- Added a separate A0-screened individual-NbS response layer.
- Measured-data component order preserves the existing component TOPSIS result.
- Context-only component results are unscored and use transparent role ordering.
- Added role, pollutants, suitable/unsuitable contexts, standalone boundary,
  constraints, implementation text, non-invasive plants, and source IDs.
- Industrial components are polishing/buffer only after ETP/CETP; acidic input
  explicitly requires neutralization before biological/NbS stages.
- Mainstem/high-order screening blocks in-channel framing and exposes filtered
  components with reasons.
- Agricultural screening prioritizes bioretention, bioswale, and filter strips
  as source-control measures, not standalone wastewater treatment.
- Added a dedicated NbS Components workspace and train-first Summary section.

## Intentionally not changed

- No treatment-train rank or canonical evidence value was overwritten.
- No expert weights, removal efficiencies, standards, citations, or health-risk
  values were invented.
- No canonical database or source data was modified.
- Catalogue expansion and broader responsive language changes remain Modules 3
  and 4.

## Known limitations

- Context-only component order is a documented rule-based screen, not a numeric
  scientific rank.
- Some components have no explicit plant mapping; the UI states that planting
  guidance requires local validation.
- The existing component TOPSIS can still assign high technical suitability to
  unusual components, but standalone/context safeguards now prevent unsafe
  treatment claims.
- Known local prompt/safety artifacts remain untracked and outside commits.

## Commit status

This module is included in the scoped checkpoint commit:
`Module 2: Add individual NbS component recommendations`.

## Exact next step

Start Module 3 from `NEXT_CODEX_PROMPT.md`. Fix the narrow input-modal field
layout first, then apply responsive and user-language changes across results,
component cards, side tabs, evidence panels, and upload validation. Add 390,
768, and desktop widget coverage.

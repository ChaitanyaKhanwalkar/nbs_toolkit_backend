# Engines

This folder is for scientific engine modules.

Engines are where future scientific calculations will live, but only when each
step is ready and documented. The API layer should not calculate science, and
repositories should not calculate science. Engines should receive clean inputs
from services and return clear, explainable results.

## Current Status: Steps A, B, C, D, and E Only

The current files implement Step A:

- normalize raw input fields
- validate that `use_case` is supplied
- check that the selected `use_case` exists in stored standards use cases
- validate user measured observations enough to know whether they are usable

They also implement Step B:

- assemble water observations from the highest-priority available source
- prefer user measured observations over stored station observations
- prefer station observations over basin observations
- return a safe missing-data bundle when no water data is available
- preserve `source_id` values where raw observations provide them
- document that `water_type_profiles` remains a future fallback and is not used yet

They also implement Step C:

- fetch standards for one explicit use case through the service layer
- match observation parameters to standard parameters with transparent normalization
- calculate max-limit, min-limit, and range-limit pollutant gaps
- report missing standards, invalid values, and unit mismatches safely
- preserve source IDs where raw observations provide them

They also implement Step D:

- classify broad treatment-need groups from Step C gap results
- use explicit parameter mapping only
- ignore `within_standard` results
- turn missing standards, unit mismatches, and invalid values into warnings
- keep unknown exceeded parameters visible as unclassified

They also implement Step E:

- evaluate NbS catalogue candidates against Step D treatment need groups
- use explicit removal-efficiency rows or explicit catalogue support only
- return `eligible`, `ineligible`, or `data_pending` statuses
- report unsupported treatment needs, data gaps, cautions, and source IDs
- add safety cautions for pathogens, metals, infiltration, soil/slope, and
  drinking/domestic use cases when source fields support those checks

Steps A, B, C, D, and E do not recommend anything.

They do not:

- rank with MCDA or TOPSIS
- use AHP weights
- calculate confidence labels
- recommend plants
- classify health risk

## Future Steps

Future engine modules may be added in this order:

1. MCDA/TOPSIS ranking
2. confidence scoring
3. plant matching after technology ranking

Do not skip ahead. Follow `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

## Pending Data

AHP weights and health-risk tables remain pending. Do not invent criteria
weights, health-risk values, default target use cases, or scientific thresholds.

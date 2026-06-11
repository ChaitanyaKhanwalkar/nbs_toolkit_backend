# Engines

This folder is for scientific engine modules.

Engines are where future scientific calculations will live, but only when each
step is ready and documented. The API layer should not calculate science, and
repositories should not calculate science. Engines should receive clean inputs
from services and return clear, explainable results.

## Current Status: Step A Only

The current files implement Step A:

- normalize raw input fields
- validate that `use_case` is supplied
- check that the selected `use_case` exists in stored standards use cases
- validate user measured observations enough to know whether they are usable

Step A does not recommend anything.

It does not:

- calculate pollutant exceedance
- classify treatment need
- filter NbS candidates
- rank with MCDA or TOPSIS
- use AHP weights
- calculate confidence labels
- recommend plants
- classify health risk

## Future Steps

Future engine modules may be added in this order:

1. pollutant gap / exceedance calculation
2. treatment-need classification
3. candidate NbS filtering
4. MCDA/TOPSIS ranking
5. confidence scoring
6. plant matching after technology ranking

Do not skip ahead. Follow `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

## Pending Data

AHP weights and health-risk tables remain pending. Do not invent criteria
weights, health-risk values, default target use cases, or scientific thresholds.

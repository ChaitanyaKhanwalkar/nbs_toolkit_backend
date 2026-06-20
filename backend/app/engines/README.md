# Engines

This folder is for scientific engine modules.

Engines are where future scientific calculations will live, but only when each
step is ready and documented. The API layer should not calculate science, and
repositories should not calculate science. Engines should receive clean inputs
from services and return clear, explainable results.

## Current Status: Steps A through K, plus Step L-A Only

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

They also implement Step F:

- prepare raw MCDA matrix rows for eligible and data-pending NbS candidates
- exclude ineligible candidates from the matrix and count them
- collect available raw criteria buckets from removal evidence, footprint,
  implementation, catalogue criteria, and option fields
- keep missing raw criteria visible in each row and in a summary
- mark `weights_status` as `not_applied`

They also implement Step G:

- normalize numeric MCDA criteria values with unweighted min-max normalization
- use only explicit criterion direction rules
- mark missing, non-numeric, direction-unknown, and no-variation criteria clearly
- keep `weights_status` as `not_applied`

They also implement Step H:

- validate optional supplied MCDA criteria weights
- reject non-numeric or negative weights
- normalize supplied weights so the used weights sum to 1.0
- report missing and extra criteria weights
- clearly distinguish temporary weights from explicitly expert-validated weights

They also implement Step I:

- apply Step H weights to Step G normalized MCDA criteria
- calculate TOPSIS ideal-best and ideal-worst distances
- calculate TOPSIS closeness coefficients
- rank eligible/data-pending candidates by TOPSIS closeness
- carry the weight status honestly, including temporary/non-expert warnings

They also implement Step J:

- calculate rule-based confidence scores separately from TOPSIS closeness
- preserve Step I rank without changing it
- include water data, candidate evidence, criteria completeness, weight
  reliability, and caution flags as transparent confidence factors
- label confidence as high, medium, or low
- carry provisional warnings when temporary weights are used

They also implement Step K:

- attach plants only when an explicit plant-to-NbS mapping is returned by the
  plant provider
- preserve TOPSIS rank and closeness without changing them
- preserve confidence score and label without changing them
- return empty plant match lists with warnings when mappings are missing

They also implement Step L-A:

- assemble internal recommendation-shaped objects from TOPSIS ranking,
  confidence scoring, and optional plant matching
- copy `match_score` directly from `topsis_closeness`
- keep `confidence_score` separate from `match_score`
- preserve rank, weight status, methods, warnings, source IDs, and caution flags

The canonical treatment-train recommendation layer also reports a separate
rule-based result-confidence score. Its transparent data-completeness caps are
0% for no usable parameters, 35% for one parameter, 55% for two or three
parameters, 72% for four or more parameters with an incomplete BOD/COD/TSS/pH
screening panel, and 90% when that panel is complete. These are conservative UX
safeguards, not scientific confidence intervals or expert-validated weights.
Blank values remain unknown, skipped CSV rows reduce confidence, and neither
confidence nor its cap changes the TOPSIS technical-match score.

Each ranked treatment train includes a pollutant-gap breakdown for every
supplied parameter. It preserves the observed value, selected-use-case target,
input source, target status, and whether canonical train-performance evidence
addresses that parameter. `EngineDataRepository.canonical_dataset_counts()` is
a read-only diagnostic used by tests to guard against accidentally selecting a
legacy database.

The API also exposes an individual-NbS component layer assembled by
`IndividualNbsRecommendationEngine`. It enriches the existing A0-screened
component TOPSIS result with canonical profile, pollutant, implementation,
non-invasive plant, and source fields. It never replaces the primary treatment
train. Context-only requests remain unscored and use a documented role ordering
after A0: agricultural source-control components first, industrial components
as polishing/buffer only, and high-order/mainstem options off-channel only.

`DesignReadinessEngine` is a separate post-ranking interpretation layer. It
classifies output as early screening, planning-level, preliminary-design-ready,
or needing expert review. The rules use only supplied water-quality values,
explicit design/site context, verified location flags, and existing pH safety
bounds. Its checklist preserves missing values as missing and mapped profile
values as needing field verification; it does not size systems or change rank.

`SizingEstimator` adds a separate screening-level footprint interpretation. It
uses user-supplied design flow or population only when matching canonical
footprint or hydraulic-loading records exist. It reports evidence coverage,
missing inputs, source IDs, and land fit. Partial component coverage never
produces a positive land-fit claim.

`ScenarioComparisonEngine` packages the already-ranked alternatives for one
run and lists eligible supporting components with their stored roles and
constraints. It does not rerank options or fill evidence gaps. Comparing
different water-quality, site, or land inputs requires separate recommendation
runs.

Steps A through K and Step L-A do not create API routes or `/recommend`.

They do not:

- calculate AHP pairwise weights
- treat plant matches as final plant recommendations
- classify health risk

## Future Steps

Future engine modules may be added in this order:

1. implementation-plan attachment after internal recommendation assembly
2. endpoint design only after the internal assembly outputs are reviewed

Do not skip ahead. Follow `backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

## Pending Data

AHP weights and health-risk tables remain pending. Do not invent criteria
weights, health-risk values, default target use cases, or scientific thresholds.

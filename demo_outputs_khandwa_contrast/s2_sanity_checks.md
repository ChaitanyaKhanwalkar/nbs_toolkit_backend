# Scenario 2: Khandwa irrigation/reuse contrast sanity checks

Use case: `irrigation`
Weights status: `temporary_not_expert_validated`; expert_validated: `False`
Contrast selection note: Irrigation was selected because the DB has use-case-specific criteria weights and stored standards for pH, BOD, TSS, conductivity, and SAR. The same sewage profile supplies pH/BOD/TSS; COD, ammonia-N, and total phosphorus remain disclosed standard gaps for this use case.

## Soil-filter wiring
On-site disposal status: `conditional` at rank 8; rules: `APP_RULE_023`.
APP_RULE_023 now fires for the low-infiltration Indirasagar clay site. The train is cautioned/conditioned rather than removed because the current train-ranking engine treats component-level hard filters as train-level conditional hits unless the whole train is directly targeted.
No other train was rejected or made conditional by APP_RULE_023 in this scenario.

## Influent and standards
Influent is representative domestic sewage/blackwater profile source_id 9, not measured Khandwa field sampling.
Ammonia-N is 200 mg/L, a high blackwater representative value; ammonia-driven outcomes remain sensitive to that assumption.
Pollutant gap statuses: bod: exceeds_standard; cod: standard_missing; tss: exceeds_standard; ammonia_n: standard_missing; total_phosphorus: standard_missing; ph: within_standard

## Missing values and under-crediting
Missing train evidence remains disclosed as unknown/median-imputed for TOPSIS geometry and confidence; it is not converted to 0% removal.
Trains with unknown/median-imputed criteria: On-site disposal: C1, C2, C7

## Ranking
| Rank | Train | Ci | Status | Use-case verdict |
|---:|---|---:|---|---|
| 1 | WSP Train (pond series) | 0.943677 | allowed | unknown |
| 2 | DEWATS modular train | 0.898073 | allowed | pass |
| 3 | Septic + HSSF + polishing | 0.790588 | allowed | marginal |
| 4 | VF nitrifying hybrid | 0.787594 | allowed | pass |
| 5 | UASB-based STP | 0.716795 | allowed | marginal |
| 6 | French VF (no primary) | 0.650842 | allowed | pass |
| 7 | Pond + sewage-fed aquaculture | 0.454349 | allowed | pass |
| 8 | On-site disposal | 0.700499 | conditional | unknown |

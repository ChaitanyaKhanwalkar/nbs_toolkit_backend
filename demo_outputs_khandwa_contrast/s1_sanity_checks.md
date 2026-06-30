# Scenario 1: Khandwa discharge to river sanity checks

Use case: `discharge_inland`
Weights status: `temporary_not_expert_validated`; expert_validated: `False`
Contrast selection note: Primary corrected scenario requested by user; C4 source_fit is active through pollution_source_type=domestic_sewage.

## Soil-filter wiring
On-site disposal status: `conditional` at rank 8; rules: `APP_RULE_023`.
APP_RULE_023 now fires for the low-infiltration Indirasagar clay site. The train is cautioned/conditioned rather than removed because the current train-ranking engine treats component-level hard filters as train-level conditional hits unless the whole train is directly targeted.
No other train was rejected or made conditional by APP_RULE_023 in this scenario.

## Influent and standards
Influent is representative domestic sewage/blackwater profile source_id 9, not measured Khandwa field sampling.
Ammonia-N is 200 mg/L, a high blackwater representative value; ammonia-driven outcomes remain sensitive to that assumption.
Pollutant gap statuses: bod: exceeds_standard; cod: exceeds_standard; tss: exceeds_standard; ammonia_n: exceeds_standard; total_phosphorus: exceeds_standard; ph: within_standard

## Missing values and under-crediting
Missing train evidence remains disclosed as unknown/median-imputed for TOPSIS geometry and confidence; it is not converted to 0% removal.
Trains with unknown/median-imputed criteria: On-site disposal: C1, C2, C7

## C4 activation check
Earlier C4-inactive comparison: top train was VF nitrifying hybrid with Ci 0.838083; with C4 active, top train is VF nitrifying hybrid with Ci 0.841506.
C4 activation did not change the #1 train in this case, but it changed the active TOPSIS criteria set and shifted closeness coefficients.

## Ranking
| Rank | Train | Ci | Status | Use-case verdict |
|---:|---|---:|---|---|
| 1 | VF nitrifying hybrid | 0.841506 | allowed | marginal |
| 2 | DEWATS modular train | 0.712711 | allowed | fail |
| 3 | WSP Train (pond series) | 0.631334 | allowed | marginal |
| 4 | Septic + HSSF + polishing | 0.63104 | allowed | fail |
| 5 | French VF (no primary) | 0.608826 | allowed | fail |
| 6 | UASB-based STP | 0.523287 | allowed | fail |
| 7 | Pond + sewage-fed aquaculture | 0.493391 | allowed | marginal |
| 8 | On-site disposal | 0.61061 | conditional | unknown |

# Corrected S1 discharge sensitivity summary

Scenario: Khandwa / Indira Sagar, domestic sewage, discharge_inland.
Fallback profile selected: `Domestic sewage — combined municipal (medium-strong, India)`.

Corrected fallback values:
- `bod` = `250.0`
- `cod` = `500.0`
- `tss` = `250.0`
- `ammonia_n` = `40.0`
- `total_phosphorus` = `12.0`
- `ph` = `7.4`

## Baseline ranking

| Rank | Train | Ci | use-case verdict |
|---|---|---:|---|
| 1 | DEWATS modular train | 0.858103 | marginal |
| 2 | VF nitrifying hybrid | 0.814391 | marginal |
| 3 | Septic + HSSF + polishing | 0.729578 | fail |
| 4 | French VF (no primary) | 0.659896 | marginal |
| 5 | UASB-based STP | 0.649843 | fail |
| 6 | Pond + sewage-fed aquaculture | 0.570778 | unknown |
| 7 | WSP Train (pond series) | 0.527598 | fail |
| 8 | On-site disposal | 0.664596 | unknown |

DEWATS vs VF margin: `0.043711` Ci.

## Monte Carlo

Setting: ±30% per weight, 5000 draws.
DEWATS top-1 retention: `99.98%`.
Mean Spearman vs baseline: `0.931`.
Top-1 flips: VF nitrifying hybrid (1/5000).
Equal-weights winner: `DEWATS modular train`.
Drop-C2 winner: `UASB-based STP`.
Drop-C7 winner: `Pond + sewage-fed aquaculture`.

Old blackwater artifacts avoided: yes. Export assertions confirmed NH3-N=200 and TP=40 were not present in the selected fallback values.

# Irrigation final weights sensitivity summary

Scenario: Khandwa / Indira Sagar region 27, domestic sewage, corrected municipal fallback, use_case `irrigation`.

## Final irrigation weights

| Criterion | Name | Direction | Weight |
|---|---|---|---:|
| C1 | treatment_fit | benefit | 0.228136 |
| C2 | standard_fit | benefit | 0.228136 |
| C3 | site_fit | benefit | 0.095330 |
| C4 | source_fit | benefit | 0.117709 |
| C6 | hydrologic_fit | benefit | 0.057781 |
| C7 | footprint_land | cost | 0.117709 |
| C8 | om_energy_difficulty | cost | 0.155200 |

Six-decimal sum: `1.000001`.
Label: final working weights used in this report; not expert-validated unless approval is documented.

## Ranking

| Rank | Train | Ci | Use-case verdict | CBR | CBR label |
|---|---|---:|---|---:|---|
| 1 | WSP Train (pond series) | 0.941646 | unknown | 1.32 | Favourable |
| 2 | UASB-based STP | 0.904582 | unknown | 1.14 | Balanced / site-dependent |
| 3 | DEWATS modular train | 0.894311 | pass | 1.41 | Favourable |
| 4 | Septic + HSSF + polishing | 0.856638 | pass | 1.39 | Favourable |
| 5 | VF nitrifying hybrid | 0.764335 | pass | 1.01 | Balanced / site-dependent |
| 6 | French VF (no primary) | 0.604656 | pass | 0.90 | Balanced / site-dependent |
| 7 | Pond + sewage-fed aquaculture | 0.423219 | pass | 0.64 | Cost-heavy / needs review |
| 8 | On-site disposal | 0.691217 | unknown | 0.67 | Cost-heavy / needs review |

Top ranked train: `WSP Train (pond series)`.
WSP remains #1: `yes`.
VF nitrifying hybrid rank: `5`.

## Sensitivity

Monte Carlo: +/-30% per weight, 5000 draws.
Top-1 retention for `WSP Train (pond series)`: `98.08%`.
Mean Spearman vs baseline: `0.983`.
Top-1 flips: UASB-based STP (96/5000).
Equal-weights winner: `WSP Train (pond series)`.
Drop-C8 winner: `UASB-based STP`.

## Change from previous revised irrigation report

Previous top: `WSP Train (pond series)`; new top: `WSP Train (pond series)`.
Previous VF rank: `4`; new VF rank: `5`.

## Discharge control

Discharge #1: `DEWATS modular train` Ci `0.858103`.
Discharge #2: `VF nitrifying hybrid` Ci `0.814391`.
Discharge changed by irrigation sync: no, control values remain at the corrected baseline.

## CBR check

CBR appears on ranked trains and `official_ranking_unchanged` is true; TOPSIS rank remains primary.

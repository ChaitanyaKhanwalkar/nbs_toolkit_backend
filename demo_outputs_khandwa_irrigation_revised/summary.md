# Revised Khandwa irrigation run

## Weight update

- Live DB: `canonical db/narmada_nbs_canonical.db`, table `criteria_weights`, irrigation rows IDs 36-42.
- Seed file path: `backend/criteria_weights_ahp_fuzzy_ensemble.sql`.
- CSV mirror path: `canonical db/criteria_weights_ahp_fuzzy_ensemble.csv`.
- Status label: `temporary_not_expert_validated`; source_id remains 104; provenance_status_id remains 2.
- Derivation note: `Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.`
- Integrity note: the supplied four-decimal vector sums to 0.9999, not 1.0000. Values were not adjusted; the sensitivity script renormalizes weights internally.

## Engine run

- Scenario: region_id 27 / Indirasagar Dam, use_case `irrigation`, domestic-sewage profile source_id 9 values from the prior s2 run.
- API weights_status: `temporary_not_expert_validated`.
- API expert_validated: `False`.
- New #1: WSP Train (pond series) with Ci 0.945099.
- Historical old irrigation result: WSP pond series #1 (Ci 0.944), VF hybrid #4.
- New VF hybrid rank: #4 (Ci 0.779164).
- Winner changed: no.

## Ranked Ci

1. WSP Train (pond series) - Ci 0.945099
2. DEWATS modular train - Ci 0.900698
3. Septic + HSSF + polishing - Ci 0.800574
4. VF nitrifying hybrid - Ci 0.779164
5. UASB-based STP - Ci 0.727264
6. French VF (no primary) - Ci 0.621404
7. Pond + sewage-fed aquaculture - Ci 0.463555
8. On-site disposal - Ci 0.706698

## Decisive criterion

- Top-vs-second separator: C7 footprint. WSP and DEWATS tie on C1, C2, C3, C4, C6, and C8 in this run; WSP's lower footprint cost gives the visible weighted-value edge over DEWATS.
- Sensitivity-critical criterion: C8 O&M. In the extreme-case battery, dropping C8 changes top-1 to `French VF (no primary)`, while all one-at-a-time +/- factor perturbations kept WSP as top-1.

## Sensitivity

- OAT top-1 changes: 0/49.
- Monte Carlo: WSP top-1 retention 100.0% under +/-30%, 5000 draws.
- Mean Spearman vs baseline: 0.976, from `sensitivity_stdout.txt`.
- WSP top-3 retention: 100.0%.

## Output files

- `ranked_results.csv`
- `decision_matrix.csv`
- `decision_matrix_status.csv`
- `weights_used.json`
- `weights.csv`
- `engine_flags.json`
- `filtered_out.csv`
- `confidence.csv`
- `baseline_ranking.csv`
- `monte_carlo_stability.csv`
- `oat_results.csv`
- `extreme_cases.csv`
- `top_vs_second_criterion_delta.csv`
- `sensitivity_stdout.txt`

## Sanity checks

- Drinking and discharge DB row snapshots were unchanged during the DB update.
- On-site disposal is conditional and demoted after assessed options because all use-case verdicts are unknown; its unknown C1/C2/C7 values are median-imputed for TOPSIS geometry and disclosed in `decision_matrix_status.csv` plus data gaps, not treated as zero.
- Standards gaps remain visible for irrigation: COD, NH4-N, and TP are supporting context because no stored irrigation target limit is available.

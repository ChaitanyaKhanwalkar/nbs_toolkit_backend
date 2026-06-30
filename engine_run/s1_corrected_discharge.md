# S1 (corrected) — Khandwa discharge_inland, all 8 trains

Re-run of the s1 discharge scenario with the **corrected municipal influent**.

## Inputs

- **Site:** Indirasagar Dam (regions.id=27), Khandwa district, Narmada mainstem (Strahler 7).
- **Use-case:** discharge_inland (discharge to inland river).
- **Source:** domestic (domestic_sewage).
- **Influent:** corrected municipal profile (`water_type_profiles` source_id 109, *Domestic sewage — combined municipal (medium-strong, India)*):

  | parameter | value | unit |
  |---|---|---|
  | bod | 250 | mg_l |
  | cod | 500 | mg_l |
  | tss | 250 | mg_l |
  | ammonia_n | 40 | mg_l |
  | total_phosphorus | 12 | mg_l |
  | ph | 7.4 | ph_units |

  > Correction vs prior s1 run: **NH3-N 200 → 40**, **TP 40 → 12** (over-strong blackwater fractions replaced by municipal defaults); TSS 275 → 250 to match the canonical municipal profile. BOD/COD/pH unchanged.

- **Weights:** current `criteria_weights` for discharge_inland (FINAL_V1_AHP_FUZZY_ENSEMBLE, `temporary_not_expert_validated`).

## Ranking by TOPSIS closeness coefficient (Ci)

| Rank | Train | Ci | use-case verdict |
|---|---|---|---|
| 1 | DEWATS modular train | 0.858103 | marginal |
| 2 | VF nitrifying hybrid | 0.814391 | marginal |
| 3 | Septic + HSSF + polishing | 0.729578 | fail |
| 4 | French VF (no primary) | 0.659896 | marginal |
| 5 | UASB-based STP | 0.649843 | fail |
| 6 | Pond + sewage-fed aquaculture | 0.570778 | unknown |
| 7 | WSP Train (pond series) | 0.527598 | fail |
| 8 | On-site disposal | 0.664596 | unknown |

## Decisive-criterion check

Baseline #1 (all criteria active): **DEWATS modular train**. Each active criterion dropped in turn; re-ranked with the same TOPSIS + tie-break.

| Criterion dropped | Name | New #1 | New #1 Ci | Leader flips? |
|---|---|---|---|---|
| C1 | treatment_fit | DEWATS modular train | 0.882579 | no |
| C2 | standard_fit | UASB-based STP | 0.901610 | **YES** |
| C3 | site_fit | DEWATS modular train | 0.852558 | no |
| C4 | source_fit | DEWATS modular train | 0.854681 | no |
| C6 | hydrologic_fit | DEWATS modular train | 0.858103 | no |
| C7 | footprint | Pond + sewage-fed aquaculture | 0.921732 | **YES** |
| C8 | om | DEWATS modular train | 0.847140 | no |

**Decisive criterion:** **C2** (standard_fit) → UASB-based STP; **C7** (footprint) → Pond + sewage-fed aquaculture.

## Match % vs Ci

The UI **"match %"** is the **same number as Ci**, just formatted. Backend field `ranked_trains[].match_score` *is* the TOPSIS closeness coefficient (`distance_worst / (distance_best + distance_worst)` in `_apply_topsis`). Flutter maps `match_score` → `matchScore` → `matchPercent` = `(matchScore * 100).clamp(0,100).toStringAsFixed(1) + '%'` (`frontend/lib/models/recommendation_models.dart`), and labels it "TOPSIS closeness".

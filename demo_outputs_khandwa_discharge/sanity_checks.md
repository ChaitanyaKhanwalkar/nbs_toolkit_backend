# Sanity checks — Khandwa / discharge_inland demo (flagged, not hidden)

All weights are **INTERIM / PROVISIONAL** (final v1 AHP-Fuzzy ensemble,
`temporary_not_expert_validated`, not expert/field validated).

## 1. On-site disposal was NOT hard-filtered on soil/infiltration (disclosed gap)
- Train 7 (Septic + **Soak Pit / Soakaway**, component nbs_id 20, family
  "Infiltration & Soil Systems") survived to ranking. It placed **last only**
  because its `discharge_inland` use-case verdict is `unknown` (no canonical
  performance evidence) — **not** because of any soil rule.
- A relevant hard rule **exists** — `APP_RULE_023` (hard_filter, family
  "Infiltration & Soil Systems", `soil_infiltration =
  low_infiltration_or_rocky_or_shallow_soil` → remove) — and the site **is**
  low-infiltration (Indirasagar region 27: `infiltration_class='low'`, HSG `D`,
  Clay). It still did not fire because:
  1. **Train path:** `train_recommendation._site_rule_context()` passes only
     stream_order/slope/builtup/agri/land-cover to the rule context — it does
     **not** pass `soil_infiltration`, so the rule can never trigger in train
     ranking.
  2. **Option path:** `_factor_matches` compares `normalize('low')` against the
     rule token `'low_infiltration_or_rocky_or_shallow_soil'`; with no
     value→category mapping the equality fails, so it doesn't fire there either.
- **Implication:** on low-infiltration clay, a soak-pit/leach system should
  arguably be cautioned or removed. Here it is a disclosed gap, not a
  soil-validated pass.

## 2. On-site disposal's Ci is propped up by median imputation
- Train 7 has three **unknown** criteria (C1 treatment_fit, C2 standard_fit, C7
  footprint) that are **median-imputed for TOPSIS geometry only**
  (`data_status='unknown_median_imputed'`). This gives it a raw closeness
  coefficient of **0.6912** — the 3rd-highest raw Ci — despite having the
  thinnest evidence. The final sort pushes it to rank 8 via the
  `all_use_cases_unknown` flag, and its confidence is correctly **low (0.45)**,
  but the raw Ci itself is inflated by imputation. Every other train had all six
  active criteria known.

## 3. Influent ammonia is high and inflates ammonia "fails"
- The representative influent uses **ammonia_n = 200 mg/L** (canonical
  "Domestic sewage (blackwater mix)" *blackwater fraction*, range 100–300). This
  is a strong-sewage value, not a measured Khandwa value. It drives a **75%
  required ammonia removal** target.
- Non-nitrifying trains (WSP ponds, UASB, sewage-fed aquaculture) cannot be
  credited for ammonia and are pushed toward `fail`/`marginal` on that
  parameter, partly because of this high representative value. Treat
  ammonia-driven outcomes as sensitive to the assumed influent.

## 4. Ponds are under-credited from missing removal rows
- For the WSP pond train (train 1), `train_addresses_parameter` is **False** for
  TSS, ammonia_n, and total_phosphorus (no removal_efficiency rows), while True
  only for BOD/COD. Ponds remove TSS/TP in reality, so missing rows
  under-credit them. This is a data-coverage gap, not evidence of poor
  performance.

## 5. Confidence ≠ suitability
- Several trains with a canonical `discharge_inland` verdict of **fail** (DEWATS,
  Septic+HSSF, UASB, French VF) still carry **high confidence (0.80–0.93)**.
  Confidence measures input/evidence completeness, not whether the train passes
  the use case. Read Ci + verdict + confidence together, never confidence alone.

## 6. Active criteria — C4 (source_fit) is inactive
- The train TOPSIS ran on **C1, C2, C3, C6, C7, C8** only. **C4 (source_fit) was
  dropped** because no `pollution_source_type` was supplied, so every train's C4
  was null. Weights were renormalized over the 6 active criteria. C5 is
  intentionally reserved (health-risk).

## 7. Site-row anomaly (recorded per request)
- Site row used = **Indirasagar Dam (region 27)**, Strahler 7. The alternative
  Khandwa WQ station **Mortakka (region 39)** was **not** used because its
  `stream_order_strahler=1` and `nat_discharge_cms=0.427` are anomalous against
  its `drainage_area_km2=67,184` (likely a HydroRIVERS snap error).

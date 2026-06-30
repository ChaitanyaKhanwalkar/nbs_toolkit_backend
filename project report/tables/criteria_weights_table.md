# Criteria & Weights (Methods table) - final working AHP-Fuzzy-AHP ensemble

Source: `criteria_weights` table, `narmada_nbs_canonical.db` (source_id 104,
status `FINAL_V1_AHP_FUZZY_ENSEMBLE`). The irrigation column is labelled as
final working weights used in this report, not expert-validated unless approval
documentation is recorded. C5 is reserved. Direction: benefit = higher better;
cost = lower better.

| Code | Criterion | Direction | Irrigation | Drinking | Discharge (inland) |
|---|---|---|---:|---:|---:|
| C1 | Treatment fit / pollutant-gap closure | benefit | 0.228136 | 0.2668 | 0.2583 |
| C2 | Use-case standard fit | benefit | 0.228136 | 0.2668 | 0.2583 |
| C3 | Site / applicability fit | benefit | 0.095330 | 0.1065 | 0.0997 |
| C4 | Pollution-source fit | benefit | 0.117709 | 0.1217 | 0.1139 |
| C6 | Hydrologic / stream-order fit | benefit | 0.057781 | 0.0583 | 0.0561 |
| C7 | Footprint / land requirement | cost | 0.117709 | 0.0583 | 0.0998 |
| C8 | O&M / energy difficulty | cost | 0.155200 | 0.1217 | 0.1139 |

C5 (health risk) is reserved; no validated dataset is available and it remains
documented as future work.

**Fuzzy layer:** crisp AHP and Fuzzy-AHP weights differ by at most 0.68
percentage points across all 21 cells. The irrigation column reflects the final
O&M re-blend.

# Khandwa scenario comparison

Did the #1 train change? **Yes**.
Scenario 1 top: **VF nitrifying hybrid** (Ci 0.841506).
Scenario 2 top: **WSP Train (pond series)** (Ci 0.943677).

The main driver is the use-case standard/criteria context. Discharge_inland evaluates stringent domestic sewage discharge targets including COD, ammonia-N, and total phosphorus. Irrigation/reuse has stored targets for BOD, TSS, pH, conductivity, and SAR; for this same sewage profile, COD, ammonia-N, and total phosphorus are disclosed as standard gaps rather than scored gaps. The irrigation weight vector also gives slightly more relative penalty to footprint and O&M than the discharge vector.

Criterion snapshot for each scenario's #1 train:

| Criterion | S1 top raw | S1 top weight | S2 top raw | S2 top weight |
|---|---:|---:|---:|---:|
| C1 | 0.9 | 0.2583127416872584 | 1.0 | 0.24026175973824024 |
| C2 | 0.9 | 0.2583127416872584 | 1.0 | 0.24026175973824024 |
| C3 | 1.0 | 0.09970490029509972 | 1.0 | 0.09425490574509425 |
| C4 | 0.5 | 0.11390588609411391 | 0.5 | 0.1157058842941157 |
| C6 | 1.0 | 0.056102943897056105 | 1.0 | 0.057252942747057244 |
| C7 | 14.0 | 0.09975490024509975 | 7.0 | 0.1157058842941157 |
| C8 | 0.3333333333333333 | 0.11390588609411391 | 0.19999999999999998 | 0.13655686344313656 |

C4 activation versus earlier run:
Earlier/no-source comparison top: VF nitrifying hybrid (Ci 0.838083).
Corrected C4-active Scenario 1 top: VF nitrifying hybrid (Ci 0.841506).
C4 activation did not change the #1 train here, but C4 is now present as a known active criterion in the decision matrix. The earlier run had C4 inactive and renormalized the remaining criteria.

Side-by-side rankings:

| Rank | Scenario 1: discharge to river | S1 Ci | Scenario 2: irrigation/reuse | S2 Ci |
|---:|---|---:|---|---:|
| 1 | VF nitrifying hybrid | 0.841506 | WSP Train (pond series) | 0.943677 |
| 2 | DEWATS modular train | 0.712711 | DEWATS modular train | 0.898073 |
| 3 | WSP Train (pond series) | 0.631334 | Septic + HSSF + polishing | 0.790588 |
| 4 | Septic + HSSF + polishing | 0.63104 | VF nitrifying hybrid | 0.787594 |
| 5 | French VF (no primary) | 0.608826 | UASB-based STP | 0.716795 |
| 6 | UASB-based STP | 0.523287 | French VF (no primary) | 0.650842 |
| 7 | Pond + sewage-fed aquaculture | 0.493391 | Pond + sewage-fed aquaculture | 0.454349 |
| 8 | On-site disposal | 0.61061 | On-site disposal | 0.700499 |

Soil-filter before/after:
Before this patch, the previous Khandwa output reported all 8 trains survived and On-site disposal had no APP_RULE_023 hit.
After this patch, Scenario 1 On-site disposal status is conditional with rules APP_RULE_023; Scenario 2 status is conditional with rules APP_RULE_023.
No other train was rejected or made conditional by APP_RULE_023 in either scenario.

# Narmada NbS Planner

Research-grade decision-support toolkit for screening nature-based treatment
trains in the Narmada basin.

## Final working irrigation weights

The live canonical database and fallback weight source use the final working
AHP-Fuzzy AHP ensemble irrigation vector used in this report:

| Criterion | Weight | Direction |
|---|---:|---|
| C1 treatment_fit | 0.228136 | benefit |
| C2 standard_fit | 0.228136 | benefit |
| C3 site_fit | 0.095330 | benefit |
| C4 source_fit | 0.117709 | benefit |
| C6 hydrologic_fit | 0.057781 | benefit |
| C7 footprint_land | 0.117709 | cost |
| C8 om_energy_difficulty | 0.155200 | cost |

These are final working weights used in this report, not labelled
expert-validated unless explicit approval documentation is added.

## Cost-Benefit Ratio Analysis - Screening Level

The app includes `screening_non_monetary_v1`, a secondary interpretation panel
for each ranked treatment train. It is **not** ROI, financial feasibility,
economic return, or true monetary cost-benefit analysis. It does not estimate
rupee CAPEX/OPEX.

Formula:

```text
benefit_score =
weighted_average(C1 treatment fit, C2 standard fit, C3 site fit,
C4 source fit, C6 hydrologic fit, confidence score, readiness score,
safety suitability score)

cost_burden_score =
weighted_average(C7 footprint burden, C8 O&M burden, energy burden,
land constraint burden, design complexity burden, missing data burden)

screening_cbr = benefit_score / max(cost_burden_score, 0.20)
```

The official recommendation rank remains the criteria-weighted TOPSIS train
ranking. CBR labels are scenario-local explanatory aids only: Very favourable,
Favourable, Balanced / site-dependent, or Cost-heavy / needs review. Safety
conditions such as industrial pretreatment, drinking/strict-use, and mainstem
placement add caveats or cap favourable labels.

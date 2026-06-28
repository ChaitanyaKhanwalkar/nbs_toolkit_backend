-- Final v1 AHP-Fuzzy AHP ensemble weights for Narmada NbS Planner.
-- C5 is intentionally absent/inactive pending future health-risk integration.
-- Values are stored with 6 decimals exactly as supplied for this demo version.

DELETE FROM criteria_weights
WHERE use_case IN ('discharge_inland', 'drinking', 'irrigation');

INSERT INTO criteria_weights (
    use_case_id,
    use_case,
    criterion_code,
    criterion_name,
    weight,
    benefit_or_cost,
    status,
    derivation_note,
    source_id,
    provenance_status_id,
    created_at
) VALUES
(1, 'drinking', 'C1', 'treatment_fit', 0.266800, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(1, 'drinking', 'C2', 'standard_fit', 0.266800, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(1, 'drinking', 'C3', 'site_fit', 0.106500, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(1, 'drinking', 'C4', 'source_fit', 0.121700, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(1, 'drinking', 'C6', 'hydrologic_fit', 0.058250, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(1, 'drinking', 'C7', 'footprint', 0.058250, 'cost', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(1, 'drinking', 'C8', 'om', 0.121700, 'cost', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(2, 'discharge_inland', 'C1', 'treatment_fit', 0.258313, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(2, 'discharge_inland', 'C2', 'standard_fit', 0.258313, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(2, 'discharge_inland', 'C3', 'site_fit', 0.099705, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(2, 'discharge_inland', 'C4', 'source_fit', 0.113906, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(2, 'discharge_inland', 'C6', 'hydrologic_fit', 0.056103, 'benefit', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(2, 'discharge_inland', 'C7', 'footprint', 0.099755, 'cost', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(2, 'discharge_inland', 'C8', 'om', 0.113906, 'cost', 'FINAL_V1_AHP_FUZZY_ENSEMBLE', 'Final v1 AHP-Fuzzy AHP ensemble weights for demo ranking. C5 health-risk integration remains reserved for future expert data.', 104, 2, datetime('now')),
(3, 'irrigation', 'C1', 'treatment_fit', 0.231600, 'benefit', 'temporary_not_expert_validated', 'Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.', 104, 2, datetime('now')),
(3, 'irrigation', 'C2', 'standard_fit', 0.231600, 'benefit', 'temporary_not_expert_validated', 'Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.', 104, 2, datetime('now')),
(3, 'irrigation', 'C3', 'site_fit', 0.095100, 'benefit', 'temporary_not_expert_validated', 'Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.', 104, 2, datetime('now')),
(3, 'irrigation', 'C4', 'source_fit', 0.116000, 'benefit', 'temporary_not_expert_validated', 'Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.', 104, 2, datetime('now')),
(3, 'irrigation', 'C6', 'hydrologic_fit', 0.054900, 'benefit', 'temporary_not_expert_validated', 'Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.', 104, 2, datetime('now')),
(3, 'irrigation', 'C7', 'footprint', 0.116000, 'cost', 'temporary_not_expert_validated', 'Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.', 104, 2, datetime('now')),
(3, 'irrigation', 'C8', 'om', 0.154700, 'cost', 'temporary_not_expert_validated', 'Irrigation perf-vs-O&M intensity revised 1.8->1.2, 2026-06-29; crisp-AHP interim, CR=0.003; ensemble re-blend pending; provisional.', 104, 2, datetime('now'));

SELECT use_case, ROUND(SUM(weight), 6) AS weight_sum, COUNT(*) AS criteria_count
FROM criteria_weights
GROUP BY use_case;

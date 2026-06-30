-- Synchronize final working irrigation AHP-Fuzzy AHP ensemble weights.
--
-- This is an additive/reproducibility update script for the live canonical DB.
-- It updates only use_case='irrigation' rows in criteria_weights. It does not
-- alter TOPSIS logic, CBR logic, discharge/drinking weights, standards, or
-- evidence tables.

UPDATE criteria_weights
SET
    criterion_name = CASE criterion_code
        WHEN 'C1' THEN 'treatment_fit'
        WHEN 'C2' THEN 'standard_fit'
        WHEN 'C3' THEN 'site_fit'
        WHEN 'C4' THEN 'source_fit'
        WHEN 'C6' THEN 'hydrologic_fit'
        WHEN 'C7' THEN 'footprint_land'
        WHEN 'C8' THEN 'om_energy_difficulty'
        ELSE criterion_name
    END,
    weight = CASE criterion_code
        WHEN 'C1' THEN 0.228136
        WHEN 'C2' THEN 0.228136
        WHEN 'C3' THEN 0.095330
        WHEN 'C4' THEN 0.117709
        WHEN 'C6' THEN 0.057781
        WHEN 'C7' THEN 0.117709
        WHEN 'C8' THEN 0.155200
        ELSE weight
    END,
    benefit_or_cost = CASE criterion_code
        WHEN 'C7' THEN 'cost'
        WHEN 'C8' THEN 'cost'
        ELSE 'benefit'
    END,
    status = 'FINAL_V1_AHP_FUZZY_ENSEMBLE',
    derivation_note = 'Final working weights used in this report; irrigation crisp + fuzzy AHP ensemble after O&M re-blend, 2026-06-30. Not labelled expert-validated unless supervisor approval is documented.',
    source_id = COALESCE(source_id, 104),
    provenance_status_id = COALESCE(provenance_status_id, 2)
WHERE use_case = 'irrigation'
  AND criterion_code IN ('C1','C2','C3','C4','C6','C7','C8');

SELECT
    use_case,
    ROUND(SUM(weight), 6) AS weight_sum,
    COUNT(*) AS criteria_count
FROM criteria_weights
WHERE use_case = 'irrigation'
GROUP BY use_case;

-- Add Cost-Benefit Ratio Analysis metadata for screening-only display.
--
-- This migration is additive. It stores method metadata and transparent
-- non-monetary display weights only; it does not store rupee CAPEX/OPEX,
-- replace AHP/TOPSIS weights, or alter evidence/ranking tables.

CREATE TABLE IF NOT EXISTS cost_benefit_method (
    id INTEGER PRIMARY KEY,
    method_key TEXT UNIQUE NOT NULL,
    method_name TEXT NOT NULL,
    version TEXT NOT NULL,
    is_monetary INTEGER NOT NULL DEFAULT 0,
    formula_text TEXT NOT NULL,
    denominator_floor REAL NOT NULL DEFAULT 0.20,
    display_cap REAL,
    caveat_text TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cost_benefit_component_weights (
    id INTEGER PRIMARY KEY,
    method_key TEXT NOT NULL,
    component_key TEXT NOT NULL,
    component_label TEXT NOT NULL,
    side TEXT NOT NULL CHECK(side IN ('benefit','cost_burden')),
    weight REAL NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('higher_better','higher_worse')),
    source_field TEXT,
    notes TEXT,
    UNIQUE(method_key, component_key)
);

INSERT INTO cost_benefit_method (
    method_key,
    method_name,
    version,
    is_monetary,
    formula_text,
    denominator_floor,
    display_cap,
    caveat_text
) VALUES (
    'screening_non_monetary_v1',
    'Cost-Benefit Ratio Analysis - Screening Level',
    'v1',
    0,
    'benefit_score = weighted_average(C1 treatment fit, C2 standard fit, C3 site fit, C4 source fit, C6 hydrologic fit, confidence score, readiness score, safety suitability score); cost_burden_score = weighted_average(C7 footprint burden, C8 O&M burden, energy burden, land constraint burden, design complexity burden, missing data burden); screening_cbr = benefit_score / max(cost_burden_score, 0.20)',
    0.20,
    5.0,
    'Screening-level non-monetary ratio. Does not estimate rupee CAPEX/OPEX.'
) ON CONFLICT(method_key) DO UPDATE SET
    method_name = excluded.method_name,
    version = excluded.version,
    is_monetary = excluded.is_monetary,
    formula_text = excluded.formula_text,
    denominator_floor = excluded.denominator_floor,
    display_cap = excluded.display_cap,
    caveat_text = excluded.caveat_text;

INSERT INTO cost_benefit_component_weights (
    method_key,
    component_key,
    component_label,
    side,
    weight,
    direction,
    source_field,
    notes
) VALUES
('screening_non_monetary_v1','C1','C1 treatment fit','benefit',0.25,'higher_better','criteria_breakdown.C1','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','C2','C2 standard fit','benefit',0.25,'higher_better','criteria_breakdown.C2','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','C3','C3 site fit','benefit',0.10,'higher_better','criteria_breakdown.C3','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','C4','C4 source fit','benefit',0.10,'higher_better','criteria_breakdown.C4','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','C6','C6 hydrologic fit','benefit',0.05,'higher_better','criteria_breakdown.C6','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','confidence','Confidence score','benefit',0.10,'higher_better','confidence_score','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','readiness','Readiness score','benefit',0.10,'higher_better','design_readiness.level','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','safety_suitability','Safety suitability score','benefit',0.05,'higher_better','applicability/context warnings','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','C7','C7 footprint burden','cost_burden',0.30,'higher_worse','criteria_breakdown.C7','Transparent v1 display weight; uses inverse of TOPSIS cost suitability where needed.'),
('screening_non_monetary_v1','C8','C8 O&M burden','cost_burden',0.30,'higher_worse','criteria_breakdown.C8','Transparent v1 display weight; uses inverse of TOPSIS cost suitability where needed.'),
('screening_non_monetary_v1','energy','Energy burden','cost_burden',0.15,'higher_worse','energy_class/om_intensity','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','land_constraint','Land constraint burden','cost_burden',0.10,'higher_worse','sizing_estimate.land_fit','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','design_complexity','Design complexity burden','cost_burden',0.10,'higher_worse','pretreatment/applicability/design readiness','Transparent v1 display weight; not expert-ratified AHP.'),
('screening_non_monetary_v1','missing_data','Missing data burden','cost_burden',0.05,'higher_worse','missing criteria and sizing gaps','Transparent v1 display weight; missing data is burden, not zero cost.')
ON CONFLICT(method_key, component_key) DO UPDATE SET
    component_label = excluded.component_label,
    side = excluded.side,
    weight = excluded.weight,
    direction = excluded.direction,
    source_field = excluded.source_field,
    notes = excluded.notes;

CREATE VIEW IF NOT EXISTS v_app_cost_benefit_method AS
SELECT
    m.method_key,
    m.method_name,
    m.version,
    m.is_monetary,
    m.formula_text,
    m.denominator_floor,
    m.display_cap,
    m.caveat_text,
    w.component_key,
    w.component_label,
    w.side,
    w.weight,
    w.direction,
    w.source_field,
    w.notes
FROM cost_benefit_method AS m
JOIN cost_benefit_component_weights AS w
  ON w.method_key = m.method_key
ORDER BY
    CASE w.side WHEN 'benefit' THEN 1 ELSE 2 END,
    w.id;

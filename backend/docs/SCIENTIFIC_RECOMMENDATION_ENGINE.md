# SCIENTIFIC_RECOMMENDATION_ENGINE.md — NbS Toolkit

**Purpose:** This file defines the scientific recommendation logic for the Narmada NbS Toolkit backend.  
It should be treated as the main instruction file for building the recommendation engine.

This document exists so that Codex / Claude Code / future developers do **not** improvise the logic.  
The engine must stay transparent, source-linked, beginner-readable, and scientifically defensible.

---

## 1. Core principle

The app must not recommend NbS solutions by fuzzy text matching or by simple labels such as "Grey Water".

The correct logic is:

```text
water quality problem → treatment need → feasible NbS technology → suitable plants → implementation plan
```

Plants are selected **after** the engineering solution is selected.  
The plant layer supports the treatment system; it does not drive the treatment-system decision.

---

## 2. Non-negotiable scientific rules

1. **No invented values.**  
   Do not invent pollutant values, removal efficiencies, criteria weights, health-risk scores, citations, costs, or thresholds.

2. **Measured data first.**  
   Use measured water observations or uploaded user data first. Use `water_type_profiles` only as a fallback.

3. **Standards define the target.**  
   A recommendation is meaningless unless the system knows the target use case: drinking, irrigation, surface-water discharge, reuse, etc.

4. **Exceedance drives treatment need.**  
   The engine must calculate which parameters exceed the selected standard and by how much.

5. **Removal efficiency is the treatment bridge.**  
   NbS options must be judged by their ability to remove the specific pollutants that exceed the standard.

6. **Hard filters come before ranking.**  
   Unsafe or impossible solutions must be removed or capped before TOPSIS ranking.

7. **Match score and confidence score are separate.**  
   A solution may fit well but have weak data support. Do not merge these into one magic number.

8. **Every recommendation must explain itself.**  
   Output must include rank, score, confidence, reasons, cautions, data gaps, and source IDs/citations.

9. **AHP weights are expert inputs.**  
   Do not finalize scientific rankings using fake AHP weights. Use transparent temporary/default weights only for development, clearly flagged as non-final.

10. **Keep gaps visible.**  
    Missing health risk, stream order, point sources, cost, or footprint data should be returned as limitations, not silently ignored.

---

## 3. Required data tables

The engine should use these tables from the production database:

| Table | Role in recommendation |
|---|---|
| `sources` | Provenance backbone for every value and rule |
| `basins` | Basin/sub-basin context |
| `regions` | Station/catchment/district context, climate, soil, coordinates |
| `site_attributes` | Slope, elevation, drainage area, LULC, dilution proxy, stream order when available |
| `pollution_sources` | Non-point and, later, point pollution pressure |
| `water_observations` | Measured water-quality values |
| `water_type_profiles` | Fallback profiles when measured data is unavailable |
| `standards` | Target thresholds by use case and parameter |
| `nbs_options` | Candidate NbS technologies |
| `removal_efficiency` | Parameter-wise treatment capability of each NbS |
| `nbs_footprint` | Land/area/hydraulic loading constraints where available |
| `nbs_criteria` | O&M, co-benefit, complexity, or other qualitative criteria |
| `plants` | Plant catalogue, native/invasive status, tolerance, ecological role |
| `plant_solution_map` | Which plants fit which NbS technologies |
| `nbs_implementation` | Construction and maintenance guidance |
| `criteria_weights` | AHP-derived expert weights; pending until supervisor review |
| `health_risk` | HQ/HI/cancer-risk layer; pending until supervisor data is integrated |

---

## 4. End-to-end recommendation pipeline

The backend recommendation service should follow this exact order.

```text
1. Resolve site
2. Load water-quality data
3. Select target standard
4. Calculate exceedance gaps
5. Convert gaps into treatment needs
6. Generate candidate NbS technologies
7. Apply hard filters and score caps
8. Build MCDA decision matrix
9. Rank using TOPSIS with AHP weights
10. Calculate separate confidence score
11. Attach suitable plants
12. Attach implementation plan
13. Return explanation, cautions, sources, and gaps
```

---

## 5. Step 1 — Resolve site

Input may be one of:

- station ID / station name
- region ID
- district/catchment selection
- latitude/longitude snapped to nearest available Narmada catchment/station
- user-uploaded water data with selected location

The site resolver should return:

```json
{
  "region_id": 12,
  "station": "Example Station",
  "district": "Example District",
  "basin_id": 1,
  "lat": 22.0,
  "lon": 76.0,
  "site_attributes_available": true
}
```

If the selected site is outside the supported Narmada demonstration layer, the app may still run only if enough user-provided data exists, but confidence must be reduced and the gap must be reported.

---

## 6. Step 2 — Load water-quality data

Priority order:

1. User-uploaded measured values for the selected site/sample.
2. `water_observations` for the selected station or nearest station.
3. Catchment/district-level measured data if station-level data is missing.
4. `water_type_profiles` only as fallback.

Return a `data_quality_level`:

| Level | Meaning |
|---|---|
| `measured_user` | User uploaded actual measured sample |
| `measured_station` | Official station observation available |
| `measured_regional` | Regional/catchment observation used |
| `profile_fallback` | Generic water-type profile used |
| `insufficient` | Not enough data for reliable ranking |

---

## 7. Step 3 — Select target standard

The engine must know the target use case. Recommended initial options:

| Use case | Main concern |
|---|---|
| `surface_discharge` | BOD, TSS, pH, nutrients, pathogens where applicable |
| `irrigation_reuse` | salinity, sodium, nutrients, pathogens, metals |
| `drinking_domestic` | strict health/pathogen/metals limits; usually requires caution that NbS alone may not be enough |
| `landscape_reuse` | BOD, TSS, odour, pathogens, nutrients |

If the user has not selected a use case, default to the project-approved use case only if the supervisor has confirmed it. Otherwise return a clear error/message:

```text
Target use case is required because treatment standards differ by use.
```

---

## 8. Step 4 — Calculate exceedance gaps

For each measured parameter, compare observed value against the selected standard.

### 8.1 Maximum-limit parameters

For pollutants where lower is better, such as BOD, TSS, nitrate, phosphate, coliform, metals:

```text
exceedance_ratio = max(0, (observed_value - limit_high) / limit_high)
required_removal_fraction = max(0, (observed_value - limit_high) / observed_value)
```

### 8.2 Minimum-limit parameters

For parameters where higher is better, such as DO:

```text
deficit_ratio = max(0, (limit_low - observed_value) / limit_low)
```

DO should usually be treated as an oxygenation/ecological-stress indicator, not as a normal "removal" pollutant.

### 8.3 Range-limit parameters

For pH or other acceptable-range parameters:

```text
if observed_value < limit_low:
    range_gap = (limit_low - observed_value) / limit_low
elif observed_value > limit_high:
    range_gap = (observed_value - limit_high) / limit_high
else:
    range_gap = 0
```

### 8.4 Severity classes

| Gap class | Suggested rule | Meaning |
|---|---|---|
| `none` | ratio = 0 | Within target standard |
| `low` | 0 < ratio <= 0.25 | Mild exceedance |
| `moderate` | 0.25 < ratio <= 1.0 | Needs treatment |
| `high` | 1.0 < ratio <= 3.0 | Strong treatment need |
| `severe` | ratio > 3.0 | High-risk / may need treatment train |

These class thresholds are transparent defaults and should be configurable.

---

## 9. Step 5 — Convert pollutant gaps into treatment needs

Map exceeded parameters into treatment-need groups:

| Treatment need | Parameters |
|---|---|
| `organic_load_reduction` | BOD, COD, low DO stress |
| `solids_removal` | TSS, turbidity |
| `nutrient_reduction` | nitrate, ammonia, total nitrogen, phosphate |
| `pathogen_reduction` | faecal coliform, E. coli, total coliform |
| `salinity_management` | EC, TDS, chloride, sodium, SAR where available |
| `metal_toxicity_reduction` | arsenic, lead, chromium, cadmium, iron, manganese, etc. |
| `pH_correction` | pH outside accepted range |
| `runoff_volume_control` | high urban/agriculture runoff pressure, stormwater context |

The treatment need profile should be carried forward into scoring.

---

## 10. Step 6 — Generate candidate NbS technologies

Candidates come from `nbs_options`.

A candidate is considered relevant if at least one of these is true:

- It has `removal_efficiency` evidence for one or more exceeded parameters.
- It belongs to a technology family known to address the treatment-need group.
- It is suitable as a pre-treatment or polishing stage for the detected problem.
- It is manually whitelisted by validated project rules with a source.

Do not recommend a candidate as high-confidence if it lacks pollutant-specific removal evidence.

---

## 11. Step 7 — Hard filters and score caps

Hard filters protect the tool from unsafe recommendations.

### 11.1 Exclude or cap rules

| Condition | Action |
|---|---|
| No removal evidence for the main exceeded pollutant group | Cap treatment score at 0.40 or exclude if severe |
| High pathogen water + open public contact system | Exclude or require warning/treatment train |
| Toxic metals + food-chain/aquaculture/reuse pathway | Exclude unless controlled disposal is defined |
| Infiltration system + untreated pathogen/toxic water | Exclude unless pre-treatment is included |
| Very low infiltration soil + pure infiltration technology | Exclude or heavily penalize |
| Very steep slope + pond/wetland without earthwork feasibility | Penalize or exclude based on configurable threshold |
| Invasive plant species | Exclude plant from recommendation |
| Missing implementation guidance | Allow only if marked as low maturity; do not rank top unless strong reason |
| Drinking/domestic target + simple NbS only | Add caution: may require advanced/disinfection treatment; do not overclaim |

### 11.2 Treatment train flag

If exceedance is severe for multiple pollutant groups, return a treatment-train recommendation instead of pretending one NbS is enough.

Example:

```text
settling tank / pond → horizontal subsurface-flow wetland → polishing pond / disinfection
```

Treatment-train logic is optional for first build, but severe cases must at least return a warning.

---

## 12. Step 8 — MCDA criteria

The decision matrix should score each remaining NbS from 0 to 1 for each criterion.

### 12.1 Core criteria

| Code | Criterion | Direction | Data source |
|---|---|---|---|
| C1 | Treatment gap closure | Benefit | `removal_efficiency`, `standards`, observed values |
| C2 | Health-risk reduction | Benefit | `health_risk`; pending placeholder |
| C3 | Site suitability | Benefit | `regions`, `site_attributes` |
| C4 | Hydrological suitability | Benefit | slope, drainage area, stream order/dilution proxy |
| C5 | Pollution-source fit | Benefit | `pollution_sources`, water profile |
| C6 | Footprint feasibility | Cost/benefit transformed | `nbs_footprint`; land availability if available |
| C7 | O&M simplicity | Benefit | `nbs_criteria`, implementation evidence |
| C8 | Evidence strength | Benefit | source quality, confidence, data completeness |
| C9 | Co-benefits | Benefit | `nbs_criteria`; optional |
| C10 | Cost/resource demand | Cost | pending/partial; optional until sourced |

### 12.2 Minimum viable criteria for first production engine

If not all criteria are available, the first defensible production engine should use at least:

1. Treatment gap closure
2. Site suitability
3. Hydrological suitability / dilution proxy
4. Pollution-source fit
5. Footprint / space feasibility where available
6. O&M simplicity where available
7. Evidence strength

Health risk should remain a placeholder until supervisor data is integrated.

---

## 13. Criterion scoring formulas

### C1 — Treatment gap closure

For each exceeded parameter:

```text
mid_efficiency = (eff_low + eff_high) / 2 / 100
parameter_fit = min(1, mid_efficiency / required_removal_fraction)
```

Then weight parameter fits by severity:

```text
treatment_gap_closure = weighted_average(parameter_fit, weight = exceedance_ratio)
```

If a parameter has no removal-efficiency data:

```text
parameter_fit = 0
missing_evidence_flag = true
```

For parameters like pH and DO, use special technology capability rules rather than normal removal efficiency.

### C2 — Health-risk reduction

Pending until health-risk data is integrated.

For now:

```text
health_risk_reduction = null
criterion_status = "pending_expert_data"
```

Do not invent HQ, HI, or cancer-risk values.

### C3 — Site suitability

Score based on:

- soil/infiltration class compatibility
- slope compatibility
- rainfall/climate compatibility
- dominant land cover
- flood/waterlogging context where available

Example structure:

```text
site_suitability = average(
    soil_fit,
    slope_fit,
    climate_fit,
    land_cover_fit
)
```

Each sub-score must be rule-based and documented in code comments/config.

### C4 — Hydrological suitability

Use:

- true stream order if available
- otherwise `dilution_proxy = drainage_area_km2`
- slope and drainage area
- hydraulic loading/retention constraints where available

This criterion must report if it uses a proxy instead of true stream order.

### C5 — Pollution-source fit

Map solution families to pollution contexts:

| Pollution context | Strong solution families |
|---|---|
| agricultural runoff | riparian buffers, vegetated filter strips, constructed wetlands, ponds |
| urban runoff | bioswales, rain gardens, retention ponds, stormwater wetlands |
| sewage / domestic wastewater | DEWATS, anaerobic baffled reactor + wetland, stabilization ponds, constructed wetlands |
| industrial/metals | controlled phytoremediation, polishing wetlands only with strong caution |
| mixed catchment pressure | hybrid/treatment-train systems |

### C6 — Footprint feasibility

If area availability is known:

```text
footprint_score = clamp(available_area / required_area, 0, 1)
```

If only technology footprint data is available:

- lower land demand = higher score
- higher land demand = lower score

If data is missing, mark criterion as missing and lower confidence.

### C7 — O&M simplicity

Suggested scoring:

| O&M level | Score |
|---|---:|
| very simple | 1.00 |
| simple | 0.80 |
| moderate | 0.60 |
| complex | 0.35 |
| expert/energy-intensive | 0.20 |
| unknown | null + confidence penalty |

### C8 — Evidence strength

Evidence is based on:

- source type: government/manual/peer-reviewed > legacy/derived
- whether removal efficiency has a range
- whether source_id exists
- whether site data is measured or fallback
- whether plant-solution mapping is expert-validated

Suggested scoring:

| Evidence condition | Score |
|---|---:|
| measured water + sourced removal range + site data + implementation source | 1.00 |
| measured water + sourced removal + partial site data | 0.80 |
| station/regional data + sourced removal | 0.70 |
| fallback water profile + sourced removal | 0.55 |
| missing removal for key pollutant | 0.30 |
| unsourced/legacy only | 0.20 or exclude |

---

## 14. AHP weights

AHP weights should be stored in `criteria_weights`.

The supervisor should provide pairwise comparisons for each use case.

Example use-case differences:

| Criterion | Drinking/domestic | Irrigation | Surface discharge |
|---|---:|---:|---:|
| Treatment gap closure | Very high | High | Very high |
| Health-risk reduction | Very high | Medium/high | Medium |
| Site suitability | Medium | High | High |
| Footprint feasibility | Medium | Medium | Medium |
| O&M simplicity | Medium | High | High |
| Co-benefits | Low/medium | Medium | Medium |

Until AHP is completed:

- use transparent temporary weights only in development mode
- label outputs as `weights_status = "temporary_not_expert_validated"`
- do not claim final scientific ranking

---

## 15. TOPSIS ranking

For each candidate NbS:

1. Build decision matrix: rows = solutions, columns = criteria.
2. Normalize each criterion.
3. Apply AHP weights.
4. Identify ideal best and ideal worst.
5. Calculate distance to ideal best and ideal worst.
6. Calculate closeness coefficient:

```text
closeness = distance_to_worst / (distance_to_best + distance_to_worst)
```

7. Rank by descending closeness.

Important: `closeness` is the **match score**, not the confidence score.

---

## 16. Confidence score

Confidence should be calculated separately.

Suggested components:

| Component | Weight suggestion |
|---|---:|
| water_data_quality | 0.25 |
| removal_evidence_quality | 0.25 |
| site_data_completeness | 0.20 |
| criteria_weight_status | 0.15 |
| plant_mapping_validation | 0.10 |
| implementation_source_quality | 0.05 |

Development formula:

```text
confidence_score = weighted_average(available_confidence_components)
```

Suggested labels:

| Score | Label |
|---:|---|
| >= 0.80 | High |
| 0.60–0.79 | Medium |
| 0.40–0.59 | Low |
| < 0.40 | Very low / research only |

Confidence output must include reasons:

```json
{
  "confidence_score": 0.72,
  "confidence_label": "Medium",
  "confidence_reasons": [
    "Measured station water data available",
    "Removal efficiency sourced for BOD and TSS",
    "Stream order unavailable; drainage area used as proxy",
    "AHP weights not yet expert-finalized"
  ]
}
```

---

## 17. Plant recommendation logic

Plants are attached after NbS ranking.

Plant filters:

1. Must be linked to selected NbS in `plant_solution_map`.
2. Prefer native or non-invasive species.
3. Exclude invasive species unless supervisor explicitly allows a controlled research-only context.
4. Match climate preference.
5. Match soil/water regime.
6. Match pollutant tolerance where evidence exists.
7. Prefer species with source_id and evidence note.

Plant output should include:

```json
{
  "plant_species": "Typha angustifolia",
  "native_status": "native/introduced/etc",
  "invasive": false,
  "why_selected": [
    "Mapped to horizontal subsurface-flow wetland",
    "Tolerates nutrient-rich wastewater",
    "Suitable for local climate/soil context"
  ],
  "cautions": [
    "Confirm local availability before implementation"
  ],
  "source_ids": [12, 18]
}
```

---

## 18. Final API response shape

The recommendation endpoint should return something like this:

```json
{
  "site": {
    "region_id": 12,
    "station": "Example Station",
    "district": "Example District",
    "basin": "Narmada"
  },
  "input_summary": {
    "use_case": "surface_discharge",
    "data_quality_level": "measured_station",
    "parameters_used": ["BOD", "TSS", "pH", "nitrate"]
  },
  "exceedances": [
    {
      "parameter": "BOD",
      "observed": 18.0,
      "standard_limit": 3.0,
      "unit": "mg/L",
      "exceedance_ratio": 5.0,
      "severity": "severe"
    }
  ],
  "recommendations": [
    {
      "rank": 1,
      "nbs_id": 4,
      "solution": "Horizontal subsurface-flow constructed wetland",
      "family": "Constructed Wetlands",
      "match_score": 0.86,
      "confidence_score": 0.72,
      "confidence_label": "Medium",
      "criteria_breakdown": {
        "treatment_gap_closure": 0.91,
        "site_suitability": 0.82,
        "hydrological_suitability": 0.70,
        "pollution_source_fit": 0.85,
        "footprint_feasibility": 0.60,
        "operation_maintenance": 0.75,
        "evidence_strength": 0.78
      },
      "why_recommended": [
        "Strong fit for BOD and TSS reduction",
        "Suitable for domestic/sewage-type organic load",
        "Site slope and soil conditions are acceptable",
        "Native plant options available"
      ],
      "cautions": [
        "Requires pre-treatment to reduce clogging risk",
        "AHP weights are not yet supervisor-finalized",
        "Stream order unavailable; drainage area used as dilution proxy"
      ],
      "plants": [],
      "implementation_summary": "Short summary here",
      "source_ids": [1, 7, 21]
    }
  ],
  "global_gaps": [
    "Health-risk layer pending integration",
    "Point-source pollution inventory pending",
    "Some footprint data incomplete"
  ]
}
```

---

## 19. Backend architecture mapping

Follow this responsibility split:

```text
api/                  HTTP endpoints only
schemas/              request/response models
repositories/         database queries only
services/             orchestration/business/scientific workflow
engines/              scoring, exceedance, hard filters, TOPSIS
validators/           input validation and data-quality checks
utils/                small helpers only; no major recommendation logic
```

Suggested files:

```text
backend/app/engines/exceedance_engine.py
backend/app/engines/treatment_need_engine.py
backend/app/engines/hard_filter_engine.py
backend/app/engines/topsis_engine.py
backend/app/engines/confidence_engine.py
backend/app/engines/plant_selection_engine.py

backend/app/services/recommendation_service.py
backend/app/repositories/water_repository.py
backend/app/repositories/site_repository.py
backend/app/repositories/nbs_repository.py
backend/app/repositories/standards_repository.py
backend/app/repositories/sources_repository.py
```

API routes must not query database tables directly.

---

## 20. Minimum tests required

Add tests before calling the engine production-ready.

### 20.1 Exceedance tests

- BOD above limit calculates correct exceedance ratio.
- pH inside range returns zero gap.
- pH below range returns correct gap.
- Missing standard returns clear error.

### 20.2 Treatment fit tests

- Candidate with strong removal for exceeded pollutant scores higher than irrelevant candidate.
- Missing removal efficiency reduces score/confidence.
- Severe pollutant with no evidence triggers cap/exclusion.

### 20.3 Hard filter tests

- Infiltration solution excluded for untreated pathogen-heavy water.
- Invasive plants excluded.
- Food-chain/aquaculture solution excluded for metal-toxic water.

### 20.4 Confidence tests

- Measured data produces higher confidence than fallback profile.
- Missing stream order lowers confidence but does not crash.
- Temporary AHP weights produce warning.

### 20.5 API response tests

- Response includes rank, match_score, confidence_score, reasons, cautions, source_ids.
- Response does not contain unsourced invented values.

---

## 21. Validation plan

The tool should be validated using three layers.

### Layer 1 — Internal consistency

Check that the engine recommends expected technologies for known pollutant profiles.

Examples:

| Scenario | Expected output |
|---|---|
| High BOD + high TSS domestic wastewater | DEWATS / constructed wetland / pond-wetland train |
| Agricultural runoff + nutrients + sediment | riparian buffer / vegetated filter strip / wetland |
| Urban stormwater + TSS + runoff pressure | bioswale / retention pond / stormwater wetland |
| Heavy metals | controlled phytoremediation or caution-heavy recommendation, not food-chain reuse |
| Pathogen-heavy water | avoid unsafe open-contact reuse without treatment train/disinfection warning |

### Layer 2 — Expert face validation

Supervisor reviews:

- AHP criteria weights
- plant-solution mapping
- top recommendations for sample stations
- cautions and limitations

### Layer 3 — Sensitivity analysis

Vary criteria weights and check if top recommendations remain stable.

This is not required at runtime but is important for the report/paper.

---

## 22. What moves the project closer to 10/10

Priority order:

1. Finalize use-case standard with supervisor.
2. Fill and validate AHP criteria weights.
3. Keep match score and confidence score separate.
4. Add hard filters before TOPSIS.
5. Integrate health-risk data when available.
6. Add true stream order / river network where possible.
7. Add point-source pollution inventory.
8. Validate plant-solution mapping with supervisor.
9. Complete footprint/O&M criteria for all 28 technologies.
10. Add sensitivity analysis for the final report/paper.
11. Add treatment-train logic for severe multi-pollutant cases.
12. Write tests for all important engine pieces.
13. Return source IDs and explanations in every API response.

---

## 23. Implementation status labels

Use these labels in code/docs:

| Label | Meaning |
|---|---|
| `production_ready` | sourced, tested, validated enough for app use |
| `expert_pending` | structure exists but awaits supervisor validation |
| `data_pending` | logic exists but data table is empty/missing |
| `research_only` | useful for analysis but not safe for user-facing claim |
| `fallback` | used only because better data is unavailable |

---

## 24. Post-ranking interpretation outputs

The API may also return two post-ranking interpretation objects:

- `sizing_estimates` uses supplied design flow and canonical hydraulic-loading
  evidence for absolute area bands. Population-only cases may show a stored
  per-person footprint band, but no absolute area or land-fit claim. It is a
  screening estimate, not engineering design.
- `scenario_comparison` summarizes the current ranked alternatives without
  changing rank and lists supporting components without treating them as train
  replacements. Different input scenarios must be run independently.

Both outputs preserve unknown evidence as unknown and expose their limitations.

---

## 25. Final engine statement

The recommendation engine must be:

```text
pollutant-first,
standard-based,
site-constrained,
evidence-ranked,
confidence-labelled,
and provenance-linked.
```

If a recommendation cannot explain **why**, **based on which data**, and **with what confidence**, it should not be shown as a scientific recommendation.


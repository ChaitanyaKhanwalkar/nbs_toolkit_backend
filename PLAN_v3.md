# PLAN_v2.md — NbS Toolkit (finalized one-month plan)

> The single reference for the project. Supersedes the earlier PLAN.md.
> `CLAUDE.md` is the short operational version Claude Code reads each session; this is the full plan.
> **Status legend:** ✅ have · 🔧 build this month · ⏳ defer / future work · ❓ decide with supervisor

---

## 0. The plan in one paragraph

Take the existing working MVP and turn it into an evidence-based decision-support tool that recommends nature-based solutions for water treatment — **demonstrated properly on one river basin**, where every recommendation traces back to a government dataset, an official standard, or peer-reviewed literature. We are not rebuilding the app; we are deepening its data and replacing fuzzy guessing with transparent, sourced, multi-criteria scoring. Everything outside the chosen basin stays an honestly-documented gap, not a fake number.

---

## 1. What this is (project description)

The NbS Toolkit is an evidence-based decision-support tool that recommends nature-based solutions for water treatment, tailored to local conditions and traceable to verifiable sources. Given a location and its water quality — measured or specified — it assesses the contaminant load against the relevant use-case standard, accounts for local soil and climate, and returns a ranked set of nature-based solutions (constructed wetlands, planted filtration systems, etc.), each paired with suitable plant species, a confidence level, and an implementation and maintenance plan. It adapts the multi-criteria decision-support approach established in the international literature to the Indian context — Indian government datasets, native species, national standards — and is demonstrated on a single river basin where every recommendation is grounded in real, sourced data.

**Defining feature: provenance.** Every value and every recommendation points back to a real source. That is the difference between "an app that suggests plants" and "a tool a water-resources researcher can trust and cite."

---

## 2. Scope decision (LOCKED)

**Demonstrate the framework on ONE river basin — the Narmada — built deep, with the engine kept basin-agnostic so the basin is *data, not logic*.**

This is the decision that makes a one-month timeline realistic. It also unifies three things at once: it shrinks the data problem from "all of India" to "the districts inside one basin," it satisfies the river-basin direction (a basin is a more natural unit than a district for water work — surface and groundwater are interrelated within its boundary), and it matches the supervisor's basin-scale hydrology lineage. Because the engine treats the basin as data, this is a national-capable framework *demonstrated* on the Narmada — extensible later by ingesting another basin, not rebuilding.

### The scope ladder

| | Option | When it applies |
|---|---|---|
| 🔒 **Locked** | **Narmada basin, deep, engine basin-agnostic** | The plan. Build this. |
| ⬆️ **Upside** | Add a second contrasting basin (arid or high-rainfall) for a comparative result | Only if Weeks 1–2 run ahead of schedule. Strengthens the generalization claim. |
| 🛟 **Floor** | One sub-basin / district cluster within the Narmada, very deep | Fall back here if full-basin data proves hard to access. No architectural change. |

**Why this is sound across all lenses:** feasible in a month, scientifically standard (single-basin demonstration is the accepted norm, not a weakness), and the kind of deep, sourced, defensible work the supervisor's field trusts — versus broad, shallow national coverage, which it does not.

**Two confirmations for Week 1, not blockers:** that the Narmada water-quality and soil data are accessible (else drop to the floor), and that the supervisor doesn't already have a different basin's data worth reusing (an easy swap, since the basin is data).

**Scope trap to avoid:** "integrate river basin" must NOT become "build a national basin-level GIS map system." One basin, used as the organizing frame plus a source of real water-quality data. Maps are a stretch goal, not a deliverable.

---

## 3. What the app does (user loop)

> *here's my water and where I am → here are the best natural ways to treat it, ranked, with the plants to use, why they were chosen, and how to build and maintain them.*

| Step | What happens |
|---|---|
| 1. Input | User picks a location in the basin, or enters/selects water quality |
| 2. Knowledge base | App pulls sourced data: basin context, soil, standards, solutions, removal data |
| 3. Scoring engine | MCDA matches the contaminant gap (observed vs standard) to the best-fit solutions |
| 4. Result | Ranked nature-based solutions + suitable plants + confidence + citations |
| 5. Detail | Tap a solution for implementation steps and maintenance plan |

---

## 4. Architecture

An **evolution of the current stack, not a rewrite.** Keep FastAPI + PostgreSQL on Azure + Flutter. The change is in the data model and the scoring logic.

### 4.1 Data layer (PostgreSQL tables)

The `sources` table is the backbone — everything references it. This is both the credibility claim and the legal safety net (§7).

| Table | Holds | Notes |
|---|---|---|
| `sources` | id, citation, type, url, **license** | Everything points here |
| `basins` | basin / sub-basin names, source_id | 🔧 new |
| `regions` | district, state, **basin_id**, soil_type, rainfall, source_id | Evolved from `merged_district_data` |
| `water_observations` | station, basin_id, date, parameters, source_id | 🔧 new — real CPCB/WRIS data |
| `standards` | use_case, parameter, threshold, source_id | 🔧 new — BIS / CPCB limits |
| `plants` | species, pollution_tolerance, ecological_role, soil, climate, source_id | ✅ clean + dedup existing |
| `nbs_options` | solution, suitability fields, source_id | ✅ clean + dedup existing |
| `removal_efficiency` | nbs, parameter, eff_low, eff_high, confidence, source_id | 🔧 new — the missing bridge |
| `plant_solution_map` | which species suit which solution | 🔧 new — closes a structural gap (§6) |
| `site_attributes` | per-location: elevation, slope, stream_order, %agri, %builtup, LULC class, source_id | 🔧 new — GIS-derived, one-time prep |
| `river_network` | Narmada + tributaries geometry, stream_order, source_id | 🔧 new — India-WRIS / HydroRIVERS |
| `pollution_sources` | type (point/non-point), location, source_id | 🔧 new — CPCB + state PCB; non-point from LULC |
| `health_risk` | station, non-carcinogenic (HQ/HI), carcinogenic (cancer risk), metals, source_id | 🔧 new — **supervisor's data, in scope** |
| `criteria_weights` | criterion, use_case, weight | 🔧 new — AHP output, set once with supervisor |
| `nbs_implementation` | steps, maintenance, source_id | ✅ clean existing |

### 4.2 Logic layer — the AHP–TOPSIS engine (LOCKED method)

Replace the fuzzy text matching with a two-step multi-criteria engine. The decision splits into two jobs: **weighting the criteria** (done once) and **ranking the solutions** (done per location).

**Step 1 — AHP sets the criteria weights (offline, once, with the supervisor).**
The supervisor compares criteria two at a time (Saaty 1–9 scale); the method turns those pairwise judgments into weights that sum to 1, with a consistency-ratio check. The weights embed his expertise and are citable. Stored in `criteria_weights` — one weight-set per use-case (drinking weights pathogens/health-risk far higher than irrigation). The app never reruns AHP.

**Step 2 — TOPSIS ranks the solutions (runtime, per location).**
For the queried site, build a decision matrix (solutions × criteria) from the site profile, apply the AHP weights, and score each solution by its closeness to the ideal-best / ideal-worst — a 0–1 closeness coefficient. Rank by it. That 0–1 score doubles as the match/confidence number shown to the user.

**Criteria** (the rich, full-vision set): treatment fit (removal vs the standard gap), health-risk reduction, site suitability (soil/climate/slope), stream order (dilution capacity), land footprint *(cost criterion)*, pollution-source pressure, and — if reached — cost and co-benefits. Each criterion is tagged **benefit** or **cost**; TOPSIS normalization handles the mixed units, so raw measured values go in and the cost/benefit flag handles direction.

**Enhancements:**
- **Fuzzy** (Fuzzy-AHP / Fuzzy-TOPSIS) — carries the ranges in `removal_efficiency` through the math instead of forcing crisp numbers. Add once the crisp version works.
- **Sensitivity analysis** — vary the weights, show the top recommendation holds. The rigor stamp for the paper. One-off study, not runtime.
- **ANFIS** — ⏳ future work only. Needs a labelled training set (site → known-best solution) that does not exist yet, and is a black box that fights the traceability ethos.

Return a **per-criterion breakdown + closeness score + citations** — never a bare number.

### 4.3 API & frontend

- **API (FastAPI):** keep endpoints; enrich responses with reasoning, citations, and confidence. Optional `/basin/{id}` context endpoint.
- **Frontend (Flutter):** do **not** rebuild. Surface the new fields (reasoning, citations, confidence) in existing screens. A basin map is the optional stretch.

### 4.4 Tools

| Purpose | Tool |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Pandas (FuzzyWuzzy retired) |
| Database | PostgreSQL — Azure PostgreSQL Flexible Server |
| Frontend | Flutter 3.x / Dart |
| Hosting | Microsoft Azure (App Service + PostgreSQL) |
| Build + docs | Claude Code (engineering), Claude Cowork + Notion (daily journal → report + paper), git |
| One-time data prep | QGIS or India-WRIS WebGIS for the district↔basin lookup (not a runtime dependency) |
| Monitoring | UptimeRobot (planned) |

### 4.5 Build approach — evolve, don't rebuild (LOCKED)

**Default to evolving the existing MVP in place. Do NOT start a from-scratch rewrite.**

The stack (FastAPI + PostgreSQL + Flutter on Azure) is sound for this goal, so there is no architectural reason to restart. The plan already rebuilds the parts that carry the contribution — the data model and the scoring engine — and reuses the solved, debugged plumbing (app scaffolding, DB connection, routing, screens, deployment). That is surgical reuse, not laziness, and it keeps a working system running the whole month so scarce time goes to the science (removal matrix, basin data, validation), not to re-solving solved problems.

Rules:
- **Refactor aggressively, in the existing repo.** Gut and rewrite `recommendation_utils` entirely, redesign the schema with migrations, restructure modules, delete dead code — all while keeping the app runnable.
- **Rewrite a module only when it earns it.** If a specific module is genuinely unworkable (undocumented spaghetti, fighting every change), rewrite that one module. This is a per-module call made with the code in hand — never a blanket "rebuild everything."
- **"Done nicely" = clean schema + sourced data + defensible logic + documentation.** It is not "typed fresh." A clean data layer on reused plumbing is a properly-built system.
- **A clean fork is optional and cosmetic** — only for narrative separation between the old MVP and the research tool. If chosen, copy the plumbing over and do all new work in the fork; same effort, cleaner git history, no technical gain.

> Note for Claude Code: seeing messy code is a reason to refactor that part, not a license to restart the project.

---

## 5. Data sources, depth & licensing

Deep where it counts (one basin: spatial, water-quality, soil, standards), basic-but-documented everywhere else.

| Dataset | Source | Depth | License / use rule | Status |
|---|---|---|---|---|
| Basin / sub-basin boundaries | India-WRIS (CWC + ISRO), River Basin Atlas | Deep, authoritative | GODL-India — attribution | 🔧 pull once |
| Water quality (the input) | CPCB + India-WRIS water-quality sub-system | Deep — multi-year | GODL / portal terms (verify) | 🔧 real station data |
| Soil | NBSS&LUP | Deep — national survey | Verify portal terms | 🔧 basin districts |
| Climate / rainfall | IMD | Deep | Verify terms | 🔧 basin |
| Treatment standards | BIS (IS 10500) + CPCB norms | Authoritative, exact | Cite values (facts); do NOT republish the standard text | 🔧 standards table |
| Removal efficiencies | Peer-reviewed literature + Nat4Wat | Moderate–deep, ranges | Cite facts + primary papers; do NOT copy their DB or images | 🔧 efficiency matrix |
| Solutions / plants / steps | Existing CSVs + literature | Currently shallow | Own data; clean + add citations | ✅ clean |

India-WRIS is unusually rich: it carries multi-decade attribute data per theme, with unclassified CWC station data and CGWB groundwater data free to download.

---

## 6. What we have vs what we need (gap analysis)

Benchmarked against Nat4Wat, whose per-solution model is: treatment capability per pollutant + cost + operational requirements + co-benefits + market cases + scientific publications.

**✅ We already have (keep these — the last three are our edge):**
- Water-type contaminant profiles (4 types × 12 parameters)
- Native plant catalogue (15 India species with pollution tolerance + ecological role) — *Nat4Wat does not have this*
- Step-by-step implementation + maintenance per solution — *Nat4Wat does not have this*
- India-specific solutions (East Kolkata Wetlands, staircase wetlands, vermifiltration, DEWATS) — *Nat4Wat does not have these*
- Basic climate / location / soil suitability tags

**🔧 We need (acquisition priority order):**
1. **Per-pollutant removal / treatment matrix** — the missing bridge between the water problem and the solution. *Highest-leverage task.* Take + cite from Nat4Wat's primary literature.
2. **Plant↔solution mapping** — which species belong in which solution.
3. **Use-case target standards** — defines "clean enough."
4. **Real basin water observations** + real basin soil & rainfall.
5. Per-solution **citations** (provenance).
6. Structured **co-benefits / operational constraints**, **footprint** (if time).

**Key insight:** we have the two ends (a water problem with the right parameters, and a solution list) and are missing the middle (which solution treats which pollutant, how well). Filling that one matrix is what makes the engine work.

---

## 7. Legal / data-use rules

*Not legal advice — verify each portal's terms; licenses change. But for cited academic research, this is the protected, normal use case.*

- **Indian government data (India-WRIS, CGWB, CPCB, anything via data.gov.in):** Government Open Data License – India (GODL). Grants royalty-free use, adaptation, and derivative works for commercial and non-commercial use — **requires attribution** (provider, source, URL/DOI). Excludes personal/sensitive data and official logos.
- **BIS standards:** the standard *document* is copyrighted — do not republish it. Threshold *values* are facts — cite them ("per IS 10500, limit for X is Y").
- **Nat4Wat:** European, possibly share-alike (ODbL) and EU database right. Extract individual *factual values*, cite the **primary papers** behind them (cleaner legally and academically), and never copy their database wholesale, their text, their illustrations, or their branding.
- **Peer-reviewed papers:** cite facts and figures; do not reproduce whole figures, tables, or paragraphs.
- **The `sources` table is the safety net** — provider + license + URL on every value satisfies attribution automatically and proves provenance.

---

## 8. Known gaps / loopholes to resolve

| Gap | Resolution |
|---|---|
| Plant–solution disconnect | Add `plant_solution_map` (§4.1) |
| Input model conflates source-type with chemistry | Two modes: measured parameters preferred, water-type typology as fallback; engine runs on parameters-vs-standard |
| No target standard = "clean enough" undefined | ❓ Pick use-case with supervisor (the unlock) |
| Solution granularity vs actionability (10 broad buckets) | ❓ Decide: keep broad, or split at least the wetland family |
| Soil-vocabulary mismatch across tables | Reconcile to one controlled list during data hygiene |
| No field validation possible in a month | Face validity (supervisor) + literature consistency + back-test known cases (e.g., does it recommend wetlands for an East-Kolkata-type situation?); state as a named limitation |
| Confidence representation | Simple scheme: high = measured data + sourced efficiency; low = state-level fallback / missing data |
| Seasonal variation (monsoon) | Use a representative value or flag seasonality |

---

## 9. Scope tiers — full vision, built in priority order

**Decision: aim for the full vision.** The protection against overreach is *build order*, not cutting features — finish each layer completely before starting the next, so any cutoff still leaves a whole working tool at the layer reached.

**Layer 1 — Core (must be complete and runnable first):** location-first lookup · water / soil / rainfall · removal matrix · plant↔solution map · use-case standard · AHP weights + TOPSIS ranking · reasoning + citations + confidence · data hygiene.

**Layer 2 — Site-profile depth (the supervisor's additions):** slope/elevation · stream order · LULC (%agri, %builtup) · pollution-source identification · **health risk (carcinogenic + non-carcinogenic — data in hand, in scope)** · river-path map view.

**Layer 3 — Method depth & rigor:** Fuzzy-AHP / Fuzzy-TOPSIS · sensitivity analysis · entropy weighting as an objective cross-check · co-benefits scoring · footprint as a cost criterion.

**Layer 4 — ⏳ Stretch / future work:** cost estimation · treatment-train logic (pond → wetland sequences) · ANFIS (needs a training set that doesn't exist yet) · second contrasting basin · PDF report export · user-contribution mechanism.

> Build downward only when the layer above is finished. "God's hands" still leaves a complete tool at whatever layer you reached.

---

## 10. Four-week plan

| Week | Focus |
|---|---|
| **1** | Confirm scope with supervisor (the 3 questions, §11) — basin already locked to Narmada, verify data access. Data hygiene: dedup, normalize dirty water-type values, drop junk column, reconcile soil vocabulary. Stand up `sources` table. Build Narmada district↔basin map. |
| **2** | Ingest the slice: CPCB/WRIS water quality for the basin's stations, NBSS&LUP soil + IMD rainfall for its districts, BIS/CPCB standards for the chosen use-case — all with `source_id`. |
| **3** | Rebuild logic as documented MCDA with the cited removal-efficiency matrix + confidence scores; add `plant_solution_map`; expose reasoning + citations in the API. |
| **4** | Validate on the basin demonstration; write the internship report; draft the paper skeleton. **Keep this week half-empty on purpose — Week 2 always slips.** |

**Throughout:** append a dated entry to the Notion / DEVLOG every session (what changed, *why*, sources added, blockers). Never invent data or citations.

---

## 11. Decisions to confirm with the supervisor

1. **Use-case standard** — irrigation reuse, surface-water discharge, or drinking? *(Sets every threshold; unlocks most gaps.)*
2. **Narmada confirmation** — basin is locked to the Narmada (§2); confirm only that its water-quality/soil data is accessible, and that the lab doesn't already have a different basin's data worth reusing instead.
3. **Paper target** — conference / workshop / preprint, or full journal? *(Decides how much validation must fit in-window vs after.)*

---

## 12. Working conventions

1. **Provenance is mandatory.** Every row and rule carries a `source_id`.
2. **Never invent data.** No source → leave NULL and log it as a gap. Holds for anything generated, including by AI tools.
3. **Ranges, not false precision.** Removal efficiencies are ranges + confidence, never single fake numbers.
4. **Log as you go.** Daily DEVLOG / Notion entry — this is the report's methods trail.
5. **Smallest defensible change** over large rewrites. Don't over-engineer.

---

## 13. The contribution (paper angle)

Decision-support systems for nature-based water treatment already exist (Nat4Wat, the IWA/Corominas DSS, Poseidon). The category is established — so the contribution is **regional, applied, and integrative:** adapting the proven MCDM approach to the Indian context, and going beyond the comparators by fusing, in one basin-scale tool, (1) a location-first model where any point in the Narmada basin auto-resolves its full site profile — water quality, soil, slope, stream order, LULC, pollution sources; (2) a **health-risk layer** (carcinogenic + non-carcinogenic) feeding solution selection; (3) a native-species recommendation layer and India-specific solutions with implementation guidance; and (4) a transparent, expert-weighted **AHP–TOPSIS** engine with sensitivity analysis — none of which the existing European, solution-centric tools combine. Demonstrated on the Narmada with real observed data. Standing on the prior tools' shoulders (citing and positioning against them) is a strength in review, not a weakness. Output: a working tool, an internship report, and the draft of a co-authored paper finished after the internship on a normal academic timeline.

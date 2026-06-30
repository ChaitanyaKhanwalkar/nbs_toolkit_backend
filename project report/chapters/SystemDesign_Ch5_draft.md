# Chapter 5 — System Design and Implementation (draft)

> Tags: [author-voice approved] = built from author's reasoning & confirmed ·
> [factual-draft, review] = drafted from HANDOFF/DB for author review.
> Ch.5 = HOW it is built (kept deliberately separate from Ch.4, the WHAT, for clean paper extraction).
> Pairs with Figure 2 (architecture) and Figure 3 (provenance lineage).

---

## 5.1 Design Philosophy: A Layered, Foundation-First System  *[author-voice approved]*

The system was built in layers, from the bottom up, and the order was deliberate rather than incidental. The data is the base of everything: without it there is no application. The first task was therefore not to build software but to assemble the evidence — water quality across the Narmada basin, the catalogue of nature-based solutions, their removal efficiencies, the plants and their tolerances — and only once that evidence was collected and organised could it be made sense of. Every layer above rests on that base, and the strength of the whole structure is limited by the strength of its foundation.

Provenance is part of that foundation, not a layer added on top of it. A value and its source are collected together: each removal efficiency, each site attribute, each influent profile enters the database carrying the citation it came from and a record of how reliable it is. Where a value can be corroborated by a second independent source, the base does not gain a new component — it simply becomes more trustworthy at that point, and a more trustworthy base is a sounder thing to build on. Treating provenance as inseparable from the data is what allows everything above to be traced back to evidence rather than assertion.

Only once a layer was complete was the next one begun, and this discipline reflects a real dependency rather than a preference for tidiness. Each layer's design is constrained by the one beneath it: the recommendation engine cannot be sensibly designed until the shape of the data it will consume is fixed, and the interface cannot be designed until the engine's outputs exist. Building the layers in parallel, or from the top down, would mean repeatedly reworking upper layers every time the foundation shifted. Building bottom-up, against a settled foundation, lets each layer be designed once, against something stable — the principle of evolving the system rather than rebuilding it.

With the data and its provenance in place, the second major effort was the recommendation engine: how it would be designed, how its parts would interact, and how the methodology of Chapter 4 — screening, weighting, ranking — would be turned into working logic. The engine consumes the foundation and produces the recommendations; it is the layer where the framework's reasoning actually executes.

The final layer is the interface — the part of the system that the user interacts with. Its design carries a genuine tension: it must be scientific enough to present sourced, defensible recommendations, yet accessible enough that a wide range of users — not only specialists — can navigate it and understand what they are being told. Resolving that tension is also where the provenance principle reaches the user: the interface surfaces the sources behind a recommendation at the point of use, so that the traceability built into the foundation is visible at the surface rather than hidden in the backend.

---

## 5.2 The Data Layer: Canonical Database and Provenance Model  *[factual-draft, review]*

The foundation is a single canonical database (`narmada_nbs_canonical.db`) holding roughly 52 tables and 17 read views. It carries the full evidence base described in Chapter 3 — 28 NbS options, 167 removal-efficiency records (98 corroborated), 8 treatment trains, 47,244 ambient water-quality observations, the river network, and the site, soil, climate, and pollution-source layers — together with the controlled vocabulary and provenance machinery that make it production-grade rather than a flat collection of spreadsheets.

**Normalisation and controlled vocabulary.** Entities are normalised to foreign-key identifiers, and nine controlled-vocabulary dimension tables (`dim_parameter`, `dim_unit`, `dim_country`, `dim_scale`, `dim_confidence`, `dim_source_type`, `dim_nbs_family`, `dim_use_case`, `dim_provenance_status`) canonicalise terms that would otherwise fragment the data — for example collapsing parameter-name and casing variants (BOD5/BOD, COD casing) that would silently break joins. Redundant free-text columns were dropped after normalisation and are recoverable through read views (`v_removal`, `v_nbs_profile`, `v_plant_use`, `v_standards`, `v_train`, and the train-performance and use-case views), so downstream code reads stable, normalised relations rather than raw text.

**The provenance model, as implemented.** Provenance is realised by two structures. A `sources` table holds the 104 sources, each with its citation, URL, licence, and source type. A field-level `column_provenance` ledger (324 records) then records, for individual values, the table and column they occupy, the source identifier(s) behind them, and a provenance status drawn from `dim_provenance_status`. That status takes one of three implemented values — **sourced**, **derived_rule** (transformed by an explicit rule), or **derived_heuristic** (estimated) — which is the concrete, implemented form of the conceptual cited/derived/gap model of Chapter 4; disclosed gaps appear as the deliberate absence of a value rather than a fabricated entry. A separate five-level confidence vocabulary (`dim_confidence`: high, medium, low, variable, insufficient-data) carries the strength of evidence behind a value, kept distinct from the value itself.

**Integrity, and the two-database arrangement.** Referential integrity is expressed differently in the two deployment targets, by design (Section 5.5). The production PostgreSQL schema (`schema_pg.sql`) enforces relationships with foreign-key constraints and CHECK constraints (for example, efficiency bounded to 0–100, low ≤ high, invasive flag binary). The SQLite working mirror carries the same relationships as keyed columns plus the `column_provenance` ledger, with integrity maintained by build-time validation (row-count parity checks and integrity checks were run at each merge) rather than by runtime foreign-key enforcement. This keeps the working mirror lightweight for development while the production database enforces the constraints formally.

> REVIEW NOTE: `HANDOFF.md` and `DATA_DICTIONARY_canonical.md` describe the canonical DB as having "enforced foreign keys." The shipped SQLite file has FK enforcement off and no FK constraints defined — relationships are logical (via `source_ids`/keyed columns + provenance ledger), and the enforced FK/CHECK constraints live in `schema_pg.sql`. Reconcile this wording in the HANDOFF, and confirm `schema_pg.sql` is current (it must be regenerated to the present ~52-table count before Azure deployment — it presently reflects an older 27-table schema). Exact table/view counts (52/17 here vs 48/16 in the data dictionary) should also be reconciled before final.

---

## 5.3 The Recommendation Engine  *[factual-draft, review]*

The engine is the layer where the methodology of Chapter 4 becomes executable logic. It is organised as a **screen-then-rank pipeline** over the canonical data, and it does not store a precomputed answer: the decision matrix is assembled at runtime from the current data and weights, so the recommendation always reflects the live evidence base.

**Screening.** Candidate trains first pass through the applicability layer of 46 rules (Section 4.5): hard filters and hard safety filters remove infeasible or unsafe options outright (for example, infiltration systems on low-infiltration soil, or industrial/biomedical sources requiring pretreatment), while conditional filters, scoring modifiers, and confidence modifiers gate, adjust, or down-weight the survivors. Only feasible, safe trains reach the ranking.

**Weighting and ranking.** Criteria weights are derived by AHP and are use-case-specific (discharge, irrigation, drinking), with consistency-ratio checks (Section 4.4); a Fuzzy-AHP variant is computed as a robustness confirmation. The surviving trains are then ranked by TOPSIS over the seven active criteria, treating benefit and cost criteria appropriately, to produce a closeness-coefficient ordering.

**Train-level performance.** Because the framework recommends trains rather than single units (Section 4.3), per-train performance is computed by multiplicative chaining of the constituent stages' removal efficiencies (`train_performance`, 40 records), and the resulting effluent is matched against use-case standards (`train_usecase_match`, 64 records; surfaced through `v_train_performance`, `v_train_usecase`, and `v_engine_usecase_matrix`). The engine reads all normalised inputs through the read views rather than raw tables, so a change in the data foundation propagates without code changes.

> REVIEW NOTE (known, documented limitations to state plainly): (i) a `criteria_weights` table may be absent from the canonical DB, in which case `match_score` can return `None` silently rather than falling back to equal weighting — the documented fix is to wire a `use_default_weights` fallback; (ii) the C1 criterion is implemented as severity-weighted pollutant-gap closure, not the flat average-removal proxy; (iii) missing removal data must be treated as a disclosed gap, never as 0% removal (the corrected behaviour — see Ch.6). These are implementation caveats to disclose, consistent with the provenance ethos, not to hide.

---

## 5.4 The Application Layer  *[factual-draft, review]*

The application exposes the engine to users through a **FastAPI** backend and a **Flutter** front end. The backend serves the engine's outputs and the underlying evidence over an API; the front end presents them as a navigable interface across web, mobile, and desktop.

A dedicated application layer in the database (six `app_*` tables and nine `v_app_*` views) shapes the engine's relational outputs into user-facing material: location profiles, NbS and plant catalogue cards, train cards, use-case summaries, an upload template for user water-quality data, map layers, and an open-caveats view. A district profile cache (`app_district_profile_cache`, 45 districts) provides fast location lookup. Critically — and as the design philosophy requires — the sources behind a recommendation are surfaced at the point of use through these views, so the traceability built into the foundation is visible to the user rather than buried in the backend. Parameter aliases (`app_parameter_aliases`) reconcile the varied names users give to the same water-quality parameter, part of keeping the interface accessible without sacrificing scientific precision.

> REVIEW NOTE: confirm the current front-end/back-end feature set against the live app before final (this section is drawn from the database app-layer and HANDOFF, not from a code audit). Two honesty-related items flagged in project notes to verify in the running UI: the provisional-weights disclosure label (it must be visible per the supervisor-gated honesty rule), and the `use_default_weights` flag wiring.

---

## 5.5 Deployment: Working Mirror and Production Target  *[factual-draft, review]*

The system uses two databases by design. Development runs against a **SQLite working mirror** (`narmada_nbs_canonical.db`) — a single portable file that is fast to query, easy to validate, and convenient to move between the parallel work streams of the project. Production targets **Azure PostgreSQL**, for which a PostgreSQL DDL (`schema_pg.sql`) defines the formally constrained schema (foreign-key, CHECK, and unique constraints). The two are kept in correspondence: the SQLite mirror is the evolving working copy, and the PostgreSQL schema is the deployment target that enforces the constraints the mirror maintains by validation.

This split is the deployment expression of the same foundation-first philosophy: the working mirror lets the data and engine layers be developed and revalidated quickly, while the production schema imposes formal integrity for the deployed application.

> REVIEW NOTE: `schema_pg.sql` is stale — it reflects an older 27-table schema and must be regenerated from the current canonical DB (~52 tables) before Azure deployment. PostgreSQL hardening is deprioritised in project notes until the website is fully stabilised; state deployment status accurately for the report's snapshot date.

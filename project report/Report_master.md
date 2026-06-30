# Narmada NbS Planner — REPORT MASTER
**Development of a Decision Support Framework for Selection of Nature-Based Solutions for Wastewater Management in the Narmada Basin**

> Single running document. Chapters appear in report order; pending chapters are noted.
> Last assembled: 2026-06-26.
> Status: **Chapters 1, 3, 4, 5, 7, 8 drafted.** Pending: Ch.2 (Lit Review — parallel chat, Elicit),
> Ch.6 (Results — gated on live-engine numbers), Ch.9 (Conclusion — follows 6/7). NOTE: Ch.7 arguments are shape-stable; number-claims tagged [reconcile w/ live engine].
>
> Tag key — [author-voice approved] / [author-derived from locked material, review] = author's reasoning ·
> [factual-draft, review] = drafted from data/report for review · [CITE] = pin in Zotero.
>
> PARKED CITATIONS: [CITE: groundwater stress — CGWB] (§3.1) · [CITE: CPCB Priority IV] (§3.1) · [CITE: Kalbar, Karmakar & Asolekar] (§4.2.1)
>
> KEY REVIEW NOTES carried in-file:
> - §3.2 source table: confirm vs canonical `sources`; pin in Zotero.
> - §3.3 numbers trace to cNarmada & cGanga (2024) — spot-check.
> - Ch.4 §§4.4–4.6 await author-voice pass.
> - Ch.5: "enforced FK" wording — true only for PostgreSQL production, NOT the SQLite mirror; reconcile HANDOFF. `schema_pg.sql` stale (regenerate before Azure).
> - Ch.6 Khandwa decimals DB-reconstructed — reconcile with live engine before writing 6/7/9.
> - Ch.8 weights: only upgrade to "expert-validated" if explicit approval documentation is recorded before submission.

---

# CHAPTER 1 — INTRODUCTION

# Chapter 1 — Introduction (draft)

> [author-derived from locked material, review] — assembled from the locked contribution statement,
> the four pillars, and the §3.1 basin argument. Framework-first framing (the contribution is the
> framework; the Narmada is its demonstration testbed). Written to be revised in the author's voice.

---

## 1.1 Background and Motivation

Untreated and inadequately treated wastewater remains one of the most pervasive threats to water quality in India, particularly across the many small and medium towns that lack the centralised treatment infrastructure of large cities. Where conventional mechanised treatment is costly to build, power-hungry, and difficult to operate and maintain, **nature-based solutions** (NbS) — constructed wetlands, pond systems, and related technologies that recruit natural processes to treat water — offer a low-energy, low-maintenance, and locally appropriate alternative. Their promise is greatest precisely where the need is greatest: dispersed settlements, limited operating capacity, and constrained budgets.

That promise, however, is not self-executing. Choosing the right nature-based solution for a given place is a genuinely difficult decision. NbS are diverse, each suited to particular pollutants, particular site conditions, and particular operating regimes; their performance depends on local soil, climate, and hydrology in ways that a concrete treatment plant does not; and no single NbS unit typically treats wastewater fully on its own. Selecting and configuring them well therefore requires reconciling many factors at once — treatment performance, site feasibility, pollution source, and operating burden — against evidence that is scattered across the literature and rarely assembled in one place. This is a multi-criteria decision problem, and it is the problem this work addresses.

## 1.2 The Gap in Existing Approaches

Existing tools for selecting nature-based solutions tend to recommend treatment options generically. They do not resolve their recommendations to local site conditions, to the ambient quality of the receiving water, or to the type of pollution source being treated; and they typically recommend single technologies, which on their own cannot bring real, mixed wastewater to a usable standard. The result is advice that is hard to act on: a practitioner is told *what* might work in general, but not whether it fits *this* site, *this* source, or whether it will actually complete the treatment.

Three weaknesses recur. Recommendations are not **location-specific** — the soil, slope, climate, and river position that determine whether a natural treatment process will function are not brought into the decision. Recommendations are not **source-aware** — the contaminant profile of domestic, industrial, and agricultural wastewater differs sharply, yet the same options are offered regardless. And recommendations are made at the level of **single units** rather than complete treatment sequences, even though real wastewater carries many contaminants at once and no single unit removes them all. Underlying all three is a quieter problem of **evidence**: the values behind a recommendation are often unsourced, so a user cannot tell where a number came from or how far to trust it.

## 1.3 Aim and Contribution

The contribution of this work is a decision-support framework that addresses these gaps directly. The framework is the publishable contribution; the Narmada basin is the setting in which it is developed and demonstrated, not the limit of its applicability.

Stated in full: this work develops a **location-specific, provenance-first decision-support framework** for the selection of nature-based solutions for wastewater management, which screens candidate solutions by pollution source, conditions its recommendations on local data (soil, climate, rainfall, slope, and stream order), and recommends complete **treatment trains** rather than isolated units — with every value behind a recommendation traceable to a cited source.

The framework rests on four design commitments, which also serve as the objectives of the work:

- **P1 — Location-specific.** Recommendations are conditioned on the physical conditions that determine whether a natural treatment process will function at a site: soil, slope, climate, rainfall, and stream order.
- **P2 — Provenance-first.** Every value carries its source and a record of its reliability; missing data is disclosed as a gap rather than filled with a guess, and the traceability is surfaced to the user.
- **P3 — Source-aware.** Candidate solutions are screened against the dominant pollution source — domestic, industrial, or agricultural — because the source determines the contaminant profile to be treated.
- **P4 — Treatment trains.** The framework recommends complete, staged treatment sequences (pretreatment → secondary → polishing) rather than single units, so that recommendations can treat wastewater end-to-end.

Methodologically, the framework operationalises these commitments through a screen-then-rank decision pipeline that combines applicability filtering, the Analytic Hierarchy Process (AHP) for criteria weighting, and the Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS) for ranking, over a provenance-tracked evidence base.

## 1.4 Scope and Demonstration

The framework is demonstrated on the Narmada basin in central India — a setting whose dominant wastewater pressure is distributed domestic sewage from many small and medium towns, which makes it well matched to decentralised, source-screened, location-specific NbS recommendation (Chapter 3). The demonstration focuses on the discharge-to-river use-case and a representative district, and exercises the full pipeline from evidence base to ranked recommendation. The scope of the present work is the framework and its demonstration; field deployment of recommended systems, and the basin-specific performance data such deployment would generate, lie beyond it (Chapter 8).

## 1.5 Structure of the Report

The report is organised as follows. **Chapter 2** reviews related work on nature-based solutions and on multi-criteria decision-making for wastewater technology selection, and locates the contribution within it. **Chapter 3** describes the study area and the data the framework stands on — why the Narmada basin is an apt test case, why each local data layer earns its place, and the physical setting of the basin. **Chapter 4** sets out the methodology: the provenance model, the criteria and their weighting, the treatment-train logic, and the AHP–TOPSIS decision procedure. **Chapter 5** describes how the framework is built as a system — the canonical database, the recommendation engine, the application layer, and the deployment arrangement. **Chapter 6** presents the demonstration and its results, including a sensitivity analysis of the ranking. **Chapter 7** discusses what the results mean and how they should be read. **Chapter 8** states the limitations of the framework and of the present demonstration, and sets out the future scope. **Chapter 9** concludes.



---

# CHAPTER 3 — STUDY AREA AND DATA

# Section 3.1 — The Narmada Basin as a Test Case (draft)

> [author-voice approved] — built from Eco Soul's reasoning, evidenced from cNarmada & cGanga (2024).
> Parked citations: [CITE: groundwater stress — CGWB/state report], [CITE: CPCB Priority IV].

---

## 3.1 The Narmada Basin as a Test Case

The Narmada is the fifth-longest river in India and the longest of its west-flowing rivers, and the largest river in Madhya Pradesh — bound so tightly to the state that it is commonly called its lifeline (cNarmada & cGanga, 2024). Its basin covers roughly 95,960 km², close to 3% of India's land area, of which nearly 89% lies within Madhya Pradesh. It is, before anything else, a central-Indian and a Madhya Pradesh river. The basin holds about 61 million people (2011 Census) and is a crucial source of water for irrigation, drinking, and hydropower across Madhya Pradesh and Gujarat — its water carried even to drought-prone parts of Gujarat and Rajasthan. Its condition is therefore not an isolated environmental question; it bears directly on the water security of tens of millions of people.

That dependence is growing. As industrialisation and development across the basin accelerate, the pollution load on the river rises with them; at the same time, deepening groundwater stress in the surrounding region pushes more communities back onto the Narmada as their dependable source [CITE: groundwater stress — CGWB/state report]. The river is being asked to give more even as it is put under more pressure, which makes keeping it clean enough to meet those demands an urgent problem now, not a future one.

Crucially, the dominant pressure on the Narmada is not heavy industry but untreated domestic sewage. In every segment of the river, untreated sewage discharged from the towns and cities along its banks is named as a leading source of pollution (cNarmada & cGanga, 2024); Madhya Pradesh alone is estimated to release on the order of 51 million litres per day of untreated sewage directly into the river. Industrial effluent — heavy metals and chemicals from paper, chemical, and textile units — is a real but spatially concentrated problem, confined to specific corridors such as those near Jabalpur, Itarsi, Barwani, Bharuch, and Ankleshwar rather than a basin-wide one; agricultural pollution enters more diffusely, as fertiliser and pesticide runoff. The basin-wide signature of the problem is thus domestic: organic load and pathogens from the sewage of many small and medium towns spread all along the river, not a handful of large point sources.

The river is also still recoverable. Water quality remains acceptable in the upper reaches and degrades progressively downstream (cNarmada & cGanga, 2024) — the Narmada is under growing strain but not yet past the point of return. This shapes what kind of intervention fits: the right treatment, placed in the right locations now, can hold the line rather than having to reverse a collapse. [Optional strengthening, source later: CPCB Priority-IV "relatively clean" classification — CITE: CPCB.]

This combination is what makes the Narmada basin an apt test case for the framework developed here. A problem that is distributed — untreated domestic sewage arising town by town across a very large basin — is poorly matched to a few pieces of large centralised infrastructure, but well matched to decentralised treatment deployed at the scale of individual towns. Nature-based solutions suit exactly that scale: implemented as small-to-medium systems sited at the many sewage sources along the basin, offering treatment that is natural and low-maintenance, and therefore durable where operational capacity is limited. The fit between the basin's dominant pressure — distributed domestic sewage — and the solution class this framework recommends — decentralised NbS treatment trains, screened by source and conditioned on local conditions — is the reason the Narmada is not merely a convenient setting for this work but the right one.


---

# Section 3.2 — Study Area Data and Sources (draft)

> Tags: [author-voice approved] = built from Eco Soul's reasoning and confirmed;
> [factual-draft, review] = mechanism/data drafted for review.
> Parked citations: [CITE: groundwater stress — CGWB/state report] (in 3.1), [CITE: CPCB Priority IV] (in 3.1).
> Pairs with the data-source table (Table 3.x) below.

---

## 3.2 Study Area Data and Sources

### 3.2.1 Why these data layers  *[author-voice approved]*

The framework recommends nature-based solutions, and nature-based solutions are exactly what the name implies — they recruit a natural process to do the treatment. A conventional treatment plant imposes treatment on the water through engineered machinery, and the same concrete tank can be dropped into almost any site. A nature-based solution instead relies on a natural mechanism — a plant's growth and uptake, a soil's capacity to infiltrate, a microbial community's metabolism — and natural mechanisms are conditional: they only run if the local conditions allow them. Every solution in this framework involves phytoremediation as part of its treatment process, using plants to draw contaminants out of the wastewater, and those plants must fit the climatic and physical conditions of the place where the system is built.

This is the principle that decides which data the framework needs. A data layer earns its place only if it changes whether the natural process will work at a given site; a layer that does not change a decision is decoration, not evidence. On that test, four local layers are load-bearing — soil, stream order, pollution source, and climate — and each is included because it changes a specific decision in the recommendation, not because it makes the analysis look thorough.

### 3.2.2 Soil  *[author-voice approved + mechanism]*

**Soil decides whether an entire infiltration-based class of solutions is admitted or hard-filtered out before ranking.** Soil acts on a nature-based system in two ways. First, it is the growth medium: the wetland and pond species the framework relies on (for example Typha, Phragmites, Canna) have texture and pH preferences, and the soil governs the moisture and nutrients reaching the root zone — if it is wrong for the planting, the phytoremediation engine stalls. Second, and more decisively, soil controls infiltration. A whole class of solutions — soak pits, leach fields, infiltration trenches, bioretention — works by letting water percolate into the ground, which is only possible where the soil actually permits it. On clay or low-infiltration soils, percolation-based systems do not merely underperform; they fail, and can cause ponding or groundwater contamination. For that reason soil is not a scoring nicety but a hard filter: where infiltration capacity is absent, an entire NbS class is removed from consideration before any ranking occurs. Soil therefore decides not only how well a system performs, but whether it is allowed at all.

### 3.2.3 Stream order  *[author-voice approved + mechanism]*

**Stream order decides whether the system is placed in-channel or off-channel, and the scale at which it is planned.** Strahler stream order is a proxy for the size, discharge, and assimilative capacity of the river at a given point, and it governs the recommendation in three ways. It sets placement: low-order headwater streams are small and easily dominated by a discharge, while high-order reaches carry large flows where in-channel intervention is impractical and treatment belongs off-channel, intercepting the sewage before it reaches the main river. It sets the dilution and assimilative context: a larger stream dilutes a given effluent load more, which changes how strict the effluent must be to protect the receiving water — the hydrologic side of the standard-fit logic. And it sets scale: stream order is the variable that distinguishes a small decentralised unit serving a headwater town from the larger or differently-sited system a high-order reach requires. Stream order is thus a driver of the recommendation, not a descriptor of the site; resolving recommendations to it is part of what makes this framework location-specific.

### 3.2.4 Pollution source  *[author-voice approved + mechanism]*

**Pollution source screens out solutions unfit for that source's contaminant profile, demoting them in the ranking — and, for industrial or biomedical sources, triggers a hard safety filter.** The source of the wastewater determines its contaminant profile, and nature-based solutions are contaminant-selective: no single unit removes everything, which is the same fact that forces treatment trains rather than single units. The framework therefore matches source to contaminant profile to the treatment chemistry that addresses it. Domestic sewage carries high BOD, pathogens, and nutrients — the regime constructed wetlands and pond systems are built for, and the dominant load in this basin. Industrial effluent carries heavy metals and recalcitrant chemicals, requires pretreatment, and is screened differently, with an NbS train alone not credited to treat it — which is why source is not only a scoring input but a hard safety filter. Agricultural runoff is a nutrient problem, dominated by nitrate and fertiliser-derived chemicals, different again. Matching source to solution is not a refinement applied after the recommendation; it is the screening step that makes the recommendation safe and relevant.

### 3.2.5 Climate  *[author-voice approved + honesty framing]*

**Climate decides which plant species are viable, and therefore which plant-dependent solutions can be recommended at all.** Temperature and rainfall govern the biology the treatment depends on: microbial and plant metabolism — nitrification in particular — slows in cold conditions, plant water-demand and temperature tolerance decide which species establish locally, and rainfall and evapotranspiration shift the hydraulic load and water balance a system must handle. The Narmada basin is humid and tropical, which is favourable for plant-based treatment but imposes a strongly seasonal, monsoon-driven load that systems must accommodate.

It is worth being precise about how climate operates here. Because the whole basin lies within one broad climate zone, climate does not discriminate between sites within the study area — every district receives a similar climate signal, so at basin scale climate functions as a viability gate that fixes the feasible plant palette for the basin as a whole (it is why the framework draws on Typha, Canna, and Phragmites rather than temperate species) rather than as a site-by-site differentiator. The layer is nonetheless built into the framework as a discriminating input: when the framework is applied beyond this basin, to regions with different or more varied climates, climate becomes an active differentiator between sites — so it is load-bearing for the generality of the framework even where it is near-constant for this basin.

### 3.2.6 The data behind each layer  *[factual-draft, review]*

Each layer above is backed by a sourced dataset, and every value carries its provenance. The site-resolved physical layers are held at the resolution of 52 study sites: soil and climate attributes (soil type, hydrologic soil group, infiltration class, sand/silt/clay fractions, soil depth, annual rainfall, temperature range, aridity, and potential evapotranspiration) are stored per site, and the hydrologic attributes (Strahler stream order, natural discharge, and a dilution proxy) are populated for all 52 sites. The receiving-water layer — 47,244 ambient water-quality observations across the basin's monitored stations and seasons — provides the discharge and effluent-target context. Pollution sources (155 records) and influent water-type profiles (48) supply the source and contaminant-profile layer. The river network is represented by 6,339 reaches carrying true Strahler order. These location layers are what allow recommendations to be conditioned on local conditions rather than issued generically.

Provenance is enforced structurally rather than by intention: every value is tied by a foreign key to a catalogue of 104 sources, and a field-level provenance table (324 records) records, for each value, its source and its status (cited/corroborated, derived, or disclosed gap). The principal sources for the study-area layers are summarised in Table 3.x.

**Table 3.x — Principal data sources for the study-area layers**

| Layer | What it provides | Principal source(s) | Records |
|---|---|---|---|
| Ambient water quality | Receiving-water / effluent-target, seasonal discharge | CWC (seasonal ambient WQ, via WCSL lab) | 47,244 |
| River network & stream order | Strahler order, reach hydrology | HydroRIVERS | 6,339 reaches |
| Site physical attributes | Slope, elevation, land-cover fractions, discharge, dilution | CAMELS-IND; HydroRIVERS; derived | 52 sites |
| Soil & climate | Soil type, infiltration class, texture, rainfall, temperature, aridity, PET | NBSS&LUP (soil); IMD (climate); CAMELS-IND | 52 sites |
| Pollution sources | Point/diffuse sources, dominant source type | CPCB; NRCD Narmada reports (cNarmada & cGanga) | 155 |
| Influent profiles | Contaminant profile by water type | Literature + CPHEEO | 48 |
| District context | Basin-resolved district profiles | Report-mining (cNarmada & cGanga 2024) | 45 |
| NbS evidence base | Removal efficiency, footprint, design | Dotro 2017; von Sperling 2007; DEWATS; CPHEEO; UASB literature | 167 removal / 19 footprint |
| Provenance ledger | Field-level source + status for every value | (internal provenance model) | 324 |

> NOTE for review: source attributions in the table's "Principal source(s)" column are drawn from the data-sourcing log; confirm each against the canonical `sources` catalogue and pin in Zotero before the table is final. The CAMELS-IND / NBSS&LUP / IMD split for the 52-site soil-climate layer should be verified against `regions.source_climate_soil` and `regions.source_district`.


---

# Section 3.3 — Physical Setting of the Basin (draft)

> [factual-draft, review] — descriptive backdrop, drawn from cNarmada & cGanga (2024),
> *Narmada River at a Glance*, NRCD, Ministry of Jal Shakti, Government of India.
> All numeric values in this section trace to that report unless otherwise noted.

---

## 3.3 Physical Setting of the Basin

### 3.3.1 Location and course

The Narmada is the fifth-longest river in India and the longest of its westward-flowing rivers. It rises from the Amarkantak Plateau in the Anuppur district of Madhya Pradesh and flows roughly 1,312 km westward before discharging into the Arabian Sea through the Gulf of Khambhat, about 30 km west of Bharuch in Gujarat. The basin covers 95,959.70 km² — close to 3% of India's land area — and has a markedly elongated form, extending about 915.65 km east to west but only 236 km north to south. Its annual water potential is 45.65 billion cubic metres (BCM), of which 34.50 BCM (75.57%) is considered utilisable (cNarmada & cGanga, 2024).

The river is conventionally divided into three segments on geomorphological grounds, and the framework treats them as physically distinct settings: the **Upper Narmada** (Amarkantak to Hoshangabad, ≈720 km), the **Middle Narmada** (Hoshangabad to Navagam, ≈485 km), and the **Lower Narmada** (Navagam to the Gulf of Khambhat, ≈145 km). The drainage network comprises 19 major tributaries (41 in total), the Tawa being the largest sub-basin.

### 3.3.2 Administrative spread and population

The basin holds 61,243,103 people (2011 Census) and spreads over 40 districts across four states — 27 in Madhya Pradesh, seven in Gujarat, four in Chhattisgarh, and two in Maharashtra. It is overwhelmingly a Madhya Pradesh basin: about 89.3% of the basin area lies in Madhya Pradesh, with 8.2% in Gujarat, 1.8% in Maharashtra, and 0.8% in Chhattisgarh (cNarmada & cGanga, 2024). This concentration is why the river is described as the lifeline of Madhya Pradesh and central India, and why the demonstration in this work is sited in Madhya Pradesh.

### 3.3.3 Topography and slope

The basin spans five physiographic zones, from upper hilly areas through upper and middle plains to lower hilly areas and the lower coastal plain. Mean basin elevation is 355.60 m, the highest point reaches 1,261 m, and the largest share of the basin (27.26%) lies in the 200–300 m elevation band. The terrain is mostly flat: nearly level and very gently sloping land dominates the central and northern basin — large tracts suited to cultivation — while strongly sloping and steep terrain is confined to the southern and eastern edges (cNarmada & cGanga, 2024). This gentle central topography is relevant to the framework because slope is one of the site constraints on where a given solution can be placed.

### 3.3.4 Soil

Soil across the basin is predominantly clay loam in the central and most extensive parts, grading to loam in the eastern and south-eastern regions, with pockets of clay in the north-eastern and south-western extremities and sandy clay loam along the north-western fringes (cNarmada & cGanga, 2024). This distribution matters directly to the recommendation: the heavy clay and clay-loam soils that dominate much of the basin are low-infiltration soils, which — as Section 3.2 sets out — hard-filter the percolation-based class of solutions out of consideration at such sites.

### 3.3.5 Climate and rainfall

The basin has a humid, tropical climate, crossed by the Tropic of Cancer in its upper plains, with four distinct seasons (cold, hot, south-west monsoon, and post-monsoon). Mean annual temperature ranges from 24.92 °C to 27.39 °C across the basin, and mean annual rainfall over 1970–2023 is 1,104.59 mm, with no clear long-term increasing or decreasing trend. Rainfall is heaviest in the upper hilly and upper-plains areas of the north-east and decreases westward toward the lower plains (cNarmada & cGanga, 2024). As Section 3.2 notes, this broadly uniform humid-tropical regime is favourable for plant-based treatment but imposes a strongly seasonal, monsoon-driven hydraulic load.

### 3.3.6 Land use and land cover

The basin is predominantly agricultural. The 2021 land-cover assessment gives cropland as 57.47% of the basin, followed by tree cover (17.01%) and grassland (16.30%); built-up land is a small fraction (0.95%), with the remainder in bare/sparse vegetation (3.77%), permanent water bodies (2.33%), shrubland (2.17%), and a negligible share of herbaceous wetland (cNarmada & cGanga, 2024). The agriculture-dominated, low-built-up character of the basin is consistent with the framework's central premise — that the dominant wastewater pressure is distributed domestic sewage from many small and medium towns rather than concentrated heavy industry.

### 3.3.7 The pollution picture

Across all three segments, the *Narmada River at a Glance* report identifies the discharge of untreated sewage from riverside towns and cities as a leading source of pollution. Madhya Pradesh alone is estimated to release on the order of 51 million litres per day (MLD) of untreated sewage directly into the river, and individual towns are named as point contributors — for example, Narmadapuram (Hoshangabad) at about 1.3 MLD. Industrial effluent — heavy metals and chemicals from paper, chemical, and textile units — is reported as a real but spatially concentrated pressure, associated with specific corridors (for instance near Jabalpur, Itarsi, Barwani, Bharuch, and Ankleshwar) rather than the basin as a whole. Agricultural pollution enters diffusely, as fertiliser and pesticide runoff (cNarmada & cGanga, 2024). Water quality is reported as acceptable in the upper reaches and degrading progressively downstream — the basis for treating the river as strained but still recoverable (Section 3.1).



---

# CHAPTER 4 — METHODOLOGY

# Chapter 4 — Methodology (draft)

> Provenance tags per subsection: [author-voice approved] = written from Eco Soul's reasoning and confirmed;
> [factual-draft, review] = drafted from the data/engine for Eco Soul to review and add voice;
> [CITE] = citation to be pinned in Zotero. Pairs with Figures 2–6 and Tables 1–6.

---

## 4.1 The Provenance Model  *[author-voice approved · pairs with Figure 3]*

This framework recommends real, physical interventions for wastewater treatment, and those recommendations carry real consequences. A tool that gets used in practice shapes decisions that affect people and the environment — so its values cannot come from thin air. Every number behind a recommendation has to trace back to a verifiable scientific source: a study, a report, a design manual — something a user can fall back on and check for themselves. We did not invent removal efficiencies or design parameters out of our own heads. The evidence already existed, in peer-reviewed literature, government reports, and established manuals; the work of this framework is to use that evidence correctly and keep it attributable at every step. Tools that skip this and present unsourced values are not just weaker — they are unsafe to act on, because no one can tell where a recommendation came from or whether it holds up. Where most tools treat their underlying data as a black box, this framework makes the origin of every value something you can see and interrogate.

Every value sits in one of three states. A **cited** value is the most authoritative: it comes straight from a real study — a peer-reviewed paper, a book, or a government report or manual — and we treat it as **corroborated** when two or more independent sources agree. A **derived (unconfirmed)** value comes from sourced evidence but has been worked on — transformed, interpolated, or combined — so it is not a direct reading from the literature, and we mark it as not yet confirmed rather than pass it off as primary. A **disclosed gap** is something we simply do not have data for; instead of inventing a number to fill the hole, we state plainly that it is missing. The rule we hold throughout is simple: an honest gap beats a fabricated value, because a single invented number would cast doubt on every other number in the system.

This discipline is enforced by the structure of the data, not by good intentions. Every row is tied by a foreign key to a central catalogue of 104 sources, and a dedicated `column_provenance` table — 324 field-level records — stores, for each value, its provenance state, whether we derived it, where it came from, and a link to the source where one exists. Corroboration is tracked directly: of 167 removal-efficiency values, 98 are corroborated by more than one source. Because every field carries its source and its status, an unsourced value cannot slip into a recommendation unnoticed — it surfaces as a flagged derivation or a disclosed gap. And none of this is buried in the backend: on every recommendation and solution page, the sources are shown right there, in front of the user, at the moment the recommendation is being read.

For the user, this turns provenance into trust. Anything the application shows can be traced and verified independently. The interface is also honest about which parts are our own contribution rather than established fact — most importantly the criteria weights, which we derived ourselves. No published source hands you weights for this decision; we set them as informed judgements, reasoned from NbS implementation studies and checked for consistency, and the tool labels them as our own contribution so the user can see exactly what is drawn from the literature and what is our reasoning on top of it. Confidence labels then express how much of a given recommendation rests on corroborated sources versus our own provisional input. In short, the framework lets a sceptical engineer or reviewer question not only *what* it recommends, but *why* — and on whose authority.

> **Disclosure (place once in Methods or Acknowledgements):** the extraction, transformation, and interpolation of values from sourced literature were performed with computational/AI assistance; such values are flagged as *derived (unconfirmed)* and were not treated as primary evidence.

---

## 4.2 The Criteria and Their Weighting  *[pairs with Figure 4, Table 2, Table 3]*

### 4.2.1 The criteria set  *[factual-draft, review]*

The framework evaluates each candidate treatment train against a set of decision criteria chosen to operationalise the four aims of this work — that recommendations be location-specific, evidence-grounded, source-aware, and built from complete treatment trains. Seven criteria are active; an eighth is defined but held in reserve.

Two criteria capture **treatment performance**, the primary purpose of any recommendation. C1 (treatment fit) measures how far a train closes the gap between the incoming pollutant load and what must be removed — its treatment capability against the actual problem. C2 (standard fit) measures whether the train's effluent meets the limit set by the intended use of the water. These carry the most weight, because a system that does not adequately treat the wastewater, or does not meet the discharge standard, fails at the one thing it exists to do.

Three criteria make the recommendation **location-specific**. C3 (site fit) tests the train against the physical conditions of the site — slope, soil, and available land. C6 (hydrologic fit) tests it against the river itself, using stream order to judge whether a system belongs at that point in the network. C4 (source fit) screens the train against the dominant pollution source — domestic, industrial, or agricultural.

Two criteria capture **practicality**, which decides whether a system can realistically be built and kept running. C7 (footprint) is the land a train requires; C8 (O&M) is the operational and energy burden of running it. Both are cost criteria — lower is better. Their inclusion follows established multi-criteria practice for wastewater technology selection in Indian and developing-country settings, where land availability and operation-and-maintenance capacity are binding constraints rather than secondary concerns [CITE: Kalbar, Karmakar & Asolekar].

The eighth criterion, C5 (health risk), is defined but held in reserve: no validated health-risk dataset was available, and rather than populate it with weak proxies it is left inactive and recorded as a disclosed gap and an item of future work. This is the provenance principle applied to the criteria themselves — a criterion without a defensible basis is disclosed, not faked.

### 4.2.2 Weighting the criteria  *[author-voice approved]*

The relative importance of the criteria was set through pairwise comparison (AHP), and the resulting weights reflect a deliberate ordering of priorities grounded in how nature-based systems actually succeed or fail in practice.

Treatment performance was placed at the top. C1 and C2 together carry roughly half the total weight because they decide whether a recommendation is viable at all: every other consideration is secondary to whether the system can actually treat the wastewater at that site. Treatment capability is what gets a candidate through the door — if a train cannot adequately clean the water, its land requirement or operational simplicity is irrelevant. C2 (standard fit) is weighted almost equally to C1 because treating the water is not enough on its own; it must be treated *to the level the intended use demands*. A system that produces irrigation-grade water where discharge-to-river quality is required has not solved the problem, so use-case compliance must influence the choice as heavily as raw treatment capability. The two are co-primary, and weighted equally, because neither is sufficient without the other.

Practicality was placed below performance but kept substantial. C7 (footprint) and C8 (O&M) sit beneath C1 and C2 because a system that is easy to build but does not meet the treatment requirement is of no use — feasibility cannot compensate for inadequate treatment. At the same time, these criteria were given meaningful weight, not a token one, because the purpose of the framework is to support solutions that practitioners can realistically deploy: systems with lower operational burden and cost are easier to install and maintain, which encourages uptake and, in turn, the wider adoption of nature-based solutions. They are weighted below performance for a deliberate reason — final engineering decisions are made in the field, where conditions vary and a design that looks demanding on paper can often be optimised on site. This framework is a decision-*support* tool, not a decision-*making* one; an automated tool cannot account for every on-site condition, so practicality is weighted to inform the choice without overriding the engineering judgement that must happen on the ground.

Hydrologic fit (C6) is the lightest of the active criteria. This is not because river position is unimportant, but because the most decisive location and hydrology constraints are applied *before* ranking, as hard filters, rather than as scored criteria. By the time a train reaches the weighted comparison, options that are unsuitable for the site's stream order, slope, or soil have already been screened out. C6 therefore captures the residual, finer-grained hydrologic preference among options that have already passed the binding constraints — which is real, but secondary.

A clarification on the location and hydrology factors (C3, C4, C6): these operate at two distinct levels in the framework. As **hard filters**, they enforce binding feasibility and safety constraints — a train unsuited to the site's soil, slope, or stream-order position is removed from consideration entirely, not merely penalised. As **scored criteria**, they then express a finer preference among the options that survive filtering. This two-level treatment is deliberate and is reflected in the weights: because the decisive constraints are already enforced upstream as filters, the same factors carry only light weight in the ranking, where their role is to capture residual preference rather than to make or break a recommendation. The sensitivity analysis confirms this division of labour — at the demonstration site, removing the site and hydrology criteria from the weighted ranking left the order of the surviving trains unchanged, while the hard filter independently excluded an unsuitable option (on-site disposal, on low-infiltration soil). The factors do real work at both levels; the framework simply applies each level where it belongs.

**Table 2 — Criteria definitions**

| Code | Criterion | What it measures | Direction | Tier |
|---|---|---|---|---|
| C1 | Treatment fit | Closure of the pollutant-load gap (treatment capability vs the actual problem) | benefit | performance |
| C2 | Standard fit | Whether effluent meets the limit for the intended use | benefit | performance |
| C3 | Site fit | Suitability to slope, soil, available land | benefit | location |
| C4 | Source fit | Match to dominant pollution source (domestic/industrial/agricultural) | benefit | location |
| C5 | Health risk | *Reserved — no validated dataset (disclosed gap, future work)* | — | — |
| C6 | Hydrologic fit | Suitability to stream-order position in the river network | benefit | location |
| C7 | Footprint | Land requirement | cost | practicality |
| C8 | O&M | Operational and energy burden | cost | practicality |

---

## 4.3 Treatment Trains as the Unit of Recommendation  *[author-voice approved · pairs with Figure 6, Table 4]*

A defining choice in this framework is that it recommends complete treatment trains rather than individual nature-based units. This follows directly from the nature of the problem. Most NbS technologies are treatment-specific — each is effective against particular pollutants — whereas real wastewater is never a single contaminant but a mixture of organic load, solids, nutrients, and pathogens. A single unit therefore tends to improve the water by reducing one or two of these, not to bring the whole effluent to a usable standard. Conventional wastewater treatment has always been staged for exactly this reason, and the framework adopts the same logic: by combining NbS units into a train, the individual technologies act as the successive stages of a full treatment process, so the system can aim to treat the water from end to end rather than merely improve it.

The order of the train matters as much as its composition. Pretreatment brings the wastewater to a stable enough state to be treated properly, removing the constituents and characteristics that would otherwise interfere with the main treatment. Secondary treatment does the central work, removing the organic load and the biological contaminants. Polishing is the final stage — it ensures that whatever remains, anything the earlier stages missed, is removed before the water leaves the system. The three stages together are what carry the water from wastewater to fully treated; remove any one and the effluent never reaches the standard. A train that skips a stage does not simply perform a little worse — it leaves a gap that the remaining stages were not designed to close.

This is why train-level recommendation is a contribution rather than a presentational choice. An individual NbS technology usually cannot fully treat wastewater on its own, so a tool that recommends a single technology hands the practitioner an incomplete answer. By assembling and recommending trains matched to a known pollution source and intended use, the framework gives a recommendation that can actually carry the water to the required quality before it is discharged or reused. The output is something a practitioner can build, not a component they must still assemble into a working system.

Mechanically, each train is represented as an ordered sequence of steps (`train_step`), drawn from the catalogue of 28 NbS options and assembled into eight canonical trains suited to Indian conditions (Table 4). Train-level performance is computed by chaining the removal efficiencies of the constituent stages: the residual load passed to each stage is the product of the pass-through fractions of the stages before it, so the train's overall efficiency for a pollutant is the cumulative effect of the sequence rather than the figure for any single unit (`train_performance`). The resulting effluent is then compared against the limits for the intended use to judge whether the train meets the standard — this comparison is criterion C2.

---

## 4.4 Weight Derivation and Ranking: AHP and TOPSIS  *[factual-draft, review]*

The framework separates the two analytical tasks a multi-criteria decision problem requires: establishing how much each criterion matters, and ranking the alternatives against the criteria. The first is handled by the Analytic Hierarchy Process (AHP), the second by the Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS).

Weights are derived through AHP. For each use case, the criteria are compared pairwise and the comparisons are assembled into a reciprocal matrix whose principal eigenvector gives the criteria weights. Because pairwise judgements can be internally inconsistent, the consistency of each matrix is checked through the consistency ratio (CR); all matrices used here fall within the accepted threshold, so the weights are internally coherent rather than arbitrary. The weighting is use-case-specific: separate comparison matrices are built for discharge, irrigation, and drinking, because the relative importance of treatment, standard compliance, footprint, and operation differs by intended use (Table 3). The current irrigation values are the final working AHP-Fuzzy AHP ensemble weights used in this report after the O&M re-blend; they are not labelled expert-validated unless explicit approval documentation is recorded.

To test the stability of these weights under the imprecision inherent in human judgement, a Fuzzy-AHP variant was also computed, in which each pairwise judgement is expressed as a triangular fuzzy number rather than a single value. The crisp and fuzzy weight vectors agree closely — they differ by less than one percentage point on every criterion — so the fuzzy treatment is reported as a confirmation that the weights are stable to fuzzification rather than as a source of materially different weights.

Alternatives are ranked by TOPSIS. The decision matrix of trains against criteria is normalised (vector normalisation) and weighted; an ideal best and ideal worst are identified for each criterion — treating benefit criteria, where higher is better, and cost criteria, where lower is better, accordingly — and each train is scored by its relative closeness to the ideal best versus the ideal worst. The resulting closeness coefficient orders the trains from best to worst. TOPSIS was chosen because it produces a transparent, interpretable ranking from heterogeneous criteria and degrades gracefully — a property that matters here, where some criteria carry disclosed data gaps. The robustness of the resulting ranking to the weight choices is examined directly through a sensitivity analysis (Chapter 6).

---

## 4.5 Applicability and Safety Screening  *[factual-draft, review · pairs with Figure 5]*

Before any train is scored, it passes through an applicability layer of 46 rules that encode feasibility and safety constraints. This layer is what makes the recommendation location-specific and safe, and it operates ahead of the weighted ranking so that unsuitable options never reach it.

The rules fall into a few types. **Hard filters** and **hard safety filters** remove a train outright when a binding constraint is violated — for example, infiltration-based systems are removed on low-infiltration soils, in-channel placement is blocked on high-order reaches, and industrial or biomedical sources are required to undergo pretreatment before an NbS train is considered. **Conditional filters** and **conditional allowances** gate options in a context-dependent way, such as permitting an off-channel system subject to a land-availability check. **Scoring modifiers** adjust the score of a surviving train to reflect finer suitability — for instance, a decentralised train is favoured off-channel at high stream order. **Confidence modifiers** act differently again: rather than change a train's score, they lower the confidence attached to a recommendation where the supporting evidence is weak, for example where the presence of sewage is inferred from land use rather than measured.

As Section 4.2 noted, a single physical factor can act at more than one of these levels. The framework applies the decisive constraints as hard filters and reserves the corresponding scored criteria for finer preference among the options that survive — gating upstream, ranking downstream (Figure 5). The weighted comparison is therefore performed only over trains that are already feasible and safe at the site.

---

## 4.6 Separating Match from Confidence  *[factual-draft, review]*

The framework reports two distinct quantities for every recommendation, and keeps them separate by design: how well a train matches the requirement, and how much confidence can be placed in that judgement given the underlying evidence.

The **match** is the TOPSIS result — the suitability of the train against the weighted criteria. **Confidence** is a separate axis that reflects the strength and completeness of the data behind that match: whether the relevant values are cited and corroborated, derived and unconfirmed, or missing as disclosed gaps, together with any confidence modifiers triggered during screening. The two are not collapsed into a single number because they answer different questions. A train can be a strong match on the data available while that data is itself incomplete; presenting only the match would hide that, and presenting only confidence would discard the recommendation. By surfacing both, the framework lets the user see not just which train ranks highest, but how much weight the evidence can bear — the honest form of a recommendation from a tool that openly carries data gaps.

This separation also prevents a specific failure: a missing value being silently read as a zero. An absent removal figure is treated as a disclosed gap that lowers confidence, not as a measured zero that would unfairly penalise a train's match. The consequence of getting this wrong — and the correction — is documented in Chapter 6.



---

# CHAPTER 5 — SYSTEM DESIGN AND IMPLEMENTATION

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



---

# CHAPTER 7 — DISCUSSION

# Chapter 7 — Discussion (draft)

> Tags: [author-voice approved] = built from author's reasoning & confirmed.
> [reconcile w/ live engine] = claim rests on a specific number from the DB-reconstructed run; the
> *argument* is shape-stable, but the figure is to be confirmed against the live engine before final.
> Written ahead of the final Ch.6 numbers: the interpretive arguments here rest on the result SHAPE
> (which is stable), not on exact decimals.

---

## 7.1 What the Demonstration Shows  *[author-voice approved]*

The demonstration on the Khandwa discharge case shows the framework doing the thing a generic recommendation tool does not: changing its recommendation in response to local conditions. A generic tool offers the same options regardless of where they will be built. This framework, by contrast, removed on-site disposal from consideration at Khandwa because the district's clay, low-infiltration soil cannot support an infiltration-based system [reconcile w/ live engine]. That is the location logic working as intended — a recommendation that is filtered to what the site can actually sustain, rather than a generic list a practitioner must then check by hand. The practical value of this is direct: recommendations that already fit the site are more likely to be implemented and to keep working once built, which is precisely what is needed to encourage real uptake of nature-based solutions for wastewater treatment in the basin.

The sensitivity analysis adds a second, more careful finding, and it must be read precisely. Across a wide range of weightings, the top-ranked irrigation train remained WSP Train (pond series) in 98.08% of 5,000 Monte Carlo draws under +/-30% perturbation, with UASB-based STP taking the lead in the remaining draws. This does **not** prove that the criteria weights are "correct" — robustness and correctness are different properties. What it shows is that the final working report weights produce a stable top result while still disclosing where the ranking is sensitive.

At the same time, the weights are not inert. Within the robust shortlist, the identity of the single highest-ranked train can change under specific criterion tests: for the refreshed irrigation run, removing C8 shifts the leader to UASB-based STP even though equal weighting keeps WSP first. The two findings therefore work together rather than against each other — the main result is stable under broad perturbation, while individual criteria still reveal real trade-offs. This is also why expert validation remains an important next step: it is needed not because the engine is unstable, but because the weights carry visible interpretive responsibility.

## 7.2 The Relationship Between the Tool and the Practitioner  *[author-voice approved]*

The demonstration surfaces a trade-off that, handled correctly, defines what kind of tool this is. The train ranked highest on treatment quality is also the most demanding to operate and maintain, while the lowest-O&M option is not the top performer on quality. The framework does not try to resolve this trade-off on the user's behalf, and that restraint is deliberate.

An automated tool cannot know the real-time, on-the-ground conditions of a specific site — the local operating capacity, the budget, the maintenance support actually available — as well as the engineer or practitioner standing on it. What the framework can do is give that practitioner two honest anchors: the option that is best on treatment quality, and the option that is lightest to operate. The final decision — whether the higher-performing but more demanding system is realistic for this particular site, or whether the simpler system is the wiser choice given local constraints — is left with the person who holds the full picture. This is the meaning of describing the framework as a decision-*support* tool rather than a decision-*making* one, and it is consistent with the weighting choice made in the methodology, where practicality is weighted below treatment performance precisely because final engineering decisions are made in the field (Section 4.2.2).

Read this way, the trade-off is not a weakness in the recommendation but an honest division of labour. The tool streamlines and structures the decision, narrows a large set of options to a defensible shortlist, and makes the quality-versus-operability tension explicit; the practitioner brings the site knowledge the tool cannot have and makes the final call. Supporting the decision in this way — rather than pretending to make it — is what allows the framework to be genuinely useful to the people who would deploy these systems.

## 7.3 Significance and Intended Use  *[author-voice approved + CITE-gated on Ch.2]*

The significance of the framework is best stated not as a claim about its novelty but as a fact about the gap it fills. No existing tool, to the author's knowledge, brings together the three things this framework does at once: it resolves recommendations to local site conditions, it screens candidate solutions by pollution source, and it recommends complete treatment trains rather than single units — all on a provenance-tracked evidence base. Tools exist that address parts of this, but the combination, applied to nature-based solutions and conditioned on local data, is what is missing. [The precise positioning of this gap against prior multi-criteria and NbS-selection tools is established in Chapter 2 — this claim is on credit until that chapter is written. CITE: Kalbar, Karmakar & Asolekar; Nat4Wat / Pueyo-Ros.]

The framework is intended for the practitioners, planners, and decision-makers responsible for wastewater management in the basin — those choosing how to treat the untreated domestic sewage of small and medium towns, who at present have no location-aware, source-aware, train-level tool to guide that choice. For such a user, the framework converts a difficult, evidence-scattered decision into a structured one: it takes the conditions of a specific location and the source of its wastewater, and returns a shortlist of complete treatment trains that are feasible at that site, ranked and traceable to their evidence. It does not replace the engineering judgement that must follow; it gives that judgement a defensible, location-specific starting point where previously there was none. In a basin where the dominant pollution pressure is distributed domestic sewage and the appropriate response is decentralised treatment deployed town by town (Section 3.1), a tool that makes each of those many local decisions faster, more consistent, and better grounded in evidence is the practical contribution this work offers.


---

# CHAPTER 8 — LIMITATIONS AND FUTURE SCOPE

# Chapter 8 — Limitations and Future Scope (draft)

> Tags: [author-voice approved] = built from author's reasoning & confirmed ·
> [factual-draft, review] = drafted from project state for review.
> Governing distinction (do not collapse): FRAMEWORK limitations constrain the method (the contribution);
> DEMONSTRATION/DATA limitations constrain this instantiation. The contribution is the framework, not the data.

---

## 8.1 Limitations of the Framework  *[author-voice approved]*

The contribution of this work is the decision-support framework itself, and its limitations are stated here separately from those of the present demonstration (Section 8.2), because they are different in kind: these bound the method, while those bound the particular data it was exercised on.

**Final working report weights, pending recorded approval.** The criteria weights were reasoned from the nature-based-solutions implementation literature, assembled through pairwise comparison, checked for internal consistency, and blended with the Fuzzy-AHP layer where applicable. The irrigation vector used by the live engine is the final working weight set used in this report, not an expert-validated set unless explicit approval documentation is recorded. Their influence on the result is bounded by sensitivity analysis (Chapter 6), which shows that the main demonstration conclusions survive across a wide range of weight perturbations while still identifying the criteria that can move the leader.

**Transfer uncertainty in literature-derived performance.** The framework scores treatment trains using removal efficiencies drawn from the published literature (Section 8.2 explains why basin-specific values do not yet exist). A literature-derived efficiency carries an implicit assumption — that a technology will perform in the Narmada basin broadly as it did in the study it was taken from — when in reality climate, influent strength, and operating practice differ between the source study and the target site. This transfer uncertainty is inherent to any evidence-based tool built ahead of local field data, and the framework does not hide it: every transferred value carries its source and a confidence label, so the uncertainty is disclosed at the point of use rather than absorbed silently into a score.

**Single-basin demonstration.** The framework is demonstrated on one basin, the Narmada. This is a deliberate scope rather than a limit of the method — the framework's logic (source-aware screening, location-conditioned criteria, train-level recommendation) is basin-agnostic by construction — but it does mean the framework has not yet been exercised across the range of physical settings it is designed to handle. One consequence is visible already: because the Narmada basin lies within a single broad climate zone, the climate layer does not discriminate between sites in this demonstration (Section 3.2). Its discriminating power is real but latent, and is exercised only when the framework is applied across climatically varied settings — which is precisely the first item of future scope.

---

## 8.2 Limitations of the Demonstration and Data  *[author-voice approved]*

The limitations in this section constrain the present demonstration and the data available for it, not the framework. They are stated plainly, consistent with the provenance discipline of this work, but they should not be read as flaws in the contribution.

**Removal efficiencies are literature-transferred, because basin-specific data structurally cannot yet exist.** The framework's removal efficiencies are transferred from published studies rather than measured in the Narmada basin. This is not an oversight that better effort would have closed: nature-based solutions are not yet in common use in the basin, and there are no significant NbS installations on the Narmada from which performance could have been measured. Narmada-specific NbS performance data does not exist because the systems whose performance it would describe have not been built. This is exactly the condition the framework was designed for — it is *why* the work is provenance-first and evidence-transferred rather than measurement-based — and it is also why the framework is needed: to inform the first such installations, whose monitoring would in turn generate the basin-specific data a future version could use.

**No measured influent water quality.** For the same structural reason, the framework does not use measured influent (raw wastewater) quality from across the basin — comprehensive influent characterisation for the basin's many dispersed sewage sources does not exist. Influent is instead represented through sourced water-type profiles, and one value in particular — the domestic-sewage ammonia figure — is flagged in the data as a caveat to verify, because the profile value sits above the typical range. The receiving-water (ambient) quality, by contrast, is real and extensive (47,244 observations); it is the influent side that is profile-based.

**Pond removal-data coverage gap.** Removal data for pond systems is less complete than for other technology families (notably for TSS, total phosphorus, and ammonia), with the consequence that the engine under-credits ponds — a conservative artifact rather than an evidence-based judgement against them. This is disclosed so that a low pond ranking is not mistaken for a strong negative finding.

**Internal data-staging caveat.** The basin report-mining extension tables are held as a staging layer whose links to districts and regions are logical rather than verified, and are not yet used to drive location-level recommendations. This is an internal data-management caveat with no effect on the demonstration's results.

---

## 8.3 Future Scope  *[author-voice approved]*

The future directions below follow directly from the limitations above and from the design choices made to keep the framework extensible. They are ordered by priority.

**1. Generalisation to other basins.** The most important next step is to apply the framework beyond the Narmada to other river basins. This both tests the framework's central claim of transferability and activates the parts of it that are latent in a single-basin demonstration — most directly the climate layer, which becomes an active discriminator between sites once the framework spans climatically varied regions (Sections 3.2, 8.1). Generalisation is what turns a demonstrated tool into a general framework.

**2. Expert validation of the weights and a fuller fuzzy treatment.** The provisional criteria weights will be validated with domain experts and the supervisor, replacing the author-derived values with expert-corroborated ones. Alongside this, the Fuzzy-AHP variant — presently used as a robustness confirmation (Section 4.4) — can be developed into a fuller treatment of the imprecision in expert judgement, strengthening the weighting layer rather than merely testing its stability.

**3. Richer decision logic and GIS integration.** The decision engine can be extended in two complementary directions. First, the incorporation of more advanced mathematical models into the recommendation logic, to capture interactions the present additive multi-criteria scheme treats independently. Second — and most valuable for a location-specific framework — integration with GIS. Because the framework's location inputs (soil, slope, stream order, climate) are inherently spatial, a GIS layer would let a user see these decision parameters rendered on a DEM-backed map of the basin rather than read them as attributes, and would allow recommendations to be mapped to their actual positions along the river network. This turns the tool from a per-site calculator into a basin-scale planning view — the natural visual expression of the distributed-problem, distributed-solution logic that motivates the work (Section 3.1).

**Further directions.** Beyond these priorities, several items follow from the data and deployment state: extending the demonstration to additional districts and use-cases (an inexpensive extension, since the engine already supports all three use-cases); activating the reserved health-risk criterion (C5) once a validated health-risk dataset is available; acquiring measured influent and, in time, performance data from the basin's first NbS installations; and hardening the production deployment (regenerating the PostgreSQL schema to the current data model and completing the move to managed cloud hosting).

> REVIEW NOTES: (i) update the weights status to "expert-validated" only if explicit supervisor approval documentation is recorded before submission. (ii) Section 8.3 item 1's tie to Chapter 6 (sensitivity) and the multi-district extension assume the live-engine reconciliation of the Khandwa numbers is complete; keep consistent with the final Ch.6. (iii) the ammonia caveat in 8.2 should cite the specific water_type_profiles value once verified.



---

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

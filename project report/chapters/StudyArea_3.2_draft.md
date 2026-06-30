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

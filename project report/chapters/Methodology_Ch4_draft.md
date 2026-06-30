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

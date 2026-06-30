# Chapter 8 — Limitations and Future Scope (draft)

> Tags: [author-voice approved] = built from author's reasoning & confirmed ·
> [factual-draft, review] = drafted from project state for review.
> Governing distinction (do not collapse): FRAMEWORK limitations constrain the method (the contribution);
> DEMONSTRATION/DATA limitations constrain this instantiation. The contribution is the framework, not the data.

---

## 8.1 Limitations of the Framework  *[author-voice approved]*

The contribution of this work is the decision-support framework itself, and its limitations are stated here separately from those of the present demonstration (Section 8.2), because they are different in kind: these bound the method, while those bound the particular data it was exercised on.

**Provisional criteria weights.** The criteria weights are author-derived. They were reasoned from the nature-based-solutions implementation literature, assembled through pairwise comparison, and checked for internal consistency (all consistency ratios below the accepted threshold), and they are clearly labelled as provisional throughout the system. They are not, however, an unguarded assumption: their influence on the result is bounded by the sensitivity analysis (Chapter 6), which shows that the robust conclusions of the demonstration survive across a wide range of weightings. Expert validation of the weights, with the project supervisor, is in progress; when complete it will replace the provisional values, but the framework's behaviour does not rest on any single weighting being exactly correct.

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

> REVIEW NOTES: (i) update the weights status to "expert-validated" if confirmed with the supervisor before submission. (ii) Section 8.3 item 1's tie to Chapter 6 (sensitivity) and the multi-district extension assume the live-engine reconciliation of the Khandwa numbers is complete; keep consistent with the final Ch.6. (iii) the ammonia caveat in 8.2 should cite the specific water_type_profiles value once verified.

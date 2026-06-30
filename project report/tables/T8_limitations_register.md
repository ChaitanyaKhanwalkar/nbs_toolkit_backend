# Table 8 — Limitations register (quick reference for Chapter 8)

Limitations sorted by kind. The contribution is the framework, so framework limitations and
demonstration/data limitations are kept distinct (Chapter 8).

| # | Limitation | Kind | Status / how handled |
|---|---|---|---|
| 1 | Criteria weights are author-derived | Framework | Provisional; CR-checked; bounded by sensitivity analysis (Ch.6); expert validation in progress |
| 2 | Transfer uncertainty in literature-derived removal efficiencies | Framework | Inherent to evidence-ahead-of-field tools; disclosed via per-value source + confidence labels |
| 3 | Demonstrated on a single basin (Narmada) | Framework | Deliberate scope; framework is basin-agnostic by construction; generalisation = future scope #1 |
| 4 | Removal efficiencies literature-transferred, not Narmada-measured | Data | Structural — no NbS installations exist in the basin to measure; the condition the framework is built for |
| 5 | No measured influent water quality | Data | Structural; represented via sourced water-type profiles; ammonia profile value flagged to verify |
| 6 | Pond removal-data coverage gap (TSS/TP/NH4) | Data | Conservative artifact (under-credits ponds); disclosed so low rank isn't read as a finding |
| 7 | Extension tables are a logical staging layer | Data | Internal data-management caveat; not used to drive recommendations; no effect on results |
| 8 | C5 (health-risk) criterion reserved | Future (not a limitation) | Inactive; no validated dataset yet; activates when data available |
| 9 | Climate near-constant across this basin | Future (by design) | Designed-for-transfer; becomes an active discriminator when framework spans climates |
| 10 | Deployment not yet hardened | Future | `schema_pg.sql` to regenerate; Azure move pending; deprioritised until app stabilises |

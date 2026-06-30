# Khandwa demonstration — full 7-criterion ranking + sensitivity (discharge to inland water)

Scenario: a town in Khandwa district (MP, Strahler 7 mainstem, clay/low-infiltration soil,
gentle slope, 59% agricultural land, low built-up) discharging treated domestic sewage to the
Narmada. Author-derived discharge weights. Site/source/hydro factors derived from the actual
`nbs_applicability_rules` at Khandwa's context.

## Safety filter fired (the tool working)
**On-site disposal was hard-filtered out** — Khandwa's clay/low-infiltration soil trips the
`soil_infiltration` hard rule. The engine refuses to recommend soak-pit disposal there. This is
the single cleanest demonstration of the applicability layer doing its job.

## Ranking (7 surviving trains)
1. **VF nitrifying hybrid** (Ci 0.78)
2. **DEWATS modular train** (0.64)
3. **French VF** (0.63)
4. WSP train · 5. Septic+HSSF · 6. Pond+aquaculture · 7. UASB-STP

## Sensitivity — three findings
1. **Top-3 shortlist is rock-solid.** VF hybrid, DEWATS, French VF each hold top-3 in **100%**
   of 5000 Monte-Carlo draws (±30% per weight); top-1 held 99.9%; mean Spearman 0.96.
2. **The decision pivots on C2 (standard-fit).** Removing C2 collapses agreement (Spearman 0.21)
   and hands #1 to DEWATS; equal weights also give DEWATS. The author weighting — quality-first —
   is precisely what selects the high-performance VF hybrid over the more operable DEWATS.
3. **Site/source criteria barely move the ranking here** (dropping C3, C4, or C6 → Spearman 1.0).
   At Khandwa their role was a **gatekeeper** (removing on-site disposal), not a differentiator.
   Different criteria play different roles: C1/C2 rank; C3/C4/C6 filter. (Useful methods point.)

## Face-validity note (for Discussion)
VF hybrid is the highest-O&M option. The recommendation reflects a deliberate priority on
effluent quality over operational simplicity; under equal weighting the more practical DEWATS
leads. Recommended framing: report the robust top-3 and discuss the quality-vs-operability
trade-off rather than asserting a single winner.

## Honesty / reconciliation
Reconstructed transparently from `narmada_nbs_canonical.db`: C1 = mean cumulative-removal proxy
(engine uses severity-weighted gap-closure); C3/C4 are uniform at Khandwa per the rules; C6 uses
the real stream-order rule modifiers (DEWATS +0.10, UASB +0.05, wetlands −0.05). The **structural
findings above are the paper output**; the absolute Ci decimals should be reconciled against a
live-engine export for the same scenario before final numbers go in the paper.

## Headline sentence
"For discharge-to-river in Khandwa, the recommended shortlist (VF hybrid, DEWATS, French VF) is
invariant under ±30% weight perturbation (100% top-3 retention, mean Spearman 0.96); the lead
option pivots on the effluent-standard weight, and the applicability layer correctly excludes
on-site disposal on low-infiltration soil."

# Sensitivity analysis — results (discharge_inland, train-intrinsic core)

**Scope (read first):** computed on the **4 train-intrinsic criteria** (C1 treatment-fit,
C2 standard-fit, C7 footprint, C8 O&M) = **73% of the discharge weight**, reconstructed
transparently from `narmada_nbs_canonical.db`. The 3 site criteria (C3 site, C4 source,
C6 hydrologic) are **not yet included** — they are what make the ranking *district-specific*
(Khandwa) and must be added from an engine export or a documented per-district derivation.
So this is the **discharge train-intrinsic ranking**, not yet the Khandwa-resolved ranking.
Absolute Ci values are a reconstruction (C1 = mean cumulative removal proxy; the engine uses
severity-weighted gap-closure) and should be reconciled with the live engine. The
**structural findings below are the paper output** and are robust to those details.

## Baseline ranking (author-derived weights)
1. VF nitrifying hybrid (Ci 0.79) · 2. DEWATS (0.63) · 3. French VF (0.61) ·
4. Pond+aquaculture · 5. WSP · 6. Septic+HSSF · 7. UASB-STP · 8. On-site.

## Finding 1 — the top-3 shortlist is robust; the #1 is weight-sensitive
- Monte Carlo (5000 draws, ±30% per weight): **top-3 membership** — VF hybrid 100%,
  DEWATS 100%, French VF 90%. Nothing else reaches 10%. The shortlist is stable.
- But the **#1 within it depends on the weights**:
  - Author weights → **VF hybrid** #1.
  - **Equal weights → DEWATS #1** (Spearman 0.64 vs baseline).
  - Drop C2 (standard-fit) → **DEWATS #1** (Spearman 0.69).
- Interpretation: the decision hinges on **C2 (use-case standard compliance)**. Your weighting
  deliberately prioritises effluent quality (C1+C2 ≈ 52%) over operability (C7+C8), which is
  what selects the high-performance VF hybrid over the more modest DEWATS. **The weights are
  doing real work** — they are the difference between the two top recommendations.

## Finding 2 — face-validity flag (decide how to handle)
VF hybrid is the **highest-O&M option** in the set (powered, high skill). Under equal weights
the more practical, gravity-modular **DEWATS** wins. For a small/medium MP town, a practitioner
might prefer DEWATS on operability grounds. Three honest responses, pick one:
1. Report the **robust top-3 shortlist** as the recommendation and discuss the #1 trade-off
   (cleanest, most defensible).
2. Argue the weighting (quality-first) is correct for discharge-to-river and own VF hybrid as #1.
3. Re-examine whether C8 (O&M) is under-weighted for decentralised Indian contexts.

## Headline sentences for the paper
- "The recommended shortlist (VF hybrid, DEWATS, French VF) is invariant under ±30% weight
  perturbation (≥90% top-3 retention over 5000 Monte-Carlo draws; mean Spearman 0.95)."
- "The lead recommendation is sensitive to the standard-fit weight (C2): under author-derived
  weights the VF nitrifying hybrid leads, while equal weighting favours DEWATS — locating the
  decision's pivot at effluent-quality vs operability."

## Next step to make it Khandwa-resolved
Add C3/C4/C6 for Khandwa (Strahler 7, agricultural pressure, off-channel). Stream order 7
triggers off-channel filtering for in-channel families — this will move site-sensitive options
and may change ranks below the top-3. Get these from the engine export, or I derive them from
`app_district_profile_cache` + `nbs_applicability_rules` with documented logic.

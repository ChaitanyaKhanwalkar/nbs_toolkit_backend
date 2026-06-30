# Engine-Run Spec — Khandwa discharge demonstration (for Claude Code)

Purpose: produce final, verified Ch.6 results to replace the DB-reconstructed numbers.
Run location: Claude Code / local repo (NOT the report chat — that chat cannot see engine code).
Target DB: narmada_nbs_canonical.db

## Order of operations (stop at any failed checkpoint)

### 0. Confirm data foundation
- Engine points at `narmada_nbs_canonical.db`.
- Reproduces canonical signature: 28 NbS · 167 removal · 104 sources · 8 trains.
- If pointed elsewhere (e.g. narmada_nbs_with_river_network.db) → re-point first, report change.

### 1. Fix weights wiring FIRST  ← the checkpoint that matters most
- Known defect: `use_default_weights` not wired → `weights_status: "weights_missing"` →
  silent fallback to EQUAL weights. Equal-weighted output is NOT usable.
- Wire provisional AHP discharge weights into the recommendation path; label interim/provisional.
- PROVE it: one request shows `weights_status` OK and AHP discharge weights applied (not equal).
- Do not proceed until confirmed.

### 2. Run the case
- Location = Khandwa district · Use-case = discharge_inland · all 8 trains.
- Read real Khandwa site attributes from `site_attributes`/`regions` (soil/infiltration class,
  Strahler stream order, slope). Do NOT assume them; show the row used.

### 3. Capture outputs (CSV + JSON/text):
a. Ranked results: train · Ci/match score · rank
b. Filtered-out list: train · exact rule/reason (confirm on-site disposal hard-filter + on what)
c. Decision matrix: train × {C1,C2,C3,C4,C6,C7,C8} per-criterion scores (+ normalized/weighted if avail)
d. Weights used: actual vector, confirmed = AHP discharge set
e. Confidence: label/score per recommendation + method
f. Engine flags: warnings, weights_status, missing-data handling
   (confirm missing removal = disclosed gap, NOT 0% removal)

### 4. Sanity checks (flag, don't hide)
- data-coverage artifact (train scores well only from fuller data)
- influent ammonia inflating NH3 fails
- ponds under-credited (missing TSS/TP/NH4 rows)

## What happens when you bring it back to the report chat
Diff real vs DB-reconstructed numbers in results/:
- shape holds (top-3 stable, on-site filtered, C2 pivots) → swap decimals, drop [reconcile] tags, Ch.6 final
- shape breaks → rewrite affected claims honestly (better found now than post-submission)

## The likely snag
Step 1. If output shows weights_missing or all-equal criteria → STOP, weights not wired, numbers not real.

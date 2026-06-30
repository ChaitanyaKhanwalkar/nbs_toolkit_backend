# Sources Cleanup Report
Generated 2026-06-24 from `sources.csv` (104 rows) + `report_source_catalog.csv` (12 reports).
Output: `sources_cleaned.csv` (original columns + `bib_action` + `cleanup_note`).

## Headline
The bibliography is in **better** shape than the canonical files feared (all 104 rows already
carry a citation string), but it is **not yet a clean reference list**. 87 rows are clean;
**17 rows need action** before they go into a paper. One canonical-file instruction was wrong
and is reversed here.

## 1. CORRECTION — the "stray leading c" is NOT a bug (do not strip it)
`HANDOFF.md` and `DATA_DICTIONARY_canonical.md` both call the leading `c` on sources 92–103 a
"stray cosmetic artifact, clean if desired." This is incorrect. **cNarmada** and **cGanga** are
real institutions:
- **cNarmada** = Centre for Narmada River Basin Management & Studies (IIT Gandhinagar + IIT Indore, est. 2024).
- **cGanga** = Centre for Ganga River Basin Management & Studies (IIT Kanpur, est. 2016), supervising body.
- Both operate as knowledge wings of the NRCD, Ministry of Jal Shakti, Government of India.

Stripping the `c` would corrupt the institutional author on all 12 NRCD report citations.
Action taken: kept the `c`, reformatted the 12 citations to canonical form —
`cNarmada and cGanga (year). Title. NRCD, Ministry of Jal Shakti, Government of India.`
Action for you: confirm the exact published citation for each report (IIT Indore co-leads
cNarmada, so you have direct access). Fix this note in HANDOFF/DATA_DICTIONARY so no other
chat re-introduces the error.

## 2. Licenses filled (14 previously "unknown", ids 78–91)
Suggested values written into the cleaned file, marked for confirmation:
- Government: 78 (CWC), 79 (CPCB), 80 (NRCD) → Government of India / GODL-India.
- Open access to verify: 81 (Water Science), 89 (MDPI Water, likely CC-BY-4.0).
- Publisher copyright (peer-reviewed/books): 84, 85, 86, 87, 88, 90, 91.
- 82, 83 → see duplicates below.

## 3. Duplicates to merge (cite once)
- **id 82 (Dotro 2017 IWA TW) == id 31 (Dotro_2017_IWA)** → cite once; repoint DB removal rows 82→31.
- **id 83 (von Sperling 2007) == id 34 (vonSperling_WSP)** → cite once; repoint DB rows 83→34.
(Bibliography: one entry each. DB: repoint or collapse — separate task, needs the DB.)

## 4. Internal artifacts — exclude from the reference list (keep as provenance)
- **id 14 Legacy_MVP** and **id 104 APP_USER_LAYER** are internal, not citable works.
- Any data value whose **only** citation is 14 or 104 must be re-sourced to primary literature.

## 5. Bundle / placeholder sources — resolve to specific papers (the real gap)
These were early umbrella entries, not single citable works:
- **id 15 (Lit_CW_review)** — citation literally reads "see plan §7" (an internal pointer).
  Replace with the actual Vymazal / Stefanakis references.
- **ids 8–13** (greywater, domestic, stormwater, industrial, CW_Pistia, CW_integrated) —
  license "cite per row"; these are influent-characterisation buckets. Split into the named papers.
- **ids 16–21** (vermifiltration, DEWATS/ABR, FTW, EKW/WSP, bioretention, buffer) —
  bundles that name authors; several overlap individual ids (e.g. 40, 53–77). Split for the ref list.

## 6. Action summary (from cleaned file)
| bib_action | count |
|---|---|
| INCLUDE (clean) | 75 |
| INCLUDE (NRCD, reformatted) | 12 |
| SPLIT (bundle, named) | 6 |
| RESOLVE to primary (bundle) | 6 |
| RESOLVE to primary (see-plan pointer) | 1 |
| MERGE (duplicate) | 2 |
| INTERNAL — exclude from refs | 2 |

**Net:** 87 publication-ready, 17 needing a decision/lookup, 0 missing entirely.

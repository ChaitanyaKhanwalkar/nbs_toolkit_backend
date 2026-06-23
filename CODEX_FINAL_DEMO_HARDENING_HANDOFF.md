# Final Demo Hardening Handoff

## Completed

- Final v1 AHP-Fuzzy AHP ensemble weights integrated for train ranking.
- Repository fallback added for stale/missing local `criteria_weights`.
- Local canonical DB rows updated during this run; SQL seed artifact added.
- Method wording updated across backend and frontend to AHP-Fuzzy AHP weighted TOPSIS after safety/applicability screening.
- Offline verified-location map replaced with a professional verified-location context card.
- Curated references modal now uses resolved citation records instead of pending placeholders.
- Sizing, compare cards, supporting component comparison, CSV, print/PDF, and report preview copy hardened.
- Industrial acidic Mandleshwar/mainstem regression added.
- Two affected visual QA goldens refreshed.

## Current Status

- Backend: passing, `67 passed`.
- Frontend analyze: passing, no issues.
- Frontend tests: passing, `25 passed`.
- Diff check: clean, line-ending warnings only.
- Commit status: ready for scoped staging/commit.

## Notes

- The canonical DB file is not tracked by Git in this workspace. The runtime code now protects final v1 behavior even when a local DB still has older provisional rows.
- C5 health-risk scoring is still inactive and reserved for future expert data.
- Sizing remains screening-level only.
- Manual visual QA is still recommended for web print/PDF, CSV in Excel, and the four main workflows.

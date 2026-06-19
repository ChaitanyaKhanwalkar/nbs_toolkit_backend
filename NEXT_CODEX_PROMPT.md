# Continue NBSGCT Big Upgrade - Module 2

Work in:
`C:\Users\Ecosoul Enviro\OneDrive\Desktop\NBSGCT`

Read `AGENTS.md`, `codex prompt.txt`, and
`CODEX_BIG_UPGRADE_HANDOFF.md` first.

Module 1 is complete and fully verified but its commit was blocked by the Codex
approval usage limit. First run `git status --short`, confirm only the Module 1
files documented in the handoff are changed, stage only those files, and commit:
`Module 1: Research-grade scoring and confidence`.

Then continue autonomously with Module 2: Dual recommendation system -
treatment trains plus individual NbS components.

Requirements:

1. Keep treatment trains primary for wastewater contexts.
2. Add a separate backend response structure and ranking/suitability assessment
   for individual NbS components.
3. Run A0 applicability before any component scoring.
4. Do not let a component replace or outrank the primary treatment train.
5. Return component name, family, role, suitability band, pollutants addressed,
   suitable/unsuitable contexts, standalone suitability, constraints, plant
   links, and source IDs where canonical evidence exists.
6. Show filtered or conditional components and reasons where feasible.
7. Industrial components must be polishing/buffer only after ETP/CETP;
   extreme pH requires neutralization.
8. High-order/mainstem contexts must not imply in-channel treatment cells.
9. Agricultural runoff must prioritize source-control/edge-of-field components.
10. Never recommend invasive plants or invent missing evidence.
11. Add an `NbS Components` frontend workspace section and summarize
    supporting/not-standalone components.
12. Add backend and practical frontend tests.

After the module, run:

- backend pytest
- Flutter analyze
- Flutter tests
- `git diff --check`

Then overwrite `CODEX_BIG_UPGRADE_HANDOFF.md` and
`NEXT_CODEX_PROMPT.md`, make the scoped checkpoint commit:
`Module 2: Add individual NbS component recommendations`,
and continue directly to Module 3 when all gates pass.

# Continue NBSGCT Big Upgrade - Module 3

Work in:
`C:\Users\Ecosoul Enviro\OneDrive\Desktop\NBSGCT`

Read `AGENTS.md`, `codex prompt.txt`, and
`CODEX_BIG_UPGRADE_HANDOFF.md` first.

Modules 1 and 2 are complete. Continue autonomously with Module 3:
User-facing language and responsive polish.

Required work:

1. Fix the 390px input-modal overflow around pollution source context and
   intervention position by stacking fields vertically at narrow widths.
2. Verify upload page, Summary, Ranking, component cards, chips, workspace tabs,
   evidence panels, and data-gap panels at 390x844, 768x1024, and desktop.
3. Replace remaining confusing copy with the preferred professional language
   from `codex prompt.txt`, including Technical match, Result confidence,
   Water-quality input, Important limitation, What this means, and
   Water-quality values used.
4. Explain blanks, unknown values, skipped rows, match versus confidence, and
   treatment train versus individual component concisely.
5. Ensure invalid CSV messaging says:
   `No usable water-quality values found.`
6. Do not overstuff the home screen or introduce decorative gimmicks.
7. Add/update widget tests for all three viewport classes and zero overflow.

After the module, run backend pytest, Flutter analyze, Flutter tests, and
`git diff --check`. Refresh both continuation files, attempt the scoped commit
`Module 3: Polish responsive UI and user-facing language`, and continue to
Module 4 when all gates pass. If commit alone is blocked by approval limits,
create the required module snapshot/status files and continue intentionally.

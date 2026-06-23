# Next Codex Prompt

Continue from the committed final demo hardening patch.

First read:

- `AGENTS.md`
- `CODEX_BIG_UPGRADE_HANDOFF.md`
- `codex prompt.txt`

Current verified state:

- Backend tests pass: `67 passed`
- Flutter analyze passes
- Flutter tests pass: `25 passed`
- `git diff --check` is clean except line-ending warnings

Do not rework the final v1 AHP-Fuzzy AHP weights unless the user supplies a new expert-approved weight set.

Recommended next work:

1. Manual QA the four demo flows in Flutter web.
2. Inspect print/PDF output in Microsoft Print to PDF.
3. Verify CSV opens in Excel with aligned columns.
4. Decide whether to commit or clean old untracked artifacts such as previous checkpoint files and stale visual failure outputs.
5. Prepare post-demo docs only after the user approves cleanup.

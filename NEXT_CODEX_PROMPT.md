# Next Codex Prompt

Continue the final demo hardening patch in `C:\Users\Ecosoul Enviro\OneDrive\Desktop\NBSGCT`.

Read `AGENTS.md`, `codex prompt.txt`, and `CODEX_FINAL_DEMO_HARDENING_HANDOFF.md` first. The source implementation is complete but uncommitted because the new Flutter packages could not be downloaded after the tool account reached its usage limit.

Do not add features or clean unrelated untracked files. Do not replace canonical data. Do not commit until every gate passes.

Exact work:

1. From `frontend`, run `flutter pub get` with network access. Confirm `pubspec.lock` updates for `flutter_svg`, `flutter_map`, and `latlong2`.
2. Run `flutter analyze`. Fix all compile/analyzer issues with small scoped changes, especially any Flutter Map 8 API differences.
3. Run `flutter test`. Fix all failures and responsive overflows. Tests must not require internet.
4. From `backend`, run `..\.venv_canonical\Scripts\python.exe -m pytest -q`; expected baseline is 65 passing tests.
5. Run `git diff --check` and inspect `git status --short`.
6. Update `CODEX_FINAL_DEMO_HARDENING_HANDOFF.md` with final Flutter results and remove the active-blocker wording only after verification.
7. Stage only scoped source/tests/assets, `frontend/pubspec.lock`, `CODEX_FINAL_DEMO_HARDENING_HANDOFF.md`, and `NEXT_CODEX_PROMPT.md`. Do not stage prompt, checkpoint, golden, zip, `.claude`, or `.dart-tool-home` artifacts.
8. Commit exactly: `Final demo hardening for maps diagrams and trust`.

After commit, report the commit hash and the backend, Flutter analyze, Flutter test, and diff-check results.

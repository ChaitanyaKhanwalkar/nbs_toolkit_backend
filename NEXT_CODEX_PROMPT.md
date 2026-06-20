# Next Codex Prompt

Work in `C:\Users\Ecosoul Enviro\OneDrive\Desktop\NBSGCT`.

Read `AGENTS.md`, `codex prompt.txt`, `CODEX_PHASE_EF_HANDOFF.md`, the available
project handoffs, and canonical-data documentation before editing.

Phase E+F is complete. First verify:

1. backend pytest
2. Flutter analyze
3. Flutter tests
4. `git diff --check`

Recommended next phase: field/design-input collection and preliminary planning
workflow.

- Add a progressive design-input form for design flow, peak flow, available
  land, groundwater, flood risk, inlet/outlet levels, slope/soil verification,
  and O&M ownership.
- Keep every field optional until supplied; missing remains unknown, never zero.
- Preserve the Phase E+F readiness engine as the backend authority.
- Do not substitute stored river discharge for wastewater/design flow.
- Show units and validation clearly without implying engineering approval.
- Add interactive browser QA when the Windows in-app browser sandbox is
  available.
- Do not add external map tiles, fabricated coordinates, design values, expert
  weights, health-risk values, or unreviewed citations.
- Preserve train-first wastewater logic, A0-before-ranking, industrial
  pretreatment, pH neutralization, mainstem off-channel safety, agricultural
  source control, and invasive-plant safeguards.

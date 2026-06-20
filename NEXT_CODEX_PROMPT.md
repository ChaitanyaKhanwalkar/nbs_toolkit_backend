# Recommended Future Work After the Big Upgrade

The four approved upgrade modules are complete. Before further implementation:

1. Run the backend and Flutter web app together.
2. Review these cases interactively:
   - domestic sewage with BOD/COD/TSS/pH
   - industrial wastewater at pH 3
   - high-order/mainstem site-only context
   - agricultural pollution-source screening
   - valid, partial, and invalid CSV uploads
3. Confirm the catalogue and component wording with the scientific reviewer.
4. Select the next scoped priority:
   - expert calibration workflow for criteria weights and confidence rules
   - richer source/citation browser
   - authenticated project saving and comparison
   - PDF/CSV decision-report export
   - field monitoring and longitudinal sample management
   - accessibility/localization audit
   - deployment and production observability

Preserve these constraints in future work:

- Do not replace or mutate the canonical database without an approved migration.
- Do not invent health-risk values, standards, weights, efficiencies, or sources.
- Keep A0 before ranking and confidence separate from technical match.
- Keep treatment trains primary for wastewater.
- Keep industrial, pH, mainstem, agricultural, and invasive-plant safeguards.

Current verified baseline:

- backend pytest: 43 passed
- Flutter analyze: no issues
- Flutter tests: 10 passed
- git diff --check: clean

# Schemas

This folder defines safe JSON shapes for future API routes.

Schemas are Pydantic models. They explain what the backend may return to a
frontend or another client. For now, these schemas are read-only response shapes
for raw data packets from the service layer.

Use schemas here for:

- reference data responses
- site profile responses
- raw water observation responses
- standards lookup responses
- NbS catalogue responses
- plant catalogue responses
- pollution context responses
- river context responses
- data availability responses
- internal scientific engine bundle responses from Steps A-I
- internal scientific workflow result responses that wrap staged A-E bundles

Do not put database queries here. Repositories query the database.

Do not put scientific scoring here. Future engine modules will calculate
approved scientific outputs only after the repository, service, engine, and
schema layers are ready.

`engine.py` contains read-only response shapes for existing internal engine
bundles and the internal `ScientificWorkflowResult` wrapper. These schemas are
for safe future serialization and tests only. They do not create routes or run
workflow logic. Step I schemas can serialize TOPSIS rank/closeness outputs, but
they do not rename `topsis_closeness` to `match_score`, calculate confidence,
recommend plants, classify health risk, or create final recommendations.

Do not add final recommendation fields, AHP pairwise logic, confidence-score
fields, plant recommendation fields, or health-risk classifications until that
logic is explicitly implemented from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

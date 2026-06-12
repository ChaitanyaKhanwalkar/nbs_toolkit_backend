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
- internal scientific engine bundle responses from Steps A-K and Step L-A
- internal scientific workflow result responses that wrap staged A-J or A-K bundles

Do not put database queries here. Repositories query the database.

Do not put scientific scoring here. Future engine modules will calculate
approved scientific outputs only after the repository, service, engine, and
schema layers are ready.

`engine.py` contains read-only response shapes for existing internal engine
bundles and the internal `ScientificWorkflowResult` wrapper. These schemas are
for safe future serialization and tests only. They do not create routes or run
workflow logic. Step I schemas can serialize TOPSIS rank/closeness outputs, but
they do not rename `topsis_closeness` to `match_score`. Step J schemas can
serialize confidence scores separately from TOPSIS closeness and preserve rank.
Step K schemas serialize explicitly mapped plants after ranking/confidence. The
workflow result schema can include an optional Step K bundle when
`max_step="K"` is requested, but it does not let plants affect rank,
confidence, health risk, or final recommendations. Step L-A schemas serialize
internal assembled recommendation objects and may include `match_score` only as
a direct copy of `topsis_closeness`; they still do not create API route fields
or `/recommend`.

Do not add endpoint-facing recommendation fields, AHP pairwise logic, plant
recommendation fields, or health-risk classifications until that logic is
explicitly implemented from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md`.

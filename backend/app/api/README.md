# API

This folder contains FastAPI route definitions for the production backend.

Routes are thin wrappers. They should:

- receive HTTP GET requests
- use `app.db.session.get_db` for a database session
- call service classes in `backend/app/services/`
- return Pydantic response shapes from `backend/app/schemas/`

Routes should not query database tables directly. Repositories handle database
queries, and services prepare raw data packets.

Current routes are read-only raw data access routes under `/api/v1`.

Do not add POST, PUT, PATCH, or DELETE routes unless a future task explicitly
asks for them.

Do not add `/recommend` here yet. Recommendation logic must follow
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` and should only be built
after the repository, service, engine, and schema layers are ready.

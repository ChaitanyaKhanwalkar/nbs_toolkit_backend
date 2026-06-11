# Repositories

Repositories are read-only database access classes.

API routes and future services should use repositories instead of querying
tables directly. This keeps database access in one layer and makes the backend
easier to test.

Current rules:

- Return ORM objects, lists, dictionaries, `None`, or empty lists.
- Do not create, update, or delete rows.
- Do not calculate recommendation scores, rankings, exceedances, health risk,
  AHP weights, or treatment suitability.
- Keep provenance fields such as `source_id` visible in returned objects.

Example use in a future service:

```python
repository = WaterRepository(session)
observations = repository.get_observations_by_station("Station name")
```

For import and local-dev query checks, see `backend/tests/repository_smoke_test.py`.

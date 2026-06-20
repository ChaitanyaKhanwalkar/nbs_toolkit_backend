# Services

Services prepare raw data packets for future API schemas and scientific engines.

They sit above repositories:

- repositories read database tables
- services combine repository results into useful raw-data structures
- future engines may use service outputs for scientific calculations later

Current rules:

- Services accept a SQLAlchemy `Session` in the constructor.
- Services create the repositories they need internally.
- Services return dictionaries, lists, `None`, empty lists, and `missing_sections`.
- Services do not mutate database records.
- Services do not calculate pollutant exceedance, health risk, AHP weights, TOPSIS rankings, or recommendations.
- Services should preserve `source_id` fields where the data includes them.
- `scientific_workflow_service.py` coordinates existing Scientific Engine Steps A-E and returns staged bundles only.
- `location_context_service.py` combines site/profile records with request
  context for display and safety flags. It never fabricates a map point or
  design input and does not rank candidates.

Do not create a `recommendation_service.py` until the project is ready for real recommendation logic.

The scientific workflow service is internal backend orchestration. It does not expose an endpoint, create final recommendations, rank candidates, choose plants, classify health risk, or add TOPSIS/AHP outputs.

To smoke test the internal workflow service from `backend/`:

```cmd
set PYTHONPATH=%CD%
python tests\scientific_workflow_service_test.py
```

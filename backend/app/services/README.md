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

Do not create a `recommendation_service.py` until the project is ready for real recommendation logic.

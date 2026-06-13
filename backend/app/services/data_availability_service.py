"""Service for raw data availability checks.

This service reports whether major data groups exist for a site/use case/NbS
selection. It returns booleans, counts, and missing section names only. It does
not decide whether a recommendation is valid.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.repositories import (
    NbsRepository,
    PlantRepository,
    SiteRepository,
    StandardsRepository,
    WaterRepository,
)


class DataAvailabilityService:
    """Prepare raw availability summaries from repository counts."""

    def __init__(self, session: Session) -> None:
        self.nbs = NbsRepository(session)
        self.plants = PlantRepository(session)
        self.sites = SiteRepository(session)
        self.standards = StandardsRepository(session)
        self.water = WaterRepository(session)

    def report_availability(
        self,
        *,
        region_id: int | None = None,
        station: str | None = None,
        use_case: str | None = None,
        nbs_id: int | None = None,
    ) -> dict[str, Any]:
        """Return booleans/counts for key raw data groups."""

        site_attributes = self.sites.get_site_attributes(region_id) if region_id else None
        stream_attributes = (
            self.sites.get_site_stream_attributes(region_id=region_id)
            if region_id
            else []
        )
        water_observations = (
            self.water.get_observations_by_station(station)
            if station
            else []
        )
        standards = (
            self.standards.get_standards_for_use_case(use_case)
            if use_case
            else []
        )
        nbs_options = self.nbs.list_options()
        plant_mapping_count = self.plants.count_plant_mappings(nbs_id)

        sections = {
            "site_profile": {
                "available": site_attributes is not None,
                "count": 1 if site_attributes is not None else 0,
            },
            "stream_attributes": {
                "available": bool(stream_attributes),
                "count": len(stream_attributes),
            },
            "water_observations": {
                "available": bool(water_observations),
                "count": len(water_observations),
            },
            "standards": {
                "available": bool(standards),
                "count": len(standards),
            },
            "nbs_catalogue": {
                "available": bool(nbs_options),
                "count": len(nbs_options),
            },
            "plant_mappings": {
                "available": plant_mapping_count > 0,
                "count": plant_mapping_count,
                "requires_nbs_id": nbs_id is None,
            },
        }

        missing_sections = [
            name for name, details in sections.items() if not details["available"]
        ]

        return {
            "inputs": {
                "region_id": region_id,
                "station": station,
                "use_case": use_case,
                "nbs_id": nbs_id,
            },
            "sections": sections,
            "missing_sections": missing_sections,
        }

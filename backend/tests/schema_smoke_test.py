"""Smoke test for importing raw response schemas.

Run this file from the backend folder to confirm the schema layer imports and
basic validation works. It does not connect to a database and does not run
recommendation logic.
"""

from app.schemas import (
    DataAvailabilityResponse,
    NbsFullProfileResponse,
    ReferenceDataResponse,
    SiteProfileResponse,
    WaterObservationResponse,
)


def main() -> None:
    """Import and instantiate a few representative schemas."""

    water = WaterObservationResponse(station="Example", parameter="pH")
    reference = ReferenceDataResponse()
    site = SiteProfileResponse(missing_sections=["site_attributes"])
    nbs = NbsFullProfileResponse(missing_sections=["criteria"])
    availability = DataAvailabilityResponse(
        inputs={"region_id": 1},
        sections={"site_profile": {"available": False, "count": 0}},
        missing_sections=["site_profile"],
    )

    checked = [
        water.model_dump(),
        reference.model_dump(),
        site.model_dump(),
        nbs.model_dump(),
        availability.model_dump(),
    ]
    print(f"schema imports ok: {len(checked)} representative schemas")


if __name__ == "__main__":
    main()

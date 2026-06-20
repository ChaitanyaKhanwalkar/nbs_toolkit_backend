"""Build verified, user-facing location context from canonical site records.

The service reads existing profile data through ``SiteProfileService`` and
combines it with request context. It never fabricates coordinates or design
values and does not score recommendation candidates.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.services.site_profile_service import SiteProfileService


class LocationContextService:
    """Prepare one concise location-intelligence packet for a recommendation."""

    def __init__(self, session: Session) -> None:
        self.profiles = SiteProfileService(session)

    def build(
        self,
        *,
        region_id: int | None,
        station: str | None,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Return verified location fields and transparent safety flags."""

        profile = self.profiles.get_site_profile(region_id) if region_id else None
        return build_location_context(
            profile=profile,
            region_id=region_id,
            station=station,
            context=context,
        )


def build_location_context(
    *,
    profile: dict[str, Any] | None,
    region_id: int | None,
    station: str | None,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Assemble location context from supplied verified records only."""

    profile = profile or {}
    region = profile.get("region") or {}
    basin = profile.get("basin") or {}
    site = profile.get("site_attributes") or {}
    streams = profile.get("site_stream_attributes") or []
    stream = streams[0] if streams else {}

    stream_order = _first(
        stream.get("stream_order"),
        stream.get("ord_clas"),
        site.get("stream_order"),
        context.get("stream_order"),
    )
    source_type = context.get("pollution_source_type")
    position = context.get("intervention_position")
    high_order = _number(stream_order) >= 5
    in_channel = position == "in_channel"
    industrial = "industrial" in str(source_type or "").lower()
    agricultural = "agri" in str(source_type or "").lower()

    latitude = _first(stream.get("station_lat"), region.get("lat"))
    longitude = _first(stream.get("station_lon"), region.get("lon"))
    coordinates_available = latitude is not None and longitude is not None
    if not coordinates_available:
        latitude = None
        longitude = None

    resolved_station = _first(station, site.get("station"), region.get("station"))
    missing = []
    for value, label in (
        (resolved_station, "Site or station name"),
        (_first(basin.get("basin"), region.get("river")), "Basin or river context"),
        (region.get("district"), "District"),
        (stream_order, "Stream order"),
        (position, "Intervention position"),
        (source_type, "Pollution source context"),
    ):
        if value is None:
            missing.append(label)
    if not coordinates_available:
        missing.append("Verified coordinates")

    off_channel_required = high_order or in_channel
    notes = []
    if off_channel_required:
        notes.append(
            "Off-channel treatment only. Do not build treatment cells inside the river channel."
        )
    if industrial:
        notes.append("Industrial source context requires ETP/CETP pretreatment review.")
    if agricultural:
        notes.append("Prioritize field and edge-of-field source control first.")
    if missing:
        notes.append("Where site data is missing, the result remains planning-level.")

    return {
        "region_id": region_id,
        "station": resolved_station,
        "river": region.get("river"),
        "district": region.get("district"),
        "basin": basin.get("basin"),
        "sub_basin": basin.get("sub_basin"),
        "stream_order": stream_order,
        "stream_context": (
            "Mainstem or high-order river" if high_order else "Lower-order or unconfirmed"
        ),
        "intervention_position": position,
        "pollution_source_type": source_type,
        "pollution_source_record_count": context.get("pollution_source_record_count"),
        "river_discharge_cms": _first(
            stream.get("river_discharge_cms"),
            site.get("nat_discharge_cms"),
        ),
        "drainage_area_km2": _first(
            stream.get("catch_skm"),
            site.get("drainage_area_km2"),
        ),
        "slope_mean": site.get("slope_mean"),
        "soil_type": region.get("soil_type"),
        "infiltration_class": region.get("infiltration_class"),
        "coordinates_available": coordinates_available,
        "latitude": latitude,
        "longitude": longitude,
        "context_flags": {
            "mainstem_or_high_order": high_order,
            "off_channel_required": off_channel_required,
            "industrial_pretreatment_required": industrial,
            "agricultural_source_control_first": agricultural,
            "site_context_incomplete": bool(missing),
        },
        "missing_site_information": missing,
        "context_notes": notes,
    }


def _first(*values: Any) -> Any:
    """Return the first non-null value without treating zero as missing."""

    return next((value for value in values if value is not None), None)


def _number(value: Any) -> float:
    """Return a numeric comparison value while preserving unknown as zero."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

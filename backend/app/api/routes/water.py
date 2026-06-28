"""Water observation lookup and non-persistent CSV analysis routes.

These endpoints return measured water-quality records and parameter counts.
They never compare observations with standards or calculate exceedance.
"""

import csv
from io import StringIO
from math import isfinite
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.engines import PollutantGapEngine, WaterInputBundle
from app.schemas import WaterObservationResponse, WaterParameterSummaryResponse
from app.services import WaterDataService

router = APIRouter(prefix="/water", tags=["water"])


PARAMETER_ALIASES = {
    "bod": "bod",
    "bod5": "bod",
    "biological oxygen demand": "bod",
    "biochemical oxygen demand": "bod",
    "cod": "cod",
    "chemical oxygen demand": "cod",
    "tss": "tss",
    "suspended solids": "tss",
    "total suspended solids": "tss",
    "nh4": "ammonia_n",
    "nh4 n": "ammonia_n",
    "ammonia": "ammonia_n",
    "ammonia n": "ammonia_n",
    "nitrate": "nitrate_n",
    "nitrate n": "nitrate_n",
    "no3": "nitrate_n",
    "no3 n": "nitrate_n",
    "phosphate": "phosphate_p",
    "phosphate p": "phosphate_p",
    "phosphate phosphorus": "phosphate_p",
    "orthophosphate": "phosphate_p",
    "ortho phosphate": "phosphate_p",
    "po4": "phosphate_p",
    "po4 p": "phosphate_p",
    "tp": "phosphate_p",
    "total phosphorus": "phosphate_p",
    "phosphorus": "phosphate_p",
    "ph": "ph",
    "do": "do",
    "dissolved oxygen": "do",
    "tds": "tds",
    "ec": "ec",
    "electrical conductivity": "ec",
    "conductivity": "ec",
    "specific conductance": "ec",
    "turbidity": "turbidity",
    "faecal coliform": "faecal_coliform",
    "fecal coliform": "faecal_coliform",
    "fc": "faecal_coliform",
}

PARAMETER_DISPLAY_NAMES = {
    "bod": "BOD",
    "cod": "COD",
    "tss": "TSS",
    "ammonia_n": "NH4-N",
    "nitrate_n": "NO3-N",
    "phosphate_p": "PO4-P / TP",
    "ph": "pH",
    "do": "DO",
    "tds": "TDS",
    "ec": "EC",
    "turbidity": "Turbidity",
    "faecal_coliform": "Faecal coliform",
}


def _alias_key(value: Any) -> str:
    """Return a small, readable match key for supported CSV aliases."""

    text = str(value or "").strip().lower()
    for character in ("_", "-", "."):
        text = text.replace(character, " ")
    return " ".join(text.split())


def _new_validation_summary() -> dict[str, Any]:
    """Return an empty structured CSV validation summary."""

    return {
        "rows_read": 0,
        "rows_used": 0,
        "blank_rows": 0,
        "blank_parameters": 0,
        "blank_values": 0,
        "unknown_parameters": [],
        "non_numeric_values": [],
        "missing_headers": [],
        "warnings": [],
        "errors": [],
        "is_valid": False,
    }


def _normalize_unit(value: Any) -> str:
    """Normalize common unit spellings without performing unit conversion."""

    text = str(value or "").strip()
    key = text.lower().replace(" ", "")
    aliases = {
        "mg/l": "mg_l",
        "mgl": "mg_l",
        "mg_l": "mg_l",
        "µs/cm": "umho_cm",
        "μs/cm": "umho_cm",
        "us/cm": "umho_cm",
        "us_cm": "umho_cm",
        "micros/cm": "umho_cm",
        "microsiemens/cm": "umho_cm",
        "micromho/cm": "umho_cm",
        "micromhos/cm": "umho_cm",
        "umho/cm": "umho_cm",
        "umho_cm": "umho_cm",
        "umhos/cm": "umho_cm",
        "mpn/100ml": "mpn_100ml",
        "mpn_100ml": "mpn_100ml",
        "phunits": "ph_units",
        "ph_units": "ph_units",
        "ntu": "ntu",
    }
    return aliases.get(key, text)


@router.get(
    "/stations/{station}/observations",
    response_model=list[WaterObservationResponse],
)
def get_station_observations(
    station: str,
    db: Annotated[Session, Depends(get_db)],
    parameter: Annotated[str | None, Query(description="Optional exact parameter name.")] = None,
) -> list[dict[str, object]]:
    """Return raw observations for one station, optionally for one parameter."""

    service = WaterDataService(db)
    if parameter:
        grouped = service.get_observations_for_parameters(station, [parameter])
        return grouped.get(parameter, [])
    return service.get_observations_by_station(station)


@router.get(
    "/basins/{basin_id}/observations",
    response_model=list[WaterObservationResponse],
)
def get_basin_observations(
    basin_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return raw observations for one basin ID."""

    return WaterDataService(db).get_observations_by_basin(basin_id)


@router.get("/parameters", response_model=list[WaterParameterSummaryResponse])
def list_water_parameters(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return stored water-quality parameter names and raw row counts."""

    return WaterDataService(db).summarize_available_parameters()


@router.post("/upload")
async def analyze_uploaded_csv(
    file: Annotated[UploadFile, File(description="CSV with parameter,value,unit columns")],
    use_case: Annotated[str, Query()] = "discharge_inland",
    db: Annotated[Session, Depends(get_db)] = None,
) -> dict[str, Any]:
    """Parse a small CSV and calculate gaps without persisting user data."""

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload must be a CSV file.")
    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must use UTF-8 encoding.") from exc

    summary = _new_validation_summary()
    reader = csv.DictReader(StringIO(text))
    normalized_headers = [
        str(name or "").strip().lower() for name in (reader.fieldnames or [])
    ]
    required_headers = {"parameter", "value"}
    missing_headers = sorted(required_headers.difference(normalized_headers))
    if missing_headers:
        summary["missing_headers"] = missing_headers
        summary["errors"].append(
            "CSV must include parameter and value columns. The unit column is optional."
        )
        raise HTTPException(
            status_code=400,
            detail={
                "message": summary["errors"][0],
                "csv_validation_summary": summary,
            },
        )
    reader.fieldnames = normalized_headers

    observations: list[dict[str, Any]] = []
    blank_value_parameters: list[str] = []
    for index, row in enumerate(reader, start=2):
        summary["rows_read"] += 1
        normalized = {
            str(key or "").strip().lower(): str(value or "").strip()
            for key, value in row.items()
        }
        if not any(normalized.values()):
            summary["blank_rows"] += 1
            continue

        raw_parameter = normalized.get("parameter", "")
        if not raw_parameter:
            summary["blank_parameters"] += 1
            summary["warnings"].append(f"Row {index}: blank parameter name was skipped.")
            continue
        parameter = PARAMETER_ALIASES.get(_alias_key(raw_parameter))
        if parameter is None:
            summary["unknown_parameters"].append(f"Row {index}: {raw_parameter}")
            summary["warnings"].append(
                f"Row {index}: unknown parameter '{raw_parameter}' was skipped."
            )
            continue

        raw_value = str(normalized.get("value") or "").strip()
        if not raw_value:
            summary["blank_values"] += 1
            blank_value_parameters.append(parameter)
            summary["warnings"].append(
                f"Row {index}: {PARAMETER_DISPLAY_NAMES[parameter]} is blank and remains unknown."
            )
            continue
        try:
            value = float(raw_value)
        except ValueError:
            value = None
        if value is None or not isfinite(value):
            summary["non_numeric_values"].append(
                f"Row {index}: {raw_parameter}={raw_value}"
            )
            summary["warnings"].append(
                f"Row {index}: non-numeric value for '{raw_parameter}' was skipped."
            )
            continue
        observations.append(
            {
                "parameter": parameter,
                "display_name": PARAMETER_DISPLAY_NAMES[parameter],
                "value": value,
                "unit": _normalize_unit(normalized.get("unit")),
                "source": "user_csv",
            }
        )

    summary["rows_used"] = len(observations)
    summary["is_valid"] = bool(observations)
    if not observations:
        summary["errors"].append("No usable water-quality values found.")

    bundle = WaterInputBundle(
        selected_source_type="user_measured",
        observations=observations,
        observation_count=len(observations),
        selected_parameters=[row["parameter"] for row in observations],
        use_case=use_case,
        data_quality_notes=[
            "Parsed from a user-uploaded CSV; values were not persisted.",
            *summary["warnings"],
        ],
    )
    gaps = PollutantGapEngine.from_session(db).calculate(bundle, use_case=use_case)
    return {
        "filename": file.filename,
        "use_case": use_case,
        "observation_count": len(observations),
        "unknown_parameter_count": summary["blank_values"],
        "unknown_parameters": blank_value_parameters,
        "observations": observations,
        "observations_used": observations,
        "csv_validation_summary": summary,
        "contaminant_gaps": gaps.to_dict(),
    }

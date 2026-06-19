"""Water observation lookup and non-persistent CSV analysis routes.

These endpoints return measured water-quality records and parameter counts.
They never compare observations with standards or calculate exceedance.
"""

import csv
from io import StringIO
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.engines import PollutantGapEngine, WaterInputBundle
from app.schemas import WaterObservationResponse, WaterParameterSummaryResponse
from app.services import WaterDataService

router = APIRouter(prefix="/water", tags=["water"])


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

    reader = csv.DictReader(StringIO(text))
    required = {"parameter", "value", "unit"}
    if not reader.fieldnames or not required.issubset(
        {name.strip().lower() for name in reader.fieldnames}
    ):
        raise HTTPException(
            status_code=400,
            detail="CSV must include parameter, value, and unit columns.",
        )

    observations: list[dict[str, Any]] = []
    unknown_parameters: list[str] = []
    for index, row in enumerate(reader, start=2):
        normalized = {str(key).strip().lower(): value for key, value in row.items()}
        parameter = str(normalized.get("parameter") or "").strip()
        raw_value = str(normalized.get("value") or "").strip()
        if not parameter:
            raise HTTPException(
                status_code=400,
                detail=f"Row {index} is missing a parameter name.",
            )
        if not raw_value:
            unknown_parameters.append(parameter)
            continue
        try:
            value = float(raw_value)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Row {index} has a non-numeric value.",
            ) from exc
        observations.append(
            {
                "parameter": parameter,
                "value": value,
                "unit": str(normalized.get("unit") or "").strip(),
                "source": "user_upload",
            }
        )

    bundle = WaterInputBundle(
        selected_source_type="user_measured",
        observations=observations,
        observation_count=len(observations),
        selected_parameters=[row["parameter"] for row in observations],
        use_case=use_case,
        data_quality_notes=[
            "Parsed from a user-uploaded CSV; values were not persisted.",
            *(
                ["Blank values were retained as unknown parameters and were not treated as zero."]
                if unknown_parameters
                else []
            ),
        ],
    )
    gaps = PollutantGapEngine.from_session(db).calculate(bundle, use_case=use_case)
    return {
        "filename": file.filename,
        "use_case": use_case,
        "observation_count": len(observations),
        "unknown_parameter_count": len(unknown_parameters),
        "unknown_parameters": unknown_parameters,
        "observations": observations,
        "contaminant_gaps": gaps.to_dict(),
    }

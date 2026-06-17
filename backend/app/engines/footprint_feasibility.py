"""C6 engine for NbS footprint feasibility (land requirement).

Implements the MCDA criterion **C6 — Footprint feasibility** from
`backend/docs/SCIENTIFIC_RECOMMENDATION_ENGINE.md` (section 12.6).

Site-specific available-area data is not yet ingested, so this scores the
**technology land requirement** from real `nbs_footprint` values
(`area_per_pe_*`): more land demand = worse. It emits a numeric
`footprint_requirement` (a **cost** criterion that Step G normalizes so lower
demand normalizes higher). This uses only sourced catalogue numbers — nothing is
invented. When footprint data is missing the criterion is left unscored and a
confidence-lowering note is added.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


FOOTPRINT_STATUS_SOURCED = "sourced_catalogue"
FOOTPRINT_STATUS_DATA_PENDING = "data_pending"


@dataclass(slots=True)
class FootprintFeasibilityResult:
    """C6 land-requirement value (cost) plus its transparent breakdown."""

    footprint_requirement: float | None
    area_per_pe_used: float | None
    basis: str | None
    status: str
    used_inputs: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary for matrix rows, tests, or future APIs."""

        return asdict(self)


def compute_footprint_requirement(
    footprint_rows: list[dict[str, Any]] | None,
) -> FootprintFeasibilityResult:
    """Score technology land requirement from sourced area-per-PE values."""

    notes: list[str] = []
    used_inputs: list[str] = []
    rows = footprint_rows or []

    mids = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        low = _as_float(row.get("area_per_pe_low"))
        high = _as_float(row.get("area_per_pe_high"))
        if low is not None and high is not None:
            mids.append((low + high) / 2)
        elif low is not None:
            mids.append(low)
        elif high is not None:
            mids.append(high)

    if not mids:
        notes.append(
            "No numeric area_per_pe footprint data available; C6 left unscored "
            "and confidence lowered."
        )
        return FootprintFeasibilityResult(
            footprint_requirement=None,
            area_per_pe_used=None,
            basis=None,
            status=FOOTPRINT_STATUS_DATA_PENDING,
            used_inputs=used_inputs,
            missing_inputs=["footprint_area_per_pe"],
            notes=notes,
        )

    used_inputs.append("area_per_pe")
    area = sum(mids) / len(mids)
    notes.append(
        f"footprint_requirement={round(area, 4)} (mean area_per_pe across "
        f"{len(mids)} sourced footprint row(s)); cost criterion, lower is better. "
        "Site available-area not yet ingested, so this is technology-relative only."
    )
    return FootprintFeasibilityResult(
        footprint_requirement=area,
        area_per_pe_used=area,
        basis="area_per_pe",
        status=FOOTPRINT_STATUS_SOURCED,
        used_inputs=used_inputs,
        missing_inputs=[],
        notes=notes,
    )


def _as_float(value: Any) -> float | None:
    """Convert a scalar value to float without accepting booleans."""

    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

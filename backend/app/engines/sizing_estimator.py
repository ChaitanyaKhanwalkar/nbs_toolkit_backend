"""Build screening-level land estimates from canonical footprint evidence.

The estimator performs only transparent arithmetic on user-supplied flow or
population and stored component footprint/loading ranges. It never substitutes
river discharge for design flow and never fills missing canonical values.
"""

from collections import defaultdict
from typing import Any

from app.repositories import EngineDataRepository


class SizingEstimator:
    """Estimate train footprints while preserving evidence coverage gaps."""

    def __init__(self, repository: EngineDataRepository) -> None:
        self.repository = repository

    def estimate(
        self,
        *,
        ranked_trains: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Return one screening estimate for each ranked treatment train."""

        rows_by_train: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in self.repository.list_train_component_footprints():
            rows_by_train[int(row["train_id"])].append(row)
        return [
            _estimate_train(
                train=train,
                rows=rows_by_train.get(int(train["train_id"]), []),
                context=context,
            )
            for train in ranked_trains
        ]


def _estimate_train(
    *,
    train: dict[str, Any],
    rows: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Calculate one evidence-bounded train estimate."""

    component_ids = {
        int(row["nbs_id"])
        for row in train.get("nbs_components") or []
        if row.get("nbs_id") is not None
    }
    by_component: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("nbs_id") is not None:
            by_component[int(row["nbs_id"])].append(row)

    population = _positive(context.get("population_equivalent"))
    design_flow = _positive(context.get("design_flow_m3_d"))
    available_land = _positive(context.get("available_land_m2"))
    pe_band = _per_person_band(by_component)
    flow_band = _flow_band(by_component, design_flow)
    flow_evidence_count = _flow_evidence_count(by_component)
    component_count = len(component_ids)

    estimate_low = None
    estimate_high = None
    basis = "insufficient_data"
    coverage_count = 0
    inputs_used: list[str] = []
    if design_flow is not None and flow_band[0] is not None:
        estimate_low, estimate_high, coverage_count = flow_band
        basis = "design_flow"
        inputs_used.append(f"Design flow: {design_flow:g} m³/day")
    elif population is not None and pe_band[0] is not None:
        estimate_low = pe_band[0] * population
        estimate_high = pe_band[1] * population
        coverage_count = pe_band[2]
        basis = "population_equivalent"
    elif pe_band[0] is not None:
        coverage_count = pe_band[2]
        basis = "area_per_person_band"
    if population is not None:
        inputs_used.append(f"Population equivalent: {population:g}")

    full_coverage = component_count > 0 and coverage_count == component_count
    if not full_coverage:
        estimate_low = None
        estimate_high = None
        if coverage_count:
            basis = "component_only_incomplete"
    if available_land is not None:
        inputs_used.append(f"Available land: {available_land:g} m²")
    land_fit = _land_fit(
        available_land=available_land,
        estimate_low=estimate_low,
        estimate_high=estimate_high,
        full_coverage=full_coverage,
    )
    missing = []
    if basis == "area_per_person_band" and population is None:
        missing.append("Population or population equivalent")
    elif basis == "insufficient_data":
        if flow_evidence_count and design_flow is None:
            missing.append("Design flow")
        if pe_band[0] is not None and population is None:
            missing.append("Population or population equivalent")
    if available_land is None:
        missing.append("Available land")
    if not full_coverage:
        missing.append("Canonical footprint data for every train component")

    per_person_label = None
    if pe_band[0] is not None:
        per_person_label = f"{pe_band[0]:g}-{pe_band[1]:g} m²/person"
    estimate_label = _estimate_label(
        estimate_low=estimate_low,
        estimate_high=estimate_high,
        per_person_label=per_person_label,
        full_coverage=full_coverage,
        basis=basis,
        population_supplied=population is not None,
        design_flow_supplied=design_flow is not None,
    )
    source_ids = sorted(
        {
            int(row["source_id"])
            for row in rows
            if row.get("source_id") is not None
        }
    )
    return {
        "train_id": int(train["train_id"]),
        "train_name": train.get("name"),
        "basis": basis,
        "flow_status": "supplied" if design_flow is not None else "not_supplied",
        "population_status": (
            "supplied" if population is not None else "not_supplied"
        ),
        "sizing_confidence": (
            "screening_band"
            if estimate_low is not None and full_coverage
            else "insufficient_data"
        ),
        "estimate_label": estimate_label,
        "estimated_area_low_m2": estimate_low,
        "estimated_area_high_m2": estimate_high,
        "area_per_person_band": per_person_label,
        "land_fit": land_fit,
        "full_component_coverage": full_coverage,
        "covered_component_count": coverage_count,
        "train_component_count": component_count,
        "inputs_used": inputs_used,
        "missing_inputs": missing,
        "key_assumptions": _assumptions(basis)
        if estimate_low is not None
        else [],
        "design_caution": (
            "This is a screening estimate, not final design. Final sizing needs "
            "confirmed hydraulics, pollutant loads, setbacks, access, freeboard, hydraulic profile, "
            "inlet and outlet levels, sludge handling, flood safety, land ownership, design margins, "
            "and a site survey."
        ),
        "source_ids": source_ids,
    }


def _per_person_band(
    by_component: dict[int, list[dict[str, Any]]],
) -> tuple[float | None, float | None, int]:
    """Return the summed envelope of stored component m2/person ranges."""

    lows: list[float] = []
    highs: list[float] = []
    for rows in by_component.values():
        row_lows = [_positive(row.get("area_per_pe_low")) for row in rows]
        row_highs = [_positive(row.get("area_per_pe_high")) for row in rows]
        known_lows = [value for value in row_lows if value is not None]
        known_highs = [value for value in row_highs if value is not None]
        if known_lows and known_highs:
            lows.append(min(known_lows))
            highs.append(max(known_highs))
    if not lows:
        return None, None, 0
    return sum(lows), sum(highs), len(lows)


def _flow_band(
    by_component: dict[int, list[dict[str, Any]]],
    design_flow: float | None,
) -> tuple[float | None, float | None, int]:
    """Return summed areas from stored hydraulic loading-rate envelopes."""

    if design_flow is None:
        return None, None, 0
    lows: list[float] = []
    highs: list[float] = []
    for rows in by_component.values():
        rates = [_positive(row.get("hlr_m3_m2_d")) for row in rows]
        known = [value for value in rates if value is not None]
        if known:
            lows.append(design_flow / max(known))
            highs.append(design_flow / min(known))
    if not lows:
        return None, None, 0
    return sum(lows), sum(highs), len(lows)


def _flow_evidence_count(
    by_component: dict[int, list[dict[str, Any]]],
) -> int:
    """Count train components with a stored hydraulic-loading basis."""

    return sum(
        any(_positive(row.get("hlr_m3_m2_d")) is not None for row in rows)
        for rows in by_component.values()
    )


def _land_fit(
    *,
    available_land: float | None,
    estimate_low: float | None,
    estimate_high: float | None,
    full_coverage: bool,
) -> str:
    """Compare supplied land with a complete evidence-bounded range."""

    if (
        available_land is None
        or estimate_low is None
        or estimate_high is None
        or not full_coverage
    ):
        return "insufficient_data"
    if available_land >= estimate_high:
        return "fits"
    if available_land >= estimate_low:
        return "borderline"
    return "likely_too_little_land"


def _estimate_label(
    *,
    estimate_low: float | None,
    estimate_high: float | None,
    per_person_label: str | None,
    full_coverage: bool,
    basis: str,
    population_supplied: bool,
    design_flow_supplied: bool,
) -> str:
    """Return a concise estimate label without hiding partial coverage."""

    if estimate_low is not None and estimate_high is not None:
        input_basis = (
            "supplied design flow"
            if basis == "design_flow"
            else "supplied population or PE"
        )
        return (
            f"Estimated screening area: {estimate_low:,.0f}-{estimate_high:,.0f} "
            f"m², based on {input_basis} and stored footprint evidence"
        )
    if per_person_label is not None:
        if not full_coverage:
            return f"Known components only: stored footprint range {per_person_label}"
        if not population_supplied:
            suffix = (
                " Design flow alone is not enough for this footprint basis."
                if design_flow_supplied
                else ""
            )
            return (
                f"This option has a stored footprint range of {per_person_label}. "
                "To estimate area from this method, provide population or PE."
                + suffix
            )
    return "The toolkit does not have enough footprint evidence to estimate area for this option."


def _positive(value: Any) -> float | None:
    """Return a positive user/stored number; zero and missing remain unusable."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _assumptions(basis: str) -> list[str]:
    """Return basis-specific exclusions without adding hidden design values."""

    first = (
        "Every component with a stored hydraulic loading rate receives the supplied design flow."
        if basis == "design_flow"
        else "The user-supplied population or PE is applied only to stored area-per-person evidence."
    )
    return [
        first,
        "Excluded: setbacks, access, freeboard, hydraulic profile, inlet and outlet levels, sludge handling, flood safety, land ownership, and detailed design margins.",
    ]

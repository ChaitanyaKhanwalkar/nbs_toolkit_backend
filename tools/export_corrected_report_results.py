"""Export corrected Khandwa discharge sensitivity and location contrast outputs.

This helper is intentionally read-only with respect to the canonical database:
it calls the live FastAPI recommendation route through TestClient, then writes
CSV/JSON/Markdown report artifacts for reproducibility.
"""

from __future__ import annotations

import csv
import json
import math
import os
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from random import Random
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DB_PATH = ROOT / "canonical db" / "narmada_nbs_canonical.db"
ENGINE_RUN = ROOT / "engine_run"

CORRECTED_PROFILE = "Domestic sewage \u2014 combined municipal (medium-strong, India)"
CORRECTED_VALUES = {
    "bod": 250.0,
    "cod": 500.0,
    "tss": 250.0,
    "ammonia_n": 40.0,
    "total_phosphorus": 12.0,
    "ph": 7.4,
}
ACTIVE_CRITERIA = ["C1", "C2", "C3", "C4", "C6", "C7", "C8"]


def main() -> None:
    """Run exports for the corrected report-result gap closure."""

    ENGINE_RUN.mkdir(exist_ok=True)
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
    sys.path.insert(0, str(BACKEND))

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    dindori_region_id = _find_dindori_region_id()

    khandwa = _run(client, region_id=27)
    dindori = _run(client, region_id=dindori_region_id)

    _assert_corrected_profile(khandwa)
    _assert_corrected_profile(dindori)
    _assert_no_old_blackwater_values(khandwa)
    _assert_no_old_blackwater_values(dindori)

    _write_json(ENGINE_RUN / "p1_khandwa_corrected_result.json", khandwa)
    _write_json(ENGINE_RUN / "p1_dindori_corrected_result.json", dindori)

    matrix, weights = _matrix_and_weights(khandwa)
    _write_matrix(ENGINE_RUN / "corrected_s1_discharge_decision_matrix.csv", matrix)
    _write_weights(ENGINE_RUN / "corrected_s1_discharge_weights.csv", weights)
    _write_baseline(
        ENGINE_RUN / "corrected_s1_discharge_baseline_ranking.csv",
        khandwa["ranked_trains"],
    )

    sensitivity = _run_sensitivity(matrix, weights)
    _write_oat(ENGINE_RUN / "corrected_s1_discharge_oat_results.csv", sensitivity["oat"])
    _write_extremes(
        ENGINE_RUN / "corrected_s1_discharge_extreme_cases.csv",
        sensitivity["extremes"],
    )
    _write_monte_carlo(
        ENGINE_RUN / "corrected_s1_discharge_monte_carlo_stability.csv",
        sensitivity["monte_carlo"],
    )
    _write_sensitivity_summary(
        ENGINE_RUN / "corrected_s1_discharge_sensitivity_summary.md",
        khandwa,
        sensitivity,
    )
    _write_location_table(
        ENGINE_RUN / "p1_location_contrast_table.csv",
        khandwa,
        dindori,
    )
    _write_location_summary(
        ENGINE_RUN / "p1_location_contrast_summary.md",
        khandwa,
        dindori,
    )

    print(
        "Exported corrected discharge sensitivity and P1 location contrast "
        f"to {ENGINE_RUN}"
    )


def _run(client: Any, *, region_id: int) -> dict[str, Any]:
    payload = {
        "use_case": "discharge_inland",
        "selected_parameters": list(CORRECTED_VALUES),
        "measured_observations": [],
        "region_id": region_id,
        "context": {
            "workflow_mode": "pollution_source_screening",
            "pollution_source_type": "domestic_sewage",
            "source_type": "municipal_sewage",
            "influent_profile": CORRECTED_PROFILE,
            "intervention_position": "off_channel",
        },
        "notes": (
            "Corrected municipal fallback export; no user-measured WQ override; "
            "do not use archived blackwater profile."
        ),
    }
    response = client.post("/api/v1/recommend", json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Recommendation failed for region {region_id}: {response.text}")
    return response.json()


def _find_dindori_region_id() -> int:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, station, district
            FROM regions
            WHERE lower(coalesce(district, '')) LIKE '%dindori%'
               OR lower(coalesce(station, '')) LIKE '%dindori%'
            ORDER BY
                CASE WHEN lower(coalesce(district, '')) LIKE '%dindori%' THEN 0 ELSE 1 END,
                id
            """
        ).fetchall()
    if not rows:
        raise RuntimeError("No Dindori region was found in canonical regions table.")
    return int(rows[0]["id"])


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _profile_observations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    summary = payload.get("input_summary") or {}
    data_used = summary.get("data_used") or []
    return [row for row in data_used if row.get("source") == "water_type_profile"]


def _profile_values(payload: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    for row in _profile_observations(payload):
        key = _norm(row.get("parameter"))
        if key:
            values[key] = float(row.get("value"))
    return values


def _profile_label(payload: dict[str, Any]) -> str:
    for row in _profile_observations(payload):
        water_type = row.get("water_type")
        if water_type:
            return str(water_type)
        original = row.get("original") or {}
        if original.get("water_type"):
            return str(original["water_type"])
    return ""


def _assert_corrected_profile(payload: dict[str, Any]) -> None:
    label = _profile_label(payload)
    if label != CORRECTED_PROFILE:
        raise RuntimeError(f"Expected corrected profile label, got {label!r}.")
    values = _profile_values(payload)
    for key, expected in CORRECTED_VALUES.items():
        actual = values.get(key)
        if actual is None or abs(actual - expected) > 1e-9:
            raise RuntimeError(f"Expected {key}={expected}, got {actual}.")


def _assert_no_old_blackwater_values(payload: dict[str, Any]) -> None:
    values = _profile_values(payload)
    if values.get("ammonia_n") == 200.0 or values.get("total_phosphorus") == 40.0:
        raise RuntimeError("Old blackwater NH3-N=200 or TP=40 appeared in output.")


def _matrix_and_weights(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ranked = payload["ranked_trains"]
    values_by_code: dict[str, list[float]] = {code: [] for code in ACTIVE_CRITERIA}
    raw_rows: list[dict[str, Any]] = []
    for train in ranked:
        criteria = {row["criterion_code"]: row for row in train.get("criteria_breakdown", [])}
        row = {"option": _train_name(train), "train_id": train["train_id"]}
        for code in ACTIVE_CRITERIA:
            value = criteria.get(code, {}).get("raw_value")
            row[code] = None if value is None else float(value)
            if value is not None:
                values_by_code[code].append(float(value))
        raw_rows.append(row)

    medians = {
        code: sorted(values)[len(values) // 2] if values else 0.0
        for code, values in values_by_code.items()
    }
    for row in raw_rows:
        for code in ACTIVE_CRITERIA:
            if row[code] is None:
                row[code] = medians[code]

    first = ranked[0].get("criteria_breakdown") or []
    weights = [
        {
            "criterion": row["criterion_code"],
            "weight": float(row["weight"]),
            "direction": row["benefit_or_cost"],
        }
        for row in first
        if row["criterion_code"] in ACTIVE_CRITERIA
    ]
    return raw_rows, weights


def _write_matrix(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["option", *ACTIVE_CRITERIA])
        for row in rows:
            writer.writerow([row["option"], *[row[code] for code in ACTIVE_CRITERIA]])


def _write_weights(path: Path, weights: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["criterion", "weight", "direction"])
        writer.writeheader()
        writer.writerows(weights)


def _write_baseline(path: Path, ranked: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rank", "train", "Ci", "use_case_verdict"])
        for row in ranked:
            verdict = _selected_verdict(row)
            writer.writerow([row["rank"], _train_name(row), row["match_score"], verdict])


def _run_sensitivity(
    matrix_rows: list[dict[str, Any]],
    weight_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    options = [row["option"] for row in matrix_rows]
    criteria = [row["criterion"] for row in weight_rows]
    directions = [row["direction"] for row in weight_rows]
    weights = _renorm([row["weight"] for row in weight_rows])
    matrix = [[float(row[code]) for code in criteria] for row in matrix_rows]
    baseline = _topsis(matrix, weights, directions)
    baseline_order = _order(baseline)
    baseline_ranks = _ranks(baseline)
    baseline_top = options[baseline_order[0]]

    oat = []
    for j, criterion in enumerate(criteria):
        for factor in [0.5, 0.8, 0.9, 1.1, 1.2, 1.5, 2.0]:
            varied = list(weights)
            varied[j] *= factor
            scores = _topsis(matrix, _renorm(varied), directions)
            order = _order(scores)
            oat.append(
                {
                    "criterion": criterion,
                    "factor": factor,
                    "new_top1": options[order[0]],
                    "top1_changed": options[order[0]] != baseline_top,
                    "spearman_vs_base": _spearman(baseline, scores),
                }
            )

    extremes = []
    equal_scores = _topsis(matrix, _renorm([1.0] * len(criteria)), directions)
    equal_order = _order(equal_scores)
    extremes.append(
        {
            "case": "equal_weights",
            "new_top1": options[equal_order[0]],
            "top3": "|".join(options[i] for i in equal_order[:3]),
            "spearman_vs_base": _spearman(baseline, equal_scores),
        }
    )
    for j, criterion in enumerate(criteria):
        varied = list(weights)
        varied[j] = 0.0
        scores = _topsis(matrix, _renorm(varied), directions)
        order = _order(scores)
        extremes.append(
            {
                "case": f"drop_{criterion}",
                "new_top1": options[order[0]],
                "top3": "|".join(options[i] for i in order[:3]),
                "spearman_vs_base": _spearman(baseline, scores),
            }
        )

    rng = Random(42)
    draws = 5000
    delta = 0.30
    top1_counts: Counter[str] = Counter()
    top3_counts: Counter[str] = Counter()
    spearman_values: list[float] = []
    for _ in range(draws):
        varied = [weight * (1.0 + rng.uniform(-delta, delta)) for weight in weights]
        scores = _topsis(matrix, _renorm(varied), directions)
        order = _order(scores)
        top1_counts[options[order[0]]] += 1
        for index in order[:3]:
            top3_counts[options[index]] += 1
        spearman_values.append(_spearman(baseline, scores))

    monte_carlo = []
    for index in baseline_order:
        option = options[index]
        monte_carlo.append(
            {
                "option": option,
                "baseline_rank": baseline_ranks[index],
                "P_top1_percent": 100.0 * top1_counts[option] / draws,
                "P_top3_percent": 100.0 * top3_counts[option] / draws,
            }
        )
    return {
        "baseline_scores": baseline,
        "baseline_order": baseline_order,
        "options": options,
        "oat": oat,
        "extremes": extremes,
        "monte_carlo": monte_carlo,
        "monte_carlo_draws": draws,
        "monte_carlo_delta": delta,
        "top1_counts": dict(top1_counts),
        "mean_spearman": mean(spearman_values),
    }


def _topsis(
    matrix: list[list[float]],
    weights: list[float],
    directions: list[str],
) -> list[float]:
    cols = list(zip(*matrix))
    normalized_cols: list[list[float]] = []
    for col, direction in zip(cols, directions):
        denom = math.sqrt(sum(value * value for value in col)) or 1.0
        vector = [value / denom for value in col]
        if direction == "cost":
            vector = [1.0 - value for value in vector]
        normalized_cols.append(vector)
    weighted_cols = [
        [value * weights[index] for value in col]
        for index, col in enumerate(normalized_cols)
    ]
    best = [max(col) for col in weighted_cols]
    worst = [min(col) for col in weighted_cols]
    scores = []
    for row_index in range(len(matrix)):
        d_best = math.sqrt(
            sum((col[row_index] - best[index]) ** 2 for index, col in enumerate(weighted_cols))
        )
        d_worst = math.sqrt(
            sum((col[row_index] - worst[index]) ** 2 for index, col in enumerate(weighted_cols))
        )
        scores.append(d_worst / (d_best + d_worst) if d_best + d_worst else 0.5)
    return scores


def _renorm(values: list[float]) -> list[float]:
    total = sum(max(0.0, value) for value in values)
    if total == 0:
        return [1.0 / len(values)] * len(values)
    return [max(0.0, value) / total for value in values]


def _order(scores: list[float]) -> list[int]:
    return sorted(range(len(scores)), key=lambda index: (-scores[index], index))


def _ranks(scores: list[float]) -> list[int]:
    ranks = [0] * len(scores)
    for rank, index in enumerate(_order(scores), start=1):
        ranks[index] = rank
    return ranks


def _spearman(a: list[float], b: list[float]) -> float:
    ra = _ranks(a)
    rb = _ranks(b)
    n = len(ra)
    if n < 2:
        return 1.0
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def _write_oat(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["criterion", "factor", "new_top1", "top1_changed", "spearman_vs_base"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_extremes(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["case", "new_top1", "top3", "spearman_vs_base"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_monte_carlo(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["option", "baseline_rank", "P_top1_percent", "P_top3_percent"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_sensitivity_summary(
    path: Path,
    payload: dict[str, Any],
    sensitivity: dict[str, Any],
) -> None:
    ranked = payload["ranked_trains"]
    top = ranked[0]
    second = ranked[1]
    margin = float(top["match_score"]) - float(second["match_score"])
    top_name = _train_name(top)
    retention = _mc_top1_retention(sensitivity, top_name)
    flips = {
        name: count
        for name, count in sensitivity["top1_counts"].items()
        if name != top_name
    }
    equal = _extreme(sensitivity, "equal_weights")
    drop_c2 = _extreme(sensitivity, "drop_C2")
    drop_c7 = _extreme(sensitivity, "drop_C7")
    lines = [
        "# Corrected S1 discharge sensitivity summary",
        "",
        "Scenario: Khandwa / Indira Sagar, domestic sewage, discharge_inland.",
        f"Fallback profile selected: `{_profile_label(payload)}`.",
        "",
        "Corrected fallback values:",
        *_profile_value_lines(payload),
        "",
        "## Baseline ranking",
        "",
        "| Rank | Train | Ci | use-case verdict |",
        "|---|---|---:|---|",
    ]
    lines.extend(
        f"| {row['rank']} | {_train_name(row)} | {float(row['match_score']):.6f} | {_selected_verdict(row)} |"
        for row in ranked
    )
    lines.extend(
        [
            "",
            f"DEWATS vs VF margin: `{margin:.6f}` Ci.",
            "",
            "## Monte Carlo",
            "",
            f"Setting: ±{int(sensitivity['monte_carlo_delta'] * 100)}% per weight, "
            f"{sensitivity['monte_carlo_draws']} draws.",
            f"DEWATS top-1 retention: `{retention:.2f}%`.",
            f"Mean Spearman vs baseline: `{sensitivity['mean_spearman']:.3f}`.",
            (
                "Top-1 flips: none."
                if not flips
                else "Top-1 flips: "
                + ", ".join(
                    f"{name} ({count}/{sensitivity['monte_carlo_draws']})"
                    for name, count in sorted(flips.items())
                )
                + "."
            ),
            f"Equal-weights winner: `{equal['new_top1']}`.",
            f"Drop-C2 winner: `{drop_c2['new_top1']}`.",
            f"Drop-C7 winner: `{drop_c7['new_top1']}`.",
            "",
            "Old blackwater artifacts avoided: yes. Export assertions confirmed "
            "NH3-N=200 and TP=40 were not present in the selected fallback values.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _profile_value_lines(payload: dict[str, Any]) -> list[str]:
    values = _profile_values(payload)
    return [f"- `{key}` = `{values.get(key)}`" for key in CORRECTED_VALUES]


def _extreme(sensitivity: dict[str, Any], case: str) -> dict[str, Any]:
    return next(row for row in sensitivity["extremes"] if row["case"] == case)


def _mc_top1_retention(sensitivity: dict[str, Any], option: str) -> float:
    for row in sensitivity["monte_carlo"]:
        if row["option"] == option:
            return float(row["P_top1_percent"])
    return 0.0


def _write_location_table(
    path: Path,
    khandwa: dict[str, Any],
    dindori: dict[str, Any],
) -> None:
    rows = [_location_row("Khandwa / Indira Sagar", khandwa), _location_row("Dindori", dindori)]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _location_row(label: str, payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("location_context") or {}
    top = payload["ranked_trains"][0]
    return {
        "scenario": label,
        "region_id": context.get("region_id"),
        "station": context.get("station"),
        "district": context.get("district"),
        "profile_label": _profile_label(payload),
        "profile_values": json.dumps(_profile_values(payload), sort_keys=True),
        "top_train": _train_name(top),
        "Ci": top.get("match_score"),
        "match_percent": round(float(top.get("match_score") or 0.0) * 100.0, 1),
        "confidence": top.get("confidence_label"),
        "design_readiness": (payload.get("design_readiness") or {}).get("short_label")
        or (payload.get("design_readiness") or {}).get("level"),
        "stream_order": context.get("stream_order"),
        "soil_type": context.get("soil_type"),
        "infiltration_class": context.get("infiltration_class"),
        "safety_placement_warning": _join_warnings(payload),
        "off_channel_mainstem_warning": _off_channel_warning(context, payload),
        "filtered_or_cautioned_train_set": _filtered_or_cautioned(payload),
        "applicability_rules_fired": _rules_fired(payload),
    }


def _write_location_summary(
    path: Path,
    khandwa: dict[str, Any],
    dindori: dict[str, Any],
) -> None:
    krow = _location_row("Khandwa / Indira Sagar", khandwa)
    drow = _location_row("Dindori", dindori)
    winner_changed = krow["top_train"] != drow["top_train"]
    changed_fields = [
        field
        for field in (
            "Ci",
            "confidence",
            "design_readiness",
            "stream_order",
            "soil_type",
            "infiltration_class",
            "safety_placement_warning",
            "off_channel_mainstem_warning",
            "filtered_or_cautioned_train_set",
        )
        if str(krow.get(field)) != str(drow.get(field))
    ]
    lines = [
        "# P1 location numeric contrast",
        "",
        "Both runs hold source, use case, and corrected municipal fallback constant; only region_id changes.",
        "",
        "| Field | Khandwa / Indira Sagar | Dindori |",
        "|---|---|---|",
    ]
    for field in krow:
        lines.append(f"| {field} | {_md(krow[field])} | {_md(drow[field])} |")
    lines.extend(
        [
            "",
            f"Top winner changes: {'yes' if winner_changed else 'no'}.",
        ]
    )
    if not winner_changed:
        lines.append(
            "The winner does not change, but the run still demonstrates location "
            "sensitivity through changed site context fields: "
            + ", ".join(changed_fields)
            + ". These fields alter site/hydrologic/applicability evidence while "
            "the treatment train remains robust for this domestic discharge case."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _selected_verdict(train: dict[str, Any]) -> str:
    use_case = train.get("selected_use_case") or "discharge_inland"
    verdict = (train.get("all_use_case_verdicts") or {}).get(use_case) or {}
    return str(verdict.get("verdict") or "unknown")


def _join_warnings(payload: dict[str, Any]) -> str:
    values = payload.get("warnings") or []
    return " | ".join(str(value) for value in values)


def _off_channel_warning(context: dict[str, Any], payload: dict[str, Any]) -> str:
    flags = context.get("context_flags") or {}
    if flags.get("off_channel_required") or flags.get("mainstem_or_high_order"):
        return "Off-channel/source-control placement required for mainstem or high-order context."
    return ""


def _filtered_or_cautioned(payload: dict[str, Any]) -> str:
    rejected = [
        f"{_train_name(row)}: rejected"
        for row in payload.get("rejected_options") or []
        if _train_name(row)
    ]
    cautioned = [
        f"{_train_name(row)}: {row.get('applicability_result', {}).get('status')}"
        for row in payload.get("ranked_trains") or []
        if row.get("applicability_result", {}).get("status") not in {None, "allowed"}
    ]
    return " | ".join([*rejected, *cautioned])


def _rules_fired(payload: dict[str, Any]) -> str:
    rules = []
    for train in payload.get("ranked_trains") or []:
        for reason in train.get("applicability_result", {}).get("technical_reasons") or []:
            rules.append(f"{_train_name(train)}: {reason}")
    return " | ".join(rules)


def _norm(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _train_name(row: dict[str, Any]) -> str:
    return str(row.get("train_name") or row.get("name") or "")


def _md(value: Any) -> str:
    text = str(value).replace("|", "\\|")
    return text if text else "n/a"


if __name__ == "__main__":
    main()

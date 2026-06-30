"""Verify a PostgreSQL migration against the canonical SQLite mirror.

The default `--sqlite-only` mode verifies the live SQLite signature and writes a
report without requiring PostgreSQL. Supplying `--postgres-url` compares table
counts and checks generated views in PostgreSQL.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE = ROOT / "canonical db" / "narmada_nbs_canonical.db"
DEFAULT_REPORT = (
    ROOT / "deployment" / "postgres" / "generated" / "postgres_migration_verification.md"
)
EXPECTED_COUNTS = {
    "sources": 109,
    "nbs_options": 28,
    "removal_efficiency": 167,
    "treatment_train": 8,
    "ambient_water_quality": 47244,
    "river_network": 6339,
    "site_attributes": 52,
    "pollution_sources": 155,
}


def quote_ident(identifier: str) -> str:
    """Return a SQL-safe quoted identifier."""

    return '"' + identifier.replace('"', '""') + '"'


def sqlite_tables(con: sqlite3.Connection) -> list[str]:
    """Return non-internal SQLite tables."""

    return [
        str(row[0])
        for row in con.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
    ]


def sqlite_views(con: sqlite3.Connection) -> list[str]:
    """Return SQLite views."""

    return [
        str(row[0])
        for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'view' ORDER BY name"
        )
    ]


def sqlite_counts(con: sqlite3.Connection) -> dict[str, int]:
    """Return row counts for every non-internal table."""

    return {
        table: int(con.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}").fetchone()[0])
        for table in sqlite_tables(con)
    }


def postgres_counts(pg_conn: Any, tables: list[str]) -> dict[str, int]:
    """Return PostgreSQL row counts for imported tables."""

    counts: dict[str, int] = {}
    with pg_conn.cursor() as cur:
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}")
            counts[table] = int(cur.fetchone()[0])
    return counts


def postgres_views(pg_conn: Any) -> set[str]:
    """Return PostgreSQL public view names."""

    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            """
        )
        return {str(row[0]) for row in cur.fetchall()}


def normalize_postgres_url(url: str) -> str:
    """Normalize common PostgreSQL URL forms for psycopg."""

    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url[len("postgresql+psycopg://") :]
    return url


def write_report(
    *,
    report_path: Path,
    sqlite_count_map: dict[str, int],
    sqlite_view_names: list[str],
    pg_count_map: dict[str, int] | None,
    pg_view_names: set[str] | None,
    failures: list[str],
) -> None:
    """Write a Markdown verification report."""

    lines = [
        "# PostgreSQL Migration Verification",
        "",
        "This report compares the canonical SQLite mirror with PostgreSQL when a PostgreSQL URL is supplied.",
        "",
        "## Expected Canonical Counts",
        "",
        "| Table | Expected | SQLite actual | Status |",
        "|---|---:|---:|---|",
    ]
    for table, expected in EXPECTED_COUNTS.items():
        actual = sqlite_count_map.get(table)
        status = "ok" if actual == expected else "mismatch"
        lines.append(f"| {table} | {expected} | {actual} | {status} |")
    lines.extend(["", "## SQLite Table Counts", "", "| Table | Rows |", "|---|---:|"])
    for table, count in sqlite_count_map.items():
        lines.append(f"| {table} | {count} |")
    if pg_count_map is None:
        lines.extend(
            [
                "",
                "## PostgreSQL Comparison",
                "",
                "PostgreSQL comparison was not run because no PostgreSQL URL was supplied.",
            ]
        )
    else:
        lines.extend(
            ["", "## PostgreSQL Comparison", "", "| Table | SQLite | PostgreSQL | Status |", "|---|---:|---:|---|"]
        )
        for table, sqlite_count in sqlite_count_map.items():
            pg_count = pg_count_map.get(table)
            status = "ok" if pg_count == sqlite_count else "mismatch"
            lines.append(f"| {table} | {sqlite_count} | {pg_count} | {status} |")
        if pg_view_names is not None:
            lines.extend(["", "## View Check", ""])
            generated = sorted(set(sqlite_view_names) & pg_view_names)
            missing = sorted(set(sqlite_view_names) - pg_view_names)
            lines.append(f"- SQLite views: {len(sqlite_view_names)}")
            lines.append(f"- Matching PostgreSQL view names: {len(generated)}")
            lines.append(f"- Missing/commented/manual-review view names: {len(missing)}")
            if missing:
                lines.extend(f"  - `{name}`" for name in missing)
    lines.extend(["", "## Failures", ""])
    if failures:
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("- None.")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, default=Path(os.getenv("SQLITE_PATH", DEFAULT_SQLITE)))
    parser.add_argument("--postgres-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--sqlite-only",
        action="store_true",
        help="Verify only the SQLite canonical signature and do not connect to PostgreSQL.",
    )
    return parser.parse_args()


def main() -> int:
    """Run verification."""

    args = parse_args()
    if not args.sqlite.exists():
        raise SystemExit(f"SQLite database not found: {args.sqlite}")
    sqlite_con = sqlite3.connect(args.sqlite)
    sqlite_count_map = sqlite_counts(sqlite_con)
    sqlite_view_names = sqlite_views(sqlite_con)
    failures = [
        f"{table}: expected {expected}, SQLite has {sqlite_count_map.get(table)}"
        for table, expected in EXPECTED_COUNTS.items()
        if sqlite_count_map.get(table) != expected
    ]
    pg_count_map = None
    pg_view_names = None
    if args.postgres_url and not args.sqlite_only:
        try:
            import psycopg
        except ImportError as exc:
            raise SystemExit("psycopg is required. Install backend/requirements.txt first.") from exc
        with psycopg.connect(normalize_postgres_url(args.postgres_url)) as pg_conn:
            pg_count_map = postgres_counts(pg_conn, list(sqlite_count_map))
            pg_view_names = postgres_views(pg_conn)
            for table, sqlite_count in sqlite_count_map.items():
                if pg_count_map.get(table) != sqlite_count:
                    failures.append(
                        f"{table}: SQLite={sqlite_count}, PostgreSQL={pg_count_map.get(table)}"
                    )
    write_report(
        report_path=args.report,
        sqlite_count_map=sqlite_count_map,
        sqlite_view_names=sqlite_view_names,
        pg_count_map=pg_count_map,
        pg_view_names=pg_view_names,
        failures=failures,
    )
    print(f"Wrote verification report: {args.report}")
    if failures:
        print("Verification completed with failures.")
        return 1
    print("Verification completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

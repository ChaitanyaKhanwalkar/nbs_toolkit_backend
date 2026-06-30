"""Smoke-check the generated PostgreSQL schema for obvious SQLite-only syntax."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "deployment" / "postgres" / "generated" / "schema_pg.sql"

FAIL_PATTERNS = {
    "group_concat(": re.compile(r"\bgroup_concat\s*\(", re.IGNORECASE),
    "AUTOINCREMENT": re.compile(r"\bAUTOINCREMENT\b", re.IGNORECASE),
    "sqlite_sequence": re.compile(r"\bsqlite_sequence\b", re.IGNORECASE),
    "PRAGMA": re.compile(r"\bPRAGMA\b", re.IGNORECASE),
    "WITHOUT ROWID": re.compile(r"\bWITHOUT\s+ROWID\b", re.IGNORECASE),
    "backtick identifiers": re.compile(r"`[^`]+`"),
}

WARN_PATTERNS = {
    "commented skipped views": re.compile(r"View skipped for manual review", re.IGNORECASE),
    "unknown type fallbacks": re.compile(r"\bTEXT\s+/\*\s*unknown", re.IGNORECASE),
}


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    return parser.parse_args()


def main() -> int:
    """Run the schema smoke check."""

    args = parse_args()
    if not args.schema.exists():
        raise SystemExit(f"Schema file not found: {args.schema}")
    sql = args.schema.read_text(encoding="utf-8")
    failures = {
        label: len(pattern.findall(sql))
        for label, pattern in FAIL_PATTERNS.items()
        if pattern.search(sql)
    }
    warnings = {
        label: len(pattern.findall(sql))
        for label, pattern in WARN_PATTERNS.items()
        if pattern.search(sql)
    }

    print(f"Schema smoke check: {args.schema}")
    if warnings:
        print("Warnings:")
        for label, count in warnings.items():
            print(f"  - {label}: {count}")
    if failures:
        print("FAIL: SQLite-only syntax remains:")
        for label, count in failures.items():
            print(f"  - {label}: {count}")
        return 1
    print("PASS: no obvious SQLite-only syntax found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

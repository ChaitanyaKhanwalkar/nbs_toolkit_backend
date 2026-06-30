"""Migrate canonical SQLite table data into a PostgreSQL database.

The script is deliberately credential-neutral: pass the PostgreSQL URL through
an argument or environment variable. It creates schema from the generated DDL,
imports only tables, skips views, preserves NULL values, and verifies row counts.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE = ROOT / "canonical db" / "narmada_nbs_canonical.db"
DEFAULT_SCHEMA = ROOT / "deployment" / "postgres" / "generated" / "schema_pg.sql"
BATCH_SIZE = 1000


def quote_ident(identifier: str) -> str:
    """Return a PostgreSQL-safe quoted identifier."""

    return '"' + identifier.replace('"', '""') + '"'


def sqlite_tables(con: sqlite3.Connection) -> list[str]:
    """Return non-internal SQLite table names."""

    rows = con.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [str(row[0]) for row in rows]


def sqlite_columns(con: sqlite3.Connection, table: str) -> list[str]:
    """Return column names for a SQLite table."""

    return [str(row[1]) for row in con.execute(f"PRAGMA table_info({quote_ident(table)})")]


def split_sql_statements(sql: str) -> list[str]:
    """Split generated SQL on semicolons outside single-quoted strings."""

    statements: list[str] = []
    current: list[str] = []
    in_single = False
    i = 0
    while i < len(sql):
        char = sql[i]
        current.append(char)
        if char == "'":
            if i + 1 < len(sql) and sql[i + 1] == "'":
                current.append(sql[i + 1])
                i += 2
                continue
            in_single = not in_single
        elif char == ";" and not in_single:
            statement = executable_sql("".join(current))
            if statement:
                statements.append(statement)
            current = []
        i += 1
    tail = executable_sql("".join(current))
    if tail:
        statements.append(tail)
    return statements


def executable_sql(statement: str) -> str:
    """Remove standalone line comments before executing a generated statement."""

    lines = [
        line
        for line in statement.strip().splitlines()
        if line.strip() and not line.strip().startswith("--")
    ]
    return "\n".join(lines).strip()


def execute_schema(pg_conn: Any, schema_path: Path) -> None:
    """Execute the generated PostgreSQL schema."""

    sql = schema_path.read_text(encoding="utf-8")
    with pg_conn.cursor() as cur:
        for statement in split_sql_statements(sql):
            cur.execute(statement)
    pg_conn.commit()


def insert_table(sqlite_con: sqlite3.Connection, pg_conn: Any, table: str) -> tuple[int, int]:
    """Insert one table and return source/destination row counts."""

    columns = sqlite_columns(sqlite_con, table)
    quoted_columns = ", ".join(quote_ident(col) for col in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = f"INSERT INTO {quote_ident(table)} ({quoted_columns}) VALUES ({placeholders})"
    source_count = int(
        sqlite_con.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}").fetchone()[0]
    )
    select_sql = f"SELECT {', '.join(quote_ident(col) for col in columns)} FROM {quote_ident(table)}"
    sqlite_cur = sqlite_con.execute(select_sql)
    inserted = 0
    with pg_conn.cursor() as pg_cur:
        while True:
            rows = sqlite_cur.fetchmany(BATCH_SIZE)
            if not rows:
                break
            pg_cur.executemany(insert_sql, [tuple(row) for row in rows])
            inserted += len(rows)
            print(f"{table}: inserted {inserted}/{source_count}")
    pg_conn.commit()
    with pg_conn.cursor() as pg_cur:
        pg_cur.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}")
        destination_count = int(pg_cur.fetchone()[0])
    return source_count, destination_count


def normalize_postgres_url(url: str) -> str:
    """Normalize common PostgreSQL URL forms for psycopg."""

    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url[len("postgresql+psycopg://") :]
    return url


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, default=Path(os.getenv("SQLITE_PATH", DEFAULT_SQLITE)))
    parser.add_argument("--postgres-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--schema", type=Path, default=Path(os.getenv("POSTGRES_SCHEMA", DEFAULT_SCHEMA)))
    return parser.parse_args()


def main() -> int:
    """Run the migration."""

    args = parse_args()
    if not args.sqlite.exists():
        raise SystemExit(f"SQLite database not found: {args.sqlite}")
    if not args.schema.exists():
        raise SystemExit(f"Generated schema not found: {args.schema}")
    if not args.postgres_url:
        raise SystemExit("PostgreSQL URL is required via --postgres-url or DATABASE_URL.")
    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("psycopg is required. Install backend/requirements.txt first.") from exc

    sqlite_con = sqlite3.connect(args.sqlite)
    sqlite_con.row_factory = sqlite3.Row
    pg_url = normalize_postgres_url(args.postgres_url)
    print("Connecting to PostgreSQL with supplied URL (masked).")
    with psycopg.connect(pg_url) as pg_conn:
        print(f"Creating schema from {args.schema}")
        execute_schema(pg_conn, args.schema)
        failures: list[str] = []
        print("Importing table data")
        for table in sqlite_tables(sqlite_con):
            source_count, destination_count = insert_table(sqlite_con, pg_conn, table)
            if source_count != destination_count:
                failures.append(f"{table}: SQLite={source_count}, PostgreSQL={destination_count}")
        if failures:
            raise SystemExit("Row-count verification failed:\n" + "\n".join(failures))
    print("Migration completed; all imported table row counts match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

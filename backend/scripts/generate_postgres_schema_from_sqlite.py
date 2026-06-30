"""Generate a PostgreSQL schema draft from the canonical SQLite mirror.

This helper is intentionally conservative. It reads the live canonical SQLite
database, writes a PostgreSQL DDL draft, and records anything that needs human
review before Azure PostgreSQL import. It does not change scientific data.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE = ROOT / "canonical db" / "narmada_nbs_canonical.db"
DEFAULT_SCHEMA = ROOT / "deployment" / "postgres" / "generated" / "schema_pg.sql"
DEFAULT_REPORT = (
    ROOT / "deployment" / "postgres" / "generated" / "schema_generation_report.md"
)
DEFAULT_AUDIT = ROOT / "deployment" / "postgres" / "sqlite_schema_audit.md"

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

SQLITE_ONLY_VIEW_PATTERNS = (
    "strftime(",
    "julianday(",
    "datetime(",
    "date(",
    "random(",
    "printf(",
)

VIEW_DEPENDENCY_RE = re.compile(
    r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*|\"[^\"]+\"|'[^']+'|`[^`]+`|\[[^\]]+\])",
    flags=re.IGNORECASE,
)
GROUP_CONCAT_RE = re.compile(r"GROUP_CONCAT\s*\(", flags=re.IGNORECASE)


@dataclass(frozen=True)
class ColumnInfo:
    """SQLite column metadata used to build conservative PostgreSQL DDL."""

    cid: int
    name: str
    sqlite_type: str
    notnull: bool
    default: Any
    pk_position: int


def quote_ident(identifier: str) -> str:
    """Return a PostgreSQL-safe quoted identifier."""

    return '"' + identifier.replace('"', '""') + '"'


def map_sqlite_type(sqlite_type: str) -> str:
    """Map SQLite's loose type affinity to a conservative PostgreSQL type."""

    raw = (sqlite_type or "").strip().upper()
    if not raw:
        return "TEXT"
    if "INT" in raw:
        return "BIGINT"
    if any(token in raw for token in ("REAL", "FLOA", "DOUB")):
        return "DOUBLE PRECISION"
    if any(token in raw for token in ("CHAR", "CLOB", "TEXT", "VARCHAR")):
        return "TEXT"
    if "BLOB" in raw:
        return "BYTEA"
    if any(token in raw for token in ("NUM", "DEC", "BOOL", "DATE", "TIME")):
        return "NUMERIC" if "NUM" in raw or "DEC" in raw else "TEXT"
    return "TEXT"


def safe_default(default: Any) -> str | None:
    """Convert only simple SQLite defaults; leave risky defaults for review."""

    if default is None:
        return None
    text = str(default).strip()
    lowered = text.lower()
    if lowered in {"null", "current_timestamp", "current_date", "current_time"}:
        return text.upper()
    if re.fullmatch(r"[-+]?\d+(\.\d+)?", text):
        return text
    if re.fullmatch(r"'([^']|'')*'", text):
        return text
    if re.fullmatch(r'"([^"]|"")*"', text):
        return "'" + text[1:-1].replace("'", "''") + "'"
    return None


def connect(sqlite_path: Path) -> sqlite3.Connection:
    """Open the SQLite database in read-only mode where supported."""

    uri = f"file:{sqlite_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def sqlite_objects(con: sqlite3.Connection, object_type: str) -> list[tuple[str, str]]:
    """Return non-internal SQLite objects of a given type."""

    return con.execute(
        """
        SELECT name, COALESCE(sql, '')
        FROM sqlite_master
        WHERE type = ?
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """,
        (object_type,),
    ).fetchall()


def order_views_by_dependencies(views: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Order views so views depending on other views are created later."""

    view_map = {name: sql for name, sql in views}
    ordered: list[tuple[str, str]] = []
    temporary: set[str] = set()
    permanent: set[str] = set()

    def visit(name: str) -> None:
        if name in permanent:
            return
        if name in temporary:
            return
        temporary.add(name)
        for dependency in view_dependencies(view_map[name]):
            if dependency in view_map:
                visit(dependency)
        temporary.remove(name)
        permanent.add(name)
        ordered.append((name, view_map[name]))

    for view_name, _sql in views:
        visit(view_name)
    return ordered


def table_columns(con: sqlite3.Connection, table: str) -> list[ColumnInfo]:
    """Read SQLite table columns."""

    return [
        ColumnInfo(
            cid=int(row[0]),
            name=str(row[1]),
            sqlite_type=str(row[2] or ""),
            notnull=bool(row[3]),
            default=row[4],
            pk_position=int(row[5] or 0),
        )
        for row in con.execute(f"PRAGMA table_info({quote_ident(table)})")
    ]


def foreign_keys(con: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    """Read SQLite foreign-key declarations for audit reporting."""

    return con.execute(f"PRAGMA foreign_key_list({quote_ident(table)})").fetchall()


def table_row_count(con: sqlite3.Connection, table: str) -> int:
    """Return a table row count."""

    return int(con.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}").fetchone()[0])


def column_definition(column: ColumnInfo, single_column_pk: bool) -> str:
    """Build a PostgreSQL column definition from SQLite metadata."""

    parts = [quote_ident(column.name), map_sqlite_type(column.sqlite_type)]
    if column.notnull or single_column_pk:
        parts.append("NOT NULL")
    default = safe_default(column.default)
    if default is not None and not single_column_pk:
        parts.extend(["DEFAULT", default])
    return " ".join(parts)


def create_table_sql(con: sqlite3.Connection, table: str) -> str:
    """Create conservative PostgreSQL DDL for one table."""

    columns = table_columns(con, table)
    pk_columns = [c for c in sorted(columns, key=lambda c: c.pk_position) if c.pk_position]
    single_column_pk = len(pk_columns) == 1
    definitions = [
        "    " + column_definition(column, single_column_pk)
        for column in columns
    ]
    if pk_columns:
        pk = ", ".join(quote_ident(column.name) for column in pk_columns)
        definitions.append(f"    PRIMARY KEY ({pk})")
    return f"CREATE TABLE {quote_ident(table)} (\n" + ",\n".join(definitions) + "\n);"


def index_sql(con: sqlite3.Connection, table: str) -> tuple[list[str], list[str]]:
    """Generate regular index DDL and return skipped-index notes."""

    statements: list[str] = []
    skipped: list[str] = []
    for row in con.execute(f"PRAGMA index_list({quote_ident(table)})"):
        name = str(row[1])
        unique = bool(row[2])
        origin = str(row[3]) if len(row) > 3 else ""
        if name.startswith("sqlite_autoindex") or origin in {"pk", "u"}:
            skipped.append(f"{table}.{name}: SQLite autoindex/constraint index")
            continue
        cols = []
        expression_index = False
        for col_row in con.execute(f"PRAGMA index_info({quote_ident(name)})"):
            cid = int(col_row[1])
            col_name = str(col_row[2])
            if cid < 0 or not col_name:
                expression_index = True
                break
            cols.append(quote_ident(col_name))
        if expression_index or not cols:
            skipped.append(f"{table}.{name}: expression or unsupported index")
            continue
        unique_sql = "UNIQUE " if unique else ""
        statements.append(
            f"CREATE {unique_sql}INDEX IF NOT EXISTS {quote_ident(name)} "
            f"ON {quote_ident(table)} ({', '.join(cols)});"
        )
    return statements, skipped


def convert_group_concat(sql: str) -> str:
    """Convert SQLite GROUP_CONCAT calls to PostgreSQL STRING_AGG calls.

    This is syntax conversion only. It preserves the selected expression and
    separator; it does not change scientific/data logic or add ordering that was
    not present in the SQLite view.
    """

    result: list[str] = []
    position = 0
    while True:
        match = GROUP_CONCAT_RE.search(sql, position)
        if not match:
            result.append(sql[position:])
            break
        open_paren = match.end() - 1
        close_paren = matching_paren(sql, open_paren)
        if close_paren is None:
            result.append(sql[position:])
            break
        result.append(sql[position:match.start()])
        inner = sql[open_paren + 1 : close_paren]
        result.append(convert_group_concat_inner(inner))
        position = close_paren + 1
    return "".join(result)


def matching_paren(sql: str, open_index: int) -> int | None:
    """Find the matching close parenthesis while respecting SQL strings."""

    depth = 0
    in_single = False
    in_double = False
    i = open_index
    while i < len(sql):
        char = sql[i]
        if in_single:
            if char == "'" and i + 1 < len(sql) and sql[i + 1] == "'":
                i += 2
                continue
            if char == "'":
                in_single = False
        elif in_double:
            if char == '"':
                in_double = False
        else:
            if char == "'":
                in_single = True
            elif char == '"':
                in_double = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return None


def split_top_level_comma(sql: str) -> tuple[str, str | None]:
    """Split an expression on its first top-level comma."""

    depth = 0
    in_single = False
    in_double = False
    i = 0
    while i < len(sql):
        char = sql[i]
        if in_single:
            if char == "'" and i + 1 < len(sql) and sql[i + 1] == "'":
                i += 2
                continue
            if char == "'":
                in_single = False
        elif in_double:
            if char == '"':
                in_double = False
        else:
            if char == "'":
                in_single = True
            elif char == '"':
                in_double = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif char == "," and depth == 0:
                return sql[:i].strip(), sql[i + 1 :].strip()
        i += 1
    return sql.strip(), None


def convert_group_concat_inner(inner: str) -> str:
    """Convert the inside of one GROUP_CONCAT call to STRING_AGG."""

    expression, separator = split_top_level_comma(inner)
    distinct = ""
    if expression.upper().startswith("DISTINCT "):
        distinct = "DISTINCT "
        expression = expression[9:].strip()
    separator = separator or "', '"
    if separator.startswith('"') and separator.endswith('"'):
        separator = "'" + separator[1:-1].replace("'", "''") + "'"
    return f"STRING_AGG({distinct}({expression})::text, {separator})"


def convert_ifnull(sql: str) -> str:
    """Convert simple SQLite IFNULL calls to PostgreSQL COALESCE calls."""

    return re.sub(r"\bIFNULL\s*\(", "COALESCE(", sql, flags=re.IGNORECASE)


def convert_sqlite_view_sql(sql: str) -> str:
    """Apply conservative SQLite-to-PostgreSQL view syntax conversions."""

    converted = convert_group_concat(sql)
    converted = convert_ifnull(converted)
    return converted


def view_dependencies(sql: str) -> list[str]:
    """Return table/view names referenced after FROM and JOIN tokens."""

    deps: list[str] = []
    for match in VIEW_DEPENDENCY_RE.finditer(sql):
        raw = match.group(1).strip("\"'`[]")
        if raw not in deps:
            deps.append(raw)
    return deps


def group_concat_usages(sql: str) -> list[str]:
    """Return GROUP_CONCAT usages in a view definition."""

    usages: list[str] = []
    position = 0
    while True:
        match = GROUP_CONCAT_RE.search(sql, position)
        if not match:
            break
        open_paren = match.end() - 1
        close_paren = matching_paren(sql, open_paren)
        if close_paren is None:
            usages.append(sql[match.start() :].strip())
            break
        usages.append(sql[match.start() : close_paren + 1])
        position = close_paren + 1
    return usages


def view_conversion(name: str, sql: str) -> tuple[str | None, str | None]:
    """Convert views when only known safe SQLite syntax replacements are needed."""

    converted_sql = convert_sqlite_view_sql(sql)
    lowered = converted_sql.lower()
    hits = [token for token in SQLITE_ONLY_VIEW_PATTERNS if token in lowered]
    if hits:
        return None, f"uses SQLite-specific or differently-typed functions: {', '.join(hits)}"
    match = re.search(r"\bAS\b", converted_sql, flags=re.IGNORECASE)
    if not match:
        return None, "could not locate AS clause"
    select_sql = converted_sql[match.end() :].strip().rstrip(";")
    return f"CREATE OR REPLACE VIEW {quote_ident(name)} AS\n{select_sql};", None


def generate(sqlite_path: Path, schema_path: Path, report_path: Path, audit_path: Path) -> None:
    """Generate schema SQL, generation report, and SQLite audit."""

    con = connect(sqlite_path)
    con.row_factory = sqlite3.Row
    tables = sqlite_objects(con, "table")
    views = order_views_by_dependencies(sqlite_objects(con, "view"))
    internal = con.execute(
        "SELECT type, name FROM sqlite_master WHERE name LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    internal_table_count = sum(1 for row in internal if row["type"] == "table")
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]

    row_counts = [(name, table_row_count(con, name)) for name, _ in tables]
    zero_rows = [name for name, count in row_counts if count == 0]
    expected_mismatches = [
        (name, expected, dict(row_counts).get(name))
        for name, expected in EXPECTED_COUNTS.items()
        if dict(row_counts).get(name) != expected
    ]

    ddl: list[str] = [
        "-- Generated PostgreSQL schema draft for the Narmada NbS canonical database.",
        "-- Source: canonical db/narmada_nbs_canonical.db",
        "-- Review before production import. This file changes no scientific values.",
        "",
        "BEGIN;",
        "",
    ]
    skipped_indexes: list[str] = []
    default_notes: list[str] = []
    fk_notes: list[str] = []
    for table, _sql in tables:
        ddl.append(f"-- Table: {table}")
        ddl.append(f"DROP TABLE IF EXISTS {quote_ident(table)} CASCADE;")
        ddl.append(create_table_sql(con, table))
        ddl.append("")
        for column in table_columns(con, table):
            if column.default is not None and safe_default(column.default) is None:
                default_notes.append(
                    f"{table}.{column.name}: SQLite default `{column.default}` omitted for review"
                )
        for fk in foreign_keys(con, table):
            fk_notes.append(
                f"{table}: {dict(fk)}"
            )

    ddl.append("-- Indexes")
    for table, _sql in tables:
        statements, skipped = index_sql(con, table)
        ddl.extend(statements)
        skipped_indexes.extend(skipped)
    ddl.append("")

    converted_views: list[str] = []
    skipped_views: list[tuple[str, str, str]] = []
    ddl.append("-- Views")
    for name, sql in views:
        converted, reason = view_conversion(name, sql)
        if converted:
            ddl.append(f"DROP VIEW IF EXISTS {quote_ident(name)} CASCADE;")
            ddl.append(converted)
            ddl.append("")
            converted_views.append(name)
        else:
            skipped_views.append((name, reason or "not safely convertible", sql))
            ddl.append(f"-- View skipped for manual review: {name}")
            ddl.append(f"-- Reason: {reason or 'not safely convertible'}")
            for line in sql.splitlines():
                ddl.append("-- " + line)
            ddl.append("")

    ddl.extend(["COMMIT;", ""])
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text("\n".join(ddl), encoding="utf-8")

    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        build_audit(
            sqlite_path=sqlite_path,
            tables=tables,
            views=views,
            internal=internal,
            internal_table_count=internal_table_count,
            integrity=str(integrity),
            row_counts=row_counts,
            zero_rows=zero_rows,
            expected_mismatches=expected_mismatches,
            skipped_indexes=skipped_indexes,
            skipped_views=skipped_views,
            default_notes=default_notes,
            fk_notes=fk_notes,
            con=con,
        ),
        encoding="utf-8",
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_generation_report(
            sqlite_path=sqlite_path,
            schema_path=schema_path,
            tables=tables,
            views=views,
            converted_views=converted_views,
            skipped_views=skipped_views,
            skipped_indexes=skipped_indexes,
            default_notes=default_notes,
            integrity=str(integrity),
        ),
        encoding="utf-8",
    )


def build_audit(
    *,
    sqlite_path: Path,
    tables: list[tuple[str, str]],
    views: list[tuple[str, str]],
    internal: list[sqlite3.Row],
    internal_table_count: int,
    integrity: str,
    row_counts: list[tuple[str, int]],
    zero_rows: list[str],
    expected_mismatches: list[tuple[str, int, int | None]],
    skipped_indexes: list[str],
    skipped_views: list[tuple[str, str, str]],
    default_notes: list[str],
    fk_notes: list[str],
    con: sqlite3.Connection,
) -> str:
    """Build the SQLite schema audit report."""

    lines = [
        "# SQLite Schema Audit",
        "",
        f"Source database: `{sqlite_path}`",
        "",
        "## Summary",
        "",
        f"- SQLite table count including internal tables: {len(tables) + internal_table_count}",
        f"- User table count generated for PostgreSQL: {len(tables)}",
        f"- View count: {len(views)}",
        f"- Integrity check: `{integrity}`",
        f"- SQLite internal objects present: {'yes' if internal else 'no'}",
        "- SQLite internal objects should be skipped during PostgreSQL migration.",
        "",
        "## Expected Count Check",
        "",
    ]
    if expected_mismatches:
        lines.append("| Table | Expected | Actual |")
        lines.append("|---|---:|---:|")
        for table, expected, actual in expected_mismatches:
            lines.append(f"| {table} | {expected} | {actual} |")
    else:
        lines.append("All key expected counts match the live canonical DB signature.")
    lines.extend(["", "## Row Counts", "", "| Table | Rows |", "|---|---:|"])
    for table, count in row_counts:
        lines.append(f"| {table} | {count} |")

    lines.extend(["", "## Tables, Columns, Primary Keys, Indexes, Foreign Keys", ""])
    for table, sql in tables:
        lines.append(f"### `{table}`")
        lines.append("")
        lines.append(f"Rows: `{dict(row_counts)[table]}`")
        lines.append("")
        lines.append("| Column | SQLite type | Not null | Primary key position | Default |")
        lines.append("|---|---|---:|---:|---|")
        for col in table_columns(con, table):
            default = "" if col.default is None else f"`{col.default}`"
            lines.append(
                f"| {col.name} | {col.sqlite_type or '(blank)'} | "
                f"{int(col.notnull)} | {col.pk_position} | {default} |"
            )
        indexes = list(con.execute(f"PRAGMA index_list({quote_ident(table)})"))
        if indexes:
            lines.append("")
            lines.append("Indexes:")
            for idx in indexes:
                lines.append(f"- `{idx[1]}` unique={bool(idx[2])} origin={idx[3] if len(idx) > 3 else ''}")
        fks = foreign_keys(con, table)
        if fks:
            lines.append("")
            lines.append("Foreign keys:")
            for fk in fks:
                lines.append(f"- `{dict(fk)}`")
        lines.append("")

    lines.extend(["## Views", ""])
    for name, sql in views:
        status = "skipped/commented for review" if any(v[0] == name for v in skipped_views) else "generated"
        lines.append(f"### `{name}`")
        lines.append("")
        lines.append(f"Status: {status}")
        dependencies = view_dependencies(sql)
        usages = group_concat_usages(sql)
        if dependencies:
            lines.append(f"Dependencies: {', '.join(f'`{dep}`' for dep in dependencies)}")
        if usages:
            lines.append("")
            lines.append("GROUP_CONCAT usages:")
            lines.extend(f"- `{usage}`" for usage in usages)
        lines.append("")
        lines.append("```sql")
        lines.append(sql)
        lines.append("```")
        lines.append("")

    lines.extend(["## Suspicious Or Review Items", ""])
    if zero_rows:
        lines.append("Zero-row tables:")
        lines.extend(f"- `{name}`" for name in zero_rows)
    else:
        lines.append("- No zero-row tables found.")
    lines.append("")
    if internal:
        lines.append("SQLite internal objects to skip:")
        lines.extend(f"- `{row['type']}` `{row['name']}`" for row in internal)
    if default_notes:
        lines.append("")
        lines.append("Defaults omitted for manual review:")
        lines.extend(f"- {note}" for note in default_notes)
    if skipped_indexes:
        lines.append("")
        lines.append("Indexes skipped/commented for manual review:")
        lines.extend(f"- {note}" for note in skipped_indexes)
    if skipped_views:
        lines.append("")
        lines.append("Views skipped/commented due SQLite-only or unsafe syntax:")
        lines.extend(f"- `{name}`: {reason}" for name, reason, _ in skipped_views)
    if fk_notes:
        lines.append("")
        lines.append("Foreign-key declarations found:")
        lines.extend(f"- {note}" for note in fk_notes)
    else:
        lines.append("")
        lines.append("No SQLite foreign-key declarations found.")
    return "\n".join(lines) + "\n"


def build_generation_report(
    *,
    sqlite_path: Path,
    schema_path: Path,
    tables: list[tuple[str, str]],
    views: list[tuple[str, str]],
    converted_views: list[str],
    skipped_views: list[tuple[str, str, str]],
    skipped_indexes: list[str],
    default_notes: list[str],
    integrity: str,
) -> str:
    """Build the schema-generation report."""

    lines = [
        "# PostgreSQL Schema Generation Report",
        "",
        f"Source SQLite DB: `{sqlite_path}`",
        f"Generated schema: `{schema_path}`",
        "",
        "This draft is generated from the canonical SQLite mirror. It must be reviewed before production use.",
        "",
        "## Results",
        "",
        f"- Tables generated: {len(tables)}",
        f"- Views found: {len(views)}",
        f"- Views generated: {len(converted_views)}",
        f"- Views skipped/commented: {len(skipped_views)}",
        f"- SQLite integrity check: `{integrity}`",
        "",
        "## Skipped Views",
        "",
    ]
    if skipped_views:
        for name, reason, _sql in skipped_views:
            lines.append(f"- `{name}`: {reason}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Skipped Indexes", ""])
    if skipped_indexes:
        lines.extend(f"- {note}" for note in skipped_indexes)
    else:
        lines.append("- None.")
    lines.extend(["", "## Defaults Requiring Review", ""])
    if default_notes:
        lines.extend(f"- {note}" for note in default_notes)
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, default=DEFAULT_SQLITE)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    return parser.parse_args()


def main() -> int:
    """Run schema generation."""

    args = parse_args()
    if not args.sqlite.exists():
        raise SystemExit(f"SQLite database not found: {args.sqlite}")
    generate(args.sqlite, args.schema, args.report, args.audit)
    print(f"Wrote schema: {args.schema}")
    print(f"Wrote generation report: {args.report}")
    print(f"Wrote SQLite audit: {args.audit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

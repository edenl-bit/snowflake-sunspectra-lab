#!/usr/bin/env python3
"""
Export tables from a Snowflake database/schema to CSV files and optional DDL.
Uses only environment variables for connection and target database/schema.
No credentials or account names are written to any file in the repo.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from script directory, then from parent (e.g. home dir) if needed
_script_dir = Path(__file__).resolve().parent
load_dotenv(_script_dir / ".env")
load_dotenv(_script_dir.parent / ".env")

def get_connection():
    """Build connection params from environment. Use a PAT as SNOWFLAKE_PASSWORD (not your account password)."""
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    role = os.getenv("SNOWFLAKE_ROLE")
    for name, val in [("SNOWFLAKE_ACCOUNT", account), ("SNOWFLAKE_USER", user),
                     ("SNOWFLAKE_PASSWORD", password), ("SNOWFLAKE_WAREHOUSE", warehouse)]:
        if not val:
            print(f"Missing required env: {name}. Set in .env or environment.", file=sys.stderr)
            sys.exit(1)
    database = os.getenv("SNOWFLAKE_EXPORT_DATABASE") or os.getenv("SNOWFLAKE_DATABASE")
    schema = os.getenv("SNOWFLAKE_EXPORT_SCHEMA") or os.getenv("SNOWFLAKE_SCHEMA")
    if not database or not schema:
        print("Set SNOWFLAKE_EXPORT_DATABASE and SNOWFLAKE_EXPORT_SCHEMA (or SNOWFLAKE_DATABASE and SNOWFLAKE_SCHEMA).", file=sys.stderr)
        sys.exit(1)
    if account and ".snowflakecomputing.com" in account:
        account = account.replace(".snowflakecomputing.com", "")
    import snowflake.connector
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        role=role,
        database=database,
        schema=schema,
    )
    return conn, database, schema


def list_tables(conn, database, schema):
    """Return list of table names in the given database.schema."""
    cur = conn.cursor()
    cur.execute("SHOW TABLES IN SCHEMA " + f'"{database}"."{schema}"')
    rows = cur.fetchall()
    cur.close()
    # SHOW TABLES returns (created_on, name, ...); name is index 1
    return [row[1] for row in rows] if rows else []


def export_table_to_csv(conn, database, schema, table_name, out_path):
    """Export a single table to CSV. Optional: set SNOWFLAKE_EXPORT_LIMIT for max rows (e.g. 1000)."""
    import csv
    limit = os.getenv("SNOWFLAKE_EXPORT_LIMIT")
    limit_clause = f" LIMIT {int(limit)}" if limit and str(limit).isdigit() else ""
    cur = conn.cursor()
    try:
        cur.execute(f'SELECT * FROM "{database}"."{schema}"."{table_name}"{limit_clause}')
        columns = [d[0] for d in cur.description]
        rows = cur.fetchall()
    finally:
        cur.close()
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(
                str(c) if c is not None else "" for c in row
            )
    return len(rows)


def export_ddl(conn, database, schema, table_name, out_dir):
    """Export DDL for one table to schema/<table>.sql. Skip if not allowed (e.g. shared DB)."""
    import snowflake.connector.errors
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT GET_DDL('TABLE', %s)",
            [f'"{database}"."{schema}"."{table_name}"'],
        )
        row = cur.fetchone()
    except snowflake.connector.errors.ProgrammingError:
        # e.g. shared database does not support GET_DDL
        return
    finally:
        cur.close()
    if not row or not row[0]:
        return
    ddl = row[0]
    # Remove account-specific identifiers (e.g. stage URLs, account locator)
    lines = ddl.split("\n")
    cleaned = []
    for line in lines:
        if "CREATE TABLE" in line or "ALTER TABLE" in line or line.strip().startswith(")"):
            cleaned.append(line)
        elif line.strip() and not any(x in line.upper() for x in ("STAGE", "ACCOUNT", "STORAGE_INTEGRATION")):
            cleaned.append(line)
        elif line.strip():
            cleaned.append("  -- (omitted account-specific clause)")
    out_path = out_dir / f"{table_name}.sql"
    out_path.write_text("\n".join(cleaned) + "\n", encoding="utf-8")


def main():
    data_dir = Path(__file__).resolve().parent / "data"
    schema_dir = Path(__file__).resolve().parent / "schema"
    data_dir.mkdir(exist_ok=True)
    schema_dir.mkdir(exist_ok=True)

    conn, database, schema = get_connection()
    tables = list_tables(conn, database, schema)
    if not tables:
        print("No tables found in the specified database/schema.")
        conn.close()
        return

    print(f"Exporting {len(tables)} tables from {database}.{schema} to data/ and schema/")
    for name in tables:
        csv_path = data_dir / f"{name}.csv"
        n = export_table_to_csv(conn, database, schema, name, csv_path)
        print(f"  {name}.csv -> {n} rows")
        export_ddl(conn, database, schema, name, schema_dir)
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()

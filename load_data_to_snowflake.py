#!/usr/bin/env python3
"""
Create schema/tables (from schema/*.sql or inferred from CSV) and load all data/*.csv
into your Snowflake. Uses only environment variables from .env; no hardcoded credentials.
Does not add Semantic Model Configuration—tables and data only.
"""
import os
import csv
from pathlib import Path

from dotenv import load_dotenv

_script_dir = Path(__file__).resolve().parent
load_dotenv(_script_dir / ".env")
load_dotenv(_script_dir.parent / ".env")


def get_connection():
    """Connect to Snowflake using env vars only. Use a PAT as SNOWFLAKE_PASSWORD (not your account password)."""
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    database = os.getenv("SNOWFLAKE_DATABASE")
    schema = os.getenv("SNOWFLAKE_SCHEMA")
    role = os.getenv("SNOWFLAKE_ROLE")
    for name, val in [
        ("SNOWFLAKE_ACCOUNT", account),
        ("SNOWFLAKE_USER", user),
        ("SNOWFLAKE_PASSWORD", password),
        ("SNOWFLAKE_WAREHOUSE", warehouse),
        ("SNOWFLAKE_DATABASE", database),
        ("SNOWFLAKE_SCHEMA", schema),
    ]:
        if not val:
            raise SystemExit(f"Missing required env: {name}. Set in .env.")
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


def ensure_schema(conn, database, schema):
    """Create database and schema if they do not exist."""
    cur = conn.cursor()
    try:
        cur.execute(f'CREATE DATABASE IF NOT EXISTS "{database}"')
        cur.execute(f'USE DATABASE "{database}"')
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        cur.execute(f'USE SCHEMA "{schema}"')
    finally:
        cur.close()


def run_ddl_file(conn, ddl_path, database, schema):
    """Run a single DDL file. Replaces database/schema placeholders if present."""
    sql = ddl_path.read_text(encoding="utf-8")
    # Optional: substitute placeholders for user's database/schema
    sql = sql.replace("${database}", f'"{database}"').replace("${schema}", f'"{schema}"')
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt and not stmt.startswith("--"):
            conn.cursor().execute(stmt)


def create_table_from_csv(conn, database, schema, table_name, csv_path):
    """Create a table from CSV header (all columns VARCHAR) if table does not exist."""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
    cols = ", ".join(f'"{c}" VARCHAR' for c in header)
    cur = conn.cursor()
    try:
        cur.execute(f'CREATE TABLE IF NOT EXISTS "{database}"."{schema}"."{table_name}" ({cols})')
    finally:
        cur.close()


def load_csv_into_table(conn, database, schema, table_name, csv_path):
    """Load a CSV file into the given table using write_pandas or INSERT."""
    import pandas as pd
    df = pd.read_csv(csv_path)
    df.columns = [c.upper() for c in df.columns]
    if df.empty:
        return 0
    try:
        from snowflake.connector.pandas_tools import write_pandas
        success, _, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            schema=schema,
            database=database,
            auto_create_table=False,
            overwrite=False,
        )
        return nrows if success else 0
    except Exception:
        # Fallback: INSERT row by row
        cur = conn.cursor()
        cols = ", ".join(f'"{c}"' for c in df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        insert_sql = f'INSERT INTO "{schema}"."{table_name}" ({cols}) VALUES ({placeholders})'
        for _, row in df.iterrows():
            cur.execute(insert_sql, tuple(row))
        cur.close()
        return len(df)


def main():
    data_dir = _script_dir / "data"
    schema_dir = _script_dir / "schema"
    if not data_dir.exists():
        raise SystemExit("No data/ directory found. Run export_snowflake_to_csv.py first.")

    conn, database, default_schema = get_connection()

    # Multi-schema: data/SCHEMA_NAME/*.csv → create each schema and load its tables (509 tables)
    schema_dirs = sorted(d for d in data_dir.iterdir() if d.is_dir())
    if not schema_dirs:
        csv_files_flat = sorted(data_dir.glob("*.csv"))
        if not csv_files_flat:
            raise SystemExit(
                "No data in data/. Export first: set SNOWFLAKE_EXPORT_ALL_SCHEMAS=1 in .env, "
                "then run python export_snowflake_to_csv.py. See data/README.md and SCHEMAS_REFERENCE.md."
            )
    if schema_dirs:
        total_tables = 0
        for schema_path in schema_dirs:
            schema_name = schema_path.name
            csv_files = sorted(schema_path.glob("*.csv"))
            if not csv_files:
                continue
            ensure_schema(conn, database, schema_name)
            for csv_path in csv_files:
                table_name = csv_path.stem
                ddl_path = schema_dir / schema_name / f"{table_name}.sql"
                if not ddl_path.exists():
                    ddl_path = schema_dir / f"{table_name}.sql"
                if ddl_path.exists():
                    run_ddl_file(conn, ddl_path, database, schema_name)
                else:
                    create_table_from_csv(conn, database, schema_name, table_name, csv_path)
                n = load_csv_into_table(conn, database, schema_name, table_name, csv_path)
                print(f"  {schema_name}.{table_name}: {n} rows loaded")
                total_tables += 1
        print(f"Done. Loaded {total_tables} tables across {len(schema_dirs)} schemas.")
    else:
        # Flat data/*.csv (legacy): use SNOWFLAKE_SCHEMA from .env
        ensure_schema(conn, database, default_schema)
        csv_files = sorted(data_dir.glob("*.csv"))
        for csv_path in csv_files:
            table_name = csv_path.stem
            ddl_path = schema_dir / f"{table_name}.sql"
            if ddl_path.exists():
                run_ddl_file(conn, ddl_path, database, default_schema)
            else:
                create_table_from_csv(conn, database, default_schema, table_name, csv_path)
            n = load_csv_into_table(conn, database, default_schema, table_name, csv_path)
            print(f"  {table_name}: {n} rows loaded")
        print("Done.")

    conn.close()


if __name__ == "__main__":
    main()

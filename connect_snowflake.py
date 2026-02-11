#!/usr/bin/env python3
"""
Test connection to Snowflake using credentials from .env.
Run: python connect_snowflake.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv

_script_dir = Path(__file__).resolve().parent
load_dotenv(_script_dir / ".env")
load_dotenv(_script_dir.parent / ".env")


def main():
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    database = os.getenv("SNOWFLAKE_DATABASE")
    schema = os.getenv("SNOWFLAKE_SCHEMA")
    role = os.getenv("SNOWFLAKE_ROLE")

    missing = []
    for name, val in [
        ("SNOWFLAKE_ACCOUNT", account),
        ("SNOWFLAKE_USER", user),
        ("SNOWFLAKE_PASSWORD", password),
        ("SNOWFLAKE_WAREHOUSE", warehouse),
        ("SNOWFLAKE_DATABASE", database),
        ("SNOWFLAKE_SCHEMA", schema),
    ]:
        if not val or val.startswith("your_"):
            missing.append(name)
    if missing:
        print("Missing or placeholder env vars:", ", ".join(missing))
        print("Copy env.example to .env and set your Snowflake credentials.")
        raise SystemExit(1)

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
    cur = conn.cursor()
    cur.execute("SELECT CURRENT_USER(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    row = cur.fetchone()
    cur.close()
    conn.close()

    print("Connected to Snowflake successfully.")
    print(f"  User:      {row[0]}")
    print(f"  Warehouse: {row[1]}")
    print(f"  Database:  {row[2]}")
    print(f"  Schema:    {row[3]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate and create Snowflake Tasks (scheduled SQL). Uses .env for connection.
Run: python generate_tasks.py

Tasks are created in the database/schema from .env. Edit TASK_DEFINITIONS below to add or change tasks.
Does not add Semantic Model Configuration—tasks run plain SQL only.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

_script_dir = Path(__file__).resolve().parent
load_dotenv(_script_dir / ".env")
load_dotenv(_script_dir.parent / ".env")


def get_connection():
    """Connect to Snowflake using env vars. Use a PAT as SNOWFLAKE_PASSWORD."""
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


# Define tasks: (name, schedule, sql_statement)
# schedule: e.g. '60 MINUTE', '1 DAY', 'USING CRON 0 8 * * * UTC' (8am UTC daily)
TASK_DEFINITIONS = [
    (
        "LAB_VERIFY_ROW_COUNTS",
        "1 DAY",
        "SELECT CURRENT_TIMESTAMP() AS run_at, "
        "(SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = CURRENT_SCHEMA()) AS table_count",
    ),
    (
        "LAB_HEARTBEAT",
        "60 MINUTE",
        "SELECT 1 AS heartbeat, CURRENT_TIMESTAMP() AS at",
    ),
]


def generate_task_sql(database: str, schema: str, warehouse: str, task_name: str, schedule: str, sql: str) -> str:
    """Build CREATE OR REPLACE TASK statement. Single statement; no semicolons in sql."""
    sql_clean = sql.strip().replace("\n", " ")
    return (
        f'CREATE OR REPLACE TASK "{database}"."{schema}"."{task_name}" '
        f'WAREHOUSE = "{warehouse}" '
        f"SCHEDULE = '{schedule}' "
        f"AS {sql_clean}"
    )


def main():
    conn, database, schema = get_connection()
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    if not warehouse:
        raise SystemExit("SNOWFLAKE_WAREHOUSE is required in .env.")

    cur = conn.cursor()
    try:
        for task_name, schedule, sql in TASK_DEFINITIONS:
            create_sql = generate_task_sql(database, schema, warehouse, task_name, schedule, sql)
            cur.execute(create_sql)
            print(f"  Created task: {schema}.{task_name} (schedule: {schedule})")
        # Tasks are created suspended by default; optionally resume (user can run SHOW TASKS and ALTER TASK ... RESUME)
        print("Done. Tasks are created SUSPENDED. To run them: ALTER TASK <name> RESUME;")
    finally:
        cur.close()
    conn.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate and create Snowflake Tasks (scheduled SQL). Uses .env for connection.
Run: python generate_tasks.py

If tasks/tasks.sql exists (from export_tasks_from_snowflake.py), runs that DDL to duplicate tasks.
Otherwise creates tasks from TASK_DEFINITIONS below. Edit TASK_DEFINITIONS to add or change tasks.
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


def run_tasks_sql_file(conn, tasks_file: Path) -> bool:
    """Execute SQL statements from tasks/tasks.sql (from export_tasks_from_snowflake.py). Returns True if ran."""
    if not tasks_file.exists():
        return False
    content = tasks_file.read_text(encoding="utf-8")
    # Each exported task DDL is one block (joined with \n\n); don't split on ";" inside definitions
    blocks = [b.strip() for b in content.split("\n\n") if b.strip() and not b.strip().startswith("--")]
    if not blocks:
        return False
    cur = conn.cursor()
    try:
        for stmt in blocks:
            cur.execute(stmt)
            # Print task name if it looks like CREATE TASK "db"."schema"."name"
            if "CREATE" in stmt and "TASK" in stmt:
                print(f"  Created task from tasks/tasks.sql")
        return True
    finally:
        cur.close()


def main():
    conn, database, schema = get_connection()
    tasks_file = _script_dir / "tasks" / "tasks.sql"

    # Prefer duplicated tasks from export (tasks/tasks.sql)
    if run_tasks_sql_file(conn, tasks_file):
        conn.close()
        print("Done. Tasks from tasks/tasks.sql were created (typically SUSPENDED). To run: ALTER TASK <name> RESUME;")
        return

    # Else create from TASK_DEFINITIONS
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    if not warehouse:
        raise SystemExit("SNOWFLAKE_WAREHOUSE is required in .env (or export tasks to tasks/tasks.sql first).")

    cur = conn.cursor()
    try:
        for task_name, schedule, sql in TASK_DEFINITIONS:
            create_sql = generate_task_sql(database, schema, warehouse, task_name, schedule, sql)
            cur.execute(create_sql)
            print(f"  Created task: {schema}.{task_name} (schedule: {schedule})")
        print("Done. Tasks are created SUSPENDED. To run them: ALTER TASK <name> RESUME;")
    finally:
        cur.close()
    conn.close()


if __name__ == "__main__":
    main()

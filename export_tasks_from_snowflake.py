#!/usr/bin/env python3
"""
Export existing Snowflake Tasks from your Snowflake (GET_DDL) into tasks/tasks.sql.
Then run generate_tasks.py in the same or another environment to duplicate those tasks.

Uses .env for connection. Set SNOWFLAKE_DATABASE (or SNOWFLAKE_EXPORT_DATABASE) to the database to scan.
Run: python export_tasks_from_snowflake.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_script_dir = Path(__file__).resolve().parent
load_dotenv(_script_dir / ".env")
load_dotenv(_script_dir.parent / ".env")


def get_connection():
    """Connect using env vars. Use a PAT as SNOWFLAKE_PASSWORD."""
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    role = os.getenv("SNOWFLAKE_ROLE")
    for name, val in [
        ("SNOWFLAKE_ACCOUNT", account),
        ("SNOWFLAKE_USER", user),
        ("SNOWFLAKE_PASSWORD", password),
        ("SNOWFLAKE_WAREHOUSE", warehouse),
    ]:
        if not val:
            print(f"Missing required env: {name}. Set in .env.", file=sys.stderr)
            sys.exit(1)
    database = os.getenv("SNOWFLAKE_EXPORT_DATABASE") or os.getenv("SNOWFLAKE_DATABASE")
    if not database:
        print("Set SNOWFLAKE_EXPORT_DATABASE or SNOWFLAKE_DATABASE in .env.", file=sys.stderr)
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
    )
    return conn, database


def main():
    conn, database = get_connection()
    out_dir = _script_dir / "tasks"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "tasks.sql"

    cur = conn.cursor()
    try:
        cur.execute(f'SHOW TASKS IN DATABASE "{database}"')
        rows = cur.fetchall()
        col_names = [d[0].lower() for d in cur.description]
        name_idx = col_names.index("name")
        db_idx = col_names.index("database_name")
        schema_idx = col_names.index("schema_name")
    except Exception as e:
        print(f"SHOW TASKS failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print(f"No tasks found in database {database}. Writing empty tasks.sql.")
        out_file.write_text("-- No tasks exported. Run SHOW TASKS IN DATABASE in Snowflake to list tasks.\n", encoding="utf-8")
        conn.close()
        return

    ddls = []
    for row in rows:
        task_name = row[name_idx]
        db_name = row[db_idx]
        schema_name = row[schema_idx]
        full_name = f'"{db_name}"."{schema_name}"."{task_name}"'
        try:
            cur.execute("SELECT GET_DDL('TASK', %s)", (full_name,))
            ddl_row = cur.fetchone()
            if ddl_row and ddl_row[0]:
                ddls.append(ddl_row[0].strip())
                print(f"  Exported: {schema_name}.{task_name}")
            else:
                print(f"  Skipped (no DDL): {schema_name}.{task_name}", file=sys.stderr)
        except Exception as e:
            print(f"  Skipped {schema_name}.{task_name}: {e}", file=sys.stderr)

    cur.close()
    conn.close()

    if ddls:
        content = "\n\n".join(ddls) + "\n"
        out_file.write_text(content, encoding="utf-8")
        print(f"Done. Wrote {len(ddls)} task(s) to {out_file}")
    else:
        out_file.write_text("-- No task DDL could be retrieved. Check privileges (OWNERSHIP or MONITOR/OPERATE on tasks).\n", encoding="utf-8")
        print("No DDL retrieved. Wrote placeholder to tasks/tasks.sql", file=sys.stderr)


if __name__ == "__main__":
    main()

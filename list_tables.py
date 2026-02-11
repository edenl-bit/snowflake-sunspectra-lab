#!/usr/bin/env python3
"""List and count tables in the SunSpectra database (production, not the lab)."""
import os
from pathlib import Path

from dotenv import load_dotenv

_script_dir = Path(__file__).resolve().parent
load_dotenv(_script_dir / ".env")

# Database to inspect (the real SunSpectra, not the lab). Name in account: SUN_SPECTRA
SUNSPECTRA_DB = os.getenv("SUNSPECTRA_DATABASE", "SUN_SPECTRA")


def main():
    import snowflake.connector
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    role = os.getenv("SNOWFLAKE_ROLE")
    if not all([account, user, password, warehouse]):
        raise SystemExit("Missing SNOWFLAKE_* env vars in .env")
    if ".snowflakecomputing.com" in (account or ""):
        account = account.replace(".snowflakecomputing.com", "")

    # Connect without default database so we can query any DB
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        role=role,
    )
    cur = conn.cursor()

    # Prefer exact match (e.g. SUN_SPECTRA); else any SunSpectra DB excluding lab
    cur.execute("SHOW DATABASES")
    all_dbs = [r[1] for r in cur.fetchall() if r[1]]
    sunspectra = [d for d in all_dbs if d.upper() == SUNSPECTRA_DB.upper().replace(" ", "_")]
    if not sunspectra:
        sunspectra = [d for d in all_dbs if "SUN" in d.upper() and "SPECTRA" in d.upper() and "LAB" not in d.upper()]
    if not sunspectra:
        print(f"No database named '{SUNSPECTRA_DB}' found in your account.")
        print("Available databases:", ", ".join(all_dbs[:20]) + ("..." if len(all_dbs) > 20 else ""))
        cur.close()
        conn.close()
        return

    database = sunspectra[0]
    cur.execute(f'USE DATABASE "{database}"')
    cur.execute("SHOW SCHEMAS IN DATABASE")
    schemas = [r[1] for r in cur.fetchall() if r[1]]

    total = 0
    print(f"Database: {database}\n")
    for schema in schemas:
        try:
            cur.execute(f'USE SCHEMA "{schema}"')
            cur.execute("SHOW TABLES")
            tables = [r[1] for r in cur.fetchall() if r[1]]
            if tables:
                total += len(tables)
                print(f"  {schema}: {len(tables)} table(s)")
                for t in sorted(tables):
                    print(f"    - {t}")
        except Exception as e:
            print(f"  {schema}: (skip: {e})")

    print(f"\nTotal tables in {database}: {total}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()

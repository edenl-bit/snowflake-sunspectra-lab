# Getting started (4 steps)

Use this when you want to **load the 8-table lab into your Snowflake** and run queries. For the full 509 tables, see [SCHEMAS_REFERENCE.md](SCHEMAS_REFERENCE.md).

---

### 1. Clone and install

```bash
git clone <repo-url>
cd snowflake-sunspectra-lab
pip install -r requirements.txt
```

---

### 2. Configure your Snowflake

```bash
cp env.example .env
```

Edit `.env` and set:

- `SNOWFLAKE_ACCOUNT` — your account (e.g. `xy12345`)
- `SNOWFLAKE_USER` — your username
- `SNOWFLAKE_PASSWORD` — **your programmatic access token (PAT)**, not your login password
- `SNOWFLAKE_WAREHOUSE` — warehouse name
- `SNOWFLAKE_DATABASE` — database where you want the tables
- `SNOWFLAKE_SCHEMA` — schema where you want the 8 tables (e.g. `PUBLIC`)
- `SNOWFLAKE_ROLE` — role (e.g. `ACCOUNTADMIN` or your custom role)

**Create a PAT:** Snowsight → **Governance & security** → **Users & roles** → your user → **Programmatic access tokens** → **Generate new token**. Copy the token into `SNOWFLAKE_PASSWORD`.

---

### 3. Load the data

```bash
python load_data_to_snowflake.py
```

You should see each table and row count. The 8 tables (CUSTOMER, LINEITEM, NATION, ORDERS, PART, PARTSUPP, REGION, SUPPLIER) are now in your database/schema.

**Optional:** Test the connection first with `python connect_snowflake.py`.

---

### 4. Run queries in Snowflake

Open **Snowflake Worksheets** (or any SQL client connected to your account), choose your database and schema, then run any query from **`sample_queries.sql`**.

Example (verify load):

```sql
SELECT 'CUSTOMER' AS table_name, COUNT(*) AS row_count FROM CUSTOMER
UNION ALL SELECT 'LINEITEM', COUNT(*) FROM LINEITEM
UNION ALL SELECT 'NATION', COUNT(*) FROM NATION
UNION ALL SELECT 'ORDERS', COUNT(*) FROM ORDERS
UNION ALL SELECT 'PART', COUNT(*) FROM PART
UNION ALL SELECT 'PARTSUPP', COUNT(*) FROM PARTSUPP
UNION ALL SELECT 'REGION', COUNT(*) FROM REGION
UNION ALL SELECT 'SUPPLIER', COUNT(*) FROM SUPPLIER
ORDER BY table_name;
```

---

**Next:** See [README.md](README.md) for full options (509 tables, export script, project structure).

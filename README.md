# SunSpectra Database Lab

Create lab data in your own Snowflake account in a few steps. This repo includes CSV data and a loader—no credentials are stored.

## Quick start (create lab data)

```bash
git clone <repo-url>
cd snowflake-sunspectra-lab
pip install -r requirements.txt
cp env.example .env
# Edit .env: set SNOWFLAKE_PASSWORD to your PAT (programmatic access token), not your account password
python load_data_to_snowflake.py
```

Done. Tables (CUSTOMER, LINEITEM, NATION, ORDERS, PART, PARTSUPP, REGION, SUPPLIER) are created and loaded from `data/`. Run queries in Snowflake Worksheets or any client.

## Prerequisites

- Python 3.8+
- A Snowflake account (trial or paid) and a **programmatic access token (PAT)**—you put the PAT in `SNOWFLAKE_PASSWORD` (same as password for the connector)

## Setup (detailed)

1. **Clone and install**
   ```bash
   git clone <repo-url>
   cd snowflake-sunspectra-lab
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Snowflake**
   ```bash
   cp env.example .env
   ```
   Edit `.env` with: `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_ROLE`.

   **Use a programmatic access token (PAT) as the password:** Put your PAT in `SNOWFLAKE_PASSWORD`—do not use your Snowflake account login password. In Snowflake (Snowsight), go to **Governance & security** → **Users & roles**, select your user, then under **Programmatic access tokens** click **Generate new token**. Copy the token and set `SNOWFLAKE_PASSWORD=<your_token>` in `.env`. Tokens show as **Active** or **Expired**; when one expires, generate a new token and update `.env`.

3. **Load lab data**
   ```bash
   python load_data_to_snowflake.py
   ```
   Creates the schema (if needed) and loads all CSVs from `data/` into your database/schema.

## Verify and query

After loading, run SQL in Snowflake Worksheets (or any client). Examples:

**Active query (verification)** — run this in Snowflake to confirm the lab is loaded:

```sql
-- Row counts per table (active query)
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

**Complex query (SunSpectra)** — revenue by region, joining ORDERS, LINEITEM, CUSTOMER, NATION, and REGION:

```sql
SELECT
  r.R_NAME AS region_name,
  n.N_NAME AS nation_name,
  COUNT(DISTINCT o.O_ORDERKEY) AS order_count,
  SUM(l.L_EXTENDEDPRICE * (1 - l.L_DISCOUNT)) AS revenue
FROM REGION r
JOIN NATION n ON r.R_REGIONKEY = n.N_REGIONKEY
JOIN CUSTOMER c ON c.C_NATIONKEY = n.N_NATIONKEY
JOIN ORDERS o ON o.O_CUSTKEY = c.C_CUSTKEY
JOIN LINEITEM l ON l.L_ORDERKEY = o.O_ORDERKEY
WHERE o.O_ORDERSTATUS = 'F'
GROUP BY r.R_NAME, n.N_NAME
ORDER BY region_name, nation_name;
```

All of these are in `sample_queries.sql`—copy and run in Snowflake.

## Project structure

| Path | Purpose |
|------|--------|
| `data/` | CSV files (one per table). Loaded by the script. |
| `env.example` | Copy to `.env` and add your Snowflake credentials. |
| `load_data_to_snowflake.py` | **Run this to create lab data** in your Snowflake. |
| `sample_queries.sql` | Example queries to run after loading. |
| `export_snowflake_to_csv.py` | Optional: export from another Snowflake into `data/`. |

# SunSpectra Database Lab

Load Snowflake tables and queries into **your own** Snowflake. Use the 8-table lab (included) or export and load all 509 tables across 15 schemas.

**New here?** → [GETTING_STARTED.md](GETTING_STARTED.md) (4 steps to load the 8-table lab and run queries.)

---

## Table of contents

1. [Overview](#overview)
2. [Two ways to use this repo](#two-ways-to-use-this-repo)
3. [Prerequisites](#prerequisites)
4. [Quick start](#quick-start)
5. [Setup (step-by-step)](#setup-step-by-step)
6. [Sample queries](#sample-queries)
7. [Project structure](#project-structure)
8. [Reference](#reference)

---

## Overview

| What | Description |
|------|-------------|
| **Goal** | Get lab data (8 tables or 509 tables) into **your** Snowflake so you can run queries. |
| **Auth** | Use a **programmatic access token (PAT)** in `.env`—not your account password. |
| **Credentials** | None stored in the repo; you use your own account, database, and schema. |

**In one sentence:** Clone → copy `.env` and add your Snowflake PAT + database/schema → run the loader → run SQL in Snowflake.

---

## Two ways to use this repo

| Option | What you load | Data layout | When to use |
|--------|----------------|-------------|-------------|
| **A. 8-table lab** | 8 SunSpectra tables (CUSTOMER, LINEITEM, NATION, ORDERS, PART, PARTSUPP, REGION, SUPPLIER) | `data/*.csv` (flat; already in repo) | Try the lab quickly, run sample queries. |
| **B. Full (509 tables)** | All tables across 15 schemas (ANALYTICS, CATALOG, CUSTOMER, etc.) | `data/SCHEMA_NAME/TABLE.csv` (one folder per schema) | Recreate the full environment in another Snowflake. |

- **Option A:** Run the loader as-is; it loads the 8 tables into the schema you set in `.env`. Tables: CUSTOMER, LINEITEM, NATION, ORDERS, PART, PARTSUPP, REGION, SUPPLIER (see `data/*.csv`).
- **Option B:** First export from the source Snowflake with `SNOWFLAKE_EXPORT_ALL_SCHEMAS=1`, then run the loader; it creates each schema and loads all tables. See [SCHEMAS_REFERENCE.md](SCHEMAS_REFERENCE.md).

---

## Prerequisites

- Python 3.8+
- Your own Snowflake account (trial or paid)
- A **programmatic access token (PAT)** for your user → put it in `SNOWFLAKE_PASSWORD` in `.env`  
  (Create in Snowsight: **Governance & security** → **Users & roles** → your user → **Programmatic access tokens** → **Generate new token**.)

---

## Quick start

```bash
git clone <repo-url>
cd snowflake-sunspectra-lab
pip install -r requirements.txt
cp env.example .env
# Edit .env: your Snowflake account, user, PAT (SNOWFLAKE_PASSWORD), warehouse, database, schema, role
python load_data_to_snowflake.py
```

Then run the sample queries in Snowflake Worksheets (or any client). See [Sample queries](#sample-queries) below or open `sample_queries.sql`.

**Optional:** Test the connection first: `python connect_snowflake.py`

---

## Setup (step-by-step)

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
   Edit `.env` with your values:
   - `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD` (your **PAT**)
   - `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_ROLE`

3. **Load data**
   ```bash
   python load_data_to_snowflake.py
   ```
   - With **flat** `data/*.csv` (default): loads 8 tables into `SNOWFLAKE_SCHEMA`.
   - With **subdirs** `data/SCHEMA_NAME/`: creates each schema and loads all tables (509 across 15 schemas).

4. **Verify**  
   Run **Active query 1** from [Sample queries](#sample-queries) in Snowflake to confirm row counts.

---

## Sample queries

All of these are in **`sample_queries.sql`**. Copy into Snowflake Worksheets and run.

| # | Name | Purpose |
|---|------|--------|
| 1 | Row counts per table | Verify the lab is loaded |
| 2 | Regions and nation count | Nations per region |
| 3 | Sample from CUSTOMER | Top 10 by account balance |
| 4 | Revenue by region (complex) | Joins REGION, NATION, CUSTOMER, ORDERS, LINEITEM |

**Active query 1 (verification):**
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

**Complex query (revenue by region):**
```sql
SELECT r.R_NAME AS region_name, n.N_NAME AS nation_name,
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

Full SQL for all four queries: **`sample_queries.sql`**.

---

## Project structure

```
snowflake-sunspectra-lab/
├── README.md                 ← You are here
├── GETTING_STARTED.md        ← Short 4-step guide
├── SCHEMAS_REFERENCE.md      ← 509 tables / 15 schemas list and how to export/load
├── env.example               ← Copy to .env and fill in
├── requirements.txt
├── data/                     ← CSVs: flat (8 tables) or data/SCHEMA_NAME/ (509 tables)
├── schema/                   ← Optional DDL per table
├── sample_queries.sql        ← All active + complex queries
├── load_data_to_snowflake.py ← Main script: load data into your Snowflake
├── export_snowflake_to_csv.py← Export from Snowflake (optional; set SNOWFLAKE_EXPORT_ALL_SCHEMAS=1 for all)
├── connect_snowflake.py     ← Test connection
└── list_tables.py            ← List/count tables in a database (optional)
```

| Category | File | Purpose |
|----------|------|--------|
| **Setup** | `env.example` | Template for `.env` (Snowflake credentials). |
| **Load** | `load_data_to_snowflake.py` | Load `data/` into your Snowflake (run this to create lab data). |
| **Export** | `export_snowflake_to_csv.py` | Export from Snowflake into `data/` (single schema or all schemas). |
| **Verify** | `connect_snowflake.py` | Test that `.env` and PAT work. |
| **Verify** | `sample_queries.sql` | Queries to run after loading. |
| **Reference** | `SCHEMAS_REFERENCE.md` | Schema list and how to do full 509-table export/load. |
| **Optional** | `list_tables.py` | List tables in a database (e.g. SunSpectra production). |

---

## Reference

- **PAT (programmatic access token):** Snowsight → **Governance & security** → **Users & roles** → your user → **Programmatic access tokens** → **Generate new token**. Put the token in `SNOWFLAKE_PASSWORD`. Never use your account login password.
- **8-table lab:** CUSTOMER, LINEITEM, NATION, ORDERS, PART, PARTSUPP, REGION, SUPPLIER (see table in [Overview](#overview) and files in `data/`).
- **Full 509 tables:** See [SCHEMAS_REFERENCE.md](SCHEMAS_REFERENCE.md) for schema names and export/load steps.

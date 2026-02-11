# SunSpectra Database Lab

Load **509 tables across 15 schemas** into **your own** Snowflake. Export from a source Snowflake, then load into your target environment. The repo contains only `env.example` (no credentials, no table data).

**New here?** → [GETTING_STARTED.md](GETTING_STARTED.md) (export then load in 4 steps.)

---

## Table of contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick start](#quick-start)
4. [Setup (step-by-step)](#setup-step-by-step)
5. [Sample queries](#sample-queries)
6. [Project structure](#project-structure)
7. [Reference](#reference)

---

## Overview

| What | Description |
|------|-------------|
| **Goal** | Get all **509 tables across 15 schemas** into your Snowflake so you can run queries. |
| **Flow** | 1) Export from source Snowflake → `data/SCHEMA_NAME/TABLE.csv`. 2) Load into your Snowflake. |
| **Auth** | Use a **programmatic access token (PAT)** in `.env`—not your account password. |
| **Credentials** | The repo contains **only `env.example`**. Copy it to `.env` locally and fill in your values; `.env` is not in the repo. |
| **Scope** | Tables and data only. **Semantic Model Configuration is not added** by this repo. |

**In one sentence:** Clone → copy `env.example` to `.env` → export from source (509 tables) → load into your Snowflake.

---

## Prerequisites

- Python 3.8+
- Your own Snowflake account (trial or paid)
- A **programmatic access token (PAT)** for your user → put it in `SNOWFLAKE_PASSWORD` in your local `.env` (copy from `env.example`).  
  (Create in Snowsight: **Governance & security** → **Users & roles** → your user → **Programmatic access tokens** → **Generate new token**.)

---

## Quick start

**Step 1 — Export** (from the Snowflake that has the 509 tables):

```bash
git clone <repo-url>
cd snowflake-sunspectra-lab
pip install -r requirements.txt
cp env.example .env
# Edit .env: source Snowflake connection + SNOWFLAKE_EXPORT_ALL_SCHEMAS=1
python export_snowflake_to_csv.py
```

**Step 2 — Load** (into your Snowflake):

```bash
# Edit .env: your target Snowflake account, database, etc.
python load_data_to_snowflake.py
```

Then run queries in Snowflake Worksheets. See [Sample queries](#sample-queries) or `sample_queries.sql`.

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
   Copy `env.example` to `.env`, then edit `.env` with your values:
   - `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD` (your **PAT**)
   - `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_ROLE`

3. **Export** (from source Snowflake)
   - Set `SNOWFLAKE_EXPORT_ALL_SCHEMAS=1` in `.env` and point connection at the source database.
   - Run: `python export_snowflake_to_csv.py`  
   This writes `data/SCHEMA_NAME/TABLE_NAME.csv` for all 15 schemas (509 tables).

4. **Load** (into your Snowflake)
   - Point `.env` at your target account/database.
   - Run: `python load_data_to_snowflake.py`  
   Creates each schema and loads all tables.

5. **Verify**  
   Run queries from [Sample queries](#sample-queries) or `sample_queries.sql` in Snowflake (use the schema that has the relevant tables, e.g. PUBLIC).

---

## Sample queries

All of these are in **`sample_queries.sql`**. They reference tables (CUSTOMER, LINEITEM, NATION, ORDERS, PART, PARTSUPP, REGION, SUPPLIER) that may live in a schema such as PUBLIC after you load the 509 tables. Run in Snowflake Worksheets after selecting the right database/schema.

| # | Name | Purpose |
|---|------|--------|
| 1 | Row counts per table | Verify tables are loaded |
| 2 | Regions and nation count | Nations per region |
| 3 | Sample from CUSTOMER | Top 10 by account balance |
| 4 | Revenue by region (complex) | Joins REGION, NATION, CUSTOMER, ORDERS, LINEITEM |

Full SQL: **`sample_queries.sql`**.

---

## Project structure

```
snowflake-sunspectra-lab/
├── README.md                 ← You are here
├── GETTING_STARTED.md        ← 4-step export + load guide
├── SCHEMAS_REFERENCE.md      ← 509 tables / 15 schemas list
├── env.example               ← Copy to .env and fill in
├── requirements.txt
├── data/                     ← Populated by export (data/SCHEMA_NAME/*.csv). See data/README.md
├── schema/                   ← Optional DDL per table
├── sample_queries.sql        ← Queries to run after loading
├── load_data_to_snowflake.py ← Load data/ into your Snowflake (509 tables)
├── export_snowflake_to_csv.py← Export from Snowflake (set SNOWFLAKE_EXPORT_ALL_SCHEMAS=1)
├── generate_tasks.py         ← Create Snowflake Tasks (scheduled SQL). Edit TASK_DEFINITIONS to customize.
├── connect_snowflake.py      ← Test connection
└── list_tables.py            ← List tables in a database (optional)
```

| Category | File | Purpose |
|----------|------|--------|
| **Setup** | `env.example` | **Only** env file in the repo. Copy to `.env` locally. |
| **Export** | `export_snowflake_to_csv.py` | Export 509 tables from Snowflake into `data/SCHEMA_NAME/`. Set `SNOWFLAKE_EXPORT_ALL_SCHEMAS=1`. |
| **Load** | `load_data_to_snowflake.py` | Load `data/` (509 tables, 15 schemas) into your Snowflake. |
| **Tasks** | `generate_tasks.py` | Create Snowflake Tasks (scheduled SQL). Edit `TASK_DEFINITIONS` in the script to add or change tasks. |
| **Verify** | `connect_snowflake.py` | Test that your local `.env` and PAT work. |
| **Verify** | `sample_queries.sql` | Queries to run after loading. |
| **Reference** | `SCHEMAS_REFERENCE.md` | Schema list (15 schemas, 509 tables) and export/load steps. |
| **Optional** | `list_tables.py` | List tables in a database. |

---

## Reference

- **Credentials:** The repo has **only `env.example`**. Copy it to `.env` locally; `.env` is gitignored.
- **PAT:** Snowsight → **Governance & security** → **Users & roles** → your user → **Programmatic access tokens** → **Generate new token**. Put the token in `SNOWFLAKE_PASSWORD`.
- **509 tables / 15 schemas:** See [SCHEMAS_REFERENCE.md](SCHEMAS_REFERENCE.md) for schema names and step-by-step export/load.
- **Semantic Model Configuration:** Not used. This repo only creates/loads tables and data; it does not add or configure Semantic Models.

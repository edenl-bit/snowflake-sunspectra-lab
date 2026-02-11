# Getting started (509 tables)

Load **all 509 tables across 15 schemas** into your Snowflake: export from a source, then load into your target.

---

### 1. Clone and install

```bash
git clone <repo-url>
cd snowflake-sunspectra-lab
pip install -r requirements.txt
```

---

### 2. Configure Snowflake

The repo contains **only `env.example`** (no `.env`). Copy it to `.env` locally:

```bash
cp env.example .env
```

Edit `.env` and set your Snowflake connection:

- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD` (your **PAT**), `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_ROLE`

**Create a PAT:** Snowsight → **Governance & security** → **Users & roles** → your user → **Programmatic access tokens** → **Generate new token**. Put the token in `SNOWFLAKE_PASSWORD`.

---

### 3. Export from source Snowflake

In `.env` add:

```
SNOWFLAKE_EXPORT_ALL_SCHEMAS=1
```

Point the connection at the **source** Snowflake (the one that has the 509 tables). Then run:

```bash
python export_snowflake_to_csv.py
```

This creates `data/ANALYTICS/`, `data/CUSTOMER/`, … with one CSV per table (509 tables across 15 schemas).

---

### 4. Load into your Snowflake

Point `.env` at your **target** Snowflake (your account/database where you want the tables). Then run:

```bash
python load_data_to_snowflake.py
```

The loader creates each schema and loads all tables. When it finishes, run queries in Snowflake Worksheets (see `sample_queries.sql`).

**Optional:** Test the connection first: `python connect_snowflake.py`

---

**Next:** [SCHEMAS_REFERENCE.md](SCHEMAS_REFERENCE.md) for the schema list. [README.md](README.md) for full project structure.

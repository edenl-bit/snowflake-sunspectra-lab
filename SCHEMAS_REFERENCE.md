# Schemas reference — 509 tables across 15 schemas

**Total: 509 tables across 15 schemas.** When loading into **your own Snowflake environment**, you can load either the 8-table SunSpectra lab (single schema) or all 509 tables (all schemas below).

| Schema              | # Tables |
|---------------------|----------|
| ANALYTICS            | 38       |
| CATALOG              | 32       |
| CUSTOMER             | 40       |
| DBT_DEV              | 28       |
| DBT_DEV_MARTS        | 30       |
| DBT_DEV_STAGING      | 28       |
| EMAIL_CAMPAIGNS      | 34       |
| FINANCE              | 34       |
| GOOGLE               | 41       |
| INFORMATION_SCHEMA   | 28       |
| PUBLIC               | 28       |
| PUBLIC_DBT_STAGING   | 28       |
| PUBLIC_MARTS         | 30       |
| PUBLIC_STAGING       | 28       |
| SHIPBOB              | 33       |
| ZENDESK              | 29       |

**Load all 509 tables into your Snowflake**

1. **Export** (from the Snowflake that has these tables): In `.env` set `SNOWFLAKE_EXPORT_ALL_SCHEMAS=1`, then run `python export_snowflake_to_csv.py`. This writes `data/SCHEMA_NAME/TABLE_NAME.csv` for every schema.
2. **Load** (into your own Snowflake): Point `.env` at your account/database, then run `python load_data_to_snowflake.py`. The loader sees `data/ANALYTICS/`, `data/CUSTOMER/`, etc., creates each schema in your database, and loads all tables.

**Load only the 8 SunSpectra tables (single schema)**

Use flat `data/*.csv` (no subdirs). Set `SNOWFLAKE_DATABASE` and `SNOWFLAKE_SCHEMA` in `.env`. Run `python load_data_to_snowflake.py`; the loader puts all 8 tables in that schema.

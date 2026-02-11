# Schemas reference — 509 tables across 15 schemas

**Total: 509 tables across 15 schemas.** Export from your source Snowflake, then load into your own.

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

**Export (source Snowflake)**

1. In `.env` set `SNOWFLAKE_EXPORT_ALL_SCHEMAS=1` and your source Snowflake connection.
2. Run: `python export_snowflake_to_csv.py`  
   This writes `data/SCHEMA_NAME/TABLE_NAME.csv` for every schema.

**Load (your Snowflake)**

1. Point `.env` at your target account/database.
2. Run: `python load_data_to_snowflake.py`  
   The loader creates each schema in your database and loads all 509 tables.

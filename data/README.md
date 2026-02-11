# Data directory (509 tables)

This folder is populated when you **export** from Snowflake.

To get all **509 tables across 15 schemas**:

1. In `.env` set `SNOWFLAKE_EXPORT_ALL_SCHEMAS=1` and your Snowflake connection (the source account that has the tables).
2. Run: `python export_snowflake_to_csv.py`

That creates `data/SCHEMA_NAME/TABLE_NAME.csv` for each schema (e.g. `data/ANALYTICS/`, `data/CUSTOMER/`). Then run `python load_data_to_snowflake.py` to load them into your target Snowflake.

See [SCHEMAS_REFERENCE.md](../SCHEMAS_REFERENCE.md) and [README.md](../README.md).

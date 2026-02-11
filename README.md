# SunSpectra Database Lab

A Snowflake lab containing the SunSpectra database. Clone this repo and load the data into your own Snowflake account to run queries and build your own lab environment.

**Use your own Snowflake account; no credentials are stored in this repo.**

## Prerequisites

- Python 3.8+
- A Snowflake account (trial or paid)
- Snowflake credentials (account, user, password, warehouse, database, schema, role)

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd snowflake-sunspectra-lab
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your Snowflake credentials:
   ```bash
   cp env.example .env
   # Edit .env with your Snowflake account, user, password, warehouse, database, schema, and role.
   ```

## How to run

### Create schema and load data

Run the load script to create the schema (if needed) and load all CSV data from `data/` into your Snowflake:

```bash
python load_data_to_snowflake.py
```

This script reads connection settings from your `.env` file and loads each CSV in `data/` into the corresponding table in your database/schema.

### Verify the lab

After loading, you can run the sample queries in `sample_queries.sql` (e.g. in Snowflake Worksheets or via the connector) to verify the data.

## Project structure

```
snowflake-sunspectra-lab/
├── README.md
├── env.example          # Template for .env (copy to .env and fill in)
├── requirements.txt
├── data/                # CSV exports (one file per table)
├── schema/              # DDL scripts to create tables
├── export_snowflake_to_csv.py   # One-time export from a Snowflake instance
├── load_data_to_snowflake.py    # Load data/ CSVs into your Snowflake
└── sample_queries.sql   # Example queries to verify the lab
```

## Data source

The CSV files in `data/` were exported from a Snowflake schema. They are provided so you can load the same structure and sample data into your own Snowflake account for lab use.

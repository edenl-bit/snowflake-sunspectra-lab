-- Sample queries to verify the lab after loading data.
-- Run these in Snowflake (Worksheets or your client) after load_data_to_snowflake.py.
-- Replace YOUR_SCHEMA with your actual schema name if needed, or use the schema you set in .env.

-- Row counts per table
SELECT 'CUSTOMER' AS table_name, COUNT(*) AS row_count FROM CUSTOMER
UNION ALL SELECT 'LINEITEM', COUNT(*) FROM LINEITEM
UNION ALL SELECT 'NATION', COUNT(*) FROM NATION
UNION ALL SELECT 'ORDERS', COUNT(*) FROM ORDERS
UNION ALL SELECT 'PART', COUNT(*) FROM PART
UNION ALL SELECT 'PARTSUPP', COUNT(*) FROM PARTSUPP
UNION ALL SELECT 'REGION', COUNT(*) FROM REGION
UNION ALL SELECT 'SUPPLIER', COUNT(*) FROM SUPPLIER
ORDER BY table_name;

-- Regions and nation count
SELECT R_NAME, COUNT(*) AS nations
FROM REGION r
JOIN NATION n ON r.R_REGIONKEY = n.N_REGIONKEY
GROUP BY R_NAME
ORDER BY R_NAME;

-- Sample from CUSTOMER
SELECT C_CUSTKEY, C_NAME, C_ACCTBAL
FROM CUSTOMER
ORDER BY C_ACCTBAL DESC
LIMIT 10;

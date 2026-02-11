-- All SunSpectra active queries and the complex query.
-- Run these in Snowflake (Worksheets or your client) after load_data_to_snowflake.py.
-- Same queries are listed in README "Verify and query" section.

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

-- ---------------------------------------------------------------------------
-- Complex query: revenue by region (SunSpectra)
-- Joins ORDERS, LINEITEM, CUSTOMER, NATION, REGION for regional revenue.
-- ---------------------------------------------------------------------------
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

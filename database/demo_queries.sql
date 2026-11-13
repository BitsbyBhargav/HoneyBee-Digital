-- Optional: run these in MySQL Workbench using the project's MySQL connection.
-- These are read-only queries. The native project server uses port 3307.
USE honeybee;
SHOW TABLES;
DESCRIBE listing_master;
SELECT COUNT(*) AS total_listings FROM listing_master;
SELECT id, business_name, category, city, address, phone, source, created_at
FROM listing_master ORDER BY id LIMIT 5;
SELECT city, COUNT(*) AS business_count
FROM listing_master GROUP BY city ORDER BY business_count DESC;
SELECT category, COUNT(*) AS business_count
FROM listing_master GROUP BY category ORDER BY business_count DESC;
SELECT source, COUNT(*) AS business_count
FROM listing_master GROUP BY source ORDER BY business_count DESC;

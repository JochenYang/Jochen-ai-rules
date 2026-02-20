# MySQL Database Guide

Best practices for MySQL database design and operations.

## Schema Design

### Normalization
- 1NF: Atomic values, no repeating groups
- 2NF: No partial dependencies
- 3NF: No transitive dependencies
- Consider denormalization for read-heavy workloads

### Data Types
```sql
-- Use appropriate types
VARCHAR(255)      -- Strings up to 255 chars
TEXT              -- Longer text content
INT UNSIGNED      -- Positive integers
BIGINT            -- Large numbers (e.g., IDs)
DECIMAL(10,2)     -- Precise decimals (money)
DATETIME          -- Specific moments
TIMESTAMP         -- Time with timezone
JSON              -- Structured data
ENUM              -- Known values set
```

### Indexing Strategy
```sql
-- Primary key
CREATE TABLE users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
);

-- Index types
CREATE INDEX idx_user_email ON users(email);
CREATE UNIQUE INDEX idx_user_email_unique ON users(email);
CREATE FULLTEXT INDEX idx_user_bio ON users(bio);

-- Composite index
CREATE INDEX idx_order_user_date ON orders(user_id, created_at DESC);

-- Covering index
CREATE INDEX idx_product_category ON products(category_id, price) INCLUDE (name);
```

## Query Optimization

### Basic Principles
- Use EXPLAIN to analyze queries
- Avoid SELECT *
- Use LIMIT for large result sets
- Pagination with indexed columns

### Common Patterns
```sql
-- Bad
SELECT * FROM orders WHERE YEAR(created_at) = 2024;

-- Good (uses index)
SELECT * FROM orders WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- Bad (function on column)
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- Good (lowercase search)
SELECT * FROM users WHERE email = LOWER('TEST@EXAMPLE.COM');
```

### JOIN Optimization
```sql
-- Ensure join columns are indexed
-- Put filtering conditions early
-- Use appropriate join types
EXPLAIN
SELECT u.*, o.*
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
  AND o.created_at > '2024-01-01';
```

## Performance Tuning

### Configuration
```ini
# my.cnf
innodb_buffer_pool_size = 4G          # 70-80% of RAM
innodb_log_file_size = 1G
innodb_log_buffer_size = 64M
max_connections = 500
query_cache_type = 0                  # Disabled in 8.0
innodb_flush_log_at_trx_commit = 1    # Durability
slow_query_log = 1
long_query_time = 1
```

### Monitoring
```sql
-- Slow query log
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- Query statistics
SHOW STATUS LIKE 'Questions';
SHOW STATUS LIKE 'Slow_queries';

-- Table statistics
SHOW TABLE STATUS FROM database_name;
ANALYZE TABLE table_name;

-- Index statistics
SHOW INDEX FROM table_name;
```

## Backup and Recovery

### Backup Strategy
```bash
# Logical backup
mysqldump -u root -p database_name > backup.sql

# Selective backup
mysqldump -u root -p database_name table1 table2 > backup.sql

# Data only backup
mysqldump -u root -p --no-create-info database_name > data.sql

# Physical backup (Percona XtraBackup)
xtrabackup --backup --target-dir=/backup/
```

### Point-in-Time Recovery
```bash
# Full backup + binlogs
mysql -u root -p database_name < full_backup.sql
mysqlbinlog --stop-datetime="2024-01-15 10:30:00" binlog.000001 | mysql -u root -p
```

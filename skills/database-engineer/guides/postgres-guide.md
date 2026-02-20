# PostgreSQL Database Guide

Best practices for PostgreSQL database design and operations.

## Schema Design

### Data Types
```sql
-- Text
VARCHAR(n)       -- Variable length
TEXT             -- Unlimited length
CITEXT           -- Case-insensitive text

-- Numbers
SERIAL           -- Auto-increment integer
BIGSERIAL        -- Auto-increment bigint
NUMERIC(10,2)    -- Exact decimal
REAL             -- Single precision
DOUBLE PRECISION -- Double precision

-- Date/Time
DATE             -- Date only
TIME             -- Time only
TIMESTAMP        -- Date + time
TIMESTAMPTZ      -- Date + time + timezone
INTERVAL         -- Time duration

-- JSON
JSON             -- Valid JSON
JSONB            -- Binary JSON (indexable)

-- Arrays
INTEGER[]        -- Array of integers
TEXT[]           -- Array of text

-- Range types
DATERANGE        -- Date range
INT4RANGE        -- Integer range
TSRANGE          -- Timestamp range
```

### Advanced Features
```sql
-- Inheritance
CREATE TABLE countries (
  name TEXT,
  population BIGINT
);

CREATE TABLE capitals (
  country_name TEXT REFERENCES countries(name)
) INHERITS (countries);

-- Partitioning
CREATE TABLE orders (
  id BIGINT,
  created_at TIMESTAMPTZ,
  user_id BIGINT
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_q1 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Enums
CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');

-- Custom types
CREATE TYPE address AS (
  street TEXT,
  city TEXT,
  country TEXT,
  postal_code TEXT
);
```

## Indexing

### Index Types
```sql
-- B-tree (default, for equality/range)
CREATE INDEX idx_user_email ON users(email);

-- Hash (for equality only)
CREATE INDEX idx_user_email_hash ON users USING HASH (email);

-- GIN (for arrays, JSONB, full-text)
CREATE INDEX idx_user_tags ON users USING GIN (tags);
CREATE INDEX idx_product_data ON products USING GIN (data jsonb_path_ops);

-- GIST (for geometric, full-text)
CREATE INDEX idx_location ON locations USING GIST (coordinates);

-- BRIN (for large sequential data)
CREATE INDEX idx_orders_created ON orders USING BRIN (created_at);
```

### Partial Indexes
```sql
-- Index only active records
CREATE INDEX idx_active_users ON users (email) WHERE status = 'active';

-- Index for specific values
CREATE INDEX idx_archived_orders ON orders (user_id, created_at DESC)
  WHERE status = 'archived';
```

## Query Optimization

### Query Analysis
```sql
-- Explain analyze
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM users WHERE email LIKE '%@example.com';

-- Query statistics
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- Index usage
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;
```

### Common Patterns
```sql
-- Use EXISTS for subquery checks
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Use CTE for clarity (PostgreSQL 12+)
WITH recent_orders AS (
  SELECT user_id FROM orders WHERE created_at > NOW() - INTERVAL '30 days'
)
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN recent_orders o ON u.id = o.user_id
GROUP BY u.id;

-- Use array functions
SELECT * FROM users WHERE tags @> '{"premium": true}';
```

## Performance Tuning

### Configuration
```ini
# postgresql.conf
shared_buffers = 4GB                    # 25% of RAM
effective_cache_size = 12GB             # 75% of RAM
work_mem = 256MB                        # Per operation
maintenance_work_mem = 1GB              # Maintenance operations
max_parallel_workers_per_gather = 4
random_page_cost = 1.1                  # For SSD
effective_io_concurrency = 200          # For SSD
max_connections = 500
log_min_duration_statement = 1000       # Log slow queries
```

### Vacuum and Maintenance
```sql
-- Monitor table bloat
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_relation_size(relid)) as table_size,
  pg_size_pretty(pg_total_relation_size(relid)) as total_size,
  n_dead_tup,
  n_live_tup,
  round(n_dead_tup::numeric / nullif(n_live_tup, 0) * 100, 2) as dead_pct
FROM pg_stat_user_tables
ORDER BY dead_pct DESC;

-- Manual vacuum
VACUUM ANALYZE users;

-- Vacuum with verbose
VACUUM VERBOSE ANALYZE users;
```

## Backup and Recovery

### pg_dump
```bash
# Custom format (recommended)
pg_dump -Fc -f backup.dump database_name

# Directory format (parallel)
pg_dump -Fd -j 4 -f backup_dir database_name

# Plain SQL
pg_dump -f backup.sql database_name
```

### Point-in-Time Recovery
```bash
# Base backup + WAL
pg_basebackup -D /data/pg -Ft -z -P

# Recovery
cat recovery.conf
restore_command = 'cp /wal/%f %p'
recovery_target_time = '2024-01-15 10:30:00+00'
```

### Logical Replication
```sql
-- Publication
CREATE PUBLICATION mydb FOR ALL TABLES;

-- Subscription
CREATE SUBSCRIPTION mysub
  CONNECTION 'host=source dbname=mydb user=replicator'
  PUBLICATION mydb;
```

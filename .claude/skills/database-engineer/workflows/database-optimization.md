# Database Performance Optimization

Systematic approach to database performance tuning.

## Performance Analysis

### Metrics Collection
```sql
-- MySQL
SHOW GLOBAL STATUS LIKE 'Questions';
SHOW GLOBAL STATUS LIKE 'Slow_queries';
SHOW ENGINE INNODB STATUS;

-- PostgreSQL
SELECT * FROM pg_stat_database WHERE datname = 'mydb';
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 20;

-- MongoDB
db.serverStatus()
db.currentOp()
db.collection.aggregate([{ $indexStats: {} }])
```

### Query Analysis
```sql
-- MySQL EXPLAIN
EXPLAIN FORMAT=JSON
SELECT * FROM orders WHERE user_id = 123 AND status = 'shipped';

-- PostgreSQL EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = 123;

-- MongoDB explain
db.orders.find({ userId: ObjectId("123"), status: "shipped" })
  .explain("allPlansExecution")
```

## Index Optimization

### Index Design
```sql
-- Analyze missing indexes
-- MySQL
SELECT * FROM mysql.innodb_index_stats
  WHERE stat_name = 'size' AND stat_value = 0;

-- Identify unused indexes
-- PostgreSQL
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- MongoDB
db.collection.aggregate([
  { $indexStats: {} },
  { $match: { ops: 0 } }
])
```

### Index Maintenance
```sql
-- MySQL
OPTIMIZE TABLE users;

-- PostgreSQL
REINDEX INDEX idx_user_email;
VACUUM ANALYZE users;

-- MongoDB
db.collection.reIndex()
```

## Query Optimization

### Common Issues
```sql
-- Missing index
-- Solution: Add index on WHERE clause columns

-- Full table scan
-- Solution: Add index or rewrite query

-- Inefficient JOIN
-- Solution: Ensure join columns indexed, consider denormalization

-- Subquery to JOIN
-- Before
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);
-- After
SELECT DISTINCT u.* FROM users u INNER JOIN orders o ON u.id = o.user_id;

-- N+1 queries
-- Solution: Use eager loading or batch queries
```

### Query Rewrites
```sql
-- Avoid functions on indexed columns
-- Before
SELECT * FROM users WHERE LOWER(email) = LOWER('test@example.com');
-- After (case-insensitive collation)
SELECT * FROM users WHERE email ILIKE 'test@example.com';

-- Use EXISTS instead of IN for subqueries
-- Before
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE status = 'shipped');
-- After
SELECT * FROM users u WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.status = 'shipped'
);

-- Pagination optimization
-- Before (slow for high offset)
SELECT * FROM users ORDER BY created_at DESC LIMIT 100000, 20;
-- After (seek method)
SELECT * FROM users
WHERE created_at < '2024-01-15T00:00:00Z'
ORDER BY created_at DESC LIMIT 20;
```

## Schema Optimization

### Denormalization Strategies
```sql
-- Read-heavy: Denormalize for performance
-- Before (normalized)
SELECT u.*, SUM(o.amount) as total
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

-- After (denormalized)
SELECT * FROM users_with_totals;

-- Materialized view (PostgreSQL)
CREATE MATERIALIZED VIEW user_totals AS
SELECT user_id, SUM(amount) as total_amount
FROM orders GROUP BY user_id;

REFRESH MATERIALIZED VIEW user_totals;
```

### Partitioning
```sql
-- PostgreSQL range partitioning
CREATE TABLE orders (
  id BIGINT,
  created_at TIMESTAMPTZ,
  user_id BIGINT,
  amount DECIMAL(10,2)
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_q1 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

## Caching Strategies

### Application-Level Cache
```javascript
// Redis cache layer
async function getUserWithCache(userId) {
  const cacheKey = `user:${userId}`;

  // Try cache first
  let user = await redis.get(cacheKey);
  if (user) return JSON.parse(user);

  // Fetch from database
  user = await db.users.findById(userId);

  // Cache result
  if (user) {
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  }

  return user;
}
```

### Query Cache
```sql
-- MySQL query cache (deprecated in 8.0)
SET GLOBAL query_cache_type = 1;
SET SESSION query_cache_type = 1;

-- PostgreSQL pgbench
pgbench -c 10 -T 30 database_name
```

## Monitoring and Alerting

### Key Metrics
| Metric | Threshold | Action |
|--------|-----------|--------|
| Query latency (p99) | > 1s | Optimize or cache |
| Slow queries | > 5/min | Analyze and index |
| Connection usage | > 80% | Increase pool or optimize |
| Lock wait time | > 100ms | Check for deadlocks |
| Cache hit ratio | < 95% | Increase cache size |
| Index hit ratio | < 99% | Review indexes |

### Alert Rules
```yaml
# Prometheus alert rules
groups:
  - name: database
    rules:
      - alert: HighQueryLatency
        expr: pg_stat_statements_mean_time_seconds > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High query latency detected

      - alert: DatabaseConnectionHigh
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 2m
        labels:
          severity: warning
```

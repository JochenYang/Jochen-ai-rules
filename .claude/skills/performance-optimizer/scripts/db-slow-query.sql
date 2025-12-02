-- 数据库慢查询分析 SQL
-- 
-- 使用方式：
--   PostgreSQL: psql -f db-slow-query.sql
--   MySQL: mysql < db-slow-query.sql

-- ============================================
-- PostgreSQL 慢查询分析
-- ============================================

-- 1. 最慢的 20 个查询（按总时间）
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time,
    stddev_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 20;

-- 2. 最慢的 20 个查询（按平均时间）
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- 3. 最频繁的 20 个查询
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;

-- 4. 未使用索引的查询
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    seq_tup_read / NULLIF(seq_scan, 0) AS avg_seq_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;

-- 5. 缺失索引建议
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND n_distinct > 100
  AND correlation < 0.1
ORDER BY n_distinct DESC
LIMIT 20;

-- 6. 表膨胀分析
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 20;

-- ============================================
-- MySQL 慢查询分析
-- ============================================

-- 1. 最慢的 20 个查询（按总时间）
SELECT 
    DIGEST_TEXT as query,
    COUNT_STAR as exec_count,
    SUM_TIMER_WAIT / 1000000000000 AS total_time_sec,
    AVG_TIMER_WAIT / 1000000000000 AS avg_time_sec,
    MAX_TIMER_WAIT / 1000000000000 AS max_time_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 20;

-- 2. 最慢的 20 个查询（按平均时间）
SELECT 
    DIGEST_TEXT as query,
    COUNT_STAR as exec_count,
    AVG_TIMER_WAIT / 1000000000000 AS avg_time_sec,
    MAX_TIMER_WAIT / 1000000000000 AS max_time_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 20;

-- 3. 未使用索引的查询
SELECT 
    DIGEST_TEXT as query,
    COUNT_STAR as exec_count,
    SUM_NO_INDEX_USED as no_index_count,
    SUM_NO_GOOD_INDEX_USED as bad_index_count
FROM performance_schema.events_statements_summary_by_digest
WHERE SUM_NO_INDEX_USED > 0 OR SUM_NO_GOOD_INDEX_USED > 0
ORDER BY SUM_NO_INDEX_USED DESC
LIMIT 20;

-- 4. 全表扫描查询
SELECT 
    DIGEST_TEXT as query,
    COUNT_STAR as exec_count,
    SUM_ROWS_EXAMINED as rows_examined,
    SUM_ROWS_SENT as rows_sent,
    SUM_ROWS_EXAMINED / NULLIF(SUM_ROWS_SENT, 0) AS examine_ratio
FROM performance_schema.events_statements_summary_by_digest
WHERE SUM_ROWS_EXAMINED > 10000
ORDER BY SUM_ROWS_EXAMINED DESC
LIMIT 20;

-- 5. 表大小统计
SELECT 
    table_schema,
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS total_mb,
    table_rows
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
ORDER BY (data_length + index_length) DESC
LIMIT 20;

-- ============================================
-- 通用优化建议
-- ============================================

/*
优化建议：

1. 添加索引
   - 对 WHERE、JOIN、ORDER BY 字段添加索引
   - 示例：CREATE INDEX idx_user_email ON users(email);

2. 优化查询
   - 避免 SELECT *，只查询需要的字段
   - 使用 LIMIT 限制返回行数
   - 避免 N+1 查询，使用 JOIN

3. 分析慢查询
   - PostgreSQL：EXPLAIN ANALYZE <query>
   - MySQL：EXPLAIN <query>

4. 定期维护
   - PostgreSQL：VACUUM ANALYZE
   - MySQL：OPTIMIZE TABLE

5. 连接池优化
   - 合理设置连接池大小
   - 设置连接超时时间
*/

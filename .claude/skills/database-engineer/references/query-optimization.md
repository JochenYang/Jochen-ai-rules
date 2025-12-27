# 查询优化指南

## 索引优化

### 索引类型

**B-Tree 索引（默认）**
```sql
-- 适用于等值查询和范围查询
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

**哈希索引**
```sql
-- 仅适用于等值查询（PostgreSQL）
CREATE INDEX idx_users_id_hash ON users USING HASH(id);
```

**GIN 索引（全文搜索）**
```sql
-- PostgreSQL 全文搜索
CREATE INDEX idx_posts_content_gin ON posts USING GIN(to_tsvector('english', content));
```

**部分索引**
```sql
-- 只索引活跃用户
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;
```

### 复合索引

**最左前缀原则**

```sql
-- 创建复合索引
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- 可以使用索引的查询
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM orders WHERE user_id = 1 AND created_at > '2024-01-01';

-- 无法使用索引的查询
SELECT * FROM orders WHERE created_at > '2024-01-01';  -- 缺少 user_id
```

**索引列顺序**

1. 等值查询列在前，范围查询列在后
2. 选择性高的列在前

```sql
-- 正确：status 选择性低，user_id 选择性高
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 错误：status 选择性低放在前面
CREATE INDEX idx_orders_status_user ON orders(status, user_id);
```

### 覆盖索引

```sql
-- 查询只需要 id, email, name
CREATE INDEX idx_users_email_covering ON users(email) INCLUDE (name);

-- 这个查询可以完全从索引获取数据，无需回表
SELECT id, email, name FROM users WHERE email = 'user@example.com';
```

## 查询优化技巧

### 1. 避免 SELECT *

**错误示例**：
```sql
SELECT * FROM users WHERE id = 1;
```

**正确示例**：
```sql
SELECT id, name, email FROM users WHERE id = 1;
```

### 2. 使用 LIMIT

```sql
-- 分页查询
SELECT id, name FROM users 
ORDER BY created_at DESC 
LIMIT 20 OFFSET 0;
```

### 3. 避免 N+1 查询

**错误示例（N+1 问题）**：
```python
# 查询所有订单
orders = db.query("SELECT * FROM orders")

# 为每个订单查询用户（N 次查询）
for order in orders:
    user = db.query("SELECT * FROM users WHERE id = ?", order.user_id)
```

**正确示例（JOIN 或 IN）**：
```sql
-- 使用 JOIN
SELECT o.*, u.name, u.email
FROM orders o
JOIN users u ON o.user_id = u.id;

-- 使用 IN
SELECT * FROM users WHERE id IN (1, 2, 3, 4, 5);
```

### 4. 使用 EXISTS 代替 IN

```sql
-- 当子查询返回大量数据时，EXISTS 性能更好
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- 而不是
SELECT * FROM users u
WHERE u.id IN (SELECT user_id FROM orders);
```

### 5. 避免函数包裹索引列

**错误示例**：
```sql
-- 无法使用索引
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';
SELECT * FROM orders WHERE YEAR(created_at) = 2024;
```

**正确示例**：
```sql
-- 可以使用索引
SELECT * FROM users WHERE email = 'user@example.com';
SELECT * FROM orders WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- 或创建函数索引
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
```

## 执行计划分析

### PostgreSQL EXPLAIN

```sql
-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- 查看实际执行统计
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
```

**关键指标**：
- **Seq Scan**：全表扫描（慢）
- **Index Scan**：索引扫描（快）
- **Index Only Scan**：仅索引扫描（最快）
- **cost**：估算成本
- **rows**：估算行数
- **actual time**：实际执行时间

### MySQL EXPLAIN

```sql
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';
```

**type 字段**（从快到慢）：
- **system**：表只有一行
- **const**：主键或唯一索引查询
- **eq_ref**：唯一索引查询
- **ref**：非唯一索引查询
- **range**：范围查询
- **index**：索引全扫描
- **ALL**：全表扫描（最慢）

## JOIN 优化

### JOIN 类型选择

```sql
-- INNER JOIN：只返回匹配的行
SELECT o.*, u.name
FROM orders o
INNER JOIN users u ON o.user_id = u.id;

-- LEFT JOIN：返回左表所有行
SELECT u.*, o.id AS order_id
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- 避免不必要的 LEFT JOIN
-- 如果只需要有订单的用户，使用 INNER JOIN
```

### JOIN 顺序

```sql
-- 小表驱动大表
SELECT *
FROM small_table s
JOIN large_table l ON s.id = l.small_id;
```

### 避免笛卡尔积

```sql
-- 错误：缺少 JOIN 条件
SELECT * FROM users, orders;  -- 笛卡尔积

-- 正确：明确 JOIN 条件
SELECT * FROM users u
JOIN orders o ON u.id = o.user_id;
```

## 批量操作优化

### 批量插入

**错误示例**：
```sql
-- 逐条插入（慢）
INSERT INTO users (name, email) VALUES ('User1', 'user1@example.com');
INSERT INTO users (name, email) VALUES ('User2', 'user2@example.com');
```

**正确示例**：
```sql
-- 批量插入（快）
INSERT INTO users (name, email) VALUES
    ('User1', 'user1@example.com'),
    ('User2', 'user2@example.com'),
    ('User3', 'user3@example.com');
```

### 批量更新

```sql
-- 使用 CASE WHEN
UPDATE users
SET status = CASE
    WHEN id IN (1, 2, 3) THEN 'active'
    WHEN id IN (4, 5, 6) THEN 'inactive'
    ELSE status
END
WHERE id IN (1, 2, 3, 4, 5, 6);
```

## 事务优化

### 选择合适的隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|----------|------|------------|------|------|
| READ UNCOMMITTED | 可能 | 可能 | 可能 | 最高 |
| READ COMMITTED | 不可能 | 可能 | 可能 | 高 |
| REPEATABLE READ | 不可能 | 不可能 | 可能 | 中 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 | 最低 |

```sql
-- PostgreSQL 默认：READ COMMITTED
-- MySQL InnoDB 默认：REPEATABLE READ

-- 设置事务隔离级别
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### 避免长事务

```sql
-- 错误：长事务锁表
BEGIN;
SELECT * FROM users FOR UPDATE;  -- 锁定所有行
-- ... 长时间处理 ...
COMMIT;

-- 正确：缩短事务时间
BEGIN;
SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 只锁定需要的行
UPDATE users SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

## 慢查询诊断

### PostgreSQL

```sql
-- 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 100;  -- 记录超过 100ms 的查询

-- 查看慢查询统计
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### MySQL

```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.1;  -- 100ms

-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log%';
```

## 缓存策略

### 查询缓存（MySQL）

```sql
-- MySQL 8.0 已移除查询缓存
-- 建议使用应用层缓存（Redis）
```

### 应用层缓存

```python
# 使用 Redis 缓存查询结果
import redis

cache = redis.Redis()

def get_user(user_id):
    # 先查缓存
    cached = cache.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # 缓存未命中，查数据库
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    # 写入缓存（TTL 1 小时）
    cache.setex(f"user:{user_id}", 3600, json.dumps(user))
    
    return user
```


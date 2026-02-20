# Schema 设计最佳实践

## 范式化设计

### 第一范式（1NF）
确保每个字段都是原子性的，不可再分。

**错误示例**：
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    phones VARCHAR(255)  -- '123-456-7890, 098-765-4321'
);
```

**正确示例**：
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE user_phones (
    id INT PRIMARY KEY,
    user_id INT REFERENCES users(id),
    phone VARCHAR(20)
);
```

### 第二范式（2NF）
消除部分依赖，非主键字段完全依赖于主键。

### 第三范式（3NF）
消除传递依赖，非主键字段不依赖于其他非主键字段。

**错误示例**：
```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(100),  -- 依赖于 customer_id
    customer_email VARCHAR(100)  -- 依赖于 customer_id
);
```

**正确示例**：
```sql
CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(id)
);
```

## 反范式化策略

### 何时反范式化

1. **读多写少的场景**：查询性能优先于数据一致性
2. **避免复杂 JOIN**：减少多表关联查询
3. **提升查询性能**：牺牲存储空间换取查询速度

### 反范式化技术

**1. 冗余字段**

```sql
-- 订单表冗余客户名称，避免每次查询都 JOIN customers 表
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    customer_name VARCHAR(100),  -- 冗余字段
    total_amount DECIMAL(10, 2)
);
```

**2. 汇总表**

```sql
-- 预计算统计数据
CREATE TABLE user_statistics (
    user_id INT PRIMARY KEY,
    total_orders INT,
    total_spent DECIMAL(10, 2),
    last_order_date DATE,
    updated_at TIMESTAMP
);
```

**3. 物化视图**

```sql
-- PostgreSQL 物化视图
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    SUM(total_amount) AS total_sales,
    COUNT(*) AS order_count
FROM orders
GROUP BY DATE_TRUNC('month', order_date);

-- 定期刷新
REFRESH MATERIALIZED VIEW monthly_sales;
```

## 数据类型选择

### 整数类型

| 类型 | 存储空间 | 范围 | 使用场景 |
|------|----------|------|----------|
| TINYINT | 1 字节 | -128 ~ 127 | 状态码、布尔值 |
| SMALLINT | 2 字节 | -32,768 ~ 32,767 | 小范围计数 |
| INT | 4 字节 | -2B ~ 2B | 主键、外键 |
| BIGINT | 8 字节 | 非常大 | 大数据量主键 |

### 字符串类型

```sql
-- 固定长度（性能更好，但浪费空间）
CHAR(10)      -- 始终占用 10 字节

-- 可变长度（节省空间）
VARCHAR(100)  -- 最多 100 字符

-- 文本类型
TEXT          -- 无长度限制（PostgreSQL）
LONGTEXT      -- 大文本（MySQL）
```

### 时间类型

```sql
-- 日期
DATE          -- 2024-01-01

-- 时间戳（推荐）
TIMESTAMP     -- 2024-01-01 12:00:00

-- 带时区的时间戳（推荐用于国际化应用）
TIMESTAMPTZ   -- PostgreSQL
```

## 约束设计

### 主键约束

```sql
-- 自增主键
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- PostgreSQL
    -- id INT AUTO_INCREMENT PRIMARY KEY,  -- MySQL
    name VARCHAR(100)
);

-- UUID 主键（分布式系统推荐）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100)
);
```

### 外键约束

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE      -- 删除用户时删除订单
        ON UPDATE CASCADE      -- 更新用户 ID 时更新订单
);
```

### 唯一约束

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE,  -- 单列唯一
    username VARCHAR(50),
    UNIQUE(username)            -- 显式唯一约束
);

-- 复合唯一约束
CREATE TABLE user_roles (
    user_id INT,
    role_id INT,
    UNIQUE(user_id, role_id)
);
```

### 检查约束

```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    price DECIMAL(10, 2) CHECK (price > 0),
    stock INT CHECK (stock >= 0),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'deleted'))
);
```

## 索引设计

详见 `./query-optimization.md` 中的索引优化章节。

## 分区策略

### 范围分区

```sql
-- PostgreSQL 范围分区
CREATE TABLE orders (
    id INT,
    order_date DATE,
    amount DECIMAL(10, 2)
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 列表分区

```sql
CREATE TABLE users (
    id INT,
    country VARCHAR(2),
    name VARCHAR(100)
) PARTITION BY LIST (country);

CREATE TABLE users_us PARTITION OF users
    FOR VALUES IN ('US');

CREATE TABLE users_cn PARTITION OF users
    FOR VALUES IN ('CN');
```

## 命名规范

### 表名
- 使用复数形式：`users`, `orders`, `products`
- 小写字母，下划线分隔：`user_profiles`, `order_items`

### 列名
- 小写字母，下划线分隔：`first_name`, `created_at`
- 布尔字段使用 `is_` 或 `has_` 前缀：`is_active`, `has_verified`
- 时间戳字段使用 `_at` 后缀：`created_at`, `updated_at`

### 索引名
- 格式：`idx_<table>_<column>`
- 示例：`idx_users_email`, `idx_orders_user_id_created_at`

### 外键名
- 格式：`fk_<table>_<column>`
- 示例：`fk_orders_user_id`


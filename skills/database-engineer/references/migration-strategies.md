# 数据迁移策略

## 迁移类型

### 1. 同构迁移
相同数据库类型之间的迁移（如 MySQL 5.7 → MySQL 8.0）

### 2. 异构迁移
不同数据库类型之间的迁移（如 MySQL → PostgreSQL）

### 3. 版本升级
同一数据库的版本升级

### 4. 云迁移
本地数据库迁移到云端（如 AWS RDS, Azure Database）

## 迁移策略

### 停机迁移（Offline Migration）

**适用场景**：
- 数据量小（< 100GB）
- 可接受停机时间（几小时）
- 非关键业务系统

**步骤**：
1. 停止应用服务
2. 备份源数据库
3. 导出数据
4. 导入目标数据库
5. 验证数据完整性
6. 切换应用连接
7. 启动应用服务

**示例（MySQL → PostgreSQL）**：
```bash
# 1. 导出 MySQL 数据
mysqldump -u root -p mydb > mydb_backup.sql

# 2. 转换 SQL（使用工具如 pgloader）
pgloader mysql://user:pass@localhost/mydb postgresql://user:pass@localhost/mydb

# 3. 验证数据
psql -U user -d mydb -c "SELECT COUNT(*) FROM users;"
```

### 零停机迁移（Online Migration）

**适用场景**：
- 大数据量（> 100GB）
- 不能接受停机
- 关键业务系统

**步骤**：
1. 搭建目标数据库
2. 全量数据同步
3. 增量数据同步（CDC）
4. 数据验证
5. 灰度切换
6. 完全切换

**方案 1：双写策略**

```python
# 应用层双写
def create_user(user_data):
    # 写入旧数据库
    old_db.insert("users", user_data)
    
    # 同时写入新数据库
    try:
        new_db.insert("users", user_data)
    except Exception as e:
        log.error(f"New DB write failed: {e}")
        # 不影响主流程
```

**方案 2：CDC（Change Data Capture）**

使用工具捕获数据变更并同步：
- **Debezium**：基于 Kafka 的 CDC 工具
- **Maxwell**：MySQL binlog 解析工具
- **AWS DMS**：AWS 数据迁移服务

```yaml
# Debezium 配置示例
name: mysql-connector
config:
  connector.class: io.debezium.connector.mysql.MySqlConnector
  database.hostname: mysql-server
  database.port: 3306
  database.user: debezium
  database.password: dbz
  database.server.id: 184054
  database.server.name: mydb
  table.include.list: mydb.users,mydb.orders
```

## 迁移工具

### MySQL → PostgreSQL

**pgloader**
```bash
# 安装
apt-get install pgloader

# 迁移
pgloader mysql://root:pass@localhost/mydb postgresql://user:pass@localhost/mydb

# 自定义配置
pgloader migration.load
```

**migration.load 配置**：
```
LOAD DATABASE
    FROM mysql://root:pass@localhost/mydb
    INTO postgresql://user:pass@localhost/mydb

WITH include drop, create tables, create indexes, reset sequences

SET maintenance_work_mem to '128MB', work_mem to '12MB'

CAST type datetime to timestamptz
     drop default drop not null using zero-dates-to-null;
```

### MongoDB → PostgreSQL

**使用 ETL 工具**：
```python
from pymongo import MongoClient
import psycopg2

# 连接 MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['mydb']

# 连接 PostgreSQL
pg_conn = psycopg2.connect("dbname=mydb user=postgres")
pg_cursor = pg_conn.cursor()

# 迁移数据
for doc in mongo_db.users.find():
    pg_cursor.execute(
        "INSERT INTO users (id, name, email) VALUES (%s, %s, %s)",
        (doc['_id'], doc['name'], doc['email'])
    )

pg_conn.commit()
```

### 云迁移工具

**AWS DMS（Database Migration Service）**
- 支持同构和异构迁移
- 支持持续复制（CDC）
- 自动 Schema 转换

**Azure Database Migration Service**
- 支持 SQL Server, MySQL, PostgreSQL
- 在线和离线迁移
- 评估工具

## 数据验证

### 行数验证

```sql
-- 源数据库
SELECT COUNT(*) FROM users;

-- 目标数据库
SELECT COUNT(*) FROM users;
```

### 数据一致性验证

```sql
-- 校验和对比
-- MySQL
SELECT MD5(GROUP_CONCAT(id, name, email ORDER BY id)) AS checksum
FROM users;

-- PostgreSQL
SELECT MD5(STRING_AGG(id || name || email, '' ORDER BY id)) AS checksum
FROM users;
```

### 抽样验证

```python
import random

def validate_sample(source_db, target_db, table, sample_size=1000):
    # 随机抽取 ID
    ids = source_db.query(f"SELECT id FROM {table} ORDER BY RANDOM() LIMIT {sample_size}")
    
    for id in ids:
        source_row = source_db.query(f"SELECT * FROM {table} WHERE id = ?", id)
        target_row = target_db.query(f"SELECT * FROM {table} WHERE id = ?", id)
        
        if source_row != target_row:
            print(f"Mismatch found for ID {id}")
            return False
    
    return True
```

## Schema 转换

### 数据类型映射

| MySQL | PostgreSQL |
|-------|------------|
| INT | INTEGER |
| BIGINT | BIGINT |
| VARCHAR(n) | VARCHAR(n) |
| TEXT | TEXT |
| DATETIME | TIMESTAMP |
| ENUM | VARCHAR + CHECK |
| JSON | JSONB |

### 自增主键转换

```sql
-- MySQL
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- PostgreSQL
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- 或使用 IDENTITY（PostgreSQL 10+）
CREATE TABLE users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100)
);
```

### ENUM 类型转换

```sql
-- MySQL
CREATE TABLE users (
    id INT PRIMARY KEY,
    status ENUM('active', 'inactive', 'deleted')
);

-- PostgreSQL 方案 1：使用 ENUM 类型
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'deleted');
CREATE TABLE users (
    id INT PRIMARY KEY,
    status user_status
);

-- PostgreSQL 方案 2：使用 CHECK 约束
CREATE TABLE users (
    id INT PRIMARY KEY,
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'deleted'))
);
```

## 回滚方案

### 快速回滚

```bash
# 1. 保留旧数据库（只读模式）
# 2. 应用配置支持快速切换数据库连接
# 3. 发现问题立即切回旧数据库

# 配置示例
DATABASE_URL=postgresql://...  # 新数据库
FALLBACK_DATABASE_URL=mysql://...  # 旧数据库（备用）
```

### 数据回滚

```bash
# 从备份恢复
pg_restore -U postgres -d mydb mydb_backup.dump

# 或使用时间点恢复（PITR）
# PostgreSQL
pg_basebackup + WAL archiving

# MySQL
mysqlbinlog + binlog position
```

## 性能优化

### 并行导入

```bash
# PostgreSQL 并行导入
pg_restore -j 4 -U postgres -d mydb mydb_backup.dump

# MySQL 并行导入（使用 mydumper/myloader）
myloader -d /backup -t 4 -o -B mydb
```

### 临时禁用约束

```sql
-- PostgreSQL
ALTER TABLE users DISABLE TRIGGER ALL;
-- 导入数据
ALTER TABLE users ENABLE TRIGGER ALL;

-- MySQL
SET FOREIGN_KEY_CHECKS=0;
-- 导入数据
SET FOREIGN_KEY_CHECKS=1;
```

### 批量提交

```python
# 批量插入（每 1000 行提交一次）
batch_size = 1000
for i, row in enumerate(data):
    cursor.execute("INSERT INTO users VALUES (%s, %s)", row)
    
    if (i + 1) % batch_size == 0:
        conn.commit()

conn.commit()  # 提交剩余数据
```

## 迁移检查清单

### 迁移前
- [ ] 评估数据量和迁移时间
- [ ] 备份源数据库
- [ ] 测试环境验证迁移流程
- [ ] 准备回滚方案
- [ ] 通知相关团队

### 迁移中
- [ ] 监控迁移进度
- [ ] 验证数据一致性
- [ ] 检查应用日志
- [ ] 性能监控

### 迁移后
- [ ] 全量数据验证
- [ ] 性能测试
- [ ] 监控数据库指标
- [ ] 保留旧数据库一段时间
- [ ] 更新文档


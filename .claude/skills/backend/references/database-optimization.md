# 数据库优化指南

## 查询优化

### 1. 避免 N+1 查询问题

**问题示例**（Prisma）：

```typescript
// ❌ N+1 查询问题
const users = await prisma.user.findMany();
for (const user of users) {
  // 每个用户都会触发一次查询
  user.posts = await prisma.post.findMany({
    where: { authorId: user.id }
  });
}
// 总查询次数：1 + N（N 为用户数量）
```

**解决方案**：

```typescript
// ✅ 使用 include 预加载关联数据
const users = await prisma.user.findMany({
  include: {
    posts: true
  }
});
// 总查询次数：1（使用 JOIN）

// ✅ 或使用 select 只获取需要的字段
const users = await prisma.user.findMany({
  select: {
    id: true,
    name: true,
    posts: {
      select: {
        id: true,
        title: true
      }
    }
  }
});
```

### 2. 索引优化

**创建索引的场景**：

```sql
-- ✅ WHERE 子句中频繁使用的列
CREATE INDEX idx_users_email ON users(email);

-- ✅ JOIN 操作中使用的外键
CREATE INDEX idx_posts_author_id ON posts(author_id);

-- ✅ ORDER BY 子句中使用的列
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- ✅ 复合索引（多列查询）
CREATE INDEX idx_posts_status_created ON posts(status, created_at DESC);

-- ❌ 不要为低基数列创建索引（如性别、布尔值）
-- ❌ 不要为小表创建过多索引
```

**Prisma Schema 中定义索引**：

```prisma
model Post {
  id        String   @id @default(cuid())
  title     String
  status    String
  authorId  String
  createdAt DateTime @default(now())
  
  author    User     @relation(fields: [authorId], references: [id])
  
  @@index([authorId])
  @@index([status, createdAt(sort: Desc)])
  @@index([createdAt(sort: Desc)])
}
```

### 3. 查询分析

**使用 EXPLAIN 分析查询**：

```sql
-- PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM posts
WHERE status = 'published'
ORDER BY created_at DESC
LIMIT 20;

-- 关注指标：
-- - Seq Scan（全表扫描）→ 需要添加索引
-- - Index Scan（索引扫描）→ 良好
-- - Execution Time（执行时间）→ 应 < 100ms
```

**Prisma 查询日志**：

```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
  log      = ["query", "info", "warn", "error"]
}

// 在代码中启用日志
const prisma = new PrismaClient({
  log: [
    { emit: 'event', level: 'query' },
  ],
});

prisma.$on('query', (e) => {
  console.log('Query: ' + e.query);
  console.log('Duration: ' + e.duration + 'ms');
});
```

## 连接池配置

### PostgreSQL 连接池（Prisma）

```env
# .env
DATABASE_URL="postgresql://user:password@localhost:5432/mydb?connection_limit=10&pool_timeout=20"
```

**推荐配置**：

```typescript
// 小型应用（< 1000 并发用户）
connection_limit=10
pool_timeout=20

// 中型应用（1000-10000 并发用户）
connection_limit=20
pool_timeout=30

// 大型应用（> 10000 并发用户）
connection_limit=50
pool_timeout=60

// 计算公式
// connection_limit = (CPU 核心数 * 2) + 磁盘数量
```

### Node.js 连接池（pg）

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'user',
  password: 'password',
  max: 20,              // 最大连接数
  idleTimeoutMillis: 30000,  // 空闲连接超时
  connectionTimeoutMillis: 2000,  // 连接超时
});

// 使用连接
const client = await pool.connect();
try {
  const result = await client.query('SELECT * FROM users');
  return result.rows;
} finally {
  client.release();  // 释放连接回池
}
```

## 缓存策略

### 1. Redis 缓存

```typescript
import Redis from 'ioredis';

const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  db: 0,
});

// 缓存模式：Cache-Aside
async function getUser(id: string) {
  const cacheKey = `user:${id}`;
  
  // 1. 先查缓存
  const cached = await redis.get(cacheKey);
  if (cached) {
    console.log('Cache hit');
    return JSON.parse(cached);
  }
  
  // 2. 缓存未命中，查数据库
  console.log('Cache miss');
  const user = await prisma.user.findUnique({
    where: { id }
  });
  
  if (user) {
    // 3. 写入缓存（TTL 1小时）
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  }
  
  return user;
}

// 更新时使缓存失效
async function updateUser(id: string, data: any) {
  const user = await prisma.user.update({
    where: { id },
    data
  });
  
  // 删除缓存
  await redis.del(`user:${id}`);
  
  return user;
}
```

### 2. 缓存 TTL 策略

```typescript
// 不同数据的 TTL 建议
const CACHE_TTL = {
  USER_PROFILE: 3600,      // 1小时（用户资料）
  PRODUCT_LIST: 300,       // 5分钟（商品列表）
  HOT_DATA: 60,            // 1分钟（热点数据）
  STATIC_CONFIG: 86400,    // 24小时（静态配置）
};
```

## 事务处理

### Prisma 事务

```typescript
// 交互式事务
const result = await prisma.$transaction(async (tx) => {
  // 1. 扣减库存
  const product = await tx.product.update({
    where: { id: productId },
    data: { stock: { decrement: quantity } }
  });
  
  if (product.stock < 0) {
    throw new Error('库存不足');
  }
  
  // 2. 创建订单
  const order = await tx.order.create({
    data: {
      userId,
      productId,
      quantity,
      totalPrice: product.price * quantity
    }
  });
  
  return order;
});

// 批量事务
await prisma.$transaction([
  prisma.user.create({ data: { name: 'Alice' } }),
  prisma.user.create({ data: { name: 'Bob' } }),
  prisma.user.create({ data: { name: 'Charlie' } }),
]);
```

## 性能监控

### 慢查询日志

**PostgreSQL 配置**：

```sql
-- 记录执行时间 > 100ms 的查询
ALTER DATABASE mydb SET log_min_duration_statement = 100;

-- 查看慢查询日志
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 应用层监控

```typescript
// 查询性能监控中间件
async function monitorQuery<T>(
  queryName: string,
  queryFn: () => Promise<T>
): Promise<T> {
  const start = Date.now();
  
  try {
    const result = await queryFn();
    const duration = Date.now() - start;
    
    if (duration > 100) {
      console.warn(`Slow query: ${queryName} took ${duration}ms`);
    }
    
    return result;
  } catch (error) {
    console.error(`Query failed: ${queryName}`, error);
    throw error;
  }
}

// 使用
const users = await monitorQuery(
  'getActiveUsers',
  () => prisma.user.findMany({ where: { active: true } })
);
```

## 最佳实践

1. **使用连接池**：避免频繁创建/销毁连接
2. **添加适当索引**：WHERE、JOIN、ORDER BY 列
3. **避免 SELECT ***：只查询需要的字段
4. **使用分页**：大数据集必须分页
5. **缓存热点数据**：使用 Redis 缓存
6. **监控慢查询**：定期分析和优化
7. **使用事务**：保证数据一致性
8. **定期清理**：删除过期数据


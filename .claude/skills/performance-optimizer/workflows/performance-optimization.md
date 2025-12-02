# 性能优化工作流程

## 概述
本工作流程定义了系统性能优化的完整流程，从问题识别到优化验证。

---

## 阶段 1：性能问题识别

### 1.1 定义性能目标
**关键指标**：
- **响应时间**：API P95 < 500ms，P99 < 1s
- **吞吐量**：> 1000 RPS（根据业务需求）
- **资源使用**：CPU < 70%，内存 < 80%
- **用户体验**：LCP < 2.5s，FID < 100ms

### 1.2 收集性能数据
**工具选择**：
- **前端**：Chrome DevTools Performance、Lighthouse
- **后端**：语言内置 profiler（pprof/cProfile/VisualVM）
- **数据库**：EXPLAIN ANALYZE、慢查询日志
- **全链路**：Jaeger/Zipkin（分布式追踪）

**数据收集检查清单**：
- [ ] 在真实负载下收集数据（不是空载）
- [ ] 收集至少 5 分钟的样本数据
- [ ] 记录 P50、P95、P99 响应时间
- [ ] 记录 CPU/内存使用峰值
- [ ] 记录慢查询和热点代码

### 1.3 定位性能瓶颈
**执行步骤**：
```bash
# 1. 前端性能分析
npm run lighthouse

# 2. 后端 profiling（以 Node.js 为例）
node --prof app.js
node --prof-process isolate-0x*.log > profile.txt

# 3. 数据库慢查询
# PostgreSQL
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

# MySQL
SHOW FULL PROCESSLIST;
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;
```

**常见瓶颈模式**：
- ❌ **N+1 查询**：循环中执行数据库查询
- ❌ **未使用索引**：全表扫描
- ❌ **同步 I/O**：阻塞主线程
- ❌ **过度计算**：不必要的重复计算
- ❌ **内存泄漏**：内存持续增长

---

## 阶段 2：优化策略决策

### 2.1 影响分析矩阵
评估每个优化方案的影响和难度：

| 优化方案 | 预期提升 | 实现难度 | 优先级 |
|---------|---------|---------|--------|
| 添加数据库索引 | 50% ↓ 响应时间 | 低 | **P0** |
| 引入 Redis 缓存 | 70% ↓ 数据库负载 | 中 | **P1** |
| 代码异步化 | 30% ↑ 吞吐量 | 中 | **P1** |
| 前端代码分割 | 40% ↓ 加载时间 | 低 | **P1** |
| 数据库分库分表 | 80% ↑ 容量 | 高 | P2 |

**决策原则**：
- ✅ 优先 P0（高影响 + 低难度）
- ✅ 关注 80/20 法则（80% 问题来自 20% 代码）
- ✅ 避免过早优化（先保证正确性）

### 2.2 制定优化计划
**优化方案示例**：

#### 方案 1：数据库优化（P0）
```sql
-- 问题：用户查询慢（3 秒）
-- 原因：email 字段未建立索引

-- 优化：添加索引
CREATE INDEX idx_users_email ON users(email);

-- 预期效果：查询时间 < 50ms
```

#### 方案 2：缓存层引入（P1）
```javascript
// 问题：热点数据重复查询数据库
// 优化：Redis 缓存 + 合理 TTL

const getUser = async (id) => {
  // 1. 尝试从缓存获取
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);
  
  // 2. 缓存未命中，查询数据库
  const user = await db.query('SELECT * FROM users WHERE id = ?', [id]);
  
  // 3. 写入缓存（TTL 5 分钟）
  await redis.setex(`user:${id}`, 300, JSON.stringify(user));
  
  return user;
};
```

#### 方案 3：异步化优化（P1）
```javascript
// 问题：同步等待多个外部 API
// 优化：Promise.all 并行调用

// ❌ 串行调用（总耗时 3 秒）
const user = await fetchUser(id);      // 1s
const posts = await fetchPosts(id);    // 1s
const comments = await fetchComments(id); // 1s

// ✅ 并行调用（总耗时 1 秒）
const [user, posts, comments] = await Promise.all([
  fetchUser(id),
  fetchPosts(id),
  fetchComments(id)
]);
```

---

## 阶段 3：优化实施

### 3.1 数据库优化

#### 索引优化
```sql
-- 1. 识别缺失索引（PostgreSQL）
SELECT schemaname, tablename, attname
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
AND null_frac > 0.1  -- 超过 10% 的 NULL 值
AND n_distinct > 100; -- 高基数列

-- 2. 创建索引
CREATE INDEX CONCURRENTLY idx_orders_user_id_created_at 
ON orders(user_id, created_at DESC);

-- 3. 验证索引使用
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;
```

#### 查询优化
```sql
-- ❌ N+1 查询问题
SELECT * FROM users;
-- 循环中：SELECT * FROM posts WHERE user_id = ?

-- ✅ 使用 JOIN 一次查询
SELECT u.*, p.* 
FROM users u 
LEFT JOIN posts p ON p.user_id = u.id;
```

#### 连接池优化
```javascript
// 连接池大小公式：((CPU核数 * 2) + 磁盘数)
const pool = new Pool({
  max: 20,              // 最大连接数
  min: 5,               // 最小连接数
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});
```

### 3.2 缓存策略

#### 多级缓存架构
```
浏览器缓存 (HTTP Cache-Control)
   ↓
CDN 缓存 (CloudFront/Cloudflare)
   ↓
应用缓存 (Redis/Memcached)
   ↓
数据库查询缓存
```

#### 缓存实现示例
```javascript
// LRU 缓存 + TTL
const NodeCache = require('node-cache');
const cache = new NodeCache({ 
  stdTTL: 600,      // 默认 10 分钟
  checkperiod: 120   // 每 2 分钟清理过期
});

// Cache-Aside 模式
async function getData(key) {
  // 1. 检查缓存
  const cached = cache.get(key);
  if (cached) return cached;
  
  // 2. 查询数据库
  const data = await db.query(key);
  
  // 3. 写入缓存
  cache.set(key, data);
  
  return data;
}

// 缓存失效
function invalidateCache(key) {
  cache.del(key);
}
```

### 3.3 代码级优化

#### 算法优化
```javascript
// ❌ O(n²) 时间复杂度
function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) duplicates.push(arr[i]);
    }
  }
  return duplicates;
}

// ✅ O(n) 时间复杂度
function findDuplicates(arr) {
  const seen = new Set();
  const duplicates = new Set();
  
  for (const item of arr) {
    if (seen.has(item)) {
      duplicates.add(item);
    }
    seen.add(item);
  }
  
  return Array.from(duplicates);
}
```

#### 避免重复计算
```javascript
// ❌ 每次都重新计算
function calculateDiscount(items) {
  items.forEach(item => {
    const tax = item.price * 0.1;  // 重复计算
    const total = item.price + tax;
  });
}

// ✅ 缓存计算结果
const memoize = (fn) => {
  const cache = {};
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache[key]) return cache[key];
    cache[key] = fn(...args);
    return cache[key];
  };
};

const expensiveCalculation = memoize((x) => {
  // 复杂计算
  return x ** 2;
});
```

### 3.4 前端优化

#### 代码分割
```javascript
// React 代码分割
import React, { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Dashboard />
    </Suspense>
  );
}
```

#### 图片优化
```html
<!-- 响应式图片 + 懒加载 -->
<picture>
  <source 
    srcset="image-320w.webp 320w, image-640w.webp 640w"
    type="image/webp"
  >
  <img 
    src="image-640w.jpg" 
    loading="lazy"
    alt="Description"
  >
</picture>
```

#### 关键 CSS 内联
```html
<head>
  <!-- 内联关键 CSS（首屏渲染需要） -->
  <style>
    .header { /* 关键样式 */ }
  </style>
  
  <!-- 延迟加载非关键 CSS -->
  <link rel="preload" href="styles.css" as="style" onload="this.rel='stylesheet'">
</head>
```

---

## 阶段 4：性能验证

### 4.1 基准测试
```bash
# 压力测试（Apache Bench）
ab -n 10000 -c 100 https://api.example.com/users

# 或使用 wrk
wrk -t12 -c400 -d30s https://api.example.com/users

# K6 负载测试
k6 run --vus 100 --duration 30s script.js
```

### 4.2 对比优化前后
| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **P95 响应时间** | 3.2s | 450ms | **85.9% ↓** |
| **吞吐量 (RPS)** | 300 | 1200 | **300% ↑** |
| **CPU 使用率** | 85% | 45% | **47% ↓** |
| **内存使用** | 2.5GB | 1.8GB | **28% ↓** |
| **数据库连接数** | 150 | 40 | **73% ↓** |

### 4.3 监控配置
```yaml
# Prometheus 告警规则
groups:
- name: performance
  rules:
  - alert: HighLatency
    expr: http_request_duration_seconds{quantile="0.95"} > 0.5
    for: 5m
    annotations:
      summary: "P95 响应时间超过 500ms"
  
  - alert: LowThroughput
    expr: rate(http_requests_total[5m]) < 100
    for: 5m
    annotations:
      summary: "吞吐量低于 100 RPS"
```

---

## 阶段 5：持续监控

### 5.1 性能预算
设置性能边界，防止性能回退：

```json
{
  "budgets": [
    {
      "resource": "bundle.js",
      "maxSize": "500kb"
    },
    {
      "metric": "interactive",
      "maxTime": "3s"
    },
    {
      "metric": "first-contentful-paint",
      "maxTime": "1.5s"
    }
  ]
}
```

### 5.2 CI/CD 集成
```yaml
# GitHub Actions - 性能回归检测
- name: Performance test
  run: |
    npm run lighthouse -- --budget-path=budget.json
    if [ $? -ne 0 ]; then
      echo "Performance budget exceeded!"
      exit 1
    fi
```

---

## 优化检查清单

### ✅ 识别阶段
- [ ] 使用 profiler 定位瓶颈
- [ ] 收集真实负载数据
- [ ] 分析热点代码和慢查询
- [ ] 定义优化目标和指标

### ✅ 优化阶段
- [ ] 数据库查询优化（索引、避免N+1）
- [ ] 缓存策略实施（多级缓存）
- [ ] 算法和数据结构优化
- [ ] 并发和异步处理

### ✅ 验证阶段
- [ ] 性能测试验证优化效果
- [ ] 对比优化前后指标
- [ ] 无性能回归
- [ ] 监控和告警配置

---

## 常见问题

### Q1: 如何识别内存泄漏？
**A:** 使用堆快照对比：
```bash
# Node.js
node --inspect app.js
# 访问 chrome://inspect
# 拍摄多个堆快照，对比对象增长

# 或使用 clinic.js
clinic doctor -- node app.js
```

### Q2: 缓存击穿怎么办？
**A:** 使用互斥锁（Mutex）：
```javascript
const locks = new Map();

async function getDataWithLock(key) {
  // 已有请求在获取，等待
  if (locks.has(key)) {
    return locks.get(key);
  }
  
  // 创建新的请求 Promise
  const promise = fetchData(key);
  locks.set(key, promise);
  
  try {
    const data = await promise;
    return data;
  } finally {
    locks.delete(key);
  }
}
```

### Q3: 如何优化大列表渲染？
**A:** 虚拟滚动（Virtual Scrolling）：
```javascript
// React 使用 react-window
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={10000}
  itemSize={50}
  width="100%"
>
  {Row}
</FixedSizeList>
```

---

## 参考资源

- [Web.dev Performance Guide](https://web.dev/performance/)
- [Node.js Performance Best Practices](https://nodejs.org/en/docs/guides/simple-profiling/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

# Optimization Patterns Reference

Common performance optimization patterns and techniques.

## 1. Database Query Optimization

### Pattern: N+1 Query Prevention
```javascript
// Bad: N+1 queries
const users = await db.users.findMany();
for (const user of users) {
  user.orders = await db.orders.findMany({ userId: user.id });
}

// Good: Eager loading
const users = await db.users.findMany({
  include: { orders: true }
});

// Good: Batch loading
const userIds = users.map(u => u.id);
const ordersByUserId = await db.orders.findMany({
  where: { userId: { in: userIds } }
}).then(orders => groupBy(orders, 'userId'));

for (const user of users) {
  user.orders = ordersByUserId[user.id] || [];
}
```

### Pattern: Pagination with Seek Method
```sql
-- Bad: Offset pagination (slow for large offsets)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 100000, 20;

-- Good: Seek method (O(1) for any page)
SELECT * FROM posts
WHERE created_at < '2024-01-15T00:00:00Z'
ORDER BY created_at DESC LIMIT 20;
```

### Pattern: Covering Index
```sql
-- Index includes all queried columns
CREATE INDEX idx_orders_covering ON orders (user_id, status, created_at DESC)
  INCLUDE (total_amount, item_count);
```

## 2. Caching Patterns

### Pattern: Request Coalescing
```javascript
const pendingRequests = new Map();

async function getData(key) {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key);
  }

  const promise = fetchData(key);
  pendingRequests.set(key, promise);

  try {
    return await promise;
  } finally {
    pendingRequests.delete(key);
  }
}
```

### Pattern: Cache Warming
```javascript
// Pre-populate cache during low traffic
async function warmCache() {
  const popularItems = await getPopularItems();

  for (const item of popularItems) {
    await redis.setex(`item:${item.id}`, 3600, JSON.stringify(item));
  }
}

// Schedule during off-peak
cron.schedule('0 3 * * *', warmCache);
```

## 3. Application Patterns

### Pattern: Debouncing
```javascript
function debounce(fn, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

// Usage
const handleSearch = debounce(async (query) => {
  const results = await searchAPI(query);
  display(results);
}, 300);
```

### Pattern: Throttling
```javascript
function throttle(fn, limit) {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Usage
const handleScroll = throttle(() => {
  updateLazyLoadItems();
}, 200);
```

### Pattern: Virtual Scrolling
```javascript
function VirtualList({ items, itemHeight, containerHeight }) {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const visibleItems = items.slice(
    startIndex,
    startIndex + visibleCount + 5
  );

  return (
    <div style={{ height: containerHeight, overflow: 'auto' }}>
      <div style={{ height: items.length * itemHeight }}>
        {visibleItems.map((item, index) => (
          <div style={{
            position: 'absolute',
            top: (startIndex + index) * itemHeight,
            height: itemHeight
          }}>
            {item.content}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 4. Concurrency Patterns

### Pattern: Parallel Processing
```javascript
async function processItems(items) {
  const BATCH_SIZE = 10;
  const results = [];

  for (let i = 0; i < items.length; i += BATCH_SIZE) {
    const batch = items.slice(i, i + BATCH_SIZE);
    const batchResults = await Promise.all(
      batch.map(item => processItem(item))
    );
    results.push(...batchResults);
  }

  return results;
}
```

### Pattern: Rate Limiting
```javascript
class RateLimiter {
  constructor(maxRequests, windowMs) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.requests = [];
  }

  async acquire() {
    const now = Date.now();
    this.requests = this.requests.filter(
      t => t > now - this.windowMs
    );

    if (this.requests.length >= this.maxRequests) {
      const waitTime = this.requests[0] + this.windowMs - now;
      await sleep(waitTime);
    }

    this.requests.push(now);
  }
}
```

## 5. Memory Optimization

### Pattern: Object Pooling
```javascript
class ObjectPool {
  constructor(factory, initialSize = 10) {
    this.factory = factory;
    this.pool = [];
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(factory());
    }
  }

  acquire() {
    return this.pool.pop() || this.factory();
  }

  release(obj) {
    this.pool.push(obj);
  }
}

// Usage
const bufferPool = new ObjectPool(() => Buffer.alloc(1024));
```

### Pattern: Streaming Large Data
```javascript
async function processLargeFile(file) {
  const stream = createReadStream(file);
  const parser = new JSONParser();

  for await (const chunk of stream) {
    await processChunk(chunk);
  }
}

// Avoid loading entire file in memory
```

## 6. Network Optimization

### Pattern: Request Batching
```javascript
class RequestBatcher {
  constructor(maxBatchSize, maxWaitMs) {
    this.maxBatchSize = maxBatchSize;
    this.maxWaitMs = maxWaitMs;
    this.pending = [];
  }

  async add(request) {
    return new Promise((resolve) => {
      this.pending.push({ request, resolve });
      if (this.pending.length >= this.maxBatchSize) {
        this.flush();
      } else if (this.pending.length === 1) {
        setTimeout(() => this.flush(), this.maxWaitMs);
      }
    });
  }

  async flush() {
    const batch = this.pending.splice(0);
    const results = await api.batch(batch.map(b => b.request));
    batch.forEach((item, i) => item.resolve(results[i]));
  }
}
```

## 7. Frontend Optimization

### Pattern: Code Splitting
```javascript
// Route-based splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

// Component-based splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));
```

### Pattern: Image Optimization
```javascript
// Responsive images
<img
  srcSet="/image-400.jpg 400w, /image-800.jpg 800w"
  sizes="(max-width: 600px) 400px, 800px"
  src="/image-800.jpg"
  loading="lazy"
/>

// WebP/AVIF
<picture>
  <source srcSet="/image.avif" type="image/avif">
  <source srcSet="/image.webp" type="image/webp">
  <img src="/image.jpg" alt="Description">
</picture>
```

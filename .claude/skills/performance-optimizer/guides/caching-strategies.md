# Caching Strategies Guide

Comprehensive guide to implementing effective caching.

## Caching Layers

```
┌─────────────────────────────────────────────────────┐
│                    Client Cache                      │
│  (Browser, CDN, Service Worker)                     │
├─────────────────────────────────────────────────────┤
│                    API Gateway Cache                 │
│  (CDN, API Gateway)                                 │
├─────────────────────────────────────────────────────┤
│                  Application Cache                   │
│  (In-memory, Redis, Memcached)                      │
├─────────────────────────────────────────────────────┤
│                   Database Cache                     │
│  (Query cache, Buffer pool)                         │
└─────────────────────────────────────────────────────┘
```

## Caching Strategies

### 1. Cache-Aside (Lazy Loading)
```javascript
async function getUser(userId) {
  const cacheKey = `user:${userId}`;

  // Check cache first
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // Fetch from database
  const user = await database.users.findById(userId);

  // Cache for future requests
  if (user) {
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  }

  return user;
}
```

### 2. Write-Through
```javascript
async function updateUser(userId, data) {
  // Write to database
  const user = await database.users.update(userId, data);

  // Write to cache simultaneously
  await redis.setex(`user:${userId}`, 3600, JSON.stringify(user));

  return user;
}
```

### 3. Write-Behind (Write-Back)
```javascript
// Queue writes for batch processing
const writeQueue = [];

async function updateUser(userId, data) {
  writeQueue.push({ userId, data, timestamp: Date.now() });

  // Process queue periodically
  if (writeQueue.length >= BATCH_SIZE) {
    await processWriteQueue();
  }
}

async function processWriteQueue() {
  const batch = writeQueue.splice(0, BATCH_SIZE);
  await database.users.bulkWrite(batch.map(w => ({
    updateOne: {
      filter: { id: w.userId },
      update: w.data
    }
  })));
}
```

### 4. Refresh-Ahead
```javascript
async function getProduct(productId) {
  const cacheKey = `product:${productId}`;
  let product = await redis.get(cacheKey);

  if (!product) {
    product = await database.products.findById(productId);
    await redis.setex(cacheKey, 3600, JSON.stringify(product));
  } else {
    // Refresh cache if nearing expiration
    const ttl = await redis.ttl(cacheKey);
    if (ttl < 300) {
      const fresh = await database.products.findById(productId);
      await redis.setex(cacheKey, 3600, JSON.stringify(fresh));
    }
  }

  return product;
}
```

## Cache Invalidation

### Time-Based Invalidation
```javascript
// Set TTL
await redis.setex(cacheKey, TTL_SECONDS, data);

// Read TTL
const ttl = await redis.ttl(cacheKey);
```

### Event-Based Invalidation
```javascript
// Subscribe to events
eventBus.subscribe('user.updated', async (event) => {
  await redis.del(`user:${event.userId}`);
});

eventBus.subscribe('product.deleted', async (event) => {
  await redis.del(`product:${event.productId}`);
  await redis.del('products:featured');
});
```

### Tag-Based Invalidation
```javascript
// Tag cache entries
await redis.sadd('tag:products:category-1', 'product:123');
await redis.sadd('tag:products:category-1', 'product:456');

// Invalidate by tag
await redis.del('tag:products:category-1');

// Get all entries with tag
const products = await redis.smembers('tag:products:category-1');
```

## Cache Patterns

### Cache Stampede Prevention
```javascript
async function getCachedData(key, fetchFn) {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  // Acquire lock
  const lock = await redis.setnx(`lock:${key}`, '1');
  if (lock) {
    try {
      const data = await fetchFn();
      await redis.setex(key, 3600, JSON.stringify(data));
      return data;
    } finally {
      await redis.del(`lock:${key}`);
    }
  } else {
    // Wait for lock holder
    await sleep(100);
    return getCachedData(key, fetchFn);
  }
}
```

### Circuit Breaker Pattern
```javascript
class CacheWithBreaker {
  constructor(redis, fallbackCache) {
    this.redis = redis;
    this.fallback = fallbackCache;
    this.breaker = new CircuitBreaker(5, 30000);
  }

  async get(key) {
    try {
      return await this.breaker.execute(() => this.redis.get(key));
    } catch (error) {
      // Fallback to local cache or compute
      return this.fallback.get(key);
    }
  }
}
```

## CDN Caching

### Cache-Control Headers
```javascript
// Static assets
res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');

// API responses
res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=300');

// Private (user-specific)
res.setHeader('Cache-Control', 'private, max-age=0, no-cache');

// Stale-while-revalidate
res.setHeader('Cache-Control', 'public, max-age=60, stale-while-revalidate=600');
```

### Vary Headers
```javascript
// Cache different versions
res.setHeader('Vary', 'Accept-Encoding, Accept-Language, User-Agent');
```

## Cache Size Management

### Eviction Policies
- **LRU**: Least Recently Used
- **LFU**: Least Frequently Used
- **FIFO**: First In First Out

### Memory Management
```javascript
// Set max memory
await redis.config('set', 'maxmemory', '2gb');

// Configure eviction
await redis.config('set', 'maxmemory-policy', 'allkeys-lru');
```

## Monitoring

### Cache Metrics
| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| hit_rate | Cache hit percentage | < 90% |
| memory_usage | Used memory | > 80% max |
| evictions | Items evicted | > 0 sustained |
| miss_rate | Cache miss percentage | > 20% |
| latency_p99 | 99th percentile latency | > 10ms |

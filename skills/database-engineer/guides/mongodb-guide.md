# MongoDB Database Guide

Best practices for MongoDB database design and operations.

## Schema Design

### Data Types
```javascript
// String
{ name: "John" }

// Number
{ age: 30, price: 19.99 }

// Boolean
{ active: true }

// Date
{ createdAt: new Date() }

// Null
{ deletedAt: null }

// Array
{ tags: ["premium", "user"] }

// Object (nested document)
{
  address: {
    street: "123 Main St",
    city: "New York",
    zip: "10001"
  }
 }

// ObjectId
{ _id: ObjectId("507f1f77bcf86cd799439011") }

// Regular Expression
{ email: /^.*@example\.com$/ }

// Binary Data
{ data: BinData(0, "base64encoded") }
```

### Schema Design Patterns

#### Embed vs Reference
```javascript
// Embed: One-to-few
{
  _id: ObjectId("123"),
  name: "John",
  addresses: [
    { type: "home", street: "123 Main St" },
    { type: "work", street: "456 Office Blvd" }
  ]
}

// Reference: One-to-many or many-to-many
// User collection
{
  _id: ObjectId("123"),
  name: "John"
}

// Order collection
{
  _id: ObjectId("456"),
  userId: ObjectId("123"),
  items: [{ productId: ObjectId("789"), quantity: 2 }]
}
```

#### Patterns
```javascript
// Polymorphic pattern (different types same collection)
{
  _id: ObjectId("123"),
  type: "premium",
  features: { vipSupport: true }
}

// Attribute pattern (searchable attributes)
{
  _id: ObjectId("123"),
  entityType: "product",
  attributes: [
    { key: "color", value: "blue" },
    { key: "size", value: "large" }
  ]
}

// Outlier pattern
{
  _id: ObjectId("123"),
  type: "order",
  status: "processing",
  outlierData: { specialHandling: true }  // Only for rare cases
}
```

## Indexing

### Index Types
```javascript
// Single field index
db.users.createIndex({ email: 1 })

// Compound index
db.orders.createIndex({ userId: 1, createdAt: -1 })

// Multikey index (arrays)
db.products.createIndex({ tags: 1 })

// Text index
db.articles.createIndex({ title: "text", body: "text" })

// Wildcard index
db.products.createIndex({ "attributes.$**": 1 })

// Hashed index (for sharding)
db.users.createIndex({ _id: "hashed" })

// Geospatial index
db.places.createIndex({ location: "2dsphere" })
```

### Index Options
```javascript
// Unique index
db.users.createIndex({ email: 1 }, { unique: true })

// Partial index
db.orders.createIndex(
  { status: 1, userId: 1 },
  { partialFilterExpression: { status: "pending" } }
)

// Sparse index (indexes only non-null values)
db.orders.createIndex(
  { cancelledAt: 1 },
  { sparse: true }
)

// TTL index (auto-delete)
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 3600 }
)
```

## Query Optimization

### Query Patterns
```javascript
// Good: Use covered queries
db.users.find(
  { status: "active" },
  { _id: 0, email: 1, name: 1 }  // Only indexed fields
).explain("executionStats")

// Good: Sort using prefix of compound index
db.orders.find({ userId: "123" }).sort({ createdAt: -1 })

// Bad: Function on indexed field
db.users.find({ email: email.toLowerCase() })
```

### Explain Analysis
```javascript
db.orders.explain("allPlansExecution").find({
  userId: ObjectId("123"),
  status: "shipped"
})

// Check for:
// - COLLSCAN (avoid)
// - IXSCAN (good)
// - FETCH after IXSCAN (ok)
// - high totalDocsExamined vs nReturned
```

## Performance Tuning

### Connection Pool
```javascript
// MongoDB driver connection
const client = new MongoClient(uri, {
  maxPoolSize: 100,           // Max connections
  minPoolSize: 10,            // Min connections
  maxIdleTimeMS: 60000,       // Idle timeout
  waitQueueTimeoutMS: 30000,  // Wait for connection
  serverSelectionTimeoutMS: 5000
});
```

### Aggregation Pipeline Optimization
```javascript
// Use $match early to reduce documents
db.orders.aggregate([
  { $match: { status: "shipped" } },  // Filter first
  { $group: { _id: "$userId", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } },
  { $limit: 10 }
])

// Use $limit early
db.orders.aggregate([
  { $sort: { createdAt: -1 } },
  { $limit: 100 },
  { $lookup: { from: "users", localField: "userId", foreignField: "_id", as: "user" } }
])
```

## Backup and Recovery

### mongodump
```bash
# Full backup
mongodump --uri="mongodb://localhost:27017/mydb" --out=/backup/

# Specific collection
mongodump --uri="mongodb://localhost:27017/mydb" --collection=users --out=/backup/

# Gzip compressed
mongodump --uri="mongodb://localhost:27017/mydb" --gzip --out=/backup/

# Point-in-time (oplog)
mongodump --uri="mongodb://localhost:27017/mydb" --oplog --out=/backup/
```

### mongorestore
```bash
# Restore
mongorestore --uri="mongodb://localhost:27017/mydb" /backup/

# Drop before restore
mongorestore --uri="mongodb://localhost:27017/mydb" --drop /backup/

# Specific collection
mongorestore --uri="mongodb://localhost:27017/mydb" --nsInclude="users" /backup/
```

### Point-in-Time Recovery
```javascript
// Enable oplog
// mongod.conf:
// replication:
//   oplogSizeMB: 1024
//   replSetName: "rs0"

// Create timestamp-based backup
// Use mongodump with --oplog

// Restore to point-in-time
// mongorestore --oplogReplay --pointInTimeRecovery
```

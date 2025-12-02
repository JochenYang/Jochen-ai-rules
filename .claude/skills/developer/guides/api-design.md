# API 设计指南

## RESTful API 设计原则

### 资源命名

#### 使用名词而非动词
```
✅ GET /users
✅ POST /users
✅ GET /users/123

❌ GET /getUsers
❌ POST /createUser
```

#### 使用复数形式
```
✅ /users
✅ /products
✅ /orders

❌ /user
❌ /product
```

#### 使用小写字母和连字符
```
✅ /user-profiles
✅ /order-items

❌ /userProfiles
❌ /OrderItems
```

#### 资源层级
```
✅ /users/123/orders
✅ /products/456/reviews

⚠️ 避免超过3层嵌套
❌ /users/123/orders/456/items/789/details
```

---

### HTTP 方法

#### GET - 获取资源
```
GET /users          # 获取用户列表
GET /users/123      # 获取单个用户
GET /users/123/orders  # 获取用户的订单
```

#### POST - 创建资源
```
POST /users         # 创建新用户
POST /users/123/orders  # 为用户创建订单
```

#### PUT - 完整更新资源
```
PUT /users/123      # 完整更新用户（需要所有字段）
```

#### PATCH - 部分更新资源
```
PATCH /users/123    # 部分更新用户（只需要更新的字段）
```

#### DELETE - 删除资源
```
DELETE /users/123   # 删除用户
```

---

### HTTP 状态码

#### 2xx 成功
- `200 OK` - 请求成功（GET、PUT、PATCH）
- `201 Created` - 资源创建成功（POST）
- `204 No Content` - 请求成功但无返回内容（DELETE）

#### 4xx 客户端错误
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未认证
- `403 Forbidden` - 无权限
- `404 Not Found` - 资源不存在
- `409 Conflict` - 资源冲突（如重复创建）
- `422 Unprocessable Entity` - 验证失败
- `429 Too Many Requests` - 请求过多（限流）

#### 5xx 服务器错误
- `500 Internal Server Error` - 服务器错误
- `502 Bad Gateway` - 网关错误
- `503 Service Unavailable` - 服务不可用

---

### 请求与响应格式

#### 请求体（JSON）
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

#### 成功响应
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

#### 错误响应
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

#### 列表响应（带分页）
```json
{
  "data": [
    { "id": 1, "name": "User 1" },
    { "id": 2, "name": "User 2" }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "totalPages": 10
  }
}
```

---

## 查询参数

### 分页
```
GET /users?page=1&limit=10
GET /users?offset=0&limit=10
```

### 排序
```
GET /users?sort=createdAt:desc
GET /users?sort=-createdAt  # 降序
GET /users?sort=name,createdAt:desc  # 多字段排序
```

### 过滤
```
GET /users?status=active
GET /users?age[gte]=18&age[lte]=65
GET /users?name[contains]=john
```

### 字段选择
```
GET /users?fields=id,name,email
GET /users?exclude=password,token
```

### 搜索
```
GET /users?q=john
GET /users?search=john&searchFields=name,email
```

---

## 版本控制

### URL 版本控制（推荐）
```
GET /v1/users
GET /v2/users
```

### Header 版本控制
```
GET /users
Accept: application/vnd.api.v1+json
```

### 查询参数版本控制
```
GET /users?version=1
```

---

## 认证授权

### Bearer Token（推荐）
```
Authorization: Bearer <token>
```

### API Key
```
X-API-Key: <api-key>
```

### Basic Auth（仅HTTPS）
```
Authorization: Basic <base64(username:password)>
```

---

## 安全最佳实践

### 输入验证
- [ ] 验证所有输入数据
- [ ] 使用白名单而非黑名单
- [ ] 限制字符串长度
- [ ] 验证数据类型

### 认证授权
- [ ] 所有敏感端点需要认证
- [ ] 实现基于角色的访问控制（RBAC）
- [ ] 使用HTTPS传输
- [ ] Token设置合理过期时间

### 限流
- [ ] 实现API限流
- [ ] 返回限流信息头
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

### CORS
- [ ] 配置合理的CORS策略
- [ ] 避免使用通配符 `*`
- [ ] 明确指定允许的域名

---

## 性能优化

### 缓存
```
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### 压缩
```
Accept-Encoding: gzip, deflate, br
Content-Encoding: gzip
```

### 分页
- [ ] 默认限制返回数量
- [ ] 提供分页参数
- [ ] 返回总数和分页信息

### 字段过滤
- [ ] 支持字段选择
- [ ] 避免返回敏感字段（密码、token）

---

## 错误处理

### 统一错误格式
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [],
    "timestamp": "2024-01-01T00:00:00Z",
    "path": "/api/users",
    "requestId": "uuid"
  }
}
```

### 常见错误代码
```
VALIDATION_ERROR       - 验证失败
AUTHENTICATION_ERROR   - 认证失败
AUTHORIZATION_ERROR    - 权限不足
NOT_FOUND             - 资源不存在
CONFLICT              - 资源冲突
RATE_LIMIT_EXCEEDED   - 超过限流
INTERNAL_ERROR        - 服务器错误
```

---

## 文档

### OpenAPI/Swagger
- [ ] 使用OpenAPI 3.0规范
- [ ] 自动生成API文档
- [ ] 提供交互式API测试

### 文档内容
- [ ] 端点描述
- [ ] 请求参数
- [ ] 响应格式
- [ ] 错误代码
- [ ] 示例请求/响应
- [ ] 认证方式

---

## 测试

### 单元测试
- [ ] 验证逻辑测试
- [ ] 错误处理测试
- [ ] 边界条件测试

### 集成测试
- [ ] 完整API流程测试
- [ ] 认证授权测试
- [ ] 错误场景测试

### 性能测试
- [ ] 负载测试
- [ ] 压力测试
- [ ] 响应时间测试

---

## API 设计检查清单

### 基础
- [ ] 使用RESTful原则
- [ ] 资源命名清晰
- [ ] HTTP方法使用正确
- [ ] 状态码使用恰当

### 安全
- [ ] 认证授权实现
- [ ] 输入验证
- [ ] 限流保护
- [ ] HTTPS传输

### 性能
- [ ] 分页实现
- [ ] 缓存策略
- [ ] 响应压缩
- [ ] 字段过滤

### 可维护性
- [ ] 版本控制
- [ ] 完整文档
- [ ] 错误处理
- [ ] 日志记录

### 测试
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能测试
- [ ] 安全测试

---

## 示例：用户管理 API

### 端点列表
```
GET    /v1/users           # 获取用户列表
POST   /v1/users           # 创建用户
GET    /v1/users/:id       # 获取单个用户
PUT    /v1/users/:id       # 完整更新用户
PATCH  /v1/users/:id       # 部分更新用户
DELETE /v1/users/:id       # 删除用户
```

### 创建用户
```http
POST /v1/users
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response: 201 Created
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "createdAt": "2024-01-01T00:00:00Z"
}
```

### 获取用户列表
```http
GET /v1/users?page=1&limit=10&sort=-createdAt&status=active
Authorization: Bearer <token>

Response: 200 OK
{
  "data": [
    {
      "id": 123,
      "name": "John Doe",
      "email": "john@example.com",
      "status": "active",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "totalPages": 10
  }
}
```

---

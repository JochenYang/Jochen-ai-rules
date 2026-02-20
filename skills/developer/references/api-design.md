# API 设计规范

## RESTful API 设计原则

### 1. 资源命名规范

使用复数名词表示资源集合，避免使用动词：

```
✅ 正确示例
GET    /users              # 获取用户列表
POST   /users              # 创建新用户
GET    /users/:id          # 获取单个用户
PUT    /users/:id          # 完整更新用户
PATCH  /users/:id          # 部分更新用户
DELETE /users/:id          # 删除用户

GET    /users/:id/posts    # 获取用户的文章列表
POST   /users/:id/posts    # 为用户创建文章

❌ 错误示例
GET    /getUsers           # 不要使用动词
POST   /createUser         # 不要使用动词
GET    /user/:id           # 使用复数而非单数
```

### 2. HTTP 方法语义

严格遵循 HTTP 方法的语义：

| 方法   | 用途           | 幂等性 | 安全性 |
|--------|----------------|--------|--------|
| GET    | 获取资源       | ✅     | ✅     |
| POST   | 创建资源       | ❌     | ❌     |
| PUT    | 完整更新资源   | ✅     | ❌     |
| PATCH  | 部分更新资源   | ❌     | ❌     |
| DELETE | 删除资源       | ✅     | ❌     |

**幂等性**：多次执行产生相同结果
**安全性**：不会修改服务器状态

### 3. 状态码规范

使用正确的 HTTP 状态码：

```
2xx 成功
200 OK                  - 请求成功（GET, PUT, PATCH）
201 Created             - 资源创建成功（POST）
204 No Content          - 成功但无返回内容（DELETE）

4xx 客户端错误
400 Bad Request         - 请求参数错误
401 Unauthorized        - 未认证（需要登录）
403 Forbidden           - 无权限（已登录但权限不足）
404 Not Found           - 资源不存在
409 Conflict            - 资源冲突（如重复创建）
422 Unprocessable Entity - 验证失败（语义错误）
429 Too Many Requests   - 请求过于频繁

5xx 服务器错误
500 Internal Server Error - 服务器内部错误
502 Bad Gateway          - 网关错误
503 Service Unavailable  - 服务不可用
```

### 4. 统一响应格式

**成功响应**：

```json
{
  "success": true,
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**列表响应（带分页）**：

```json
{
  "success": true,
  "data": [
    { "id": "1", "name": "Item 1" },
    { "id": "2", "name": "Item 2" }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

**错误响应**：

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  }
}
```

### 5. 查询参数规范

**分页**：
```
GET /users?page=1&pageSize=20
GET /users?limit=20&offset=0
```

**过滤**：
```
GET /users?role=admin&status=active
GET /posts?author=123&published=true
```

**排序**：
```
GET /users?sort=createdAt          # 升序
GET /users?sort=-createdAt         # 降序（使用 - 前缀）
GET /users?sort=name,-createdAt    # 多字段排序
```

**字段选择**：
```
GET /users?fields=id,name,email    # 只返回指定字段
```

**搜索**：
```
GET /users?q=john                  # 全文搜索
GET /users?search=john&searchFields=name,email
```

### 6. 版本管理

推荐使用 URL 路径版本控制：

```
✅ 推荐
GET /v1/users
GET /v2/users

⚠️ 可选（Header 版本控制）
GET /users
Header: Accept: application/vnd.api.v1+json

❌ 不推荐（查询参数）
GET /users?version=1
```

## 错误处理

### 错误码设计

```typescript
enum ErrorCode {
  // 客户端错误 (4xx)
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  
  // 服务器错误 (5xx)
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR'
}
```

### 错误处理中间件示例（Express）

```typescript
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  console.error('[Error]', err);

  // Zod 验证错误
  if (err instanceof ZodError) {
    return res.status(400).json({
      success: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Validation failed',
        details: err.errors.map(e => ({
          field: e.path.join('.'),
          message: e.message
        }))
      }
    });
  }

  // 自定义业务错误
  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({
      success: false,
      error: {
        code: 'UNAUTHORIZED',
        message: 'Authentication required'
      }
    });
  }

  // 默认服务器错误
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred'
    }
  });
}
```

## 认证与授权

### JWT 认证示例

```typescript
import jwt from 'jsonwebtoken';

// 生成 Token
export function generateToken(userId: string): string {
  return jwt.sign(
    { userId },
    process.env.JWT_SECRET!,
    { expiresIn: '7d' }
  );
}

// 验证 Token
export function verifyToken(token: string) {
  return jwt.verify(token, process.env.JWT_SECRET!);
}

// 认证中间件
export function authenticate(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({
      success: false,
      error: { code: 'UNAUTHORIZED', message: 'Token required' }
    });
  }

  try {
    const payload = verifyToken(token);
    req.user = payload;
    next();
  } catch (error) {
    res.status(401).json({
      success: false,
      error: { code: 'UNAUTHORIZED', message: 'Invalid token' }
    });
  }
}
```

## 最佳实践

1. **使用 HTTPS**：生产环境必须使用 HTTPS
2. **输入验证**：使用 Zod/Joi 等库进行严格验证
3. **限流**：使用 express-rate-limit 防止滥用
4. **CORS 配置**：正确配置跨域资源共享
5. **日志记录**：记录所有 API 请求和错误
6. **API 文档**：使用 Swagger/OpenAPI 生成文档
7. **缓存策略**：合理使用 Cache-Control 头
8. **压缩响应**：使用 gzip/brotli 压缩


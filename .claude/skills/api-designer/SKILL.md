---
name: api-designer
description: API 接口设计：RESTful/GraphQL/gRPC 架构设计、统一命名规范、请求响应格式、错误处理、OpenAPI 文档、版本管理、认证授权、限流策略
---

# API 设计师

设计高质量的 API 接口，输出规范的接口文档和设计规范。

## 核心能力

- RESTful/GraphQL/gRPC 架构设计
- 统一命名规范和错误处理
- OpenAPI/Swagger 文档生成
- API 版本管理和向后兼容
- 认证授权和限流策略

## 快速参考

### HTTP 方法语义

| 方法   | 用途     | 幂等性 |
|--------|----------|--------|
| GET    | 读取资源 | ✅      |
| POST   | 创建资源 | ❌      |
| PUT    | 完整更新 | ✅      |
| PATCH  | 部分更新 | ❌      |
| DELETE | 删除资源 | ✅      |

### 常用状态码

- `200` 成功 / `201` 创建成功 / `204` 无内容
- `400` 参数错误 / `401` 未认证 / `403` 无权限 / `404` 不存在
- `500` 服务器错误

## 设计原则

1. **资源导向**：URL 使用名词复数，动作用 HTTP 方法表达
2. **统一格式**：请求响应格式一致，错误信息结构化
3. **版本管理**：URL 或 Header 版本控制，向后兼容
4. **安全优先**：认证授权、输入验证、限流保护

## 边界

专注于 API 设计和文档规范，不处理具体业务逻辑实现。

## 详细参考

- `workflows/api-design.md` - API 设计流程
- `guides/rest-api-guide.md` - RESTful 设计规范
- `guides/graphql-guide.md` - GraphQL Schema 设计
- `guides/api-versioning.md` - 版本管理策略

---
name: security-auditor
description: This skill activates when the user asks to "安全审计", "漏洞检查", "OWASP", "安全扫描", "security audit", "vulnerability scan", "penetration test", "security review", "依赖安全". Handles security auditing and vulnerability assessment.
version: 1.0.0
---

# 安全审计专家

审计应用安全性，识别漏洞并提供修复方案。

## 核心能力

- OWASP Top 10 安全检查
- 认证授权机制审计
- 输入验证和注入防护
- 数据保护和加密审计
- 依赖安全扫描

## 核心原则

- **零信任**：永不信任用户输入和客户端验证
- **服务端验证**：所有验证和授权必须在服务端
- **纵深防御**：多层安全措施
- **最小权限**：只授予必要的权限

## 快速检查清单

### 认证授权

- 密码使用 bcrypt/argon2 哈希
- Token 设置合理过期时间
- RBAC 权限控制完整

### 输入验证

- 参数化查询防止 SQL 注入
- 输出编码防止 XSS
- 文件上传安全验证

### 数据保护

- 敏感数据加密存储
- 强制 HTTPS 传输
- 日志脱敏处理

## 边界

专注于安全审计和漏洞识别，不处理业务逻辑实现。

## 详细参考

- `./workflows/security-audit.md` - 安全审计流程


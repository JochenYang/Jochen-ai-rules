---
description: 快速执行部署流程，包括构建、测试、部署和验证
---

# Deploy 快速部署

快速执行完整部署流程，确保代码安全上线。

## 执行流程

### 1. 部署前检查（devops-engineer）
- 检查环境配置
- 确认数据库迁移脚本
- 检查 SSL 证书有效期
- 确认备份已创建

### 2. 代码质量检查（test-engineer + code-reviewer）
- 运行所有测试（单元 + 集成 + E2E）
- 检查测试覆盖率 > 80%
- 运行 Linter 检查
- 安全扫描（npm audit/Snyk）

### 3. 构建应用（devops-engineer）
- 构建前端应用
- 构建后端应用
- 构建 Docker 镜像
- 推送镜像到仓库

### 4. 选择部署策略（devops-engineer）
- 滚动更新：标准更新，低风险
- 蓝绿部署：大版本发布，快速回滚
- 金丝雀发布：高风险变更，逐步验证

### 5. 执行部署（devops-engineer）
- 执行数据库迁移
- 部署应用
- 运行烟雾测试
- 检查健康端点

### 6. 监控验证（devops-engineer）
- 监控错误率 < 0.1%
- 监控响应时间 P95 < 500ms
- 检查错误日志
- 验证核心功能

### 7. 通知团队
- 发送部署成功通知
- 记录部署日志和版本号
- 创建 Git Tag

## 相关命令
- quickstart - 快速启动开发
- review - 代码审查
- optimize - 性能优化

## 相关 Skills
- devops-engineer
- test-engineer
- code-reviewer

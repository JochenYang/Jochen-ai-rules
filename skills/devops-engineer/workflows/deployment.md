# 部署工作流程

## 概述
本工作流程定义了从代码提交到生产环境部署的完整流程，包括测试、构建、部署、监控四个主要阶段。

---

## 阶段 1：准备与检查（Pre-deployment）

### 1.1 环境检查
**执行步骤**：
1. 确认目标环境（dev/staging/production）
2. 检查环境配置文件（.env、secrets）
3. 确认数据库迁移脚本
4. 检查依赖版本兼容性

**检查清单**：
- [ ] 环境变量配置完整
- [ ] 数据库连接正常
- [ ] 外部服务可访问（API、S3、Redis 等）
- [ ] SSL 证书有效期 > 30 天

### 1.2 代码质量检查
**执行步骤**：
1. 运行 Linter（ESLint/Pylint/golangci-lint）
2. 运行单元测试（覆盖率 > 80%）
3. 运行集成测试
4. 安全扫描（npm audit/Snyk）

**通过标准**：
- ✅ 所有测试通过
- ✅ 无阻断性安全漏洞（Critical/High）
- ✅ 代码覆盖率达标

---

## 阶段 2：构建（Build）

### 2.1 应用构建
**前端应用**：
```bash
# 安装依赖
npm ci --only=production

# 构建生产版本
npm run build

# 构建验证
ls -lh dist/  # 检查构建产物
```

**后端应用**：
```bash
# Go 示例
go build -ldflags="-s -w" -o app

# Python 示例（使用 Poetry）
poetry install --no-dev
poetry build
```

### 2.2 Docker 镜像构建
**多阶段构建示例（Node.js）**：
```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 运行阶段
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**镜像构建命令**：
```bash
# 构建镜像（包含版本标签）
docker build -t myapp:${VERSION} -t myapp:latest .

# 镜像体积优化检查
docker images myapp:${VERSION}

# 安全扫描
docker scan myapp:${VERSION}
```

**镜像优化检查**：
- [ ] 镜像体积 < 500MB（Node.js）或 < 100MB（Go）
- [ ] 无高危漏洞
- [ ] 使用非 root 用户运行

### 2.3 推送镜像到仓库
```bash
# 推送到 Docker Hub
docker push myapp:${VERSION}

# 或推送到私有仓库
docker tag myapp:${VERSION} registry.example.com/myapp:${VERSION}
docker push registry.example.com/myapp:${VERSION}
```

---

## 阶段 3：部署（Deploy）

### 3.1 选择部署策略

#### 策略 A：滚动更新（Rolling Update）
**适用场景**：标准应用更新、低风险变更

**Kubernetes 配置**：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1  # 最多 1 个 Pod 不可用
      maxSurge: 1        # 最多额外创建 1 个 Pod
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:v1.2.0
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**部署命令**：
```bash
# 更新镜像
kubectl set image deployment/myapp myapp=myapp:v1.2.0

# 观察部署进度
kubectl rollout status deployment/myapp

# 如果失败，回滚
kubectl rollout undo deployment/myapp
```

#### 策略 B：蓝绿部署（Blue-Green）
**适用场景**：大版本发布、需要快速回滚

**步骤**：
1. 部署新版本（Green）到独立环境
2. 在新环境进行烟雾测试
3. 切换流量到新环境（更新 Service selector）
4. 监控新环境运行状态
5. 确认无问题后，销毁旧环境（Blue）

**示例配置**：
```yaml
# 新版本 Deployment（green）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myapp:v1.2.0

---
# Service（流量切换）
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: green  # 切换到 green 版本
  ports:
  - port: 80
    targetPort: 3000
```

#### 策略 C：金丝雀发布（Canary）
**适用场景**：高风险变更、大型应用

**逐步增加流量**：
```bash
# 阶段1：5% 流量到新版本
kubectl apply -f canary-5percent.yaml

# 监控 5 分钟，无异常进入下一阶段
# 阶段2：25% 流量
kubectl apply -f canary-25percent.yaml

# 阶段3：50% 流量
kubectl apply -f canary-50percent.yaml

# 阶段4：100% 流量（完全切换）
kubectl apply -f canary-100percent.yaml
```

### 3.2 数据库迁移
**迁移前检查**：
- [ ] 备份数据库
- [ ] 测试环境验证迁移脚本
- [ ] 准备回滚脚本

**执行迁移**：
```bash
# 使用迁移工具（如 Flyway、Liquibase、Alembic）
npm run migrate:up

# 或手动执行 SQL
psql -h db-host -U user -d dbname -f migrations/001_add_users_table.sql
```

**迁移后验证**：
- [ ] 检查表结构正确
- [ ] 检查索引创建成功
- [ ] 运行数据一致性检查

### 3.3 部署验证（Smoke Test）
**健康检查**：
```bash
# 1. HTTP 健康端点检查
curl https://api.example.com/health
# 期望输出：{"status": "ok"}

# 2. 数据库连接检查
curl https://api.example.com/health/db
# 期望输出：{"db": "connected"}

# 3. 外部依赖检查
curl https://api.example.com/health/dependencies
```

**关键功能测试**：
- [ ] 用户登录功能正常
- [ ] 核心 API 端点响应正常
- [ ] 数据写入和读取正常

---

## 阶段 4：监控与验证（Post-deployment）

### 4.1 实时监控
**监控指标（前 15 分钟密切关注）**：
- **错误率**：< 0.1%
- **响应时间**：P95 < 500ms
- **CPU/内存**：< 70%
- **请求成功率**：> 99.9%

**告警配置**：
```yaml
# Prometheus 告警规则
groups:
- name: deployment
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
    for: 2m
    annotations:
      summary: "部署后错误率异常"
  
  - alert: HighLatency
    expr: http_request_duration_seconds{quantile="0.95"} > 1
    for: 5m
    annotations:
      summary: "部署后响应时间过长"
```

### 4.2 日志监控
**关键日志检查**：
```bash
# 实时查看应用日志
kubectl logs -f deployment/myapp --tail=100

# 搜索错误日志
kubectl logs deployment/myapp | grep -i error

# 检查特定时间段的日志（部署后）
kubectl logs deployment/myapp --since=15m
```

**需要关注的日志模式**：
- ❌ Fatal、Error、Exception 关键词
- ❌ 数据库连接失败
- ❌ 外部 API 调用超时
- ❌ 内存溢出（OOM）

### 4.3 回滚准备
**回滚触发条件**：
- 错误率 > 1%（持续 5 分钟）
- P95 响应时间 > 2 秒
- 核心功能不可用
- 数据库迁移失败

**快速回滚命令**：
```bash
# Kubernetes 回滚到上一个版本
kubectl rollout undo deployment/myapp

# 或回滚到指定版本
kubectl rollout undo deployment/myapp --to-revision=3

# 查看回滚状态
kubectl rollout status deployment/myapp
```

**数据库回滚**：
```bash
# 执行回滚脚本
npm run migrate:down
```

---

## 完整 CI/CD Pipeline 示例

### GitHub Actions 示例
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm ci
          npm test
          npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myapp:latest
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push myapp:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
          kubectl rollout status deployment/myapp
      - name: Verify deployment
        run: |
          curl -f https://api.example.com/health || exit 1
      - name: Notify team
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text": "✅ Deployed to production"}'
```

---

## 部署检查清单

### 部署前
- [ ] 代码已合并到 main/master 分支
- [ ] 所有测试通过（单元测试 + 集成测试）
- [ ] 安全扫描无阻断性漏洞
- [ ] 数据库迁移脚本已准备
- [ ] 环境变量已配置
- [ ] 备份已创建

### 部署中
- [ ] 选择合适的部署策略
- [ ] 执行数据库迁移
- [ ] 部署应用到目标环境
- [ ] 运行烟雾测试

### 部署后
- [ ] 监控关键指标（15 分钟）
- [ ] 检查错误日志
- [ ] 验证核心功能
- [ ] 通知团队部署结果
- [ ] 记录部署日志和版本号

---

## 常见问题排查

### 问题 1：Pod 启动失败
**症状**：`kubectl get pods` 显示 CrashLoopBackOff

**排查步骤**：
```bash
# 查看 Pod 详情
kubectl describe pod <pod-name>

# 查看容器日志
kubectl logs <pod-name>

# 进入容器调试（如果可以）
kubectl exec -it <pod-name> -- /bin/sh
```

### 问题 2：镜像拉取失败
**症状**：ImagePullBackOff

**解决方案**：
- 检查镜像名称和标签是否正确
- 确认镜像仓库凭据配置正确
- 验证镜像在仓库中存在

### 问题 3：健康检查失败
**症状**：Readiness probe failed

**解决方案**：
- 增加 `initialDelaySeconds`（给应用更多启动时间）
- 检查健康检查端点是否正常
- 确认端口配置正确

---

## 最佳实践总结

1. **自动化优先**：尽可能自动化每个步骤
2. **渐进式部署**：高风险变更使用金丝雀发布
3. **快速回滚**：准备好随时回滚的机制
4. **完善监控**：部署后密切监控关键指标
5. **环境隔离**：Dev → Staging → Production 严格隔离
6. **文档记录**：每次部署记录版本号、变更内容、部署时间

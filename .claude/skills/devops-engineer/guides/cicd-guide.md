# CI/CD 最佳实践指南

## 概述
本指南提供 CI/CD 流水线设计的最佳实践，涵盖 GitHub Actions、GitLab CI 和通用 CI/CD 原则。

---

## CI/CD 核心原则

### 1. 快速反馈
- **目标**：开发者提交代码后 15 分钟内获得反馈
- **实践**：
  - 单元测试 < 5 分钟
  - 集成测试 < 10 分钟
  - 构建 < 5 分钟

### 2. 阶段分离
```
提交代码 → Lint → Test → Build → Deploy Dev → Deploy Staging → Deploy Prod
```

### 3. 环境隔离
| 环境 | 用途 | 部署方式 | 数据 |
|------|------|----------|------|
| **Development** | 开发测试 | 自动部署（每次提交） | Mock/测试数据 |
| **Staging** | 预发布环境 | 自动部署（main 分支） | 生产数据副本 |
| **Production** | 生产环境 | 手动审批 | 真实数据 |

---

## GitHub Actions 最佳实践

### 基础 Workflow 结构
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  DOCKER_REGISTRY: ghcr.io

jobs:
  lint:
    name: Code Quality Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Check formatting
        run: npm run format:check

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    environment: staging
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Kubernetes
        run: |
          kubectl config use-context staging
          kubectl set image deployment/myapp \
            myapp=${{ env.DOCKER_REGISTRY }}/${{ github.repository }}:sha-${{ github.sha }}
          kubectl rollout status deployment/myapp
      
      - name: Run smoke tests
        run: |
          curl -f https://staging.example.com/health || exit 1
      
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Deployed to Staging: ${{ github.event.head_commit.message }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production  # 需要手动审批
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Kubernetes
        run: |
          kubectl config use-context production
          kubectl set image deployment/myapp \
            myapp=${{ env.DOCKER_REGISTRY }}/${{ github.repository }}:sha-${{ github.sha }}
          kubectl rollout status deployment/myapp --timeout=10m
      
      - name: Verify deployment
        run: |
          curl -f https://api.example.com/health || exit 1
      
      - name: Notify team
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "🚀 Deployed to Production: ${{ github.event.head_commit.message }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 高级技巧

#### 1. 缓存优化（加速 CI）
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-
```

#### 2. 矩阵策略（多版本测试）
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

#### 3. 可重用 Workflow
```yaml
# .github/workflows/deploy.yml（可重用）
name: Reusable Deploy Workflow

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-tag:
        required: true
        type: string
    secrets:
      KUBE_CONFIG:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Deploy to K8s
        run: |
          kubectl set image deployment/myapp myapp=${{ inputs.image-tag }}

# 调用可重用 workflow
jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      image-tag: myapp:v1.2.0
    secrets:
      KUBE_CONFIG: ${{ secrets.STAGING_KUBE_CONFIG }}
```

---

## GitLab CI 最佳实践

### 基础 .gitlab-ci.yml
```yaml
stages:
  - lint
  - test
  - build
  - deploy-staging
  - deploy-production

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

# 通用规则
.docker-template: &docker-template
  image: docker:latest
  services:
    - docker:dind

.kubectl-template: &kubectl-template
  image: bitnami/kubectl:latest
  before_script:
    - kubectl config use-context $K8S_CONTEXT

# Lint 阶段
lint:
  stage: lint
  image: node:18-alpine
  cache:
    paths:
      - node_modules/
  script:
    - npm ci
    - npm run lint
    - npm run format:check
  only:
    - merge_requests
    - main

# Test 阶段
test:unit:
  stage: test
  image: node:18-alpine
  services:
    - postgres:15
  variables:
    POSTGRES_DB: test
    POSTGRES_PASSWORD: postgres
  cache:
    paths:
      - node_modules/
  script:
    - npm ci
    - npm run test:unit
    - npm run test:integration
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

# Build 阶段
build:
  <<: *docker-template
  stage: build
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main

# Deploy Staging
deploy:staging:
  <<: *kubectl-template
  stage: deploy-staging
  variables:
    K8S_CONTEXT: staging
  script:
    - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/myapp
    - curl -f https://staging.example.com/health || exit 1
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

# Deploy Production（需要手动触发）
deploy:production:
  <<: *kubectl-template
  stage: deploy-production
  variables:
    K8S_CONTEXT: production
  script:
    - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/myapp --timeout=10m
    - curl -f https://api.example.com/health || exit 1
  environment:
    name: production
    url: https://api.example.com
  when: manual
  only:
    - main
```

### GitLab CI 高级特性

#### 1. 动态子流水线
```yaml
generate-config:
  stage: .pre
  script:
    - python generate-pipeline.py > generated-config.yml
  artifacts:
    paths:
      - generated-config.yml

run-generated:
  stage: build
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
    strategy: depend
```

#### 2. 并行测试
```yaml
test:
  stage: test
  parallel:
    matrix:
      - TEST_SUITE: [unit, integration, e2e]
        NODE_VERSION: [16, 18, 20]
  script:
    - npm run test:$TEST_SUITE
```

---

## Secret 管理

### GitHub Actions
```yaml
# 使用加密 Secret
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: |
    ./deploy.sh
```

### GitLab CI
```yaml
# 使用受保护变量（Settings → CI/CD → Variables）
deploy:
  script:
    - echo $API_KEY  # 自动脱敏
    - ./deploy.sh
  only:
    - main
```

### 最佳实践
- ✅ 永不将 Secret 硬编码在代码中
- ✅ 使用环境特定的 Secret（staging-api-key vs production-api-key）
- ✅ 定期轮换 Secret
- ✅ 限制 Secret 访问权限（只有 main 分支可访问生产 Secret）

---

## 监控与通知

### Slack 通知集成
```yaml
# GitHub Actions
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Deploy Status:* ${{ job.status }}\n*Branch:* ${{ github.ref }}\n*Commit:* ${{ github.event.head_commit.message }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

### Email 通知（GitLab）
```yaml
# .gitlab-ci.yml
deploy:production:
  script:
    - ./deploy.sh
  after_script:
    - |
      if [ "$CI_JOB_STATUS" == "success" ]; then
        echo "Deployment successful" | mail -s "Deploy Success" team@example.com
      else
        echo "Deployment failed" | mail -s "Deploy Failed" team@example.com
      fi
```

---

## 性能优化

### 1. 并行化任务
```yaml
# GitHub Actions
jobs:
  test:
    strategy:
      matrix:
        test-group: [1, 2, 3, 4]
    steps:
      - run: npm run test -- --group=${{ matrix.test-group }}
```

### 2. 使用预构建镜像
```yaml
# 自定义 CI 镜像（包含常用工具）
FROM node:18-alpine
RUN apk add --no-cache git curl docker-cli kubectl
COPY . /app
WORKDIR /app
RUN npm ci
```

### 3. 增量构建
```yaml
# 只构建变更的服务
- name: Detect changes
  id: changes
  uses: dorny/paths-filter@v2
  with:
    filters: |
      api:
        - 'api/**'
      web:
        - 'web/**'

- name: Build API
  if: steps.changes.outputs.api == 'true'
  run: docker build -t api ./api
```

---

## 安全检查

### 依赖扫描
```yaml
# GitHub Actions
- name: Run Snyk security scan
  uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high

# GitLab CI
include:
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/SAST.gitlab-ci.yml
```

### 镜像扫描
```yaml
- name: Run Trivy scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload results to GitHub Security
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

---

## 常见问题

### Q1: CI 运行太慢怎么办？
**解决方案**：
- 使用缓存（依赖、Docker layers）
- 并行化测试
- 减少不必要的步骤
- 使用更快的 Runner（自托管 Runner）

### Q2: 如何处理 Flaky Tests（不稳定测试）？
**解决方案**：
- 自动重试失败的测试（最多 3 次）
- 隔离 Flaky Tests 到单独的 Job
- 记录和修复 Flaky Tests

### Q3: 如何安全地回滚？
**解决方案**：
- 保留最近 5 个版本的镜像
- 使用 Git tags 标记发布版本
- Kubernetes 使用 `kubectl rollout undo`

---

## 参考资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitLab CI 官方文档](https://docs.gitlab.com/ee/ci/)
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes 部署策略](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---
name: database-engineer
description: Database architecture design, schema optimization, query performance tuning, and data migration. Handles PostgreSQL, MySQL, MongoDB, Redis with focus on scalability, indexing strategies, and transaction management.
license: MIT
compatibility: Requires database clients and migration tools. Works with SQL and NoSQL databases.
allowed-tools: Read Write Bash
---

# Database Engineer

专注于数据库架构设计、性能优化、数据迁移和高可用方案。适用于复杂的数据库设计、性能瓶颈分析、大规模数据迁移等专业任务。

## Core Capabilities

### 数据库设计
- Schema 设计和范式化
- 索引策略和优化
- 分区和分片设计
- 数据模型设计（关系型/文档型/图数据库）

### 性能优化
- 查询性能分析和优化
- 索引优化和覆盖索引
- 执行计划分析
- 慢查询诊断和修复

### 数据迁移
- 数据库版本升级
- 跨数据库迁移（MySQL → PostgreSQL）
- 大规模数据迁移策略
- 零停机迁移方案

### 高可用方案
- 主从复制配置
- 读写分离架构
- 故障转移和恢复
- 备份和恢复策略

## Tech Stack

| 类型 | 技术栈 |
|------|--------|
| 关系型数据库 | PostgreSQL, MySQL, MariaDB |
| NoSQL | MongoDB, Redis, Cassandra |
| 时序数据库 | InfluxDB, TimescaleDB |
| 搜索引擎 | Elasticsearch, OpenSearch |
| 迁移工具 | Flyway, Liquibase, Alembic |
| 监控工具 | pg_stat_statements, Percona Toolkit |

## 设计原则

### 1. 范式化与反范式化平衡
- 3NF 用于事务性数据
- 适度反范式化提升查询性能
- 避免过度范式化导致的 JOIN 复杂度

### 2. 索引策略
- 高选择性列优先建索引
- 复合索引遵循最左前缀原则
- 避免过度索引影响写入性能
- 使用覆盖索引减少回表

### 3. 查询优化
- 避免 SELECT *
- 使用 EXPLAIN ANALYZE 分析执行计划
- 避免 N+1 查询问题
- 合理使用批量操作

### 4. 事务管理
- 选择合适的隔离级别
- 避免长事务锁表
- 使用乐观锁处理并发
- 死锁检测和预防

## Execution Workflow

### Phase 1: 需求分析
1. 理解业务需求和数据模型
2. 评估数据量和增长趋势
3. 确定性能和可用性要求

### Phase 2: 设计方案
1. 设计 Schema 和索引
2. 选择合适的数据库类型
3. 规划分区和分片策略
4. 设计备份和恢复方案

### Phase 3: 实施优化
1. 执行 Schema 变更
2. 创建和优化索引
3. 重构慢查询
4. 配置监控和告警

## Quality Standards

- 查询响应时间 < 100ms（简单查询）
- 索引命中率 > 95%
- 数据库连接池利用率 < 80%
- 备份恢复时间目标（RTO）< 1 小时

## Boundaries

专注于数据库层面的设计和优化，不涉及应用层业务逻辑实现。

## Helper Scripts

**Always run `--help` first** to see usage.

- `scripts/analyze-schema.sh` - Schema 分析和优化建议
- `scripts/index-advisor.sh` - 索引优化建议
- `scripts/migration-plan.sh` - 数据迁移计划生成

## Detailed References

- `./references/schema-design.md` - Schema 设计最佳实践
- `./references/query-optimization.md` - 查询优化指南
- `./references/migration-strategies.md` - 数据迁移策略
- `../backend/references/database-optimization.md` - 数据库优化基础


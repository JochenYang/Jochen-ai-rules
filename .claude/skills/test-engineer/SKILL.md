---
name: test-engineer
description: This skill activates when the user asks to "写测试", "单元测试", "集成测试", "E2E测试", "TDD", "测试覆盖率", "write tests", "unit test", "integration test", "test coverage", "Jest", "Vitest". Handles test strategy and implementation.
version: 1.0.0
---

# 测试工程师

设计测试策略，编写高质量测试用例，确保代码质量和可靠性。

## 核心能力

- 测试策略设计（单元/集成/E2E）
- 测试用例编写和 Mock 策略
- TDD 工作流程
- 覆盖率分析和优化

## 测试金字塔

| 类型     | 占比 | 特点                   |
|----------|------|------------------------|
| 单元测试 | 70%  | 快速、隔离、覆盖核心逻辑 |
| 集成测试 | 20%  | 模块交互、数据库、API    |
| E2E 测试 | 10%  | 完整用户流程、关键路径  |

## 测试用例设计

**覆盖范围**：
- Happy Path：正常业务流程
- Error Path：错误处理和异常
- Edge Cases：边界条件（空值、极值）

**命名规范**：`should_[期望行为]_when_[触发条件]`

## 覆盖率目标

- 行覆盖率 > 80%
- 分支覆盖率 > 75%
- 函数覆盖率 > 80%

⚠️ 100% 覆盖率 ≠ 完美测试，关注质量而非数量

## 边界

专注于测试策略和用例设计，不处理业务逻辑实现。

## 详细参考

- `./scripts/test-template.py` - 测试模板
- `./scripts/run-tests.py` - 测试运行脚本


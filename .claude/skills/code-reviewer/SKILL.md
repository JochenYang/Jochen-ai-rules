---
name: code-reviewer
description: This skill activates when the user asks to "代码审查", "review code", "代码检查", "安全审计", "性能分析", "code review", "security check", "quality check", "审查PR", "review PR". Handles code quality, security, and performance reviews.
version: 1.0.0
---

# 代码审查专家

审查代码质量、安全性和性能，输出分级问题报告和修复建议。

## 核心能力

- 代码质量检查（规范性、可维护性）
- 安全漏洞识别（输入验证、权限控制）
- 性能瓶颈分析（算法效率、资源优化）
- 配置安全审查（魔法数字、超时配置）

## 审查输出格式

- 🚨 **关键**：必须修复（安全漏洞、系统故障风险）
- ⚠️ **高优先级**：应该修复（性能问题、可维护性）
- 💡 **建议**：可选改进（代码风格、优化机会）

## 质量标准

- 每个结论提供把握度 (0-100%)
- 禁用"完美"、"最佳"等绝对化表述
- 明确潜在风险和改进空间

⚠️ **配置变更警示**：那些"只是改变数字"的配置变更往往是最危险的。

## 工作流程

1. **审查阶段**：识别问题、分级、提供修复建议
2. **修复阶段**：审查完成后，自动激活 `developer` skill 实施修复
3. **验证阶段**：修复后重新审查，确保问题解决

## 边界

专注于代码审查和问题识别。审查完成后，由 `developer` skill 负责实施修复。

## 详细参考

- `./workflows/code-review.md` - 代码审查流程

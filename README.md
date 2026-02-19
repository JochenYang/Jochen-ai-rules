# Jochen AI Rules

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://claude.com/claude-code)

Personal Claude Code configuration repository with skills, commands, agents, hooks, and rules.

[English](#english) | [中文](#中文)

---

## English

### Overview

Jochen AI Rules is a comprehensive Claude Code plugin that provides:

- **Commands**: Slash commands for common development workflows
- **Agents**: Specialized AI agents for different tasks
- **Skills**: Domain-specific knowledge and best practices
- **Hooks**: Automated quality checks and formatting

### Installation

```bash
# Clone the repository
git clone https://github.com/JochenYang/Jochen-ai-rules.git

# Load as local plugin
claude --plugin-dir ./Jochen-ai-rules
```

Or install from GitHub after publishing:

```bash
/plugin install jochen-ai-rules
```

### Commands

| Command | Description |
|---------|-------------|
| `/plan` | Create implementation plans with risk assessment |
| `/orchestrate` | Orchestrate multi-agent workflows |
| `/commit` | Create conventional commits |
| `/review` | Code review with quality audit |
| `/tdd` | Test-driven development workflow |
| `/branch` | Git worktree management |
| `/build-fix` | Fix build errors |
| `/refactor-clean` | Clean up dead code |
| `/learn` | Extract reusable patterns |

### Agents

| Agent | Description |
|-------|-------------|
| `dev-planner` | Implementation planning specialist |
| `code-implementer` | Production code implementation |
| `tdd-guide` | Test-driven development |
| `code-reviewer` | Quality, security, performance audit |
| `security-reviewer` | Deep OWASP security audit |
| `database-migration` | Schema and data migration |
| `bug-analyzer` | Bug investigation and root cause analysis |
| `story-generator` | User story generation |
| `ui-sketcher` | UI/UX design prototyping |

### Skills

- **Developer**: Full-stack development workflows
- **Database Engineer**: Schema design, query optimization, migrations
- **API Designer**: REST, GraphQL, gRPC design
- **Quality Assurance**: Testing, security auditing
- **Frontend Design**: Production-grade UI creation
- **UI/UX Pro Max**: 50+ design styles, 21 color palettes
- **Remotion Best Practices**: Video creation in React
- **Agent Teams**: Multi-agent collaboration
- **Continuous Learning**: Session observation and pattern extraction

### Hooks

- Auto-format on edit (Prettier)
- Console.log detection and warnings
- Pre-push review
- Session-end audit

### Project Structure

```
.claude/
├── agents/          # AI agent definitions
├── commands/        # Slash commands
├── hooks/          # Hook configurations
├── skills/         # Domain-specific skills
└── rules/          # Coding standards and guidelines
```

---

## 中文

### 简介

Jochen AI Rules 是一个全面的 Claude Code 插件，提供：

- **Commands**: 常用开发工作流的斜杠命令
- **Agents**: 针对不同任务的专用 AI agents
- **Skills**: 领域特定的知识和最佳实践
- **Hooks**: 自动质量检查和格式化

### 安装

```bash
# 克隆仓库
git clone https://github.com/JochenYang/Jochen-ai-rules.git

# 作为本地插件加载
claude --plugin-dir ./Jochen-ai-rules
```

或发布后从 GitHub 安装：

```bash
/plugin install jochen-ai-rules
```

### Commands（命令）

| 命令 | 说明 |
|------|------|
| `/plan` | 创建带风险评估的实施计划 |
| `/orchestrate` | 编排多 agent 工作流 |
| `/commit` | 创建符合规范的提交信息 |
| `/review` | 代码审查和质量审计 |
| `/tdd` | 测试驱动开发工作流 |
| `/branch` | Git Worktree 管理 |
| `/build-fix` | 修复构建错误 |
| `/refactor-clean` | 清理死代码 |
| `/learn` | 提取可复用模式 |

### Agents（智能体）

| Agent | 说明 |
|-------|------|
| `dev-planner` | 实施规划专家 |
| `code-implementer` | 生产级代码实现 |
| `tdd-guide` | 测试驱动开发 |
| `code-reviewer` | 质量、安全、性能审计 |
| `security-reviewer` | 深度 OWASP 安全审计 |
| `database-migration` | 数据库迁移专家 |
| `bug-analyzer` | Bug 调查和根因分析 |
| `story-generator` | 用户故事生成 |
| `ui-sketcher` | UI/UX 设计原型 |

### Skills（技能）

- **Developer**: 全栈开发工作流
- **Database Engineer**: Schema 设计、查询优化、迁移
- **API Designer**: REST、GraphQL、gRPC 设计
- **Quality Assurance**: 测试、安全审计
- **Frontend Design**: 生产级 UI 创建
- **UI/UX Pro Max**: 50+ 设计风格、21 种配色方案
- **Remotion Best Practices**: React 视频创作
- **Agent Teams**: 多 agent 协作
- **Continuous Learning**: 会话观察和模式提取

### Hooks（钩子）

- 编辑时自动格式化（Prettier）
- Console.log 检测和警告
- Push 前审查
- 会话结束审计

### 项目结构

```
.claude/
├── agents/          # AI agent 定义
├── commands/        # 斜杠命令
├── hooks/          # 钩子配置
├── skills/         # 领域特定技能
└── rules/          # 编码规范和指南
```

---

## License

MIT

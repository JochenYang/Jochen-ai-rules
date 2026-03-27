<div align="center">

# **Jochen AI Rules**

<br>

[![Claude Code 插件](https://img.shields.io/badge/Claude%20Code-插件-4A90D9?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![版本](https://img.shields.io/github/v/release/JochenYang/Jochen-ai-rules?style=for-the-badge)](https://github.com/JochenYang/Jochen-ai-rules/releases)
[![许可证](https://img.shields.io/github/license/JochenYang/Jochen-ai-rules?style=for-the-badge)](LICENSE)
[![Star](https://img.shields.io/github/stars/JochenYang/Jochen-ai-rules?style=for-the-badge)](https://github.com/JochenYang/Jochen-ai-rules/stargazers)

<br>

[English](README.md)

</div>

---

## 简介

Jochen AI Rules 是一个全面的 Claude Code 插件，提供：

- **Commands**: 常用开发工作流的斜杠命令
- **Agents**: 针对不同任务的专用 AI agents
- **Skills**: 领域特定的知识和最佳实践
- **Hooks**: 自动质量检查和格式化

### 功能

| 类别     | 数量 |
|----------|------|
| Commands | 9    |
| Agents   | 11   |
| Skills   | 22   |
| 设计风格 | 50+  |
| 配色方案 | 21   |

## 安装

### 方式一：从市场安装（推荐）

```bash
# 添加市场
/plugin marketplace add JochenYang/Jochen-ai-rules

# 安装独立 skills：
/plugin install agent-teams@jochen-ai-rules
/plugin install api-designer@jochen-ai-rules
/plugin install artifacts-builder@jochen-ai-rules
/plugin install claude-audit@jochen-ai-rules
/plugin install database-engineer@jochen-ai-rules
/plugin install developer@jochen-ai-rules
/plugin install devops-engineer@jochen-ai-rules
/plugin install frontend-design@jochen-ai-rules
/plugin install handoff@jochen-ai-rules
/plugin install mcp-builder@jochen-ai-rules
/plugin install miloya-codebase@jochen-ai-rules
/plugin install performance-optimizer@jochen-ai-rules
/plugin install phaser-build@jochen-ai-rules
/plugin install product-manager@jochen-ai-rules
/plugin install quality-assurance@jochen-ai-rules
/plugin install reflect@jochen-ai-rules
/plugin install requirements-interview@jochen-ai-rules
/plugin install skills-audit@jochen-ai-rules
/plugin install tdd-workflow@jochen-ai-rules
/plugin install threejs-builder@jochen-ai-rules
/plugin install ui-ux-pro-max@jochen-ai-rules
/plugin install vercel-deploy@jochen-ai-rules

# 安装独立 agents：
/plugin install agent-bug-analyzer@jochen-ai-rules
/plugin install agent-code-implementer@jochen-ai-rules
/plugin install agent-code-reviewer@jochen-ai-rules
/plugin install agent-database-migration@jochen-ai-rules
/plugin install agent-dev-planner@jochen-ai-rules
/plugin install agent-devops-engineer@jochen-ai-rules
/plugin install agent-performance-optimizer@jochen-ai-rules
/plugin install agent-security-reviewer@jochen-ai-rules
/plugin install agent-story-generator@jochen-ai-rules
/plugin install agent-tdd-guide@jochen-ai-rules
/plugin install agent-ui-sketcher@jochen-ai-rules

# 安装独立 commands：
/plugin install command-branch@jochen-ai-rules
/plugin install command-build-fix@jochen-ai-rules
/plugin install command-commit@jochen-ai-rules
/plugin install command-learn@jochen-ai-rules
/plugin install command-orchestrate@jochen-ai-rules
/plugin install command-plan@jochen-ai-rules
/plugin install command-refactor-clean@jochen-ai-rules
/plugin install command-review@jochen-ai-rules
/plugin install command-tdd@jochen-ai-rules
```

### 方式二：本地开发

```bash
# 克隆仓库
git clone https://github.com/JochenYang/Jochen-ai-rules.git

# 作为本地插件加载
claude --plugin-dir ./Jochen-ai-rules
```

### 方式三：OpenCode 命令包装

OpenCode 支持在 `.opencode/commands/` 下定义项目级 Markdown 命令。
本仓库已提供：

- `.opencode/commands/handoff.md`

在 OpenCode 中打开项目后，可以直接使用：

```bash
/handoff write <topic-or-existing-file>
/handoff read [handoff-file]
```

这个包装层会复用 `handoff` skill 的逻辑，并保持相同的默认行为：

- `write` 未指定已有文件时，在 `repo/progress/handoffs/` 下新建交接文档
- `write` 指定已有 handoff 路径时，更新该文件
- `read` 未指定文件时，读取最新的一份
- `read` 指定文件时，读取对应的 handoff 文档

### 确定性 Handoff 解析脚本

`handoff` skill 现在包含一个跨平台 Python 辅助脚本
`skills/handoff/scripts/handoff.py`，用于把目标文件选择做成确定行为。

```bash
python skills/handoff/scripts/handoff.py write search-migration --project-root /path/to/project
python skills/handoff/scripts/handoff.py read --project-root /path/to/project
```

规则：

- `write` 只有在参数指向一个已存在的 handoff 文件时才会更新
- 否则 `write` 会在 `repo/progress/handoffs/` 下新建一份带时间戳的文档
- `read` 指定文件时读取指定文件
- `read` 未指定文件时读取最新的一份
- 如果 `--project-root` 误指向已安装的 skill 目录，脚本会返回
  `invalid_project_root`，而不是继续猜路径

> 说明：Claude Code 最终会从你的 Claude 配置目录（通常是 `.claude/`）加载这些文件。
> 这个仓库为了便于开发，把 `agents/`、`commands/`、`hooks/`、`rules/`、`skills/` 放在仓库根目录；
> 但文档里仍可能使用 `.claude/...` 路径，因为那是运行时的真实位置。

## 命令 (Commands)

| 命令              | 说明                     |
|-------------------|--------------------------|
| `/plan`           | 创建带风险评估的实施计划 |
| `/orchestrate`    | 编排多 agent 工作流      |
| `/commit`         | 创建符合规范的提交信息   |
| `/review`         | 代码审查和质量审计       |
| `/tdd`            | 测试驱动开发工作流       |
| `/branch`         | Git Worktree 管理        |
| `/build-fix`      | 修复构建错误             |
| `/refactor-clean` | 清理死代码               |
| `/learn`          | 提取可复用模式           |

## 智能体 (Agents)

| Agent                   | 说明                                   |
|-------------------------|----------------------------------------|
| `dev-planner`           | 实施规划专家                           |
| `code-implementer`      | 生产级代码实现                         |
| `tdd-guide`             | 测试驱动开发                           |
| `code-reviewer`         | 质量、安全、性能审计                     |
| `security-reviewer`     | 深度 OWASP 安全审计                    |
| `database-migration`    | 数据库迁移专家                         |
| `bug-analyzer`          | Bug 调查和根因分析                     |
| `story-generator`       | 用户故事生成                           |
| `ui-sketcher`           | UI/UX 设计原型                         |
| `performance-optimizer` | 全栈性能瓶颈识别与优化                 |
| `devops-engineer`       | CI/CD、Docker、Kubernetes 与基础设施管理 |

## 技能 (Skills)

- **Developer**: 全栈开发工作流
- **Database Engineer**: Schema 设计、查询优化、迁移
- **API Designer**: REST、GraphQL、gRPC 设计
- **Quality Assurance**: 测试，安全审计
- **Frontend Design**: 生产级前端实现，覆盖动效、本地媒体资产与转化文案
- **Handoff**: 手动上下文交接工作流，在 reset 前写出可续开发的交接文档，并在新会话中继续读取
- **UI/UX Pro Max**: 50+ 设计风格、21 种配色方案
- **Agent Teams**: 多 agent 协作
- **Three.js Builder**: 3D 网页内容创建
- **Phaser Build**: 2D HTML5 游戏开发
- **MCP Builder**: MCP 服务器开发
- **Reflect**: 会话回顾和学习提取
- **Miloya Codebase**: 项目上下文引擎，用于代码库定向、缓存交接和任务聚焦的代码检索
- **Claude Audit**: 审计 .claude/ 文件，检测冗余指令、冗长表述和可移至 memory 的内容
- **Skills Audit**: 列出所有技能及其行数，检测重复作用域和优化机会
- **Artifacts Builder**: 创建交互式 Claude 构件（图表、UI 原型、工具）
- **DevOps Engineer**: CI/CD 流水线设计、容器化、Kubernetes、监控配置
- **Performance Optimizer**: 全栈性能剖析与优化（DB、后端、前端 Core Web Vitals）
- **Product Manager**: 产品需求、用户故事、路线图规划
- **Requirements Interview**: 通过结构化引导式问答收集需求
- **TDD Workflow**: 测试驱动开发，强制执行 RED-GREEN-REFACTOR 循环
- **Vercel Deploy**: Next.js 部署、环境变量管理、边缘函数
- **Jochen Skill Creator**: 新技能创建的模板与标准规范

### UI/UX 设计能力

- **50+ 设计风格**: 玻璃拟态、黏土拟态、极简主义，粗野主义、新拟态、Bento 栅格、暗色模式、拟物化、扁平化等
- **21 种配色方案**: 适用于各种场景的完整色彩系统
- **50 种字体搭配**: 不同场景的字体组合
- **20 种图表类型**: 数据可视化选项
- **9 种技术栈**: React、Next.js、Vue、Svelte、SwiftUI、React Native、Flutter、Tailwind、shadcn/ui

#### UI 组件

- 按钮、模态框、导航栏、侧边栏、卡片、表格、表单、图表
- 响应式设计支持
- 无障碍设计 (WCAG 2.1 AA 标准)
- 动画和微交互
- 暗色模式支持

## 钩子 (Hooks)

内置两个生产可用的钩子，提供跨平台配置：

- **Self-improvement**：每次会话工具调用 8+ 次后，提示使用 `/learn` 总结模式
- **Prompt Linter**：提示词超过 50 词时，提醒确认目标

### 配置方式

将对应文件中的 `hooks` 部分复制到 Claude 设置文件：

- **Windows**：使用 `hooks/hooks.windows.json` → `%APPDATA%\Claude\settings.json`
- **Linux / macOS**：使用 `hooks/hooks.json` → `~/.claude/settings.json`

**Windows**（`hooks/hooks.windows.json`）：

```json
{
  "hooks": {
    "UserPromptSubmit": [{ "matcher": "*", "hooks": [{ "type": "command", "command": "powershell -File hooks/prompt-linter.ps1" }] }],
    "Stop":            [{ "matcher": "*", "hooks": [{ "type": "command", "command": "powershell -File hooks/self-improvement.ps1" }] }]
  }
}
```

**Linux / macOS**（`hooks/hooks.json`）：

```json
{
  "hooks": {
    "UserPromptSubmit": [{ "matcher": "*", "hooks": [{ "type": "command", "command": "bash hooks/prompt-linter.sh" }] }],
    "Stop":            [{ "matcher": "*", "hooks": [{ "type": "command", "command": "bash hooks/self-improvement.sh" }] }]
  }
}
```

## 项目结构

```
仓库结构（本仓库）：
agents/   commands/   hooks/   skills/   rules/

运行时结构（Claude 配置目录）：
.claude/
├── agents/   # AI agent 定义
├── commands/ # 斜杠命令
├── hooks/    # 钩子配置
├── skills/   # 领域特定技能
└── rules/    # 编码规范和指南
```

---

## 许可证

<p align="center">
  <a href="LICENSE">查看许可证</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules">GitHub</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules/issues">问题反馈</a>
</p>

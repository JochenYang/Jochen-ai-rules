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
| -------- | ---- |
| Commands | 9    |
| Agents   | 9    |
| Skills   | 13+  |
| 设计风格 | 50+  |
| 配色方案 | 21   |

## 安装

### 方式一：从市场安装（推荐）

```bash
# 添加市场
/plugin marketplace add JochenYang/Jochen-ai-rules

# 安装插件
/plugin install jochen-ai-rules
```

### 方式二：本地开发

```bash
# 克隆仓库
git clone https://github.com/JochenYang/Jochen-ai-rules.git

# 作为本地插件加载
claude --plugin-dir ./Jochen-ai-rules
```

## 命令 (Commands)

| 命令              | 说明                     |
| ----------------- | ------------------------ |
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

| Agent                | 说明                 |
| -------------------- | -------------------- |
| `dev-planner`        | 实施规划专家         |
| `code-implementer`   | 生产级代码实现       |
| `tdd-guide`          | 测试驱动开发         |
| `code-reviewer`      | 质量、安全、性能审计 |
| `security-reviewer`  | 深度 OWASP 安全审计  |
| `database-migration` | 数据库迁移专家       |
| `bug-analyzer`       | Bug 调查和根因分析   |
| `story-generator`    | 用户故事生成         |
| `ui-sketcher`        | UI/UX 设计原型       |

## 技能 (Skills)

- **Developer**: 全栈开发工作流
- **Database Engineer**: Schema 设计、查询优化、迁移
- **API Designer**: REST、GraphQL、gRPC 设计
- **Quality Assurance**: 测试，安全审计
- **Frontend Design**: 生产级 UI 创建
- **UI/UX Pro Max**: 50+ 设计风格、21 种配色方案
- **Remotion Best Practices**: React 视频创作
- **Agent Teams**: 多 agent 协作
- **Continuous Learning**: 会话观察和模式提取
- **Three.js Builder**: 3D 网页内容创建
- **Phaser Build**: 2D HTML5 游戏开发
- **MCP Builder**: MCP 服务器开发
- **Reflect**: 会话回顾和学习提取
- **Claude Audit**: 审计 .claude/ 文件，检测冗余指令、冗长表述和可移至 memory 的内容
- **Skills Audit**: 列出所有技能及其行数，检测重复作用域和优化机会

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

- 编辑时自动格式化 (Prettier)
- Console.log 检测和警告
- Push 前审查
- 会话结束审计
- **Self-improvement**: 8+ 次工具调用后提示使用 /learn
- **Prompt Linter**: 提示词 > 50 词时提醒确认目标

## 项目结构

```
.claude/
├── agents/          # AI agent 定义
├── commands/       # 斜杠命令
├── hooks/          # 钩子配置
├── skills/         # 领域特定技能
└── rules/          # 编码规范和指南
```

---

## 许可证

<p align="center">
  <a href="LICENSE">查看许可证</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules">GitHub</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules/issues">问题反馈</a>
</p>

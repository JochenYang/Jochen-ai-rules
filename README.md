<div align="center">

# **Jochen AI Rules**

<br>

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-4A90D9?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![Version](https://img.shields.io/github/v/release/JochenYang/Jochen-ai-rules?style=for-the-badge)](https://github.com/JochenYang/Jochen-ai-rules/releases)
[![License](https://img.shields.io/github/license/JochenYang/Jochen-ai-rules?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/JochenYang/Jochen-ai-rules?style=for-the-badge)](https://github.com/JochenYang/Jochen-ai-rules/stargazers)

<br>

[中文](README.zh-CN.md)

</div>

---

## Overview

Jochen AI Rules is a comprehensive Claude Code plugin that provides:

- **Commands**: Slash commands for common development workflows
- **Agents**: Specialized AI agents for different tasks
- **Skills**: Domain-specific knowledge and best practices
- **Hooks**: Automated quality checks and formatting

### Features

| Category       | Count |
|----------------|-------|
| Commands       | 9     |
| Agents         | 11    |
| Skills         | 21    |
| Design Styles  | 50+   |
| Color Palettes | 21    |

## Installation

### Option 1: From Marketplace (Recommended)

```bash
# Add the marketplace
/plugin marketplace add JochenYang/Jochen-ai-rules

# Install the plugin
/plugin install jochen-ai-rules
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/JochenYang/Jochen-ai-rules.git

# Load as local plugin
claude --plugin-dir ./Jochen-ai-rules
```

> Note: Claude Code ultimately loads these files from your Claude configuration folder (typically under `.claude/`).
> This repository keeps `agents/`, `commands/`, `hooks/`, `rules/`, `skills/` at the repo root for development,
> but documentation may reference `.claude/...` paths because that is the runtime location.

## Commands

| Command           | Description                                      |
|-------------------|--------------------------------------------------|
| `/plan`           | Create implementation plans with risk assessment |
| `/orchestrate`    | Orchestrate multi-agent workflows                |
| `/commit`         | Create conventional commits                      |
| `/review`         | Code review with quality audit                   |
| `/tdd`            | Test-driven development workflow                 |
| `/branch`         | Git worktree management                          |
| `/build-fix`      | Fix build errors                                 |
| `/refactor-clean` | Clean up dead code                               |
| `/learn`          | Extract reusable patterns                        |

## Agents

| Agent                   | Description                                              |
|-------------------------|----------------------------------------------------------|
| `dev-planner`           | Implementation planning specialist                       |
| `code-implementer`      | Production code implementation                           |
| `tdd-guide`             | Test-driven development                                  |
| `code-reviewer`         | Quality, security, performance audit                     |
| `security-reviewer`     | Deep OWASP security audit                                |
| `database-migration`    | Schema and data migration                                |
| `bug-analyzer`          | Bug investigation and root cause analysis                |
| `story-generator`       | User story generation                                    |
| `ui-sketcher`           | UI/UX design prototyping                                 |
| `performance-optimizer` | Performance bottleneck identification across full stack  |
| `devops-engineer`       | CI/CD pipeline, Docker, Kubernetes, infrastructure setup |

## Skills

- **Developer**: Full-stack development workflows
- **Database Engineer**: Schema design, query optimization, migrations
- **API Designer**: REST, GraphQL, gRPC design
- **Quality Assurance**: Testing, security auditing
- **Frontend Design**: Production-grade UI creation
- **UI/UX Pro Max**: 50+ design styles, 21 color palettes
- **Agent Teams**: Multi-agent collaboration
- **Three.js Builder**: 3D web content creation
- **Phaser Build**: 2D HTML5 game development
- **MCP Builder**: MCP server development
- **Reflect**: Session reflection and learning extraction
- **Claude Audit**: Audit .claude/ files for redundant instructions, verbose phrasing, and memory candidates
- **Skills Audit**: List all skills with line counts, find overlapping scopes and optimization opportunities
- **Artifacts Builder**: Create interactive Claude artifacts (charts, UI prototypes, tools)
- **DevOps Engineer**: CI/CD pipeline design, containerization, Kubernetes, monitoring setup
- **Performance Optimizer**: Profiling-first performance analysis across full stack
- **Product Manager**: Product requirements, user stories, roadmap planning
- **Requirements Interview**: Structured requirements gathering through guided interviews
- **TDD Workflow**: Test-driven development with RED-GREEN-REFACTOR cycle enforcement
- **Vercel Deploy**: Next.js deployment, environment variables, edge functions
- **Jochen Skill Creator**: Template and standards for creating new skills

### UI/UX Design Capabilities

- **50+ Design Styles**: Glassmorphism, Claymorphism, Minimalism, Brutalism, Neumorphism, Bento Grid, Dark Mode, Skeuomorphism, Flat Design, and more
- **21 Color Palettes**: Complete color system for various use cases
- **50 Font Pairings**: Typography combinations for different contexts
- **20 Chart Types**: Data visualization options
- **9 Tech Stacks**: React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui

#### UI Components

- Buttons, Modals, Navbars, Sidebars, Cards, Tables, Forms, Charts
- Responsive design support
- Accessibility (WCAG 2.1 AA compliant)
- Animation and micro-interactions
- Dark mode support

## Hooks

Two production-ready hooks are included with platform-specific configurations:

- **Self-improvement**: Prompts `/learn` after 8+ tool calls per session
- **Prompt Linter**: Warns when prompt > 50 words and asks for goal confirmation

### Setup

Copy the `hooks` section from the appropriate file into your Claude settings:

- **Windows**: use `hooks/hooks.windows.json` → `%APPDATA%\Claude\settings.json`
- **Linux / macOS**: use `hooks/hooks.json` → `~/.claude/settings.json`

**Windows** (`hooks/hooks.windows.json`):

```json
{
  "hooks": {
    "UserPromptSubmit": [{ "matcher": "*", "hooks": [{ "type": "command", "command": "powershell -File hooks/prompt-linter.ps1" }] }],
    "Stop":            [{ "matcher": "*", "hooks": [{ "type": "command", "command": "powershell -File hooks/self-improvement.ps1" }] }]
  }
}
```

**Linux / macOS** (`hooks/hooks.json`):

```json
{
  "hooks": {
    "UserPromptSubmit": [{ "matcher": "*", "hooks": [{ "type": "command", "command": "bash hooks/prompt-linter.sh" }] }],
    "Stop":            [{ "matcher": "*", "hooks": [{ "type": "command", "command": "bash hooks/self-improvement.sh" }] }]
  }
}
```

## Project Structure

```
Repo layout (this repository):
agents/   commands/   hooks/   skills/   rules/

Runtime layout (Claude config):
.claude/
├── agents/   # AI agent definitions
├── commands/ # Slash commands
├── hooks/    # Hook configurations
├── skills/   # Domain-specific skills
└── rules/    # Coding standards and guidelines
```

---

## License

<p align="center">
  <a href="LICENSE">View License</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules">GitHub</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules/issues">Issues</a>
</p>

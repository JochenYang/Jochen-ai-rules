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
| -------------- | ----- |
| Commands       | 9     |
| Agents         | 9     |
| Skills         | 13+   |
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

## Commands

| Command           | Description                                      |
| ----------------- | ------------------------------------------------ |
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

| Agent                | Description                               |
| -------------------- | ----------------------------------------- |
| `dev-planner`        | Implementation planning specialist        |
| `code-implementer`   | Production code implementation            |
| `tdd-guide`          | Test-driven development                   |
| `code-reviewer`      | Quality, security, performance audit      |
| `security-reviewer`  | Deep OWASP security audit                 |
| `database-migration` | Schema and data migration                 |
| `bug-analyzer`       | Bug investigation and root cause analysis |
| `story-generator`    | User story generation                     |
| `ui-sketcher`        | UI/UX design prototyping                  |

## Skills

- **Developer**: Full-stack development workflows
- **Database Engineer**: Schema design, query optimization, migrations
- **API Designer**: REST, GraphQL, gRPC design
- **Quality Assurance**: Testing, security auditing
- **Frontend Design**: Production-grade UI creation
- **UI/UX Pro Max**: 50+ design styles, 21 color palettes
- **Remotion Best Practices**: Video creation in React
- **Agent Teams**: Multi-agent collaboration
- **Continuous Learning**: Session observation and pattern extraction
- **Three.js Builder**: 3D web content creation
- **Phaser Build**: 2D HTML5 game development
- **MCP Builder**: MCP server development
- **Reflect**: Session reflection and learning extraction
- **Claude Audit**: Audit .claude/ files for redundant instructions, verbose phrasing, and memory candidates
- **Skills Audit**: List all skills with line counts, find overlapping scopes and optimization opportunities

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

- Auto-format on edit (Prettier)
- Console.log detection and warnings
- Pre-push review
- Session-end audit
- **Self-improvement**: Prompts `/learn` after 8+ tool calls
- **Prompt Linter**: Warns when prompt > 50 words

### Advanced Hooks (Optional)

These hooks require manual configuration in `settings.json`:

```json
"UserPromptSubmit": [
  {
    "matcher": "*",
    "hooks": [
      { "type": "command", "command": "powershell -File hooks/self-improvement.ps1" }
    ]
  },
  {
    "matcher": "*",
    "hooks": [
      { "type": "command", "command": "powershell -File hooks/prompt-linter.ps1" }
    ]
  }
]
```

## Project Structure

```
.claude/
├── agents/          # AI agent definitions
├── commands/        # Slash commands
├── hooks/          # Hook configurations
├── skills/         # Domain-specific skills
└── rules/          # Coding standards and guidelines
```

---

## License

<p align="center">
  <a href="LICENSE">View License</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules">GitHub</a> •
  <a href="https://github.com/JochenYang/Jochen-ai-rules/issues">Issues</a>
</p>

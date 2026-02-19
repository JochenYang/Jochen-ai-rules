# Jochen AI Rules

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://claude.com/claude-code)

Personal Claude Code configuration repository with skills, commands, agents, hooks, and rules.

## Overview

Jochen AI Rules is a comprehensive Claude Code plugin that provides:

- **Commands**: Slash commands for common development workflows
- **Agents**: Specialized AI agents for different tasks
- **Skills**: Domain-specific knowledge and best practices
- **Hooks**: Automated quality checks and formatting

## Installation

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

## Commands

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

## Agents

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

## Project Structure

```
.claude/
├── agents/          # AI agent definitions
├── commands/        # Slash commands
├── hooks/          # Hook configurations
├── skills/         # Domain-specific skills
└── rules/          # Coding standards and guidelines
```

## License

MIT

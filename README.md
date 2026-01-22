# Jochen AI Rules

Personal Claude Code configuration repository with skills, commands, agents, hooks, and rules.

## Structure

```
.claude/
├── agents/          # Specialized agents (bug-analyzer, code-reviewer, etc.)
├── commands/        # Slash commands (build-fix, commit, plan, tdd, etc.)
├── hooks/           # Hook system (PreToolUse, PostToolUse, Stop, SessionStart)
├── skills/          # Skill definitions (developer, frontend-design, ui-ux-pro-max, etc.)
└── rules/           # Coding standards, git workflow, security, testing guidelines

System Prompt/       # AI Protocol documentation (Chinese & English)
```

## Features

- **Skills**: Developer, Database Engineer, API Designer, Quality Assurance, Frontend Design, UI/UX Pro Max, Remotion Best Practices, and more
- **Commands**: Build Fix, Code Reviewer, Commit, Plan, Refactor Clean, TDD
- **Agents**: Bug Analyzer, Code Reviewer, Dev Planner, Story Generator, TDD Guide, UI Sketcher
- **Hooks**: Pre-tool validation, Post-tool checks, Session start/end, Console.log audit, Auto-format
- **Rules**: Coding standards, immutability, error handling, git workflow, security, testing

## Usage

This repository is designed to be used with [Claude Code](https://claude.com/claude-code). Clone it to your machine and configure Claude Code to use this configuration.

## License

MIT

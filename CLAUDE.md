# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Overview

This is a **Claude Code plugin** - a collection of production-ready agents, skills, hooks, commands, and rules for AI-assisted development. The project provides battle-tested workflows for software development using Claude Code.

## Architecture

The project is organized into several core components:

- **agents/** - Specialized subagents for delegation (dev-planner, code-reviewer, tdd-guide, etc.)
- **skills/** - Workflow definitions and domain knowledge (coding standards, patterns, testing)
- **commands/** - Slash commands invoked by users (/tdd, /plan, /branch, etc.)
- **hooks/** - Trigger-based automations (prompt linting, session self-improvement)
- **rules/** - Always-follow guidelines (security, coding style, testing requirements)

## Key Commands

- `/branch` - Git worktree management
- `/commit` - Create well-formatted commits
- `/plan` - Implementation planning
- `/tdd` - Test-driven development workflow
- `/code-review` - Quality review
- `/build-fix` - Fix build errors
- `/refactor-clean` - Clean up dead code
- `/orchestrate` - Orchestrate multi-agent workflows

## Key Skills

- **developer** - Full-stack development
- **ui-ux-pro-max** - UI/UX design intelligence
- **mcp-builder** - MCP server development
- **threejs-builder** - Three.js web apps
- **quality-assurance** - Code review and testing
- **reflect** - Session reflection and learning
- **claude-audit** - Audit .claude/ files
- **skills-audit** - Audit skills collection

## Development Notes

- Agent format: Markdown with YAML frontmatter (name, description, tools, model)
- Skill format: Markdown with clear sections for when to use, how it works, examples
- Hook format: JSON with matcher conditions and command hooks
- Rule format: Markdown with clear guidelines

## File Naming

- Agents: lowercase with hyphens (e.g., `dev-planner.md`)
- Skills: folder with `SKILL.md` inside
- Commands: lowercase with hyphens (e.g., `branch.md`)

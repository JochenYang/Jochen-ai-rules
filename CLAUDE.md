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

- `/plan` - Approval-gated implementation planning
- `/orchestrate` - Sequential multi-agent workflow with repair loops
- `/tdd` - Test-driven development workflow (RED-GREEN-REFACTOR-VERIFY)
- `/review` - Code review via `code-reviewer` agent (returns `Recommendation: SHIP|NEEDS WORK|BLOCKED`)
- `/commit` - Create conventional commit messages with confirmation gate
- `/branch` - Git worktree branch management
- `/build-fix` - Fix build/compile errors
- `/refactor-clean` - Clean up dead code

## Key Skills

Engineering core (most-used):

- **developer** - Full-stack development workflows
- **tdd-workflow** - RED-GREEN-REFACTOR cycle enforcement
- **quality-assurance** - Code review, testing, security audit standards
- **handoff** - Manual session handoff for long-running work
- **context-codebase** - Project context engine for repo orientation
- **reflect** - Session reflection and lesson extraction

Specialist domains:

- **api-designer** - REST/GraphQL/gRPC design
- **database-engineer** - Schema design, query optimization, migrations
- **performance-optimizer** - Bottleneck identification across full stack
- **devops-engineer** - CI/CD, containers, Kubernetes, monitoring
- **vercel-deploy** - Next.js deployment, env vars, edge functions
- **mcp-builder** - MCP server development

Product & design:

- **product-manager** - PRD, user stories, roadmap
- **requirements-interview** - Structured requirement Q&A
- **frontend-design** - Production-grade frontend with motion + assets
- **ui-ux-pro-max** - 50+ design styles, 21 color systems
- **artifacts-builder** - Interactive React/HTML artifacts
- **threejs-builder** - 3D web content
- **phaser-build** - 2D HTML5 games

Meta & maintenance:

- **agent-teams** - Parallel multi-agent collaboration
- **claude-audit** - Audit `.claude/` files for redundancy
- **skills-audit** - Inventory and review skill collection

> Total: 8 commands · 11 agents · 22 skills. Counts auto-synced via
> `scripts/sync-doc-counts.js`; do not edit manually after running the sync.

## Development Notes

- Agent format: Markdown with YAML frontmatter (name, description, tools, model)
- Skill format: Markdown with clear sections for when to use, how it works, examples
- Hook format: JSON with matcher conditions and command hooks
- Rule format: Markdown with clear guidelines

## File Naming

- Agents: lowercase with hyphens (e.g., `dev-planner.md`)
- Skills: folder with `SKILL.md` inside
- Commands: lowercase with hyphens (e.g., `branch.md`)

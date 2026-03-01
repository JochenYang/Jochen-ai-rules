---
name: mcp-builder
description: MCP server development for AI agents. Designs tool schemas, implements Python/TypeScript servers, creates evaluation tests. Use when user asks to build MCP server, create tool integration, or develop Claude plugins. Supports GitHub/Notion/Slack integrations.
---

# MCP Server Development Tool

Build high-quality Model Context Protocol servers to provide external tool capabilities for AI agents.

## Core Capabilities

- MCP protocol understanding and server architecture design
- Python/TypeScript SDK implementation
- Tool schema design for AI agents
- Evaluation test creation and validation

## Tech Stack

| Language   | SDK                | Validation  | Runtime     |
|------------|--------------------|-------------|-------------|
| Python     | MCP Python SDK     | Pydantic v2 | asyncio     |
| TypeScript | MCP TypeScript SDK | Zod         | Node.js 18+ |

## Executable Tools

The following scripts can be run directly without reading source code:

- `scripts/evaluation.py` - Run MCP server evaluation tests
- `scripts/connections.py` - Test server connection status

## Design Principles

1. **Workflow-Oriented**: Build complete task tools, not simple API wrappers
2. **Optimize Context**: Return high-signal information, avoid data dumping
3. **Actionable Errors**: Error messages guide agents to correct usage
4. **Evaluation-Driven**: Create evaluation scenarios early, iterate based on agent feedback

## Boundaries

Focus on MCP server development and tool design, not third-party API development or client integration.

## Detailed References

- `./workflows/mcp-development.md` - Complete development workflow
- `./guides/mcp_best_practices.md` - MCP best practices
- `./guides/python_mcp_server.md` - Python implementation guide
- `./guides/node_mcp_server.md` - TypeScript implementation guide
- `./guides/evaluation.md` - Evaluation creation guide

---
name: subagent-boundary
description: Global subagent orchestration boundary and nesting-safety rules for OpenCode agents.
---

# Subagent Boundary

**RULE TYPE**: Mandatory orchestration and child-safety boundary.

## Scope

Applies to all OpenCode agents and subagents, not only Forge.

## Core Rule

Forge or the active primary agent owns orchestration. Ordinary subagents execute one bounded task and must not spawn additional subagents unless an agent file explicitly grants `task: allow` and documents why fanout is required.

## Default Boundary

- Default maximum depth is one delegation hop: primary agent → subagent.
- Subagent → subagent delegation is denied by default.
- New subagent definitions must include an explicit `task` permission.
- If `task: allow` is ever added to a subagent, the agent prompt must define scope, depth, budget, and stop conditions.
- Child prompts must not inherit parent-only orchestration instructions as executable authority; they should receive only the task goal, scope, context, constraints, and output contract.

## Allowed Exceptions

- A dedicated fanout/research coordinator may be created for read-only parallel discovery if it has explicit owner approval and a bounded depth/budget.
- Mission verification agents may invoke only the tools required by their verification contract and must not create implementation subtasks.

## Dispatch Requirements

Every subagent dispatch should include:

1. Goal - exact outcome for the child task.
2. Scope - files, modules, or systems in bounds.
3. Non-goals - what the child must not change or decide.
4. Context - enough evidence to avoid rediscovery.
5. Verification expectation - tests, commands, or file evidence required.
6. Output contract - status, evidence, risks, next recommendation.

## Red Flags

- A child asks to spawn another child to understand its own task.
- A reviewer delegates review instead of reporting findings.
- An implementer starts a planner or researcher without explicit permission.
- Parent prompts include old tool logs or orchestration history as instructions for the child.

When any red flag appears, stop fanout and return `BLOCKED` or ask the owner through the configured decision protocol.

---
name: coding-standards
description: Mandatory engineering standards for code quality.
---

# Coding Standards

**RULE TYPE**: Mandatory engineering standards.

## Core Rules

1. Minimal change: modify only what is required by the goal.
2. Readability first: clear naming, short functions, shallow nesting.
3. Comments explain **why**, not obvious **what**.
4. Treat inputs and shared state as immutable.
5. Avoid `any` unless an explicit boundary requires it.
6. Validate all external inputs before use.
7. Handle errors with actionable context.

## Immutability Rule

- Never mutate function arguments.
- Never mutate shared state directly.
- Local mutation is allowed only on fresh local copies with clear justification.

## Error Handling Rule

- Wrap failure-prone operations.
- Preserve original error context in logs.
- Return/throw stable, user-safe error messages.

## Type & Validation Rule

- Prefer strict types and explicit interfaces.
- Add runtime validation for request payloads, env vars, and external data.

## Size Guidelines

- Function: <= 50 lines preferred.
- File: 200-400 lines preferred, <= 800 hard limit.
- Nesting depth: <= 4.

## Quality Gate Before Done

- [ ] Naming and flow are readable
- [ ] Error paths are handled
- [ ] No hardcoded secrets
- [ ] No unsafe shared-state mutation
- [ ] Input validation is present
- [ ] No leftover debug logs
- [ ] Tests cover changed behavior

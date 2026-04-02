---
name: testing
description: Mandatory testing and verification standards.
---

# Testing Guidelines

**RULE TYPE**: Mandatory testing and verification standards.

## Done Definition

Never mark a task complete without proof.

Required evidence:
- Test results summary
- Behavior delta (before vs after) for bugfixes/features
- Relevant log/output snippet when applicable

## Coverage Policy

- Baseline target: >= 80% overall
- High-risk modules target: 100%
  - Authentication/authorization
  - Security-critical paths
  - Core business logic
  - Financial calculations

## Test Strategy

1. Unit tests for functions/components/utilities
2. Integration tests for API, DB, and external dependencies
3. E2E tests for critical user flows

## Bugfix Rule (TDD-First)

1. Add a failing test that reproduces the bug (RED)
2. Apply minimal fix to pass test (GREEN)
3. Refactor while preserving passing tests (REFACTOR)

If the host does not expose a dedicated `tdd-guide` agent, the bugfix workflow
must still preserve the same lifecycle explicitly:

1. Analyze and isolate the defect
2. Reproduce it with a failing test or equivalent failing verification proof
3. Apply the minimal fix
4. Re-run verification and review the result

If a reliable failing test cannot be produced, the task must be escalated with
the missing proof called out explicitly before closing.

## Test Quality

- Use clear behavior-driven test names.
- Use AAA structure (Arrange, Act, Assert).
- Avoid vague names like `works` or `test1`.

## Execution Checklist (Mandatory)

- [ ] Bugfix includes a failing reproduction test first
- [ ] Changed behavior is covered by unit/integration/E2E at suitable level
- [ ] Test suite results are attached to delivery summary
- [ ] High-risk paths receive strengthened coverage
- [ ] Flaky tests are identified with mitigation notes

## Escalation Rules

Escalate before closing task when:

1. key tests cannot run in current environment
2. regression risk exists but reproducible evidence is incomplete
3. required coverage target is unmet for high-risk modules

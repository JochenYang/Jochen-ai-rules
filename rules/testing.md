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

## Test Quality

- Use clear behavior-driven test names.
- Use AAA structure (Arrange, Act, Assert).
- Avoid vague names like `works` or `test1`.

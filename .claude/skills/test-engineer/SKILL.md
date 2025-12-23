---
name: test-engineer
description: Test strategy design and implementation for unit, integration, and E2E testing. Handles TDD workflows, mock strategies, and coverage analysis using Jest, Vitest, pytest, or JUnit.
license: MIT
compatibility: Requires testing framework installation (Jest/Vitest/pytest/JUnit). Works with any modern development environment.
allowed-tools: Read Write Bash
---

# Test Engineer

Design test strategies and write high-quality test cases to ensure code quality and reliability.

## Core Capabilities

- Test strategy design (unit/integration/E2E)
- Test case writing and mock strategies
- TDD workflow
- Coverage analysis and optimization

## Test Pyramid

| Type              | Ratio | Characteristics                     |
|-------------------|-------|-------------------------------------|
| Unit Tests        | 70%   | Fast, isolated, cover core logic    |
| Integration Tests | 20%   | Module interaction, database, API   |
| E2E Tests         | 10%   | Complete user flows, critical paths |

## Test Case Design

**Coverage Scope**:

- Happy Path: Normal business flows
- Error Path: Error handling and exceptions
- Edge Cases: Boundary conditions (null, extreme values)

**Naming Convention**: `should_[expected_behavior]_when_[trigger_condition]`

## Coverage Targets

- Line coverage > 80%
- Branch coverage > 75%
- Function coverage > 80%

⚠️ 100% coverage ≠ perfect testing, focus on quality over quantity

## Boundaries

Focus on test strategy and case design, not business logic implementation.

## Detailed References

- `./scripts/test-template.py` - Test template
- `./scripts/run-tests.py` - Test execution script

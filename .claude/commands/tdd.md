---
description: Enforce test-driven development workflow. Write failing tests FIRST, then implement minimal code to pass.
---

# TDD Command

Enforce test-driven development methodology.

## TDD Cycle

```
RED → GREEN → REFACTOR → REPEAT

RED:      Write a failing test (code doesn't exist yet)
GREEN:    Write minimal code to pass the test
REFACTOR: Improve code while keeping tests green
```

## Workflow

1. **Define interfaces** - Define types/interfaces first
2. **Write failing tests** - Tests that FAIL (code doesn't exist)
3. **Implement minimal code** - Just enough to make tests pass
4. **Refactor** - Improve code while keeping tests green
5. **Verify coverage** - Ensure 80%+ test coverage

## Usage

```
/tdd Implement a user authentication function with JWT tokens
```

## What This Does

1. Parse the feature request
2. Define TypeScript interfaces/types first
3. Write failing unit tests (RED phase)
4. Run tests to verify they fail
5. Implement minimal code (GREEN phase)
6. Run tests to verify they pass
7. Refactor for clarity and best practices
8. Check test coverage (target: 80%+)

## Best Practices

- Write tests FIRST, before implementation
- Each test should test one behavior
- Use descriptive test names
- Aim for 80%+ coverage
- Test edge cases and error scenarios

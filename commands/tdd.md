---
description: Enforce test-driven development workflow. Write failing tests FIRST, then implement minimal code to pass. Invokes the tdd-guide agent.
---

# TDD Command

Enforce test-driven development methodology using the tdd-guide agent.

## Usage

```
/tdd Implement a user authentication function with JWT tokens
/tdd Add password reset functionality
/tdd Create a shopping cart with item management
```

## What This Does

This command invokes the **tdd-guide** agent (`.claude/agents/tdd-guide.md`) to enforce the RED-GREEN-REFACTOR cycle:

```
RED → GREEN → REFACTOR → REPEAT

RED:      Write a failing test (code doesn't exist yet)
GREEN:    Write minimal code to pass the test
REFACTOR: Improve code while keeping tests green
```

## TDD Workflow

1. **Define interfaces** - Define types/interfaces first
2. **Write failing tests** - Tests that FAIL (code doesn't exist)
3. **Run tests** - Verify they fail (RED phase)
4. **Implement minimal code** - Just enough to make tests pass
5. **Run tests** - Verify they pass (GREEN phase)
6. **Refactor** - Improve code while keeping tests green
7. **Verify coverage** - Ensure 80%+ test coverage

## Test Structure (AAA Pattern)

```typescript
describe("Feature", () => {
  it("should behave correctly", () => {
    // Arrange: Set up initial state
    const input = setupTestData();
    
    // Act: Execute the function
    const result = functionUnderTest(input);
    
    // Assert: Verify the outcome
    expect(result).toBe(expectedValue);
  });
});
```

## Coverage Requirements

- **Minimum**: 80% code coverage
- **Happy path**: Standard success scenarios
- **Edge cases**: Empty inputs, null/undefined, boundary values
- **Error handling**: Network failures, invalid formats, exceptions

## Best Practices

- Write tests FIRST, before implementation
- Each test should test one behavior
- Use descriptive test names
- Test edge cases and error scenarios
- Keep tests independent and isolated

## Related Commands

- `/plan` - Create implementation plan before TDD
- `/review` - Review code after TDD implementation
- `/orchestrate feature-tdd` - Full TDD workflow: plan → tdd → review

## Related Agent

This command invokes: `.claude/agents/tdd-guide.md`

## Related Skills

- `.claude/skills/tdd-workflow/` - TDD best practices and patterns

---
name: tdd-workflow
description: Standardized Test-Driven Development (TDD) cycle (RED-GREEN-REFACTOR-VERIFY). Use this skill to ensure code quality, high coverage, and regression prevention.
---

# TDD Workflow Skill

This skill standardizes the Test-Driven Development process to achieve high code quality and maintainability.

## The TDD Cycle

Follow these 4 steps strictly for every new feature or bug fix:

### 1. RED: Write a Failing Test

- **Action**: Create a new test file or add a case to an existing one.
- **Requirement**: The test must fail (showing that the feature is missing or the bug is present).
- **Goal**: Define the expected behavior before writing implementation code.

### 2. GREEN: Make it Pass

- **Action**: Write the minimal implementation code necessary to make the test pass.
- **Requirement**: Don't worry about code elegance yet. Correctness is the only priority.
- **Goal**: Confirm the solution works as intended.

### 3. REFACTOR: Clean Up

- **Action**: Optimize implementation and test code while ensuring tests remain green.
- **Requirement**: Remove duplication, improve naming, optimize performance, and follow project standards.
- **Goal**: Ensure the code is maintainable and efficient.

### 4. VERIFY: Final Validation

- **Action**: Run the full test suite and check coverage.
- **Requirement**:
  - Ensure all tests (not just the new ones) pass.
  - Target coverage: **>80%** for the new/modified component.
  - Verify edge cases (null values, network failures, out-of-bounds, etc.).

## Best Practices

### Test First, Always

Never write implementation code before its corresponding test. If you find yourself implementing logic first, stop and write a test that covers it.

### One Test at a Time

Don't write multiple tests at once. Follow the cycle: one test → implementation → refactor → next test.

### Keep Tests Simple

Tests should be easy to read and understand. Use the **Arrange-Act-Assert** pattern:

- **Arrange**: Set up the initial state and dependencies.
- **Act**: Invoke the function or method being tested.
- **Assert**: Verify the output or state change.

### Test Behavior, Not Implementation

Focus on _what_ the code does, not _how_ it does it. This makes your tests more resilient to internal refactoring.

## Common Pitfalls

- **Skipping RED**: Writing a test that accidentally passes (e.g., because it doesn't assert anything) provides no value.
- **The "Big Bang" implementation**: Writing too much code in the GREEN phase. Keep it minimal.
- **Ignoring REFACTOR**: Leaving "quick and dirty" code in the codebase after tests pass.
- **Incomplete Mocks**: Using real dependencies (databases, APIs) in unit tests, making them slow and flaky.

## Integration with other Agents

- **dev-planner**: Provides the feature breakdown that informs which tests to write.
- **code-reviewer**: Verifies that the TDD process was followed and that tests are high-quality.
- **bug-analyzer**: Uses tests to reproduce bugs before implementing fixes.

## Helper Scripts

- `scripts/run-tests.sh` - Run the test suite and generate coverage report.
- `scripts/init-test.sh` - Scaffold a new test file based on project templates.

## Mastery Checklist

- [ ] Does every new feature have a failing test first?
- [ ] Is implementation minimal in the GREEN phase?
- [ ] Was the code refactored and linted after passing?
- [ ] Is test coverage >80% for the modified areas?
- [ ] Are all tests passing after the final implementation?

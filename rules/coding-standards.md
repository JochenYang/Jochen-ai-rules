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

## Anti-Rationalization Pattern

This pattern prevents common rationalization failures where models skip verification steps.

### Pre-Execution Traps

When planning or implementing, you may feel the urge to skip these checks:

| Urge                      | Reality                               | Correct Action            |
|---------------------------|---------------------------------------|---------------------------|
| "The code looks right"    | Reading ≠ verification. Run it.       | Execute and verify output |
| "Tests already passed"    | Trust nothing. Verify independently.  | Run tests yourself        |
| "The logic is simple"     | Prove it with tests.                  | Write verification tests  |
| "I already read the file" | Files change. Read the current state. | Verify before editing     |
| "It worked before"        | Dependencies may have changed.        | Retest the affected flow  |
| "No errors in output"     | Check exit code and side effects.     | Verify full completion    |

### Decision Traps

When making decisions, question these assumptions:

| Assumption                   | Counter-Question                   |
|------------------------------|------------------------------------|
| "This is the right approach" | What would make this wrong?        |
| "No breaking changes"        | Did you verify all callers?        |
| "Performance is fine"        | Did you measure it?                |
| "It's tested"                | Is coverage >80% on changed paths? |
| "Edge cases are handled"     | Did you enumerate them?            |

### Remember

**When you feel like skipping a verification step, that's exactly when you should do it.**

Skip-proof checklist:
- [ ] Did I run the code, not just read it?
- [ ] Did I verify the test results myself?
- [ ] Did I check for side effects?
- [ ] Did I confirm exit codes?
- [ ] Did I measure performance when it matters?

### How to Apply

Reference this pattern in Skill execution when:
- Starting a new implementation phase
- Reviewing someone else's work
- Declaring a task complete
- Skipping a verification step feels "obvious"

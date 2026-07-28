---
description: Remove dead code and improve code organization with a scoped cleanup pass. Can invoke the review flow when changes need additional quality verification.
argument-hint: "[scope]"
---

# Refactor Clean Command

Clean up dead code and improve code organization.

## Usage

```
/refactor-clean
/refactor-clean Remove unused utilities in lib/
/refactor-clean Clean up deprecated API usage
```

## What This Does

1. **Identify dead code** - Find unused functions, variables, imports
2. **Find unused files** - Detect orphaned files not imported anywhere
3. **Check deprecated APIs** - Find usage of deprecated patterns
4. **Suggest improvements** - Identify code smells and refactoring opportunities
5. **Implement safe changes** - Remove confirmed dead code

**After cleanup**, this command may invoke the **code-reviewer** agent (`.claude/agents/code-reviewer.md`) to verify the changes are safe.

## Dead Code Types

| Type             | Detection                   |
|------------------|-----------------------------|
| Unused functions | No calls, no exports used   |
| Unused variables | Defined but never used      |
| Unused imports   | Import exists, nothing used |
| Unreachable code | Code after return/throw     |
| Dead branches    | if(false) { ... }           |
| Orphaned files   | No imports from anywhere    |

## Safety Rules

- **DO** remove code that is confirmed unused
- **DO** verify tests still pass after removal
- **DON'T** remove code that might be used via reflection
- **DON'T** remove code that might be used in other projects
- **DON'T** remove code without checking test coverage

## Best Practices

- Run tests after each removal
- Commit removals separately from new code
- Document removed code in commit message
- Keep deprecated code marked with @deprecated

## Final Output Format (MANDATORY)

```markdown
# Refactor Cleanup Report

## Summary
- Scope:
- Cleanup strategy:

## Removed / Simplified Items
1. file/path - [what removed]
2. file/path - [what simplified]

## Safety Verification
- import/build checks:
- tests:
- behavior regression check:

## Not Removed (With Reason)
- item:
- reason:

## Risks
- residual risk + mitigation:
```

## Related Commands

- `/review` - Review refactoring changes
- `/tdd` - Add tests to verify refactoring didn't break functionality
- `/orchestrate refactor` - Full workflow: plan → refactor → review

## Related Agents

- `.claude/agents/code-reviewer.md` - For safety verification
- `.claude/agents/dev-planner.md` - For planning large refactors

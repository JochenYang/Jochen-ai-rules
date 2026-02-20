---
description: Expert code review for quality, security, and maintainability. Invokes the code-reviewer agent.
---

# Review Command

Perform comprehensive code review using the code-reviewer agent.

## Usage

```
/review
/review Check the auth module changes
/review Review security in payment flow
```

## What This Does

This command invokes the **code-reviewer** agent (`.claude/agents/code-reviewer.md`) to:

1. **Analyze recent changes** - Run git diff to see modifications
2. **Security audit** - Check for vulnerabilities and exposed secrets
3. **Quality check** - Verify code readability and maintainability
4. **Performance review** - Identify potential bottlenecks
5. **Provide feedback** - Organized by priority (Critical/Warning/Suggestion)

## Review Checklist

The code-reviewer agent checks:

- ✓ Code is simple and readable
- ✓ Functions and variables are well-named
- ✓ No duplicated code
- ✓ Proper error handling
- ✓ No exposed secrets or API keys
- ✓ Input validation implemented
- ✓ Good test coverage
- ✓ Performance considerations addressed

## Output Format

```markdown
# Code Review Report

## Summary
[Pass / Request Changes / Block]

## Critical Issues (Must Fix)
1. **[Security/Bug]** [Description] (File: line)
   - Recommendation: [Fix suggestion]

## Improvements (Should Fix)
1. **[Performance/Style]** [Description] (File: line)
   - Recommendation: [Fix suggestion]

## Nitpicks (Optional)
- [Small style suggestions]

## Final Verdict
[Clear statement on whether code is ready to merge]
```

## When to Use

- Before merging pull requests
- After implementing new features
- When refactoring existing code
- Before production deployments

## Related Commands

- `/plan` - Create implementation plan before coding
- `/tdd` - Test-driven development workflow
- `/orchestrate feature` - Full workflow: plan → implement → review

## Related Agent

This command invokes: `.claude/agents/code-reviewer.md`

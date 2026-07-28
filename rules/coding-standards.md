---
name: coding-standards
description: Mandatory engineering standards for code quality.
---

# Coding Standards

**RULE TYPE**: Mandatory engineering standards.

## Core Rules

1. **Correct minimal change**: change only what the goal requires; prefer the **shortest correct** implementation. Not a license for hacks, missing validation, or wrong stack choices; not a license for over-engineering, extra layers, or premature abstraction. Correct and maintainable first; then simple and small.
2. Readability first: clear naming, short functions, shallow nesting.
3. Comments explain design intent, constraints, or non-obvious exceptions; do not restate what clear code already says or record task history. Comment language follows project conventions; docs and user-facing text follow the target audience and localization strategy.
4. Avoid mutating inputs or shared state unless ownership, compatibility impact, and concurrency implications are explicit.
5. Avoid `any` unless an explicit boundary requires it.
6. Validate all external inputs before use.
7. Handle errors with actionable context.
8. No leftover debug logs, temp files, unrelated edits, or hardcoded secrets/paths.

## State and API Change Rule

- Prefer immutable inputs and local copies.
- Do not change public function contracts or mutate shared state without checking callers, ownership, and concurrent access.
- Local mutation is allowed for newly created local objects when it improves clarity.

## Error Handling Rule

- Wrap failure-prone operations.
- Preserve original error context in logs.
- Return/throw stable, user-safe error messages.

## Type & Validation Rule

- Prefer strict types and explicit interfaces.
- Add runtime validation for request payloads, env vars, and external data.

## Size Guidelines

- **Code files**: Function <= 50 lines and file 200-400 lines are review signals, not mechanical limits. Investigate files above 800 lines unless generated, vendored, or required by an established framework convention. Nesting depth: <= 4 where practical.

## Quality Gate

- Naming and flow are readable; error paths are handled.
- No hardcoded secrets; input validation is present.
- Tests cover changed behavior; no leftover debug logs.

## Testing Norms

- Never mark a task complete without proof (test results, behavior delta, or log snippet).
- Bugfix: reproduce with failing test first, apply a **correct minimal** fix (short and right, not a hack), then refactor only if needed.
- Cover changed behavior and the failure paths that define correctness. For high-risk modules (auth, security, business logic), test critical properties and boundary failures. Coverage is a supporting signal, never a substitute for a relevant assertion.
- If a project has no runnable tests, use the strongest available evidence: typecheck, lint, smoke command, diff review, or behavior log.
- Use AAA structure; behavior-driven test names.

## Testing Escalation Rules

Escalate before closing the task when:

1. Key tests cannot run in the current environment.
2. Regression risk exists but reproducible evidence is incomplete.
3. Required coverage is unmet for high-risk modules.

## Anti-Rationalization Pattern

This pattern prevents rationalization failures where models skip verification steps.

**Pre-Execution Traps — when you feel like skipping, do it instead:**
- "The code looks right" → Execute and verify, don't just read
- "Tests already passed" → Run them yourself, trust nothing
- "The logic is simple" → Prove it with tests
- "I already read the file" → Files change, re-read before editing
- "It worked before" → Dependencies change, retest
- "No errors in output" → Check exit codes and side effects

**Decision Traps — question every assumption:**
- "This is the right approach" → What would make this wrong?
- "No breaking changes" → Did you verify all callers?
- "Performance is fine" → Did you measure it?
- "It's tested" → Can this check fail while the user-visible claim is still false?
- "Edge cases are handled" → Did you enumerate them?

**Skip-proof checklist:**
- [ ] Did I run the code, not just read it?
- [ ] Did I verify the test results myself?
- [ ] Did I check for side effects, confirm exit codes?
- [ ] Did I measure performance when it matters?

Reference this when starting implementation, reviewing work, or declaring a task complete.

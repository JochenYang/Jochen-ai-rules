# Handoff Template

Use this template when writing a session handoff. Keep it concise, explicit,
and biased toward immediate resumability.

```md
# Handoff: <task slug>

## Task
- Objective:
- Current phase:
- Requested outcome:

## Repository State
- Repo:
- Branch:
- Working tree:
- Relevant commit or checkpoint:

## Current Status
- Completed:
- In progress:
- Not started:

## Key Files
- `<path>`: why it matters
- `<path>`: why it matters

## Decisions Already Made
- Decision:
  Reason:
- Decision:
  Reason:

## Verification
- Commands run:
  - `<command>` -> passed / failed / not run
- Tests:
  - `<test command>` -> passed / failed / not run
- Manual checks:
  - `<check>` -> result

## Risks And Blockers
- Risk:
  Impact:
  Mitigation:
- Blocker:
  What is needed:

## Open Questions
- Question:
  Current best guess:

## Resume Order
1. Read `<file>` and confirm `<condition>`.
2. Run `<command>` to verify current state.
3. Continue with `<next action>`.

## Next Action
- The very next thing the next session should do:

## Notes For The Next Session
- Facts that are verified:
- Assumptions that still need checking:
- Things to avoid repeating:
```

## Writing Rules

- Prefer bullets over long prose.
- Name exact file paths.
- Preserve failed attempts when they prevent repeated mistakes.
- Mark unknowns clearly instead of smoothing them over.
- Keep “Next Action” singular and concrete.

## Minimum Acceptance

A handoff is acceptable only if:

- the next session can tell what to do first
- verification status is explicit
- key files are named
- blockers are not hidden
- assumptions are separated from facts

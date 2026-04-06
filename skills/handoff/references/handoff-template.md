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

## Field Explanations

| Section                    | Required | Purpose                                  |
|----------------------------|----------|------------------------------------------|
| Task                       | Yes      | What is the objective and current phase? |
| Repository State           | Yes      | Where to resume, current branch/commit   |
| Current Status             | Yes      | Completed vs in-progress vs not started  |
| Key Files                  | Yes      | Which files matter and why               |
| Decisions Already Made     | Yes      | Avoid re-litigating settled questions    |
| Verification               | Yes      | Proof that state is understood           |
| Risks And Blockers         | Yes      | What could go wrong or is stuck          |
| Open Questions             | Optional | Unresolved questions with guesses        |
| Resume Order               | Yes      | Step-by-step path to resume              |
| Next Action                | Yes      | The single most important next step      |
| Notes For The Next Session | Yes      | Verified facts, assumptions, avoidances  |

### Tips for Each Section

**Task** - Be specific: "refactor auth module" not "work on auth". Include
current phase percentage when known.

**Repository State** - Include branch AND working tree status. If there are
unstaged changes that matter, mention them.

**Current Status** - Use three buckets: Completed, In progress, Not started.
Be honest about "not started" items.

**Key Files** - Don't list every file. List 3-7 files that actually matter.
Include why each file matters in 1 phrase.

**Decisions Already Made** - Include the reason, not just the decision. This
prevents re-litigating settled questions.

**Verification** - Mark commands as "passed", "failed", or "not run". Don't
say "passed" for tests you didn't run.

**Risks And Blockers** - Distinguish between a risk (may happen) and blocker
(happening now). Blockers need "What is needed" to unblock.

**Resume Order** - Numbered steps that assume minimal context. Each step should
be independently verifiable.

**Next Action** - One sentence. The next session should be able to act on this
without reading the whole handoff.

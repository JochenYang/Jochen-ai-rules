---
argument-hint: "<feature|feature-tdd|bugfix|refactor|ui-design|secure-feature|db-feature|performance-audit|deploy> <task-description> | custom \"<agents>\" \"<task-description>\""
description: Run sequential multi-agent workflows with approval gates, structured handoffs, and repair loops. Coordinates the right agent chain and finishes at a review recommendation.
---

# Orchestrate Command

Sequential multi-agent workflow engine for complex engineering tasks. This
command coordinates specialized **Agents** (loaded from `.claude/agents/`) with
explicit approval gates, structured handoffs, and mandatory review loops.

> **Source of truth.** Agent responsibilities, base workflow chains, repair
> ownership rules, and trigger hints are defined in `rules/agents.md`. This
> command only adds **execution semantics** on top: approval gates, specialist
> re-check loops, repair iteration caps, and machine-readable handoff payloads.
> Any chain edit must update both files in lock-step.

## Usage

`/orchestrate [workflow-type] [task-description]`

Custom chain:

`/orchestrate custom "<agent-1,agent-2,...,code-reviewer>" "<task-description>"`

## Critical Rule

**The orchestrator is a COORDINATOR, not an implementer.** It MUST NEVER
directly edit code, fix issues, or make changes itself. All implementation and
repairs MUST be delegated to the correct agent.

**Routing boundary:** `/orchestrate` is a **sequential** workflow command. When
the user explicitly invokes `/orchestrate`, do not switch to `agent-teams` or
other parallel team orchestration unless the user also explicitly asks for a
parallel team, multiple simultaneous agents, or `agent-teams`.

## Workflow Catalog

| Workflow            | Primary Chain                                                                                                       | Approval Gate                                     | Default Repair Owner                                                         | Required Re-Checks                                                           |
|---------------------|---------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| `feature`           | `dev-planner -> code-implementer -> code-reviewer` `↺ repair loop if needed`                                        | After `dev-planner`                               | `code-implementer`                                                           | `code-reviewer`                                                              |
| `feature-tdd`       | `dev-planner -> tdd-guide -> code-reviewer` `↺ repair loop if needed`                                               | After `dev-planner`                               | `tdd-guide`                                                                  | `code-reviewer`                                                              |
| `bugfix`            | `bug-analyzer -> tdd-guide -> code-reviewer` `↺ repair loop if needed`                                              | None unless analysis changes scope                | `tdd-guide`                                                                  | `code-reviewer`                                                              |
| `refactor`          | `dev-planner -> code-implementer -> code-reviewer` `↺ repair loop if needed`                                        | After `dev-planner`                               | `code-implementer`                                                           | `code-reviewer`                                                              |
| `ui-design`         | `story-generator -> ui-sketcher -> dev-planner -> code-implementer -> code-reviewer` `↺ repair loop if needed`      | After `dev-planner`                               | `code-implementer`                                                           | `code-reviewer`                                                              |
| `secure-feature`    | `dev-planner -> code-implementer -> security-reviewer -> code-reviewer` `↺ specialist + review loop if needed`      | After `dev-planner`                               | `code-implementer`                                                           | `security-reviewer -> code-reviewer`                                         |
| `db-feature`        | `dev-planner -> database-migration -> code-implementer -> code-reviewer` `↺ specialist + review loop if needed`     | After `dev-planner`                               | `database-migration` for schema/data issues, otherwise `code-implementer`    | `database-migration` when schema/data changed, then `code-reviewer`          |
| `performance-audit` | `bug-analyzer -> performance-optimizer -> code-implementer -> code-reviewer` `↺ specialist + review loop if needed` | None unless optimization scope changes materially | `performance-optimizer` for measurement issues, otherwise `code-implementer` | `performance-optimizer` when metrics/profiling changed, then `code-reviewer` |
| `deploy`            | `dev-planner -> devops-engineer -> code-reviewer` `↺ specialist + review loop if needed`                            | After `dev-planner`                               | `devops-engineer`                                                            | `devops-engineer` when infra/pipeline changed, then `code-reviewer`          |

### When to Use Specialist Workflows

- `secure-feature`: auth, payments, RBAC, session, API keys, PII, secrets
- `db-feature`: schema changes, index changes, migrations, data backfills
- `performance-audit`: slow endpoints, CWV regressions, N+1, memory leaks
- `deploy`: Docker, CI/CD, Kubernetes, monitoring, runtime infrastructure

### Bugfix Workflow Guardrail

For `bugfix`, `bug-analyzer` is **analysis-only**:

- it must not edit files or implement the fix
- it must always end by handing off to `tdd-guide`
- the orchestrator must continue into `tdd-guide -> code-reviewer` even if the
  root cause appears obvious

## Workflow Engine

### Phase 0: Validate the Requested Workflow

Before invoking any agent:

1. Resolve the workflow type and full agent chain.
2. For `custom`, verify:
   - every named agent exists
   - the final agent is `code-reviewer`
   - at least one non-reviewer agent performs the work
   - specialist reviewers (`security-reviewer`) appear before `code-reviewer`
3. Reject invalid custom chains instead of guessing.

### Phase 1: Run the Sequential Chain

For each agent in the chain:

1. Load `.claude/agents/[agent-name].md`.
2. Pass the previous agent's `HANDOFF` plus the original task context.
3. Collect the agent's primary artifact.
4. Collect the agent's trailing `HANDOFF` block.
5. If the output includes `WAITING FOR CONFIRMATION` or
   `Requires User Approval: Yes`, stop and ask the user to approve before
   invoking the next implementation agent.
6. For `bugfix`, do not treat root-cause analysis as completion. The workflow is
   incomplete until `tdd-guide` and `code-reviewer` have both run.

### Phase 1b: Task Loop (when dev-planner hands off a Task List)

When the dev-planner's `HANDOFF` block contains a `### Task List` table (see
`agents/dev-planner.md`), the orchestrator drives the implementation agent
**one task at a time** instead of pushing the entire plan in a single
invocation.

1. Parse the `### Task List` Markdown table from the plan handoff.
2. Sort tasks by dependency order: process tasks whose `Depends On` column is
   `-` or already-completed first.
3. For each `pending` task in order:
   a. Invoke the implementation agent (e.g. `code-implementer` or `tdd-guide`)
      with the single task description plus full plan context.
   b. Collect the agent's primary artifact and `HANDOFF`.
   c. Mark that task's `Status` as `done` in the tracking copy.
   d. If the handoff reports a blocker or failure, pause the loop and escalate.
4. After all tasks are `done`, proceed to Phase 2 (Review Gate) as normal.

**Commit policy:** Do NOT commit after individual tasks. All tasks remain
uncommitted until `code-reviewer` returns `SHIP`, at which point the full
changeset is committed as a single unit. Task tracking is for progress
visibility and interruption recovery only, not for granular commits.

**Interruption recovery:** If the session is interrupted mid-loop, restart by
reading the last handoff's Task List status column — completed tasks are
`done`, the first `pending` task is the resume point.

### Phase 2: Review Gate

The final quality gate always ends at `code-reviewer`, even when specialist
reviewers run earlier in the workflow.

After invoking `code-reviewer`, extract:

- `Recommendation: SHIP`
- `Recommendation: NEEDS WORK`
- `Recommendation: BLOCKED`

`Recommendation` is the only machine-readable verdict. Legacy wording such as
`Pass`, `Request Changes`, or `Block` may remain for human readability, but
automation MUST ignore it.

### Phase 3: Repair Loop

When the recommendation is not `SHIP`, enter the repair loop:

1. Identify the repair owner from the workflow table.
2. Pass the full review report via `REPAIR HANDOFF`.
3. Collect the new implementation `HANDOFF`.
4. Re-run any required specialist re-checks for that workflow.
5. Re-run `code-reviewer`.
6. Repeat until `SHIP` or the loop cap is reached.

**Loop cap: 3 repair iterations.** If the third iteration is still not `SHIP`,
end the workflow as `BLOCKED`.

## Repair Owner Selection Rules

Use these rules in order:

1. If the review issue is explicitly about schema safety, migration order, or
   data integrity in `db-feature`, repair owner = `database-migration`.
2. If the issue is explicitly about baseline metrics, profiling evidence, or
   optimization strategy in `performance-audit`, repair owner =
   `performance-optimizer`.
3. If the issue is explicitly about CI/CD, container, infra, or rollout safety
   in `deploy`, repair owner = `devops-engineer`.
4. Otherwise, use the workflow's default implementation owner.
5. For `custom`, default to the last non-reviewer agent that touched the
   artifact; if still ambiguous, stop and ask the user.

## Repair Loop Rules

1. **NEVER skip the repair agent.**
2. **ALWAYS pass the full Review Report** to the repair agent.
3. **ALWAYS re-run required specialist re-checks** before the final review when
   the workflow demands them.
4. **ALWAYS re-run `code-reviewer`** after each repair cycle.
5. **Track iteration count** using `Repair Iteration: N/3`.

## Repair Handoff Format

```markdown
## REPAIR HANDOFF: code-reviewer -> [repair-agent]

### Repair Iteration: [N]/3

### Review Recommendation
[NEEDS WORK | BLOCKED]

### Issues To Fix
[Copy the complete issue list from the latest reviewer output]

### Severity Breakdown
- Critical:
- Major:
- Minor:

### Files Requiring Changes
- path/to/file

### Original Task Context
[Original task description and workflow type]

### Previous Handoff Context
[Relevant context from the latest implementation handoff]

### Required Re-Checks
- [security-reviewer / database-migration / performance-optimizer / devops-engineer / code-reviewer]
```

## Agent Output Contract

Agents may keep their domain-specific primary report, but when they hand work to
another agent they MUST append a structured `HANDOFF` block.

Approval-gated agents may hand off to `user` first.

```markdown
## HANDOFF: [source] -> [target]

### Context
[What was done and why]

### Decisions
[Key decisions, trade-offs, constraints]

### Files Changed
- path/to/file

### Verification
- command -> passed / failed / not run

### Risks
- risk and mitigation

### Open Questions
- unresolved item

### Next Actions
- concrete next step for the next agent

### Approval Gate
- Requires User Approval: [Yes/No]
- Approval Question: [Only if approval is required]
```

## Self-Check Before Each Agent Invocation

- [ ] Am I loading the agent definition from `.claude/agents/[agent-name].md`?
- [ ] Am I passing the previous `HANDOFF` plus the original task context?
- [ ] If the previous output required user approval, did I stop and ask first?
- [ ] Am I letting the agent do the work instead of doing it myself?

Before final report:

- [ ] Did the last `code-reviewer` invocation return `SHIP`, or did we hit the
      3-iteration cap?
- [ ] Did I run all required specialist re-checks for this workflow?

## Example: Feature Workflow Execution

```bash
/orchestrate feature "Add user profile editing"
```

1. `dev-planner` creates the plan and outputs `HANDOFF: dev-planner -> user`
2. User approves the plan
3. `code-implementer` implements and outputs `HANDOFF: code-implementer -> code-reviewer`
4. `code-reviewer` returns `Recommendation: SHIP | NEEDS WORK | BLOCKED`
5. If not `SHIP`, invoke `code-implementer` with `REPAIR HANDOFF`, then re-review

## Example: Secure Feature Workflow Execution

```bash
/orchestrate secure-feature "Add admin-only API key rotation"
```

1. `dev-planner` plans and waits for approval
2. `code-implementer` implements the approved plan
3. `security-reviewer` performs the specialist audit
4. `code-reviewer` performs the final quality gate
5. If repair is required, re-run `security-reviewer` and then `code-reviewer`
   before shipping

## Final Report Format

```markdown
# ORCHESTRATION REPORT

Workflow: [type]
Task: [description]
Agents: [path taken, including repair iterations]
Review Iterations: [N]

## Summary
[Executive summary]

## Agent Outputs
- Agent 1:
- Agent 2:
- Code Review #1:
- Repair #1:
- Code Review #2:

## Files Changed
- path/to/file

## Test Results
- command -> passed / failed / not run

## Review History
| Iteration | Recommendation | Issues Found | Issues Fixed |
|-----------|----------------|--------------|--------------|
| 1         | NEEDS WORK     | 3 major      | -            |
| 2         | SHIP           | 0            | 3            |

## Recommendation
[SHIP / NEEDS WORK / BLOCKED]
```

## Parallel Execution Guidance

Parallel work is allowed only when outputs do not depend on each other. Good
examples:

- independent exploratory analysis before planning
- parallel specialist checks on the same completed implementation artifact

Do **not** run `code-reviewer` in parallel with a repair agent working on the
same unresolved findings.
Do **not** replace `/orchestrate` with `agent-teams` just because the task
mentions multi-agent coordination; `/orchestrate` remains the correct choice for
dependent, ordered workflows unless the user explicitly requests parallel teams.

## Available Agents

Located in `.claude/agents/`:

- `dev-planner`
- `code-implementer`
- `bug-analyzer`
- `tdd-guide`
- `code-reviewer`
- `story-generator`
- `ui-sketcher`
- `security-reviewer`
- `database-migration`
- `performance-optimizer`
- `devops-engineer`

## Arguments

$ARGUMENTS:

- `feature <description>` - Planning -> Implementation -> Review
- `feature-tdd <description>` - Planning -> TDD -> Review
- `bugfix <description>` - Analysis -> TDD Fix -> Review
- `refactor <description>` - Planning -> Refactor -> Review
- `ui-design <description>` - Story -> Sketch -> Plan -> Implement -> Review
- `secure-feature <description>` - Plan -> Implement -> Security Review -> Review
- `db-feature <description>` - Plan -> Migration -> Implement -> Review
- `performance-audit <description>` - Analyze -> Profile -> Optimize -> Review
- `deploy <description>` - Plan -> DevOps -> Review
- `custom <agents> <description>` - Custom validated chain ending in `code-reviewer`

All workflows above are review-gated and enter the repair loop when the final
recommendation is not `SHIP`.

## Tips

1. **Handoffs are mandatory**: every handoff-bearing agent must append the
   standard `HANDOFF` block.
2. **Approval gates are real**: do not auto-skip `WAITING FOR CONFIRMATION`.
3. **Specialist workflows need specialist re-checks**: secure, DB, performance,
   and deploy workflows are not review-once-only flows.
4. **Custom chains must be explicit**: if ownership or repair routing is
   unclear, stop and ask instead of guessing.

## Final Output Format (MANDATORY)

Every `/orchestrate` completion message must include:

1. `Workflow Summary` - workflow type, task, and executed agent chain
2. `Approval Events` - where user confirmation was required and the decision
3. `Review Timeline` - each review iteration and recommendation result
4. `Files Changed` - deduplicated list from handoffs/reports
5. `Verification` - tests/checks run with pass/fail/not-run
6. `Final Recommendation` - exactly one of `SHIP`, `NEEDS WORK`, `BLOCKED`
7. `Next Action` - concrete next step when recommendation is not `SHIP`

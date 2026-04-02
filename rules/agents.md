---
name: agents
description: Mandatory agent selection and orchestration rules.
---

# Agent Usage Rules

**RULE TYPE**: Mandatory agent selection and orchestration rules.

## Selection Rules

1. Select by **responsibility**, not by color.
2. For non-trivial tasks (3+ steps or architecture decisions), start with `dev-planner`.
3. Use one primary agent per task; add secondary agents only for independent concerns.
4. After major code changes, run `code-reviewer` before claiming completion.
5. When one agent hands work to another, preserve the primary artifact **and** append a structured `HANDOFF` block.
6. If an agent output says `WAITING FOR CONFIRMATION` or `Requires User Approval: Yes`, stop and get user approval before invoking the next implementation agent.

## Agent Registry

| Agent | Use When | Expected Output |
|---|---|---|
| dev-planner | complex feature/refactor | plan, risks, dependencies + approval handoff |
| code-implementer | implementation tasks | clean code + tests + review handoff |
| tdd-guide | test-first development or bugfix | RED-GREEN-REFACTOR execution + review handoff |
| code-reviewer | quality gate before delivery | prioritized findings + `Recommendation` |
| bug-analyzer | errors/crashes/unknown behavior | root cause + fix strategy + handoff to `tdd-guide` (analysis only, no edits) |
| story-generator | requirements structuring | user stories + acceptance criteria + design handoff |
| ui-sketcher | UI flow and interaction drafting | ASCII mockups + flow notes + planning handoff |
| security-reviewer | auth/payment/PII/secrets scope | security findings + remediation + review handoff |
| database-migration | schema/index/migration changes | migration plan + rollback + implementation handoff |
| performance-optimizer | latency/bottleneck issues | profiling + measurable targets + implementation handoff |
| devops-engineer | deploy/CI/CD/container/infra | pipeline + infra artifacts + review handoff |

## Standard Workflows

- Feature: `dev-planner -> code-implementer -> code-reviewer`
- Feature (TDD): `dev-planner -> tdd-guide -> code-reviewer`
- Bugfix: `bug-analyzer -> tdd-guide -> code-reviewer`
- Security-sensitive: `dev-planner -> code-implementer -> security-reviewer -> code-reviewer`
- DB schema change: `dev-planner -> database-migration -> code-implementer -> code-reviewer`
- Performance issue: `bug-analyzer -> performance-optimizer -> code-implementer -> code-reviewer`
- UI optimization: `story-generator -> ui-sketcher -> dev-planner -> code-implementer -> code-reviewer`
- Deploy / CI / infra: `dev-planner -> devops-engineer -> code-reviewer`

## Review Recommendation Contract

`code-reviewer` is the final quality gate unless a workflow explicitly adds a
specialist reviewer before it. The orchestrator must parse a single field:

- `SHIP` - quality bar met, workflow may complete
- `NEEDS WORK` - issues found, enter repair loop
- `BLOCKED` - critical issues or missing context, enter repair loop

Legacy wording such as `Pass`, `Request Changes`, and `Block` may still appear
for human readability, but `Recommendation` is the source of truth for
automation.

## Repair Ownership Rules

- Default repair owner: the last non-reviewer agent that edited or produced the
  artifact being reviewed
- Specialist-first repair:
  - schema or migration issue -> `database-migration`
  - profiling or metrics issue -> `performance-optimizer`
  - CI/CD or infra issue -> `devops-engineer`
- Security-sensitive workflows must re-run `security-reviewer` after repairs
  that touch auth, session, secrets, payments, RBAC, or PII handling.
- Custom workflows must end with `code-reviewer`; if repair ownership is still
  ambiguous after applying the rules above, stop and ask the user.

## Trigger Hints

- Bug/error/crash/logs: suggest `bug-analyzer`
- In bugfix workflows, `bug-analyzer` diagnoses only; `tdd-guide` owns the fix
  and test-first implementation.
- New feature/multi-file change: suggest `dev-planner`
- TDD/tests/coverage request: suggest `tdd-guide`
- Auth/token/payment/PII/secret: include `security-reviewer`
- Schema/migration/index: include `database-migration`
- Slow/latency/CWV/N+1: include `performance-optimizer`
- Deploy/CI/K8s/Docker: suggest `devops-engineer`

## Handoff Template

```markdown
## HANDOFF: [source] -> [target]
### Context
### Decisions
### Files Changed
### Verification
### Risks
### Open Questions
### Next Actions
```

## Execution Checklist (Mandatory)

Before finishing any agent-driven task, confirm:

- [ ] Agent choice matches responsibility and workflow stage
- [ ] Required approval gates were respected
- [ ] Required specialist re-checks were executed
- [ ] Final reviewer recommendation is present and machine-readable
- [ ] Handoff chain is complete and traceable

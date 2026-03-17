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

## Agent Registry

| Agent | Use When | Expected Output |
|---|---|---|
| dev-planner | complex feature/refactor | plan, risks, dependencies |
| code-implementer | implementation tasks | clean code + tests |
| tdd-guide | test-first development or bugfix | RED-GREEN-REFACTOR execution |
| code-reviewer | quality gate before delivery | prioritized findings |
| bug-analyzer | errors/crashes/unknown behavior | root cause + fix strategy |
| story-generator | requirements structuring | user stories + acceptance criteria |
| ui-sketcher | UI flow and interaction drafting | ASCII mockups + flow notes |
| security-reviewer | auth/payment/PII/secrets scope | security findings + remediation |
| database-migration | schema/index/migration changes | migration plan + rollback |
| performance-optimizer | latency/bottleneck issues | profiling + measurable targets |
| devops-engineer | deploy/CI/CD/container/infra | pipeline + infra artifacts |

## Standard Workflows

- Feature: `dev-planner -> code-implementer -> code-reviewer`
- Feature (TDD): `dev-planner -> tdd-guide -> code-reviewer`
- Bugfix: `bug-analyzer -> tdd-guide -> code-reviewer`
- Security-sensitive: `dev-planner -> code-implementer -> security-reviewer -> code-reviewer`
- DB schema change: `dev-planner -> database-migration -> code-implementer -> code-reviewer`
- Performance issue: `bug-analyzer -> performance-optimizer -> code-implementer -> code-reviewer`

## Trigger Hints

- Bug/error/crash/logs: suggest `bug-analyzer`
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
### Open Questions
### Next Actions
```

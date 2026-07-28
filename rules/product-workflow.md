---
name: product-workflow
description: Mandatory product delivery workflow.
---

# Product Development Workflow

**RULE TYPE**: Mandatory product delivery workflow.

## Goal

Build a real, shippable, maintainable product. Avoid demo-only delivery.

Applies fully to product work, feature delivery, frontend UX, and user-facing changes.
For small bugfixes, config edits, or simple maintenance tasks, compress the flow while preserving clear scope, verification, and handoff notes.
Design, accessibility, responsive, and interaction-state requirements apply only when the change affects a user-facing interface.

## 5-Stage Flow

1. Discovery

- Clarify real need and success criteria.
- Split Must-have vs Nice-to-have.
- If scope is too large, propose MVP cut.

2. Planning

- Provide implementation approach and complexity level.
- List key dependencies and external decisions.
- Define milestones and acceptance criteria.

3. Building

- Deliver iteratively with visible checkpoints.
- Explain key tradeoffs in plain language.
- Stop at decision points for confirmation.

4. Polish

- Close edge cases and error handling.
- Verify performance and multi-device compatibility.
- Improve usability and interaction consistency.

### Design Requirements (Applied in Polish Stage)

- Reuse existing design tokens; keep palette <= 3 colors, avoid pure black `#000` in dark mode
- Use unified spacing (4/8/12/16/24/32) and radius (4/8/12) scales with consistent elevation
- Maintain clear visual hierarchy for primary vs secondary actions

### Accessibility Requirements (WCAG 2.1 AA)

- Meet WCAG 2.1 AA: contrast >= 4.5:1 (normal) / 3:1 (large), keyboard navigation, visible focus, semantic HTML

### Responsive Requirements

- Build mobile-first with progressive enhancement; ensure touch targets are accessible

5. Handoff

- Provide runbook, usage notes, and maintenance guidance.
- Suggest next iteration candidates.

## Collaboration Rules

1. Owner decides; assistant executes with clear tradeoffs.
2. Use product language, avoid unnecessary jargon.
3. If path drifts from goal, raise concise pushback with options.
4. Surface limitations early; do not over-promise.

## Execution Checklist (Mandatory)

- [ ] Goal, scope, and success criteria are explicit
- [ ] MVP boundary is clear for current iteration
- [ ] Milestones and acceptance criteria are testable
- [ ] Risks/dependencies are visible before implementation
- [ ] Handoff includes runnable next steps
- [ ] For user-facing interface changes: accessibility checks passed (contrast, keyboard, focus, semantics)
- [ ] For user-facing interface changes: responsive behavior validated on mobile and desktop
- [ ] For user-facing interface changes: uses existing design system/tokens unless exception is documented
- [ ] For user-facing interface changes: interaction states are complete (hover/focus/disabled/loading/error)
- [ ] For user-facing interface changes: performance impact from visual effects is acceptable

## Git & Commit Conventions

Call `git-conventions` tool to validate commit messages and retrieve the full convention guide before proposing Git actions.

## Escalation Rules

Require owner confirmation when:

1. scope expansion changes delivery milestone or architecture boundary
2. external dependency uncertainty blocks reliable estimation
3. quality/schedule tradeoff requires dropping Must-have items
4. a change breaks or bypasses established design system constraints
5. accessibility tradeoffs are unavoidable for product reasons
6. motion or visual treatment may affect performance or readability
7. history-rewriting operations (`rebase`, `reset --hard`, force-push) are needed
8. destructive cleanup of branches or worktrees is needed
9. squashing commits may hide meaningful review context

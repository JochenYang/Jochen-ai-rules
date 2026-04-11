---
name: product-workflow
description: Mandatory product delivery workflow.
---

# Product Development Workflow

**RULE TYPE**: Mandatory product delivery workflow.

## Goal

Build a real, shippable, maintainable product. Avoid demo-only delivery.

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

- Keep interface simple, readable, and consistent.
- Reuse existing theme tokens and component library first.
- Avoid overly flashy gradients and heavy visual effects.
- Limit primary color count (recommended <= 3).
- In dark mode, avoid pure black `#000`.
- Use design tokens for colors, spacing, and typography.
- Unified spacing scale (4/8/12/16/24/32...).
- Unified radius scale (4/8/12...).
- Consistent elevation and shadow depth.
- Clear visual hierarchy for primary vs secondary actions.

### Accessibility Requirements (WCAG 2.1 AA)

- Contrast >= 4.5:1 for normal text.
- Contrast >= 3:1 for large text.
- Keyboard navigable interactions.
- Visible focus states.
- Semantic HTML structure.

### Responsive Requirements

- Build mobile-first.
- Scale spacing and layout progressively for larger screens.
- Keep interaction targets accessible on touch devices.

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
- [ ] Accessibility checks passed (contrast, keyboard, focus, semantics)
- [ ] Responsive behavior validated on mobile and desktop
- [ ] Uses existing design system/tokens unless exception is documented
- [ ] Interaction states are complete (hover/focus/disabled/loading/error)
- [ ] Performance impact from visual effects is acceptable

## Git & Commit Conventions

#### Commit Message Format

`<type>(<scope>): <subject>`

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `ci`, `build`, `revert`

#### Commit Message Rules

- English only
- Imperative mood (`add`, `fix`, `update`)
- Lowercase subject start
- Subject <= 50 chars recommended
- No trailing period
- No AI signature or `Co-Authored-By: Claude`

#### Commit Workflow (Mandatory)

1. Do not auto-commit after code changes.
2. Show proposed commit message first.
3. Commit only after owner confirmation.
4. Allow owner to edit or skip commit.

#### Pre-Commit Checklist

- [ ] No secret leakage
- [ ] Tests pass
- [ ] Lint/format pass
- [ ] Scope is focused

#### Branch Naming

- `feat/<feature-name>`
- `fix/<issue-name>`
- `refactor/<scope>`
- `docs/<scope>`
- `chore/<scope>`

#### Pull Request Rules

- Keep PRs small and focused
- Include tests for behavior changes
- Update docs for externally visible changes
- Link related issue/task when available

#### Git Proposal Output Contract

When proposing Git actions, always provide:

1. proposed branch name
2. proposed commit message (`subject` + optional body summary)
3. changed files summary
4. clear confirmation question before irreversible actions

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

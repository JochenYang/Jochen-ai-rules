---
name: git-workflow
description: Mandatory Git conventions for commit messages and branch naming.
---

# Git Workflow

**RULE TYPE**: Mandatory Git conventions.

## Commit Message Format

`<type>(<scope>): <subject>`

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `ci`, `build`, `revert`

## Commit Message Rules

- English only
- Imperative mood (`add`, `fix`, `update`)
- Lowercase subject start
- Subject <= 50 chars recommended
- No trailing period
- No AI signature or `Co-Authored-By: Claude`

## Commit Workflow (Mandatory)

1. Do not auto-commit after code changes.
2. Show proposed commit message first.
3. Commit only after owner confirmation.
4. Allow owner to edit or skip commit.

## Pre-Commit Checklist

- [ ] No secret leakage
- [ ] Tests pass
- [ ] Lint/format pass
- [ ] Scope is focused

## Branch Naming

- `feat/<feature-name>`
- `fix/<issue-name>`
- `refactor/<scope>`
- `docs/<scope>`
- `chore/<scope>`

## Pull Request Rules

- Keep PRs small and focused
- Include tests for behavior changes
- Update docs for externally visible changes
- Link related issue/task when available

## Escalation Rules (Mandatory)

Require explicit owner confirmation before:

1. history-rewriting operations (`rebase`, `reset --hard`, force-push)
2. destructive cleanup of branches/worktrees
3. squashing commits that may hide meaningful review context

## Delivery Output Contract

When proposing Git actions, always provide:

1. proposed branch name
2. proposed commit message (`subject` + optional body summary)
3. changed files summary
4. clear confirmation question before irreversible actions

---
argument-hint: [--no-verify] [--style=simple|full] [--type=feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert]
description: Create well-formatted commits with conventional commit messages
---

## Claude Command: Commit（Clean / No Emoji）

This command helps you create well-formatted commits following the Conventional Commits specification.

---

## Usage

Basic usage:

```bash
/commit
```

With options:

```bash
/commit --no-verify
/commit --style=full
/commit --style=full --type=feat
```

---

## Command Options

* `--no-verify`
  Skip pre-commit checks (lint, build, generate:docs)

* `--style=simple|full`

  * `simple` (default): concise single-line commit message
  * `full`: commit message with body and footer sections

* `--type=<type>`
  Specify the commit type (overrides automatic detection)

---

## What This Command Does

1. **Pre-commit checks** (unless `--no-verify`):

   * `pnpm lint` – ensure code quality
   * `pnpm build` – verify build succeeds
   * `pnpm generate:docs` – update documentation

2. **File staging**:

   * Inspect staged files via `git status`
   * If no files are staged, automatically stage all modified/new files

3. **Change analysis**:

   * Analyze `git diff` to understand changes
   * Detect whether multiple logical changes should be split
   * Suggest atomic commits when appropriate

4. **Commit message creation**:

   * Generate commit messages following Conventional Commits
   * No emoji prefixes are used
   * Include body and footer when `--style=full` is selected

---

## Conventional Commits Format

### Simple Style (Default)

```
<type>[optional scope]: <description>
```

Example:

```
feat(auth): add JWT token validation
```

---

### Full Style

```
<type>[optional scope]: <description>

<body>

<footer>
```

Example:

```
feat(auth): add JWT token validation

Implement JWT token validation middleware to ensure all
protected routes validate authentication tokens.

BREAKING CHANGE: API now requires Bearer token for all
authenticated endpoints
Closes: #123
```

---

## Commit Types

| Type     | Description   | When to Use                    |
| -------- | ------------- | ------------------------------ |
| feat     | New feature   | Adding new functionality       |
| fix      | Bug fix       | Fixing an issue                |
| docs     | Documentation | Documentation-only changes     |
| style    | Code style    | Formatting, lint-only changes  |
| refactor | Refactoring   | No functional behavior change  |
| perf     | Performance   | Performance improvements       |
| test     | Tests         | Adding or updating tests       |
| chore    | Maintenance   | Tooling, scripts, housekeeping |
| ci       | CI/CD         | CI configuration changes       |
| build    | Build system  | Build or packaging changes     |
| revert   | Revert        | Reverting a previous commit    |

---

## Body Section Guidelines (Full Style)

* Explain **what changed and why**, not how
* Use bullet points for multiple changes
* Describe behavior changes compared to previous behavior
* Wrap lines at 72 characters
* Reference related issues or decisions when relevant

---

## Footer Section Guidelines (Full Style)

Footer may include:

* `BREAKING CHANGE:` for incompatible changes
* Issue references: `Closes:`, `Fixes:`, `Refs:`
* Attribution: `Co-authored-by:`
* Review metadata: `Reviewed-by:`, `Approved-by:`

Example:

```
BREAKING CHANGE: rename config.auth to config.authentication
Closes: #123
```

---

## Scope Guidelines

* Use short, meaningful nouns
* Be consistent across the project
* Prefer module or domain names

Common scopes:

```
api, auth, ui, db, config, deps
parser, compiler, validator
```

---

## Commit Splitting Strategy

Suggest splitting commits when detecting:

1. Mixed change types (e.g. feature + fix)
2. Multiple unrelated concerns
3. Large cross-module changes
4. Dependency updates mixed with functional changes

---

## Best Practices

### DO

* Use present tense, imperative mood (“add”, not “added”)
* Keep subject line under 50 characters (72 max)
* Capitalize the first letter of the description
* Separate subject and body with a blank line
* Keep commits atomic and reviewable

### DON’T

* Mix unrelated changes in a single commit
* Include implementation details in the subject line
* Use past tense
* Commit broken code (unless explicitly intended)
* Include sensitive information
* NO Co-Authored-By: Do not add Co-Authored-By: Claude in commit footer

---

## Important Notes

* Default style is `simple` for everyday commits
* Use `full` style for:

  * Breaking changes
  * Complex features
  * Changes requiring context or explanation
* Always review the generated message before confirming

---


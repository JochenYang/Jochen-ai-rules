---
argument-hint: [--no-verify] [--style=simple|full] [--type=feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert]
description: Create conventional commits with optional pre-commit checks and full message style
---

# Commit Command

Create commit messages that follow Conventional Commits.

## Usage

```bash
/commit
/commit --no-verify
/commit --style=full
/commit --style=full --type=feat
```

## Options

- `--no-verify`: Skip pre-commit checks.
- `--style=simple|full`:
  - `simple` (default): one-line subject.
  - `full`: subject + body + footer.
- `--type=<type>`: Explicitly set commit type.

## Workflow

1. Run pre-commit checks unless `--no-verify`:
   - Detect package manager from lock files.
   - Run `lint` if available.
   - Run `build` if available.
2. Check staging state with `git status`.
3. If nothing is staged, stage modified/new files.
4. Analyze changes and suggest split commits when needed.
5. Generate commit message with selected style.
6. Ask for final user confirmation before commit.
7. Validate that subject/body/footer contain no emoji.

## Message Format

Simple:

```text
<type>[optional scope]: <description>
```

Full:

```text
<type>[optional scope]: <description>

<body>

<footer>
```

## Types

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation
- `style`: formatting/style-only
- `refactor`: internal restructuring
- `perf`: performance improvement
- `test`: tests
- `chore`: maintenance/tooling
- `ci`: CI/CD changes
- `build`: build/packaging changes
- `revert`: revert prior commit

## Subject Rules

- English only
- Imperative mood (`add`, `fix`, `update`)
- Start with lowercase verb
- Prefer <= 50 chars (hard max 72)
- No trailing period
- No emoji in subject, body, or footer
- No AI signature text

## Body Rules (`--style=full`)

- Explain what changed and why.
- Prefer short bullet points for multiple changes.
- Wrap lines at 72 chars.

## Footer Rules (`--style=full`)

Allowed examples:
- `BREAKING CHANGE: ...`
- `Closes: #123`
- `Fixes: #123`
- `Refs: #123`
- `Reviewed-by: <name>`
- `Approved-by: <name>`

## Split Commit Guidance

Suggest split commits when:
1. feature and fix are mixed
2. unrelated modules are changed together
3. dependency updates are mixed with functional changes
4. one commit is too large to review safely

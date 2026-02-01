# Git Workflow

## Commit Message Format

```
<type>(<scope>): <subject>
```

### Types
| Type | Description | Example |
|------|-------------|---------|
| feat | New feature | `feat(auth): add JWT token validation` |
| fix | Bug fix | `fix(ui): resolve button hover state` |
| refactor | Code restructuring | `refactor(api): simplify response handling` |
| docs | Documentation | `docs(readme): add installation guide` |
| style | Formatting | `style(format): run prettier on utils` |
| test | Tests | `test(auth): add login validation tests` |
| chore | Maintenance | `chore(deps): update npm dependencies` |
| perf | Performance | `perf(db): optimize query performance` |

### Rules
- **Language**: English only (no Chinese or pinyin)
- **Tense**: Present tense ("add" not "added")
- **Case**: Lowercase subject
- **Length**: ≤50 characters for subject
- **No period**: Don't end subject with period
- **Scope**: Optional, describe affected area
- **NO signature**: Never add "Generated with Claude Code" or similar signatures
- **NO Co-Authored-By**: Do not add Co-Authored-By: Claude in commit footer

### Examples

```
feat(auth): add JWT token validation
fix(api): resolve null pointer in user lookup
docs: update API documentation
refactor: simplify data transformation logic
```

### Full Format (Optional)
```
<type>(<scope>): <subject>

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

## Commit Workflow (MANDATORY)

1. **DO NOT auto-commit**: After code changes, you MUST ask for confirmation
2. **Show commit message**: Present the suggested commit message to the user
3. **Wait for approval**: Only execute `git add` and `git commit` after user confirms
4. **Allow modifications**: User can modify the commit message or skip commit

## Before Commit Checklist

- [ ] No hardcoded secrets
- [ ] No console.log statements
- [ ] Tests pass
- [ ] Code formatted
- [ ] No linting errors

## Branch Naming

```
feat/<feature-name>      # New features
fix/<issue-description>  # Bug fixes
refactor/<scope>         # Code improvements
docs/<change>            # Documentation
```

## Pull Request Guidelines

- Keep PRs small and focused
- Include tests
- Update documentation
- Link related issues

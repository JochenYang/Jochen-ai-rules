---
argument-hint: <create|list|cleanup|switch|current> [<feature-name>] [-b|--base <branch>] [-f|--force]
description: Git Worktree management - create isolated worktrees, install deps, run tests, list worktrees, cleanup completed features
---

# Branch Command

Git Worktree management for isolated feature development. Creates separate working directories to avoid polluting the main branch, then enters the worktree and sets up the project.

## Usage

`/branch [action] [arguments]`

## argument-hint Format

```
/branch create <feature-name> [-b <base-branch>]
/branch list
/branch cleanup <name> [-f]
/branch switch <name>
/branch current
```

## Actions

### create

Create a new worktree for a feature branch and enter it:

```
/branch create <feature-description>
/branch create <feature-description> -b <base-branch>
```

**Options:**
- `-b, --base <branch>` - Base branch to create from (default: current branch)

**Examples:**
```
/branch create add-notification-system
/branch create 添加用户通知功能
/branch create fix-auth-bug -b develop
/branch create refactor-api -b main
```

**Enhanced Workflow (following Superpowers pattern):**

1. **Check existing worktree directory:**
```bash
ls -d ../.worktrees 2>/dev/null || ls -d ../worktrees 2>/dev/null
```

2. **Verify directory is gitignored:**
```bash
git check-ignore -q ../worktrees 2>/dev/null || git check-ignore -q ../.worktrees 2>/dev/null
```
If NOT ignored, add to .gitignore first.

3. **Detect project name** (from package.json or git remote)

4. **Create worktree:**
```bash
git worktree add "<worktree-path>" -b "feat/<feature-name>"
```

5. **Enter the worktree:**
```bash
cd "<worktree-path>"
```

6. **Run project setup** (auto-detect):
```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

7. **Verify clean baseline** (run tests):
```bash
# Node.js
npm test

# Python
pytest

# Rust
cargo test
```

8. **Report status:**
```
✓ Worktree ready at <path>
✓ Dependencies installed
✓ Tests passing (<N> tests)
Ready to implement <feature-name>
```

**Smart Naming:**
- Input: `添加用户通知功能` → Branch: `feat/add-user-notification`
- Input: `fix the login bug` → Branch: `feat/fix-login-bug`
- Worktree: `<project-name>-add-user-notification/`

### list

List all worktrees:

```
/branch list
```

Shows:
- Branch name
- Worktree path
- Current status (clean/dirty)

### cleanup

Remove a worktree:

```
/branch cleanup <name>
/branch cleanup <feature-name> --force
```

**Options:**
- `-f, --force` - Force cleanup even if branch has uncommitted changes

**Enhanced Workflow:**

1. **Check if worktree is clean:**
```bash
git status --porcelain
```

2. **Warn if dirty** (unless --force)

3. **Remove worktree:**
```bash
git worktree remove <worktree-path>
git branch -d <branch-name>
```

4. **Report:**
```
✓ Removed worktree <name>
✓ Deleted branch <branch-name>
```

### switch

Switch to a worktree:

```
/branch switch <name>
/branch switch <feature-name>
```

**Enhanced Workflow:**

1. Check worktree exists
2. cd into the worktree
3. Run `npm install` if needed
4. Run tests to verify baseline
5. Report ready

### current

Show current worktree info:

```
/branch current
```

Displays:
- Current branch
- Worktree path
- Whether it's the main worktree or a feature worktree

## Worktree Directory Structure

```
parent-directory/
├── project-name/                    # Main worktree (original repo)
├── worktrees/
│   ├── project-name-add-feature1/  # Feature worktree 1
│   └── project-name-add-feature2/  # Feature worktree 2
```

## Best Practices

1. **One feature = One worktree**: Keep each feature isolated
2. **Descriptive names**: Use `add-user-auth` not `feature1`
3. **Clean up after merge**: Use `/branch cleanup` after PR is merged
4. **Verify tests pass**: Always verify baseline before starting work
5. **Check gitignore**: Ensure worktree directory is ignored

## Example Workflow

```bash
# Start a new feature (supports Chinese)
/branch create 添加用户通知功能

# Workflow:
# 1. Check existing worktrees directory
# 2. Verify is gitignored
# 3. Create worktree
# 4. Enter directory
# 5. Run npm install
# 6. Run npm test
# 7. Report ready

# Output:
# ✓ Worktree ready at ../myproject-notification
# ✓ Dependencies installed
# ✓ Tests passing (42 tests)
# Ready to implement notification feature

# Now in worktree - proceed with development:
/plan add notification feature
... implement ...
/commit "feat: add notification feature"

# After PR is merged, clean up
/branch cleanup notification
```

## Safety Features

- **Gitignore verification**: Ensures worktree directory is ignored before creating
- **Test baseline verification**: Runs tests to ensure clean starting point
- **No accidental main branch deletion**: Cannot delete main/master branch
- **Uncommitted changes warning**: Warns before cleaning up dirty worktrees
- **Path validation**: Checks that worktree path doesn't already exist
- **Project name detection**: Automatically uses actual project name

## Arguments

$ARGUMENTS:

- `create <description>` - Create new worktree with feature branch (supports Chinese/English), installs deps, runs tests
- `list` - List all worktrees
- `cleanup <name>` - Remove a worktree and branch
- `switch <name>` - Enter a worktree, install deps, verify tests
- `current` - Show current worktree info

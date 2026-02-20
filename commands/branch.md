# Branch Command

Git Worktree management for isolated feature development. Creates separate working directories to avoid polluting the main branch.

## Usage

`/branch [action] [arguments]`

## Project Name Detection

The command automatically detects the project name to use for worktree directories:

1. **From package.json** (if exists): Uses the `name` field
2. **From git remote URL**: Extracts repo name (e.g., `my-awesome-project` from `https://github.com/user/my-awesome-project.git`)

## Actions

### create

Create a new worktree for a feature branch:

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

**What it does:**
1. Detects project name automatically
2. Converts feature description to slug format
3. Creates a new branch named `feat/<slugified-name>`
4. Creates a worktree at `../<project-name>-<slugified-name>/`
5. Checks out the new branch in that worktree
6. Provides instructions for entering the new worktree

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

**What it does:**
1. Removes the worktree directory
2. Deletes the branch (unless it has uncommitted changes)
3. Cleans up git reference

### switch

Switch to a worktree:

```
/branch switch <name>
/branch switch <feature-name>
```

Navigates to the worktree directory and provides guidance.

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
├── project-name-add-feature1/       # Feature worktree 1
├── project-name-add-feature2/       # Feature worktree 2
└── project-name-fix-bug/          # Bugfix worktree
```

## Best Practices

1. **One feature = One worktree**: Keep each feature isolated
2. **Descriptive names**: Use `add-user-auth` not `feature1`
3. **Clean up after merge**: Use `/branch cleanup` after PR is merged
4. **Commit Design Docs**: If using design docs, commit them to preserve history

## Example Workflow

```bash
# Start a new feature (supports Chinese)
/branch create 添加用户通知功能

# Or in English
/branch create add user profile

# In the new worktree, use normal commands:
/plan add user profile feature
... implement ...
/commit "feat: add user profile feature"

# After PR is merged, clean up
/branch cleanup add-user-profile
```

## Safety Features

- **No accidental main branch deletion**: Cannot delete main/master branch
- **Uncommitted changes warning**: Warns before cleaning up dirty worktrees
- **Path validation**: Checks that worktree path doesn't already exist
- **Project name detection**: Automatically uses actual project name

## Arguments

$ARGUMENTS:

- `create <description>` - Create new worktree with feature branch (supports Chinese/English)
- `list` - List all worktrees
- `cleanup <name>` - Remove a worktree and branch
- `switch <name>` - Show how to switch to a worktree
- `current` - Show current worktree info

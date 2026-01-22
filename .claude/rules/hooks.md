# Hooks System

## Hook Types

| Type | Trigger | Purpose |
|------|---------|---------|
| **PreToolUse** | Before tool execution | Validation, checks, reminders |
| **PostToolUse** | After tool execution | Auto-format, checks |
| **PreCompact** | Before context compaction | Save state |
| **SessionStart** | New session starts | Load previous context |
| **Stop** | Session ends | Final verification, persistence |

## Current Active Hooks

### PreToolUse
- **git push review**: Shows diff stats before pushing
- **tmux reminder**: Suggests tmux for dev server and long commands
- **compact suggestion**: Suggests `/compact` after multiple edits

### PostToolUse
- **Prettier auto-format**: Auto-formats JS/TS files after edit
- **console.log warning**: Warns about console.log statements

### Stop
- **console.log audit**: Final check for console.log in modified files
- **Session persistence**: Saves session state to `~/.claude/sessions/`
- **Finish sound**: Plays completion sound

### PreCompact
- **State save**: Saves state before context compaction

### SessionStart
- **Context load**: Notifies about recent sessions and learned skills

## Hook Configuration

All hooks are configured in `~/.claude/settings.json` under the `hooks` key.

Example:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "tool == \"Bash\" && tool_input.command matches \"git push\"",
      "hooks": [{
        "type": "command",
        "command": "git diff --stat"
      }]
    }]
  }
}
```

## Hook Matchers

Common matchers:
- `tool == "Bash"` - All bash commands
- `tool == "Edit"` - File edits
- `tool == "Write"` - File creation
- `tool_input.command matches "pattern"` - Match command pattern
- `tool_input.file_path matches "pattern"` - Match file path pattern

## Hook Best Practices

1. **Use hooks for enforcement**: Code quality checks, formatting, warnings
2. **Keep hooks fast**: Long-running hooks slow down Claude
3. **Don't block unnecessarily**: Use warnings over blocking where possible
4. **Test hooks**: Verify hook behavior before adding to settings

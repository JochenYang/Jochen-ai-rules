# /learn - Extract Reusable Patterns

Analyze the current session and extract any patterns worth saving as skills.

## Trigger

Run `/learn` at any point during a session when you've solved a non-trivial problem.

## What to Extract

Look for:

1. **Error Resolution Patterns**
   - What error occurred?
   - What was the root cause?
   - What fixed it?
   - Is this reusable for similar errors?

2. **Debugging Techniques**
   - Non-obvious debugging steps
   - Tool combinations that worked
   - Diagnostic patterns

3. **Workarounds**
   - Library quirks
   - API limitations
   - Version-specific fixes

4. **Project-Specific Patterns**
   - Codebase conventions discovered
   - Architecture decisions made
   - Integration patterns

## Output Format

Topic file at `~/.claude/projects/[project-encoded-path]/memory/[pattern-name].md`:

```markdown
# [Descriptive Pattern Name]

**Extracted:** [Date]
**Context:** [Brief description of when this applies]

## Problem
[What problem this solves - be specific]

## Solution
[The pattern/technique/workaround]

## Example
[Code example if applicable]

## When to Use
[Trigger conditions - what should activate this skill]
```

`MEMORY.md` entry to add/update under the appropriate section:

```markdown
- [pattern-name].md — [one-line summary of what it covers]
```

## Process

1. Review the session for extractable patterns
2. Identify the most valuable/reusable insight
3. **Read existing `MEMORY.md`** in the project's memory directory (if it exists):
   - Understand what topics Claude Code's auto memory has already recorded
   - Check if the new pattern overlaps with or extends an existing topic file
4. Decide: **merge into an existing topic file** or **create a new one**
   - Merge: append the pattern to the relevant existing file
   - New: create `[pattern-name].md` with the format above
5. **Update `MEMORY.md` index**: add or update the entry pointing to the topic file; if `MEMORY.md` does not exist yet, create it and add the new entry
6. Show the user a summary of changes and ask for confirmation before writing

## Notes

- Don't extract trivial fixes (typos, simple syntax errors)
- Don't extract one-time issues (specific API outages, etc.)
- Focus on patterns that will save time in future sessions
- Keep topic files focused — one theme per file, multiple patterns per theme is fine
- `MEMORY.md` is auto-loaded (first 200 lines); topic files are loaded on demand — keep the index concise

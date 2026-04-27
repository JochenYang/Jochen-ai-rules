---
description: Write a structured handoff before reset, or read one back to resume long-running development work.
---

Use the `handoff` skill as the execution authority for this command.

The user invoked:

- `/handoff $ARGUMENTS`

Parse the first argument as the mode:

- `write`
- `read`

Treat the remaining arguments as either:

- a topic slug when writing a new handoff
- an explicit handoff file path when reading or updating an existing handoff

Execution rules:

- Follow `skills/handoff/SKILL.md` exactly.
- Use `skills/handoff/references/handoff-template.md` for document structure.
- Use `skills/handoff/references/handoff-vs-compact.md` when the user is
  deciding between handoff and compact.

Behavior contract:

- `/handoff write [topic-or-existing-file]`
  - if the argument is an existing handoff file, update that file
  - otherwise create a new timestamped handoff under
    `repo/progress/handoffs/`
- `/handoff read [handoff-file]`
  - if a file is specified, read that file first
  - otherwise read the latest file under `repo/progress/handoffs/`

When writing:

- produce a structured execution artifact, not a chat recap
- include goal, status, key files, verification, risks, blockers, and one next
  action
- include a `Changed Files` section populated from `skills/handoff/scripts/git_changes.py` when git evidence exists
- if git is unavailable, clean, or does not cover important session work, fall back to `skills/handoff/scripts/session_changes.py`
- include per-file line ranges and short snippets when available, and mark session-derived entries with confidence
- preserve facts vs assumptions clearly

When reading:

- restate goal, verified status, risks, and immediate next action briefly
- inspect referenced files before broad exploration
- call out stale or contradictory repo state before continuing

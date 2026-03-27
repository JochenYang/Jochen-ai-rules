---
name: handoff
description: Create and resume structured manual session handoffs for long-running development work. Use when approaching context limits, before manual reset, before switching models or IDEs, after a milestone, or when automatic compact would lose important implementation state.
---

# Handoff

Use this skill to preserve task state across manual context resets with a
structured handoff artifact. This is the preferred path for long-running
engineering work when exact status, decisions, risks, and next actions matter
more than keeping the current thread alive.

## Deterministic Resolver

Before deciding which handoff file to read or write, run the local resolver
script first so path selection does not depend on model judgment.

Path resolution rule:

- Resolve `scripts/handoff.py` relative to this installed `SKILL.md`, not
  relative to the active repository root.
- Do not try `python scripts/handoff.py ...` from the project root unless that
  repository really contains its own copy of the script.
- Preferred invocation shape:
  - `cd <installed-handoff-skill-dir> && python scripts/handoff.py ... --project-root <active-repo-root>`
  - or call the installed script by absolute path directly.

Preferred command:

```bash
cd <installed-handoff-skill-dir> && python scripts/handoff.py <write|read> [target] --project-root <active-repo-root>
```

Fallback when `python` is unavailable:

```bash
cd <installed-handoff-skill-dir> && python3 scripts/handoff.py <write|read> [target] --project-root <active-repo-root>
```

The script is the source of truth for:

- the handoff directory: `repo/progress/handoffs/`
- whether `write` creates a new file or updates an existing one
- which file `read` should load by default
- whether the provided project root accidentally points at the installed skill
  directory instead of the active repository

If the script result conflicts with intuition, trust the script.

Critical path rule:

- The script path belongs to the installed `handoff` skill.
- `--project-root` must point to the active repository root, not the skill
  installation directory.
- Do not treat `~/.claude/skills/handoff` or any similar install path as the
  project root.
- Do not treat the active repository root as the location of
  `scripts/handoff.py` unless the repository explicitly contains that file.

## Core Position

Manual handoff is not a total replacement for automatic compact.

- Use **handoff** when the task is long-running, multi-file, multi-phase, or
  the current thread has accumulated noise, dead branches, or partial analysis.
- Use **compact** only when continuity is lightweight and the thread itself is
  still the best container for context.

The point of handoff is to reset into a cleaner context while keeping a
reviewable, explicit, file-backed artifact.

## Modes

### Write Mode

Create or update a handoff document before reset.

Default output path:

- `{project}/repo/progress/handoffs/YYYY-MM-DD-HHMM-<topic>.md`

File lifecycle:

- Default to creating a new handoff file for each real checkpoint, reset point,
  or milestone pause. Treat each file as a timestamped snapshot.
- Update an existing handoff file only when the user explicitly names that file
  and asks to continue or revise it.
- Otherwise, always create a new handoff file instead of inferring which older
  file should be overwritten.
- Older handoff files are part of the project’s development trail and may be
  used later for review, audit, or reconstructing why earlier decisions were
  made.

Trigger when:

- approaching context limits
- preparing for a manual reset
- switching models, IDEs, or operator sessions
- ending a milestone with meaningful state to resume later
- the thread contains too much exploration noise for compact to be reliable

Execution steps:

1. Run the installed resolver script first, from the installed skill directory
   or by absolute script path.
2. Example:
   `cd <installed-handoff-skill-dir> && python scripts/handoff.py write [topic-or-existing-file] --project-root <active-repo-root>`
3. Use the returned JSON `path` as the only valid handoff target.
4. Inspect the current goal, active branch, working tree state, files touched,
   commands run, test status, and remaining work.
5. Separate facts from assumptions. If something was not verified, say so.
6. Write a concise, structured handoff into the resolved file using
   `references/handoff-template.md`.
7. Record exact file paths, decisions, blockers, risks, failed commands,
   partial work, and the next recommended action.
8. Tell the user exactly which handoff file was written and should be read
   after reset.

Mandatory rules:

- Prefer explicit state over conversational recap.
- Write what the next session needs to continue work immediately.
- Trust the resolver script for file targeting instead of inferring paths.
- Include branch and working tree state.
- Include verification status: passed, failed, or not run.
- Include a short “resume order” so the next session knows where to start.

Do not:

- dump the raw chat transcript
- hide uncertainty behind confident prose
- say tests passed if they were not rerun
- omit blockers, broken attempts, or risky assumptions
- write a handoff that lacks a concrete next action

### Read Mode

Resume from a handoff document after reset.

Trigger when:

- a fresh session needs to continue prior work
- the user provides a handoff file path
- the task was previously paused with a saved handoff artifact

Execution steps:

1. Run the installed resolver script first, from the installed skill directory
   or by absolute script path.
2. Example:
   `cd <installed-handoff-skill-dir> && python scripts/handoff.py read [handoff-file] --project-root <active-repo-root>`
3. If the script returns `no_handoff_found`, `specified_handoff_not_found`, or
   `invalid_project_root`,
   report that exact state instead of guessing alternatives.
4. Read the returned JSON `path` and use that file as the primary continuity
   artifact.
5. Restate the current goal, verified status, open risks, and immediate next
   actions in a few lines.
6. Start from the files, commands, and checkpoints named in the handoff before
   doing broad repo exploration.
7. If the handoff conflicts with the current working tree or branch state, call
   that out immediately.
8. Continue implementation from the recorded next action instead of re-planning
   the entire project.

Mandatory rules:

- Treat the handoff as the primary continuity artifact.
- Treat the resolver script output as the primary source of file selection.
- Verify critical assumptions against the current repo state before acting.
- Prefer reading the referenced files directly before widening search.
- Surface stale or contradictory handoffs instead of silently trusting them.
- Use older handoff files only when the user points to them or when the latest
  handoff clearly depends on earlier checkpoints for historical context.

Do not:

- ignore the handoff and start broad exploration first
- assume the repo is unchanged since the handoff was written
- re-summarize everything if the handoff already provides a good resume path

## Handoff Quality Bar

A good handoff should answer these questions quickly:

- What is the exact task and current phase?
- What has already been completed?
- Which files matter first?
- What commands or tests were run, and what happened?
- What is blocked, risky, or still unknown?
- What should the next session do first?

If the next session still needs to reconstruct basic status from scratch, the
handoff is not good enough.

## Recommended Structure

Always follow the template in `references/handoff-template.md`.

The essential sections are:

- task and objective
- current status
- branch and working tree state
- key files and why they matter
- decisions already made
- verification summary
- blockers and risks
- next actions

## Compact Vs Handoff

Read `references/handoff-vs-compact.md` when:

- the user asks whether handoff is better than compact
- you need to decide whether to write a handoff now
- you need language for explaining the tradeoff

Short version:

- **Compact** keeps continuity inside the thread.
- **Handoff** externalizes continuity into a file and expects a reset.
- For complex engineering work, handoff is often safer because it is explicit,
  inspectable, and easier to validate before resuming.

## References

Read only as needed:

- `scripts/handoff.py`
- `references/handoff-template.md`
- `references/handoff-vs-compact.md`

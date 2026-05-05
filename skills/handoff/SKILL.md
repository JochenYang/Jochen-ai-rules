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
- Pass the active project path with `--project-root`. If `repo/progress/`
  exists only in a parent workspace directory, the resolver should use the
  nearest ancestor that already contains it.
- Preferred invocation shape:
  - `cd <installed-handoff-skill-dir> && python scripts/handoff.py ... --project-root <active-repo-root>`
  - or call the installed script by absolute path directly.

Preferred command:

```bash
cd <installed-handoff-skill-dir> && python scripts/handoff.py <write|read> <topic-or-existing-file> --project-root <active-repo-root>
```

Fallback when `python` is unavailable:

```bash
cd <installed-handoff-skill-dir> && python3 scripts/handoff.py <write|read> [target] --project-root <active-repo-root>
```

The script is the source of truth for:

- the handoff directory: `repo/progress/handoffs/`
- whether the requested project path should stay in place or resolve upward to
  a parent workspace that already owns `repo/progress/`
- whether `write` creates a new file or updates an existing one
- which file `read` should load by default
- whether the provided project root accidentally points at the installed skill
  directory instead of the active repository
- `scripts/git_changes.py` is the source of truth for changed files, line
  ranges, and diff/content snippets that should appear in the handoff body
- `scripts/session_changes.py` is the fallback formatter when git evidence is
  unavailable, clean, or does not cover important changes already completed in
  the current session

If the script result conflicts with intuition, trust the script.

Critical path rule:

- The script path belongs to the installed `handoff` skill.
- `--project-root` must point to the active project path, not the skill
  installation directory.
- If implementation work happens in a nested subproject but `repo/progress/`
  belongs to a parent workspace, passing the subproject path is valid; the
  resolver should lift to the nearest matching ancestor automatically.
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

## Language Adaptation

The handoff document should be written in the same language as the current
conversation/interaction:

| Conversation Language | Handoff Document Language   |
|-----------------------|-----------------------------|
| 中文                  | 中文                        |
| English               | English                     |
| 日本語                | 日本語                      |
| Other                 | Match conversation language |

**Implementation rule**: Detect the language of the current conversation from
system context (user's input language, conversation history). Write all handoff
content in that language. Section headers, field names, and body text should all
be in the detected language.

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
   `cd <installed-handoff-skill-dir> && python scripts/handoff.py write <topic-or-existing-file> --project-root <active-repo-root>`
3. Run the installed change-summary script before writing the handoff body:
   `cd <installed-handoff-skill-dir> && python scripts/git_changes.py --project-root <active-repo-root>`
4. Use the returned JSON `path` from `scripts/handoff.py` as the only valid
   handoff target.
5. If `scripts/git_changes.py` returns `evidence_source=git` with meaningful
   file changes, use its returned JSON `markdown` to populate the
   `Changed Files` section.
6. If `scripts/git_changes.py` reports `git-unavailable`, a clean tree, or
   misses important changes that already happened in this session, build a
   session file manifest from the current conversation and run:
   `cd <installed-handoff-skill-dir> && python scripts/session_changes.py`
   Pass JSON on stdin with `files[].path`, `status`, `summary`, optional
   `line_ranges`, optional `snippets`, and `confidence`.
7. In session-derived mode, clearly mark confidence and do not claim exact line
   ranges unless they were directly verified.
8. Inspect the current goal, active branch, working tree state, files touched,
   commands run, test status, and remaining work.
9. Separate facts from assumptions. If something was not verified, say so.
10. Write a concise, structured handoff into the resolved file using
   `references/handoff-template.md`.
11. Record exact file paths, decisions, blockers, risks, failed commands,
   partial work, and the next recommended action.
12. Tell the user exactly which handoff file was written and should be read
   after reset.

Mandatory rules:

- Prefer explicit state over conversational recap.
- Write what the next session needs to continue work immediately.
- Trust the resolver script for file targeting instead of inferring paths.
- Always provide a topic slug for write mode. The resolver script will return a
  `"topic_required"` error if the topic is missing.
- Include branch and working tree state.
- The `Changed Files` section MUST be populated from `scripts/git_changes.py`
  output (or `scripts/session_changes.py` when git evidence is insufficient).
  Never write file change entries from memory.
- If `scripts/git_changes.py` reports a clean tree or unavailable git, switch
  to session-derived evidence whenever the current session still touched files
  that matter for resume.
- If neither git evidence nor session-derived evidence exists, say that
  explicitly instead of omitting the section.
- Mark session-derived file entries with confidence and approximate ranges when
  precision is not directly verified.
- Include verification status: passed, failed, or not run.
- Include a short “resume order” so the next session knows where to start.

Do not:

- dump the raw chat transcript
- hide uncertainty behind confident prose
- say tests passed if they were not rerun
- omit blockers, broken attempts, or risky assumptions
- present session-derived file edits as exact git-verified diff evidence
- write a handoff that lacks a concrete next action

### Session End Checklist (MANDATORY)

Before finalizing the handoff, confirm:

- [ ] **Environment clean**: No uncommitted changes that break the build
- [ ] **Changed files captured**: File paths, line ranges, and snippets are in
      the handoff when changes exist
- [ ] **Committed files captured**: If commits were made during this session,
      they appear in the Changed Files section with status committed-today
- [ ] **Fallback used when needed**: If git was unavailable or clean, the
      handoff still records session-derived touched files when relevant
- [ ] **Tests run**: At least basic sanity tests executed, results recorded
- [ ] **Errors documented**: Any known failures or TODOs are in the handoff
- [ ] **Next action clear**: The next session knows exactly what to do first
- [ ] **Git status**: Working tree state captured (staged/unstaged/commit)

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

## Good vs Bad Examples

### Good Handoff

```md
# Handoff: User auth refactor

## Task
- Objective: Refactor auth module to support OAuth2
- Current phase: Core implementation 70% done
- Requested outcome: Complete auth flow by EOD

## Repository State
- Repo: d:/codes/myapp
- Branch: feat/oauth-refactor
- Working tree: 3 modified files staged
- Relevant commit: a3f2b1c "add auth base structure"

## Current Status
- Completed: Token generation, user lookup
- In progress: OAuth callback handler
- Not started: Integration tests, docs

## Key Files
- src/auth/token.ts: Token generation logic
- src/auth/oauth.ts: OAuth flow (work here next)
- src/db/user.ts: User model

## Decisions Already Made
- Decision: Use JWT for tokens, not sessions
  Reason: Stateless, better for API auth
- Decision: Store OAuth tokens encrypted
  Reason: Security requirement

## Verification
- Commands run:
  - npm test -> passed
  - npm run lint -> passed
- Tests: 12/15 passing for auth module

## Risks And Blockers
- Risk: OAuth callback URL may need ngrok for dev
  Impact: Medium
  Mitigation: Already have ngrok config ready

## Resume Order
1. Read src/auth/oauth.ts and confirm callback handler structure
2. Run npm test to verify current state
3. Implement callback handler in oauth.ts

## Next Action
- Implement OAuth callback handler in src/auth/oauth.ts
```

### Bad Handoff (Don't Do This)

```md
# Handoff: Auth work

## Task
Working on auth, it's mostly done but some stuff left.

## Current Status
Did some auth stuff, might need more tests.

## Next Action
Keep working on auth.
```

| Aspect       | Good                     | Bad                |
|--------------|--------------------------|--------------------|
| Specificity  | Exact file paths         | Vague "auth stuff" |
| Verification | Test results listed      | Not mentioned      |
| Resume path  | Clear 1-2-3 steps        | "keep working"     |
| State        | Branch, working tree     | Unknown            |
| Blockers     | Explicit with mitigation | Hidden             |

## Recommended Structure

Always follow the template in `references/handoff-template.md`.

The essential sections are:

- task and objective
- current status
- branch and working tree state
- changed files with line ranges and snippets from `scripts/git_changes.py`
- session-derived change evidence when git is unavailable, clean, or incomplete
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
- `scripts/git_changes.py`
- `scripts/session_changes.py`
- `references/handoff-template.md`
- `references/handoff-vs-compact.md`

## Boundaries

- Focus on preserving state and resumability, not on implementing new feature work inside the handoff itself.
- Prefer explicit status capture over speculative future planning.
- Do not replace a normal compact or active implementation flow unless handoff is actually needed.

## Escalation Rules

Pause and ask the owner before:

- overwriting an existing handoff artifact with materially different state
- choosing handoff instead of compact when thread continuity is still sufficient
- marking uncertain implementation details as confirmed facts

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why a handoff artifact is needed now
2. `Primary Deliverable` - handoff path and captured status summary
3. `Execution Evidence` - resolver result, changed-files summary, session
   evidence fallback when used, files written, and state included
4. `Risks / Open Questions` - missing evidence, pending checks, or resume hazards
5. `Next Action` - the exact resume instruction or next operator step

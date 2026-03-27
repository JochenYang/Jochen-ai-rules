# Handoff Vs Compact

Use this note when deciding whether to rely on automatic compact or to create a
manual handoff artifact.

## Mental Model

- **Compact** compresses the active thread so the same session can continue with
  a smaller context footprint.
- **Handoff** writes a durable artifact, then expects a manual reset and a fresh
  session to resume from that artifact.

## Why Handoff Often Wins For Long-Running Development

Manual handoff is stronger when:

- the task spans many files or multiple hours
- the thread contains dead ends, partial hypotheses, or abandoned branches
- correctness depends on remembering exact repo state, commands, or blockers
- you want a reviewable artifact instead of an opaque compressed memory
- you need continuity across tools, sessions, or operators

The reset is a feature, not a bug: it clears noise and forces the next session
to load only the information that still matters.

## When Compact Is Still Fine

Compact is usually enough when:

- the interruption is short
- the task is simple or narrowly scoped
- the thread is still clean and mostly linear
- you do not need a durable external artifact

## Recommended Policy

- Prefer **handoff** before manual reset on complex engineering work.
- Prefer **handoff** at milestone boundaries, before model switches, and before
  pausing unfinished implementation.
- Prefer **compact** only for lightweight continuity inside the same thread.

## Failure Modes To Avoid

### Bad Compact Use

- continuing a noisy thread when key facts are buried
- trusting compressed continuity for fragile implementation state

### Bad Handoff Use

- writing a vague summary with no resume order
- omitting failed commands, blockers, or repo state
- treating the handoff as a transcript instead of an execution artifact

## Litmus Test

If the next fresh session can resume the work in a few minutes without
reconstructing the whole conversation, the handoff succeeded.

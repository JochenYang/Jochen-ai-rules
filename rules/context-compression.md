---
name: context-compression
description: Mandatory guidelines for compressing conversation context without losing critical state. Load when triggering compress or approaching context limits.
---

# Context Compression Guidelines

**RULE TYPE**: Mandatory context management discipline.

## Pre-Compression Self-Check (Three-Question Decision Tree)

Before using `compress`, answer three questions:

1. **Is this segment closed?** (task done / conclusion reached / exploration ended)
   - No → Do not compress; wait for natural closure.
2. **What critical information would be lost?**
   - Code line numbers, file paths, error stacks → MUST be preserved in summary.
   - User constraints/decisions/boundaries → Quote verbatim when possible.
3. **Will this information be needed later?**
   - Yes (open bugs, unimplemented features) → Do not compress, or anchor with explicit summary.
   - No → Safe to compress.

## MUST Preserve (Cannot Be Covered by Summary)

- Explicit constraints, boundaries, preferences issued by the user
- Root causes that have been located but not yet fixed
- Active implementation details (open tasks, uncommitted code)
- Critical file paths, function signatures, data flow relationships

## Allowed to Compress

- Test output that has already been verified
- Resolved bug investigation history
- Dead-end paths from multiple attempts (keep conclusion only)
- Completed and committed change retrospectives

## Summary Quality Requirements

- **Completeness**: Include all key conclusions, paths, and decision rationales from the compressed segment.
- **Traceability**: Quote user intent verbatim when involved.
- **Unambiguity**: Avoid vague summarization; keep 1-2 extra lines of detail if uncertain.

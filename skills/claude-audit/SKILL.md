---
name: claude-audit
description: Audit all .claude/*.md files for redundant instructions, verbose phrasing, and content that could move to memory. Use when user wants to optimize their Claude configuration rules.
---

# Claude Audit Skill

Analyze all `.claude/` configuration files to find optimization opportunities.

## Workflow

1. **Scan files**: Find all `.md` files in `.claude/` directory (rules/, commands/, agents/, skills/)
2. **Analyze each file** for:
   - **Redundant instructions**: Rules that repeat across multiple files
   - **Verbose phrasing**: Overly wordy explanations that can be concise
   - **Move to memory candidates**: Content rarely needed in context but referenced
3. **Present findings** in a structured format
4. **Ask user**: Which optimizations to implement?

## Analysis Criteria

### Redundant Instructions
- Same rule mentioned in multiple files
- Overlapping scope between rules and agents/skills
- Duplicate workflow descriptions

### Verbose Phrasing
- Long paragraphs that can be shortened
- Redundant examples
- Over-explanation of obvious concepts

### Memory Candidates
- Static reference material rarely changing
- Detailed examples not needed in every session
- Background context that can be loaded on-demand

## Output Format

```markdown
# Claude Audit Report

## Files Analyzed
- [file count] files reviewed

## Findings

### Redundant Instructions
| File | Issue | Recommendation |
|------|-------|-----------------|
| file.md | Description | Action |

### Verbose Phrasing
| File | Section | Suggestion |
|------|---------|------------|
| file.md | section | concise version |

### Memory Candidates
| File | Content | Rationale |
|------|---------|-----------|
| file.md | section | why to move |

## Summary
- X redundant rules
- Y verbose sections
- Z candidates for memory

## Action Items
[ ] Implement specific fix
```

Present findings to the user and ask which to implement

## Boundaries

- Focus on Claude configuration quality, duplication, and token efficiency.
- Do not rewrite unrelated product code or project business logic.
- Do not auto-apply configuration changes without the owner's confirmation.

## When NOT to Use

- Editing product/application code instead of auditing `.claude` instructions
- Running broad refactors without first producing an audit report
- Applying configuration deletions/merges without owner approval

## Escalation Rules

Pause and ask the owner before:

- deleting or heavily rewriting existing rules instead of proposing targeted reductions
- merging files in ways that change the project's instruction hierarchy
- making assumptions about which rules should move to memory versus stay in active context

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why a Claude configuration audit was needed
2. `Primary Deliverable` - findings summary and recommended actions
3. `Execution Evidence` - files analyzed and overlap patterns discovered
4. `Risks / Open Questions` - ambiguity, tradeoffs, or scope concerns
5. `Next Action` - the specific optimization step to review or implement next

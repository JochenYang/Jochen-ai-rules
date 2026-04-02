---
name: skills-audit
description: List all installed skills with line counts and analyze for improvement opportunities. Use when user wants to review, optimize, or clean up their skill collection.
---

# Skills Audit Skill

Analyze all installed skills to find optimization opportunities.

## Workflow

1. **Scan skills directories**:
   - Global: `~/.claude/skills/`
   - Project: `.claude/skills/`
2. **Collect metadata** for each skill:
   - Name from SKILL.md frontmatter
   - Line count of SKILL.md
   - File count in skill directory
3. **Analyze for improvement opportunities**:
   - **Overlapping scopes**: Similar functionality across skills
   - **Token efficiency**: Skills with excessive line counts
   - **Consolidation candidates**: Skills that could be merged
4. **Present findings** in structured format
5. **Ask user**: Which skills to review or optimize?

## Analysis Criteria

### Overlapping Scopes
- Two or more skills handling similar domains
- Redundant triggers or descriptions
- Conflicting instructions

### Token Efficiency
- SKILL.md > 500 lines: Consider splitting
- Excessive examples or explanations
- Content that could move to references/

### Consolidation Candidates
- Skills frequently used together
- Related skills in same domain
- Small skills (<50 lines) that could merge

## Output Format

```markdown
# Skills Audit Report

## Summary
- Total skills: X
- Total lines: Y
- Project skills: A
- Global skills: B

## Skills List

| Skill | Location | Lines | Files |
|-------|----------|-------|-------|
| name | global/project | N | M |

## Findings

### Overlapping Scopes
| Skill A | Skill B | Overlap |
|---------|---------|---------|
| a.md | b.md | description |

### Token Efficiency Issues
| Skill | Lines | Recommendation |
|-------|-------|---------------|
| name | 600+ | Split into references/ |

### Consolidation Candidates
| Skills | Rationale |
|--------|-----------|
| a + b | Frequently used together |

## Action Items
[ ] Review skill: name
[ ] Split skill: name
[ ] Merge skills: a + b
```

Present findings to user and ask which to implement

## Boundaries

- Focus on skill inventory quality, overlap analysis, and optimization guidance.
- Do not merge, split, or rewrite skills automatically without owner confirmation.
- Treat token-efficiency suggestions as tradeoffs, not mandatory reductions.

## Escalation Rules

Pause and ask the owner before:

- recommending deletion of heavily used skills
- consolidating skills with partially overlapping but distinct responsibilities
- changing invocation patterns that could break existing workflows

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why a skills audit is appropriate now
2. `Primary Deliverable` - inventory summary and optimization recommendations
3. `Execution Evidence` - directories scanned, counts gathered, and overlaps found
4. `Risks / Open Questions` - migration cost, ambiguity, or retained complexity
5. `Next Action` - the highest-value cleanup or review step

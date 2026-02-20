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

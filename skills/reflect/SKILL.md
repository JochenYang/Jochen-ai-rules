---
name: reflect
description: Review current conversation, analyze tasks, errors, and user feedback, extract learning opportunities for skill improvement. Use when user says "reflect", "review session", "what did we learn", "session summary", or after completing a complex task.
---

# Reflect Skill

Review the current conversation and analyze:

## Analysis Questions

1. **Tasks Completed**: What features/bugfixes were implemented?
2. **Errors Encountered**: What issues came up and how were they resolved?
3. **User Feedback**: What did the user like/dislike?
4. **Patterns Discovered**: Any reusable patterns or workflows?
5. **Skill Gaps**: What skills are missing that would help?

## Output Format

```markdown
# Session Reflection

## Summary
[Brief overview of what was accomplished]

## Key Learnings
- [Learning 1]
- [Learning 2]

## Improvement Opportunities
- [Opportunity 1]
- [Opportunity 2]

## Skill Recommendations
- [New skill to create?]
- [Existing skill to improve?]

## Action Items
- [ ] Create new skill: [name]
- [ ] Update existing skill: [name]
- [ ] Add to memory: [pattern]
```

Present findings to the user and ask what to implement or save

## Examples

### Example 1: After Bug Fix Session
User says: "reflect on what we did"
Actions:
1. Review conversation history
2. Identify: bug root cause, solution approach, key learnings
3. Note: skill gaps discovered (e.g., missing debugging patterns)
4. Generate reflection report
Result: Structured learnings for future sessions

### Example 2: After Feature Development
User says: "what did we learn from this sprint"
Actions:
1. Analyze completed tasks
2. Identify patterns: repeated code structures, useful utilities
3. Discover improvement opportunities: better testing, refactoring candidates
4. Generate actionable recommendations
Result: Actionable improvement list

### Example 3: After Complex Debugging
User says: "review session and summarize"
Actions:
1. Trace problem identification flow
2. Document hypothesis-validation pattern used
3. Note tools/approaches that worked well
4. Extract reusable debugging strategy
Result: Debugging pattern for future reference

## Boundaries

- Focus on extracting lessons, patterns, and improvement opportunities from completed work.
- Do not rewrite history, hide failures, or fabricate successful verification.
- Do not mutate code by default unless the owner explicitly asks for follow-up implementation.

## When NOT to Use

- Active implementation tasks that require writing/fixing code now
- Requirement discovery sessions that need structured Q&A (use `requirements-interview`)
- Code/security audits that need defect-level findings (use `quality-assurance`)

## Escalation Rules

Pause and ask the owner before:

- turning reflection findings into direct code or rule changes
- concluding that a repeated issue is systemic without enough evidence
- writing retrospective notes to shared artifacts that could affect future workflows

## Lessons Log Integration (MANDATORY)

Every reflection session that produces at least one durable lesson MUST append
an entry to `repo/progress/lessons.md`. Rules:

1. Append at the **top** of the `## Entries` section (newest first); never
   overwrite or delete prior entries.
2. Use the template defined in `repo/progress/lessons.md` verbatim.
3. One concrete lesson per entry; if reflection surfaces N lessons, append N
   entries.
4. Before appending, scan recent entries to avoid duplicates. If the lesson is
   a refinement of an older one, mark the older as `Superseded by <date-title>`
   and add the new entry pointing back.
5. After appending, summarise the new entries in the chat output under
   `Primary Deliverable` and link to the file path.
6. If the session produced no durable lesson (pure execution, no surprises),
   say so explicitly and skip the file write.

## Final Output Contract (MANDATORY)

Every use of this skill should end with:

1. `Skill Fit` - why reflection is useful for this session or sprint
2. `Primary Deliverable` - lesson summary, patterns, recommendations, and the
   list of `repo/progress/lessons.md` entries appended (or an explicit
   "no entry appended" note with reason)
3. `Execution Evidence` - tasks reviewed, failures observed, and signals considered
4. `Risks / Open Questions` - uncertain conclusions or missing evidence
5. `Next Action` - the best improvement to adopt in the next cycle

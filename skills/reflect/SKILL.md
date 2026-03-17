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

---
description: Create a detailed implementation plan for features or refactoring. Invokes the dev-planner agent.
---

# Plan Command

Create a comprehensive, actionable implementation plan.

## Usage

```
/plan Add OAuth2 authentication with Google and GitHub
/plan Refactor the user service to use repository pattern
/plan Create a real-time notification system
```

## What This Does

1. **Requirements Clarification** - If the request is vague, actively ask questions to clarify:
   - Use case and user story
   - Expected behavior and edge cases
   - Performance requirements
   - Integration points
   - Success criteria
   - **Use AskUserQuestion tool for multi-turn brainstorming until requirements are clear**
2. **Requirements Analysis** - Understand the feature request completely
3. **Architecture Review** - Analyze existing codebase structure
4. **Step Breakdown** - Create detailed steps with file paths
5. **Implementation Order** - Prioritize by dependencies
6. **Testing Strategy** - Define what to test

## Clarification Questions (When Needed)

If the user's request lacks detail, **proactively ask** questions like:

- What problem does this solve for users?
- What's the expected input/output?
- Are there any performance requirements? (e.g., response time, concurrent users)
- How should errors be handled?
- What existing systems does this integrate with?
- What are the acceptance criteria?

**Continue asking until you have enough context to create a concrete plan.**

## Plan Format

```markdown
# Implementation Plan: [Feature Name]

## Overview
[2-3 sentence summary]

## Requirements
- [Requirement 1]
- [Requirement 2]

## Implementation Steps

### Phase 1: Foundation
1. **[Step Name]** (File: path/to/file.ts)
   - Action: Specific action
   - Why: Reason for this step
   - Dependencies: None / Requires step X

### Phase 2: Core Features
...

## Testing Strategy
- Unit tests: [files to test]
- Integration tests: [flows to test]

## Risks & Mitigations
- **Risk**: [Description]
  - Mitigation: [How to address]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

## Best Practices

- Be specific about file paths and function names
- Consider edge cases and error scenarios
- Each step should be verifiable
- Document why, not just what

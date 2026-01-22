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

1. **Requirements Analysis** - Understand the feature request completely
2. **Architecture Review** - Analyze existing codebase structure
3. **Step Breakdown** - Create detailed steps with file paths
4. **Implementation Order** - Prioritize by dependencies
5. **Testing Strategy** - Define what to test

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

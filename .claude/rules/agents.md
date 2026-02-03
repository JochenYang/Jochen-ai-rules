# Agent Usage Rules

**RULE TYPE**: Global mandatory guidelines for agent selection and invocation.

All agents must follow these rules when deciding which specialized agent to invoke.

## Available Specialized Agents

### dev-planner (Planning)
- **Color**: Blue 🔵
- **Description**: Planning expert for complex features and refactoring
- **Trigger**: New feature requirements, complex refactoring, structural changes
- **Output**: Detailed implementation plan with risk assessment and time estimates
- **Skills**: developer, api-designer, database-engineer

### code-implementer (Implementation)
- **Color**: Green 🟢
- **Description**: Production-ready code implementation specialist
- **Trigger**: After planning phase, for standard feature development
- **Output**: Clean, maintainable, well-documented code
- **Skills**: developer, quality-assurance

### tdd-guide (Test-Driven Development)
- **Color**: Purple 🟣
- **Description**: Test-driven development expert enforcing RED-GREEN-REFACTOR cycle
- **Trigger**: When test coverage is critical, bug fixes, or TDD workflow requested
- **Output**: Test cases and implementation with 80%+ coverage
- **Skills**: tdd-workflow, quality-assurance

### code-reviewer (Quality Assurance)
- **Color**: Yellow 🟡
- **Description**: Code quality, security, and performance auditor
- **Trigger**: After code changes, before merge, or as part of orchestration
- **Output**: Quality report with prioritized improvement suggestions
- **Skills**: quality-assurance, developer

### explorer (Deep Analysis)
- **Color**: Orange 🟠
- **Description**: Root cause analysis and deep debugging expert
- **Trigger**: Complex bugs, performance issues, system behavior investigation
- **Output**: Execution flow analysis and root cause identification
- **Skills**: performance-optimizer, developer

### bug-analyzer (Bug Investigation)
- **Color**: Red 🔴
- **Description**: Bug diagnosis and analysis specialist
- **Trigger**: Bug reports, error logs, crashes
- **Output**: Root cause analysis and fix strategy
- **Skills**: tdd-workflow, quality-assurance

### story-generator (Requirements)
- **Color**: Cyan 🔷
- **Description**: User story generation from various inputs
- **Trigger**: Need to document features as user stories
- **Output**: Structured user stories with acceptance criteria

### ui-sketcher (UI/UX Design)
- **Color**: Purple 🟣
- **Description**: UI/UX design and ASCII prototyping specialist
- **Trigger**: UI design needs, interface mockups
- **Output**: ASCII interface designs and interaction flows
- **Skills**: ui-ux-pro-max, frontend-design

## Standard Workflows

### Feature Development (Standard)
```
/orchestrate feature <description>
dev-planner → code-implementer → code-reviewer
```

### Feature Development (Test-Driven)
```
/orchestrate feature-tdd <description>
dev-planner → tdd-guide → code-reviewer
```

### Bug Fix
```
/orchestrate bugfix <description>
explorer → tdd-guide → code-reviewer
```

### Refactoring
```
/orchestrate refactor <description>
dev-planner → code-implementer → code-reviewer
```

## Automated Trigger Rules

Agents should be automatically suggested or invoked based on context:

### 1. Complex Requirement Detection
If user asks for a feature involving >3 files or new components:
- **Action**: Call `dev-planner` first via `/plan` command

### 2. Code Change Awareness
After significant implementation work:
- **Action**: Call `code-reviewer` via `/review` command

### 3. Error Handling
When user provides error logs or mentions crashes:
- **Action**: Call `explorer` or `bug-analyzer` for analysis

### 4. Test Coverage Needs
When implementing critical features or fixing bugs:
- **Action**: Suggest `tdd-guide` via `/tdd` command

## Parallel vs. Sequential Agent Invocation

### Sequential (Default)
Use when one agent's output is required for the next:
```
dev-planner (Plan) → code-implementer (Code) → code-reviewer (Review)
```

### Parallel (Advanced)
Use for independent analyses of the same state:
```
code-reviewer (Quality) + performance-optimizer (Speed)
```

## Proactive Agent Suggestions

When a specialized agent is relevant but not called, proactively suggest it:

> [!TIP]
> This task involves complex architectural changes. I recommend using the **dev-planner** agent to create a detailed plan before we start implementing. Would you like to proceed with `/plan` or `/orchestrate feature`?

## Handoff Protocol

When passing control between agents, provide structured handoff:

```markdown
## HANDOFF: [source-agent] → [target-agent]

### Context
[Summary of work completed]

### Findings & Decisions
[Key discoveries and technical decisions]

### Files Modified
[List of modified files]

### Open Questions
[Unresolved issues for next agent]

### Recommendations
[Suggested next steps]
```

## Best Practices

1. **Explicit Handoffs**: Always provide clear context when passing control
2. **Minimal Context**: Only pass necessary information to keep agents focused
3. **Feedback Loops**: If output is unsatisfactory, re-invoke with corrected context
4. **Choose Right Agent**: Use `code-implementer` for standard work, `tdd-guide` for test-first
5. **Plan First**: For multi-file changes, always start with `dev-planner`

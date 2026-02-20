# Agent Usage Rules

**RULE TYPE**: Global mandatory guidelines for agent selection and invocation.

All agents must follow these rules when deciding which specialized agent to invoke.

## Available Specialized Agents

### dev-planner (Planning)
- **Color**: Blue 🔵
- **Description**: Implementation planning specialist for complex features and refactoring
- **Output**: Detailed step-by-step plans with risk assessment and dependency analysis
- **Skills**: developer, api-designer, database-engineer

### code-implementer (Implementation)
- **Color**: Green 🟢
- **Description**: Production code implementer that transforms plans into clean, maintainable code
- **Output**: Well-documented, tested implementations following project conventions
- **Skills**: developer, quality-assurance

### tdd-guide (Test-Driven Development)
- **Color**: Purple 🟣
- **Description**: Test-Driven Development specialist enforcing RED-GREEN-REFACTOR cycle
- **Output**: Test cases and implementation with 80%+ coverage
- **Skills**: tdd-workflow, quality-assurance

### code-reviewer (Quality Assurance)
- **Color**: Yellow 🟡
- **Description**: Code quality auditor focused on security, performance, and maintainability
- **Output**: Comprehensive review reports with prioritized, actionable feedback
- **Skills**: quality-assurance, developer

### bug-analyzer (Bug Investigation & Code Exploration)
- **Color**: Red 🔴
- **Description**: Deep root cause investigator for bugs and code issues
- **Output**: Detailed execution flow analysis and fix strategies
- **Skills**: tdd-workflow, quality-assurance, performance-optimizer, developer

### story-generator (Requirements)
- **Color**: Cyan 🔷
- **Description**: User story generator that transforms requirements into structured stories
- **Output**: User-centric stories with acceptance criteria
- **Skills**: None (standalone)

### ui-sketcher (UI/UX Design)
- **Color**: Purple 🟣
- **Description**: UI/UX designer that creates ASCII interface mockups and interaction flows
- **Output**: Spatial design blueprints and user journey visualizations
- **Skills**: ui-ux-pro-max, frontend-design

### security-reviewer (Security Audit)
- **Color**: Red 🔴
- **Description**: Deep security audit specialist following OWASP guidelines
- **Output**: Comprehensive security reports with vulnerability details and remediation plans
- **Skills**: quality-assurance (security-audit)

### database-migration (Database Migration)
- **Color**: Cyan 🔷
- **Description**: Database migration specialist for schema changes and data migration
- **Output**: Migration plans with validation scripts and rollback strategies
- **Skills**: database-engineer

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
bug-analyzer → tdd-guide → code-reviewer
```

### Refactoring
```
/orchestrate refactor <description>
dev-planner → code-implementer → code-reviewer
```

## Proactive Agent Suggestions

When certain patterns are detected in user messages, AI should proactively suggest relevant agents:

### Bug/Error Detection
**Triggers**: User mentions "bug", "error", "crash", "broken", "not working", "fails", provides stack traces or error logs
**Action**: Suggest bug-analyzer agent
**Example**: "I see you're encountering an error. Let me use the bug-analyzer agent to investigate the root cause."

### Feature Request Detection
**Triggers**: User says "add feature", "implement", "build", "create", mentions multiple files or components, architectural changes
**Action**: Suggest dev-planner agent
**Example**: "This looks like a complex feature. Let me use the dev-planner agent to create a detailed plan first."

### Code Review Request
**Triggers**: User says "review", "check", "audit", "look at", "before merge", "is this good"
**Action**: Suggest code-reviewer agent
**Example**: "I'll use the code-reviewer agent to audit the changes for quality and security."

### Test Coverage Needs
**Triggers**: User mentions "TDD", "test first", "need tests", "coverage", "write tests"
**Action**: Suggest tdd-guide agent
**Example**: "I'll use the tdd-guide agent to implement this with test-first approach."

### Requirements Structuring
**Triggers**: User provides requirements, PRD, feature descriptions that need to be structured
**Action**: Suggest story-generator agent
**Example**: "Let me use the story-generator agent to convert these requirements into user stories."

### UI/UX Design Needs
**Triggers**: User mentions "UI", "interface", "design", "mockup", "layout", "user flow"
**Action**: Suggest ui-sketcher agent
**Example**: "I'll use the ui-sketcher agent to create an ASCII mockup of the interface."

### Performance Issues
**Triggers**: User mentions "slow", "performance", "optimization", "bottleneck", "latency"
**Action**: Suggest bug-analyzer agent for investigation
**Example**: "Let me use the bug-analyzer agent to investigate the performance bottleneck."

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
- **Action**: Call `bug-analyzer` for deep analysis

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

# Agent Usage Rules

Guidelines for selecting and invoking specialized agents.

## Specialized Agents

### dev-planner

- **Description**: Planning expert for complex features.
- **Trigger**: New feature requirements, complex refactoring, structural changes.
- **Output**: Detailed implementation plan and dependency graph.

### tdd-guide

- **Description**: Test-driven development expert.
- **Trigger**: Implementation phase of features or bug fixes.
- **Output**: Test cases and implementation that passes those tests.

### code-reviewer

- **Description**: Code quality and security expert.
- **Trigger**: After code changes, before git commit/push, or as part of orchestration.
- **Output**: Quality score and prioritized improvement suggestions.

### bug-analyzer

- **Description**: Error diagnosis expert.
- **Trigger**: Bug reports, error logs, production issues.
- **Output**: Root cause analysis and suggested fix.

## Automated Trigger Rules

Agents should be automatically suggested or invoked based on the context:

1. **Complex Requirement Detection**
   If the user asks for a feature involving >3 files or new components:
   - **Recommended Action**: Call `dev-planner` first.

2. **Code Change Awareness**
   After significant implementation work:
   - **Recommended Action**: Call `code-reviewer` for quality control.

3. **Error Handling**
   When the user provides error logs or mentions crashes:
   - **Recommended Action**: Call `bug-analyzer`.

4. **Integration Phase**
   Before moving to execution:
   - **Recommended Action**: Suggest `tdd-guide` to ensure test coverage.

## Parallel vs. Sequential Agent Invocation

### Sequential

Use when one agent's output is required for the next.

- **Chain**: `dev-planner` (Plan) → `tdd-guide` (Implement) → `code-reviewer` (Review)

### Parallel

Use for independent analyses of the same state.

- **Workflow**: `code-reviewer` (Quality) + `performance-optimizer` (Speed)

## Proactive Agent Suggestions

When a specialized agent is relevant but not called, proactively suggest it:

> [!TIP]
> This task involves complex architectural changes. I recommend using the **dev-planner** agent to create a detailed plan before we start implementing. Would you like to proceed with `/orchestrate feature`?

## Best Practices

- **Explicit Handoffs**: Always provide a clear context summary when passing control between agents.
- **Minimal Context**: Only pass the necessary information to keep agents focused.
- **Feedback Loops**: If an agent's output is unsatisfactory, re-invoke it with corrected context rather than moving forward.

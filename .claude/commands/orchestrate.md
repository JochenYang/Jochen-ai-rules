# Orchestrate Command

Sequential agent workflow for complex tasks. This command coordinates a chain of specialized **Agents** (defined in `.claude/agents/`) to complete features, bug fixes, or refactors.

## Usage

`/orchestrate [workflow-type] [task-description]`

## Workflow Types

### feature

Full feature implementation workflow:
`dev-planner` → `code-implementer` → `code-reviewer`

### feature-tdd

Test-driven feature implementation workflow:
`dev-planner` → `tdd-guide` → `code-reviewer`

### bugfix

Deep bug investigation and resolution workflow:
`explorer` → `tdd-guide` → `code-reviewer`

### refactor

Safe refactoring workflow:
`dev-planner` → `code-implementer` → `code-reviewer`

## Execution Pattern (INTERNAL)

1. **Invoke Agent**: The orchestrator switches to the specified Agent by loading its definition from `.claude/agents/[agent-name].md`.
2. **Collect Output**: Each Agent MUST capture its findings as a structured **HANDOFF** document.
3. **Pass Context**: The orchestrator relays the handoff to the next agent in the chain to ensure continuity.
4. **Aggregate Results**: Once the final agent finishes, the system generates a consolidated **Final Report**.

## Handoff Document Format

Agents communicate via internal Handoff documents:

```markdown
## HANDOFF: [previous-agent] → [next-agent]

### Context

[Summary of work completed by the previous agent]

### Findings & Decisions

[Key discoveries, variable states, or technical decisions]

### Files Modified

[List of modified files]

### Open Questions

[Unresolved issues for the next agent]

### Recommendations

[Suggested next steps]
```

## Example: Feature Workflow Execution

```bash
/orchestrate feature "Add user profile editing"
```

1. **Dev Planner Agent**
   - Analyze requirements and create implementation plan
   - Output: `HANDOFF: dev-planner → code-implementer`
2. **Code Implementer Agent**
   - Transform plan into production-ready code
   - Output: `HANDOFF: code-implementer → code-reviewer`
3. **Code Reviewer Agent**
   - Quality, security, and performance audit
   - Output: Final Orchestration Report

## Example: Bugfix Workflow Execution

```bash
/orchestrate bugfix "Fix race condition in Auth module"
```

1. **Explorer Agent**
   - Deep root cause analysis & Reproduction
   - Output: `HANDOFF: explorer → tdd-guide`
2. **TDD Guide Agent**
   - Reads analysis & Writes test case to fail first
   - Implements fix
   - Output: `HANDOFF: tdd-guide → code-reviewer`
3. **Code Reviewer Agent**
   - Security & Regression check
   - Output: Final Orchestration Report

## Final Report Format

```markdown
# ORCHESTRATION REPORT

Workflow: [type] | Task: [description]
Agents: [Path taken]

## SUMMARY

[One-paragraph executive summary of the mission]

## AGENT OUTPUTS

- Agent 1: [summary]
- Agent 2: [summary]
  ...

## FILES CHANGED

[Complete list of modified files]

## TEST RESULTS

[Summary of test passes/failures and coverage]

## RECOMMENDATION

[SHIP / NEEDS WORK / BLOCKED]
```

## Parallel Execution

For independent checks, run agents in parallel:

```markdown
### Parallel Phase

Run simultaneously:

- code-reviewer (Quality)
- explorer (Deep Analysis)

### Merge Results

Combine outputs into a single consolidated report.
```

## Available Agents

Located in `.claude/agents/`:

- **dev-planner**: Architecture and high-level strategy planning
- **code-implementer**: Production-ready code implementation
- **explorer**: Root cause analysis and deep debugging
- **tdd-guide**: Test-driven implementation specialist
- **code-reviewer**: Quality, security, and performance auditor
- **bug-analyzer**: Bug investigation and analysis
- **story-generator**: User story generation from requirements
- **ui-sketcher**: UI/UX design and prototyping

## Arguments

$ARGUMENTS:

- `feature <description>` - Planning → Code Implementation → Review
- `feature-tdd <description>` - Planning → TDD Implementation → Review
- `bugfix <description>` - Deep Exploration → TDD Fix → Review
- `refactor <description>` - Planning → Code Implementation → Review
- `custom <agents> <description>` - Custom sequence of agents (e.g. "dev-planner,code-implementer,code-reviewer")

## Tips

1. **Handoffs are mandatory**: Ensure state is passed between agents
2. **Planner first**: For multi-file changes, always start with `dev-planner`
3. **Choose the right workflow**: 
   - Use `feature` for standard implementation
   - Use `feature-tdd` when test coverage is critical
   - Use `bugfix` for debugging and fixing issues
4. **Code implementer vs TDD guide**: 
   - `code-implementer` for general feature development
   - `tdd-guide` for test-first development or bug fixes
